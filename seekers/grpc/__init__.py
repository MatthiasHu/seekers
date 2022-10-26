import time

import grpc
from grpc._channel import _InactiveRpcError

from seekers import DecideCallable
from seekers.grpc import seekers_proto_types as types
from seekers.grpc.converters import *
import seekers

import logging


class GrpcSeekersClientError(Exception): ...


class SessionTokenInvalidError(GrpcSeekersClientError): ...


class GameFullError(GrpcSeekersClientError): ...


class ServerUnavailableError(GrpcSeekersClientError): ...


class GrpcSeekersRawClient:
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
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise SessionTokenInvalidError(f"Session token {self.token=} is invalid. It can't be empty.") from e
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
            raise ServerUnavailableError("Channel is not ready.")

        try:
            self.stub.CommandUnit(CommandRequest(token=self.token, id=id_, target=target, magnet=magnet))
        except _InactiveRpcError as e:
            if e.code() == grpc.StatusCode.CANCELLED:
                # We don't know, why this happens.
                # The CommandUnit service is called
                # though, so we can just ignore the error.
                ...
            else:
                raise


    def __del__(self):
        self.channel.close()


class GrpcSeekersClient:
    def __init__(self, token: str, decide_function: DecideCallable, address: str = "localhost:7777"):
        self.decide_function = decide_function

        self._logger = logging.getLogger(self.__class__.__name__)

        self.client = GrpcSeekersRawClient(token, address)

        self._logger.debug(f"Joining session with {token=}...")
        self.player_id = self.client.join_session()

        self._logger.debug(f"Joined session as {self.player_id=}")

        self._logger.debug(f"Properties: {self.client.server_properties()!r}")

        self.last_gametime = 0

    def mainloop(self):
        while 1:
            self.tick()

    def tick(self):
        entity_reply = self.client.entities()
        if entity_reply.passed_playtime == self.last_gametime:
            return

        if (entity_reply.passed_playtime - self.last_gametime) > 1:
            self._logger.warning(f"Missed {entity_reply.passed_playtime - self.last_gametime} ticks.")

        self.last_gametime = entity_reply.passed_playtime

        props = self.client.server_properties()

        player_reply = self.client.players_info()

        all_seekers, goals = entity_reply.seekers, entity_reply.goals
        camps, players = player_reply.camps, player_reply.players

        try:
            own_player = players[self.player_id]
        except IndexError as e:
            raise GrpcSeekersClientError("Invalid Response: Own player_id not in PlayerReply.players")

        # self._logger.debug(
        #     f"Own seekers: {len(own_seekers)}, other seekers: {len(other_seekers)}, Teams: {len(players)}")

        converted_seekers = {seeker_id: convert_seeker(seeker, props) for seeker_id, seeker in all_seekers.items()}

        converted_players = {player_id: convert_player(player, converted_seekers) for player_id, player in
                             players.items()}

        converted_camps = {player_id: convert_camp(camp, converted_players) for player_id, camp in camps.items()}

        converted_goals = [convert_goal(goal, props) for goal in goals.values()]

        converted_my_seekers = [converted_seekers[seeker_id] for seeker_id in own_player.seeker_ids]
        converted_other_seekers = [converted_seekers[seeker_id] for seeker_id in all_seekers if
                                   seeker_id not in own_player.seeker_ids]

        converted_other_players = [converted_players[player_id] for player_id in players if
                                   player_id != self.player_id]

        try:
            converted_own_camp = converted_camps[own_player.camp_id]
        except IndexError as e:
            raise GrpcSeekersClientError("Invalid Response: Own camp not in PlayerReply.camps") from e

        converted_world = seekers.World(float(props["map.width"]), float(props["map.height"]))

        new_seekers = self.decide_function(
            converted_my_seekers,
            converted_other_seekers,
            list(converted_seekers.values()),
            converted_goals,
            converted_other_players,
            converted_own_camp,
            list(converted_camps.values()),
            converted_world,
            entity_reply.passed_playtime,
        )

        self.send_updates(new_seekers)

    def send_updates(self, new_seekers: list[seekers.Seeker]):
        cur_time = time.perf_counter()
        # if self._last_update:
        #     dt = cur_time - self._last_update
        #     self._logger.debug(f"Last update took {dt:.3f}s ({1 / dt:.0f}Hz)")

        self._last_update = cur_time

        for seeker in new_seekers:
            try:
                self.client.send_command(seeker.id, convert_vector_back(seeker.target), seeker.magnet.strength)
            except _InactiveRpcError as e:
                if e.code() == grpc.StatusCode.CANCELLED:
                    self._logger.error("Server responded with CANCELLED on CommandUnit.")
                else:
                    raise


def main():
    ...


if __name__ == "__main__":
    main()
