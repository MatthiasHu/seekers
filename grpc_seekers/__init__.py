import logging
import sys

import grpc
from google._upb._message import MessageMeta
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from grpc._channel import _InactiveRpcError

from grpc_seekers import remote_control_pb2_grpc as pb2_grpc
from grpc_seekers import remote_control_types as types

# noinspection DuplicatedCode
SessionRequest: MessageMeta = pb2_grpc.remote__control__pb2.SessionRequest
PropertiesRequest: MessageMeta = pb2_grpc.remote__control__pb2.PropertiesRequest
PropertiesReply: MessageMeta = pb2_grpc.remote__control__pb2.PropertiesReply
SessionReply: MessageMeta = pb2_grpc.remote__control__pb2.SessionReply
EntityRequest: MessageMeta = pb2_grpc.remote__control__pb2.EntityRequest
EntityReply: MessageMeta = pb2_grpc.remote__control__pb2.EntityReply
PlayerRequest: MessageMeta = pb2_grpc.remote__control__pb2.PlayerRequest
PlayerReply: MessageMeta = pb2_grpc.remote__control__pb2.PlayerReply
# noinspection DuplicatedCode
CommandRequest: MessageMeta = pb2_grpc.remote__control__pb2.CommandRequest
CommandReply: MessageMeta = pb2_grpc.remote__control__pb2.CommandReply
GoalStatus: MessageMeta = pb2_grpc.remote__control__pb2.GoalStatus
PlayerStatus: MessageMeta = pb2_grpc.remote__control__pb2.PlayerStatus
CampStatus: MessageMeta = pb2_grpc.remote__control__pb2.CampStatus
SeekerStatus: MessageMeta = pb2_grpc.remote__control__pb2.SeekerStatus
Magnet: EnumTypeWrapper = pb2_grpc.remote__control__pb2.Magnet
PhysicalStatus: MessageMeta = pb2_grpc.remote__control__pb2.PhysicalStatus
Vector: MessageMeta = pb2_grpc.remote__control__pb2.Vector


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

    def properties_info(self) -> dict[str, str]:
        return self.stub.PropertiesInfo(PropertiesRequest()).entries

    def entity_status(self) -> EntityReply:
        return self.stub.EntityStatus(EntityRequest())

    def player_status(self) -> PlayerReply:
        return self.stub.PlayerStatus(PlayerRequest())

    def send_command(self, client_id: str, id_: str, target: Vector, magnet: Magnet) -> CommandReply:
        return self.stub.CommandUnit(CommandRequest(token=client_id, id=id_, target=target, magnet=magnet))

    def __del__(self):
        self.channel.close()




def main():
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, style="{", format="[{levelname}] {message}")
    logger = logging.getLogger("grpc_seekers-main")

    client = GrpcSeekersClient()

    logger.info("Joining session as 'test'...")
    client_id = client.join_session("test")

    logger.info(f"Joined session as {client_id=}")

    logger.info(f"Properties: {client.properties_info()!r}")

    # while (ss := client.get_session_status().status) != SessionStatus.CLOSED:
    #     entity_reply: types._EntityReply = client.get_entity_status()
    #     player_reply: types._PlayerReply = client.get_player_status()
    #
    #     seekers, goals = entity_reply.seekers, entity_reply.goals
    #
    #     for id_, seeker in seekers.items():
    #         print(f"Seeker {id_}: {seeker.target.x}, {seeker.target.y}")
    #         # print(f"Seeker {id_}: {seeker.disable_counter}")

    print(f"Game Over.")


if __name__ == "__main__":
    main()
