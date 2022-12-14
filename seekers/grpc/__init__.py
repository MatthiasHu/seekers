import grpc
from grpc._channel import _InactiveRpcError
from concurrent.futures import ThreadPoolExecutor
import time
import logging
import threading

from seekers import string_hash_color
from seekers.grpc import seekers_proto_types as types
from seekers.grpc.converters import *


class GrpcSeekersClientError(Exception): ...


class SessionTokenInvalidError(GrpcSeekersClientError): ...


class GameFullError(GrpcSeekersClientError): ...


class ServerUnavailableError(GrpcSeekersClientError): ...


class GrpcSeekersRawClient:
    """A client for a Seekers gRPC game.
    It is called "raw" because it is nothing but a wrapper for the gRPC services."""

    def __init__(self, token: str, address: str = "localhost:7777"):
        self.token = token

        self.channel = grpc.insecure_channel(address)
        self.stub = pb2_grpc.SeekersStub(self.channel)

        self.channel_connectivity_status = None
        self.channel.subscribe(self._channel_connectivity_callback, try_to_connect=True)

    def _channel_connectivity_callback(self, state):
        self.channel_connectivity_status = state

    def join_session(self) -> str:
        """Try to join the game and return our player_id."""
        try:
            return self.stub.JoinSession(SessionRequest(token=self.token)).id
        except _InactiveRpcError as e:
            if e.code() in [grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.INVALID_ARGUMENT]:
                raise SessionTokenInvalidError(f"Session token {self.token!r} is invalid. It can't be empty.") from e
            elif e.code() == grpc.StatusCode.ALREADY_EXISTS:
                raise SessionTokenInvalidError(f"Session token {self.token!r} is already in use.") from e
            elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                raise GameFullError("The game is full.") from e
            elif e.code() == grpc.StatusCode.UNAVAILABLE:
                raise ServerUnavailableError(
                    f"The server is unavailable. Is it running already?"
                ) from e
            raise

    def server_properties(self) -> dict[str, str]:
        return self.stub.PropertiesInfo(PropertiesRequest()).entries

    def entities(self) -> types._EntityReply:
        return self.stub.EntityStatus(EntityRequest())

    def players_info(self) -> types._PlayerReply:
        return self.stub.PlayerStatus(PlayerRequest())

    def send_command(self, id_: str, target: Vector, magnet: float) -> None:
        if self.channel_connectivity_status != grpc.ChannelConnectivity.READY:
            raise ServerUnavailableError("Channel is not ready. Or game ended.")

        try:
            self.stub.CommandUnit(CommandRequest(token=self.token, id=id_, target=target, magnet=magnet))
        except _InactiveRpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                # We don't know why this happens.
                # The CommandUnit procedure is called
                # though, so we can just ignore the error.
                ...
            else:
                raise

    def __del__(self):
        self.channel.close()


class GrpcSeekersClient:
    """A client for a Seekers gRPC game. It contains a ``GrpcSeekersRawClient`` and implements a mainloop.
    The ``decide_function`` is called in a loop and the output of that function is sent to the server."""

    def __init__(self, token: str, decide_function: seekers.DecideCallable, address: str = "localhost:7777"):
        self._logger = logging.getLogger(self.__class__.__name__)

        self.decide_function = decide_function
        self.client = GrpcSeekersRawClient(token, address)

        self._logger.debug(f"Joining session with {token=}...")
        self.player_id = self.client.join_session()

        self._logger.debug(f"Joined session as {self.player_id=}")
        self._logger.debug(f"Properties: {self.client.server_properties()!r}")

        self.last_gametime = -1

    def mainloop(self):
        """Start the mainloop. This function blocks until the game ends."""
        while 1:
            self.tick()

    def get_ai_input(self) -> seekers.AIInput:
        # wait for the next game tick
        while 1:
            entity_reply = self.client.entities()
            if entity_reply.passed_playtime != self.last_gametime:
                break

            time.sleep(0.01)

        if (entity_reply.passed_playtime - self.last_gametime) > 1:
            self._logger.info(f"Missed time: {entity_reply.passed_playtime - self.last_gametime}")

        self.last_gametime = entity_reply.passed_playtime

        props = self.client.server_properties()
        config = seekers.Config.from_properties(props)
        player_reply = self.client.players_info()
        all_seekers, goals = entity_reply.seekers, entity_reply.goals
        camps, players = player_reply.camps, player_reply.players

        # Attribute 'owner' of seekers intentionally left None, we set it when assigning the seekers to the players.
        # noinspection PyTypeChecker
        converted_seekers = {s_id: convert_seeker(s, None, config) for s_id, s in all_seekers.items()}

        converted_players = {}
        for p_id, p in players.items():
            # The player's camp attribute is not set yet. This is done when converting the camps.
            converted_player = convert_player(p)

            for seeker_id in p.seeker_ids:
                try:
                    converted_seeker = converted_seekers[seeker_id]
                except KeyError as e:
                    raise GrpcSeekersClientError(
                        f"Invalid Response: Player {p_id!r} has seeker {seeker_id!r} but it is not in "
                        f"EntityReply.seekers."
                    ) from e
                converted_player.seekers[seeker_id] = converted_seeker
                converted_seeker.owner = converted_player

            converted_players[p_id] = converted_player

        assert all(s.owner is not None for s in converted_seekers.values()), \
            GrpcSeekersClientError("Invalid Response: Some seekers have no owner.")

        converted_camps = {}
        for c_id, c in camps.items():
            try:
                owner = converted_players[c.player_id]
            except KeyError as e:
                raise GrpcSeekersClientError(
                    f"Invalid Response: Camp {c_id!r} has invalid owner {c.player_id!r}."
                ) from e

            converted_camp = convert_camp(c, owner)

            # Set the player's camp attribute as stated above.
            owner.camp = converted_camp

        try:
            me = converted_players[self.player_id]
        except IndexError as e:
            raise GrpcSeekersClientError("Invalid Response: Own player_id not in PlayerReply.players.") from e

        assert all(p.camp is not None for p in converted_players.values()), \
            GrpcSeekersClientError("Invalid Response: Some players have no camp.")

        converted_other_seekers = [s for s in converted_seekers.values() if s.owner != me]
        converted_goals = [convert_goal(g, converted_camps, config) for g in goals.values()]
        converted_other_players = [p for p in converted_players.values() if p != me]

        try:
            converted_world = seekers.World(float(props["map.width"]), float(props["map.height"]))
        except KeyError as e:
            raise GrpcSeekersClientError("Invalid Response: Essential properties missing.") from e

        return (
            list(me.seekers.values()),
            converted_other_seekers,
            list(converted_seekers.values()),
            converted_goals,
            converted_other_players,
            me.camp,
            list(converted_camps.values()),
            converted_world,
            entity_reply.passed_playtime,
        )

    def tick(self):
        """Call the ``decide_function`` and send the output to the server."""

        ai_input = self.get_ai_input()

        new_seekers = self.decide_function(*ai_input)

        self.send_updates(new_seekers)

    def send_updates(self, new_seekers: list[seekers.Seeker]):
        self._last_update = time.perf_counter()

        for seeker in new_seekers:
            self.client.send_command(seeker.id, convert_vector_back(seeker.target), seeker.magnet.strength)


class GrpcSeekersServicer(pb2_grpc.SeekersServicer):
    """A Seekers game servicer. It implements all needed gRPC services and is compatible with the
    ``GrpcSeekersRawClient``. It stores a reference to the game to have full control over it."""
    def __init__(self, seekers_game: seekers.SeekersGame, game_start_event: threading.Event):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.seekers_game = seekers_game
        self.game_start_event = game_start_event

    def JoinSession(self, request: SessionRequest, context: grpc.ServicerContext) -> SessionReply:
        # validate requested token
        requested_name = request.token.strip()

        if requested_name in {p.name for p in self.seekers_game.players.values()}:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Requested name {requested_name!r} already taken.")
            return

        if not requested_name:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT,
                          f"Requested name must not be empty or only consist of whitespace.")
            return

        # create new player
        player = seekers.GRPCClientPlayer(
            seekers.get_id("Player"), requested_name, string_hash_color(requested_name), 0, {}
        )

        # add player to game
        try:
            self.seekers_game.add_player(player)
        except seekers.GameFullError:
            context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "Game is full.")
            return

        self._logger.info(f"Player {player.name!r} joined the game. ({player.id})")
        # return player id
        return SessionReply(id=player.id)

    def PropertiesInfo(self, request: PropertiesRequest, context) -> PropertiesReply:
        return PropertiesReply(entries=self.seekers_game.config.to_properties())

    def EntityStatus(self, request: EntityRequest, context) -> EntityReply:
        self.game_start_event.wait()
        return EntityReply(
            seekers={s_id: convert_seeker_back(s) for s_id, s in self.seekers_game.seekers.items()},
            goals={goal.id: convert_goal_back(goal) for goal in self.seekers_game.goals},
            passed_playtime=self.seekers_game.ticks,
        )

    def PlayerStatus(self, request: PlayerRequest, context) -> PlayerReply:
        self.game_start_event.wait()
        players = {
            # filter out players whose camp has not been set yet, meaning they are still uninitialized
            p_id: convert_player_back(p) for p_id, p in self.seekers_game.players.items() if p.camp is not None
        }

        return PlayerReply(
            players=players,
            camps={c.id: convert_camp_back(c) for c in self.seekers_game.camps}
        )

    def CommandUnit(self, request: CommandRequest, context) -> CommandReply:
        self.game_start_event.wait()
        try:
            seeker = self.seekers_game.seekers[request.id]
        except KeyError:
            context.abort(grpc.StatusCode.NOT_FOUND, f"Seeker with id {request.id!r} not found in the game.")
            return

        # check if seeker is owned by player
        if seeker.owner.name != request.token:
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                f"Seeker with id {request.id!r} is not owned by player {request.token!r}."
            )
            return

        seeker.target = convert_vector(request.target)
        seeker.magnet.strength = request.magnet

        # noinspection PyTypeChecker
        ai: seekers.GRPCClientPlayer = seeker.owner
        ai.was_updated.set()

        return CommandReply()


class GrpcSeekersServer:
    """A wrapper around the ``GrpcSeekersServicer`` that handles the gRPC server."""
    def __init__(self, seekers_game: seekers.SeekersGame, address: str = "localhost:7777"):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f"Starting server on {address=}")

        self.game_start_event = threading.Event()

        self.server = grpc.server(ThreadPoolExecutor())
        pb2_grpc.add_SeekersServicer_to_server(GrpcSeekersServicer(seekers_game, self.game_start_event), self.server)
        self.server.add_insecure_port(address)

    def start(self):
        self.server.start()

    def start_game(self):
        self.game_start_event.set()

    def stop(self):
        self.server.stop(None)
