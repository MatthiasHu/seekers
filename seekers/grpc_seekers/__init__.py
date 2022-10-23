import grpc
from grpc._channel import _InactiveRpcError

from seekers.grpc_seekers import remote_control_types as types
from seekers.grpc_seekers.converters import *

import logging
import sys



class GrpcSeekersClientError(Exception): ...


class SessionTokenInvalidError(GrpcSeekersClientError): ...


class GameFullError(GrpcSeekersClientError): ...


class GrpcSeekersClient:
    def __init__(self, address: str = "localhost:7777"):
        self.channel = grpc.insecure_channel(address)
        self.stub = pb2_grpc.RemoteControlStub(self.channel)

    def join_session(self, ai_name: str) -> str:
        """Join the game and return the client_id."""
        try:
            return self.stub.JoinSession(SessionRequest(token=ai_name)).id
        except _InactiveRpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise SessionTokenInvalidError(f"Session token {ai_name=} is invalid. It can't be empty.") from e
            elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                raise GameFullError("The game is full.") from e

            raise

    def server_properties(self) -> dict[str, str]:
        return self.stub.PropertiesInfo(PropertiesRequest()).entries

    def entities(self) -> types._EntityReply:
        return self.stub.EntityStatus(EntityRequest())

    def players_info(self) -> types._PlayerReply:
        return self.stub.PlayerStatus(PlayerRequest())

    def send_command(self, player_id: str, id_: str, target: Vector, magnet: Magnet) -> str:
        return self.stub.CommandUnit(CommandRequest(token=player_id, id=id_, target=target, magnet=magnet)).message

    def __del__(self):
        self.channel.close()


def main():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, style="{", format="[{levelname}] {message}")
    logger = logging.getLogger("grpc_seekers-main")

    client = GrpcSeekersClient()

    logger.info("Joining session as 'test'...")
    player_id = client.join_session("test")

    logger.info(f"Joined session as {player_id=}")

    logger.info(f"Properties: {client.server_properties()!r}")

    while True:
        entity_reply = client.entities()
        player_reply = client.players_info()

        seekers, goals = entity_reply.seekers, entity_reply.goals
        camps, players = player_reply.camps, player_reply.players

        try:
            own_player = players[player_id]
        except IndexError as e:
            raise GrpcSeekersClientError("Invalid Response: Own player_id not in PlayerReply.players")

        try:
            own_camp = camps[own_player.camp_id]
        except IndexError as e:
            raise GrpcSeekersClientError("Invalid Response: Own camp not in PlayerReply.camps") from e

        own_seekers = {seeker_id: seekers[seeker_id] for seeker_id in own_player.seeker_ids}
        other_seekers = {seeker_id: seeker for seeker_id, seeker in seekers.items() if seeker_id not in own_seekers}

        logger.debug(f"Own seekers: {len(own_seekers)}, other seekers: {len(other_seekers)}, Teams: {len(players)}")
        logger.debug(f"Own Seeker ID: {list(own_seekers.values())[0].super.id}")

        for id_, seeker in seekers.items():
            ...
            # print(f"Seeker {id_}: {seeker.target.x}, {seeker.target.y}")
            # print(f"Seeker {id_}: {seeker.disable_counter}")


    print(f"Game Over.")


if __name__ == "__main__":
    main()
