import grpc
from google._upb._message import MessageMeta
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

from grpc_seekers import remote_control_pb2_grpc as pb2_grpc
from grpc_seekers import remote_control_types as types

# noinspection DuplicatedCode
SessionRequest: MessageMeta = pb2_grpc.remote__control__pb2.SessionRequest
SessionStatus: EnumTypeWrapper = pb2_grpc.remote__control__pb2.SessionStatus
SessionReply: MessageMeta = pb2_grpc.remote__control__pb2.SessionReply
EntityRequest: MessageMeta = pb2_grpc.remote__control__pb2.EntityRequest
EntityReply: MessageMeta = pb2_grpc.remote__control__pb2.EntityReply
PlayerRequest: MessageMeta = pb2_grpc.remote__control__pb2.PlayerRequest
PlayerReply: MessageMeta = pb2_grpc.remote__control__pb2.PlayerReply
WorldRequest: MessageMeta = pb2_grpc.remote__control__pb2.WorldRequest
WorldReply: MessageMeta = pb2_grpc.remote__control__pb2.WorldReply
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


class GrpcSeekersClient:
    def __init__(self, address: str = "localhost:7777"):
        self.channel = grpc.insecure_channel(address)
        self.stub = pb2_grpc.RemoteControlStub(self.channel)

    def get_session_status(self, token: str = "TODO") -> SessionReply:
        return self.stub.SessionStatus(SessionRequest(token=token))

    def get_entity_status(self) -> EntityReply:
        return self.stub.EntityStatus(EntityRequest())

    def get_player_status(self) -> PlayerReply:
        return self.stub.PlayerStatus(PlayerRequest())

    def get_world(self) -> WorldReply:
        return self.stub.WorldStatus(WorldRequest())

    def send_command(self, token: str, id_: str, target: Vector, magnet: Magnet) -> CommandReply:
        return self.stub.CommandUnit(CommandRequest(token=token, id=id_, target=target, magnet=magnet))


def main():
    client = GrpcSeekersClient()

    while (ss := client.get_session_status().status) != SessionStatus.CLOSED:
        world_reply: types._WorldReply = client.get_world()
        entity_reply: types._EntityReply = client.get_entity_status()
        player_reply: types._PlayerReply = client.get_player_status()

        seekers, goals = entity_reply.seekers, entity_reply.goals
        camps = world_reply.camps

        for id_, seeker in seekers.items():
            print(f"Seeker {id_}: {seeker.target.x}, {seeker.target.y}")
            # print(f"Seeker {id_}: {seeker.disable_counter}")


    print(f"Game Over. {ss=}")


if __name__ == "__main__":
    main()
