from seekers.grpc_seekers import remote_control_pb2_grpc as pb2_grpc
from google._upb._message import MessageMeta
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper

import seekers

SessionRequest: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "SessionRequest")
PropertiesRequest: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PropertiesRequest")
PropertiesReply: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PropertiesReply")
SessionReply: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "SessionReply")
EntityRequest: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "EntityRequest")
EntityReply: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "EntityReply")
PlayerRequest: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PlayerRequest")
PlayerReply: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PlayerReply")
CommandRequest: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "CommandRequest")
CommandReply: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "CommandReply")
GoalStatus: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "GoalStatus")
PlayerStatus: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PlayerStatus")
CampStatus: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "CampStatus")
SeekerStatus: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "SeekerStatus")
Magnet: EnumTypeWrapper = getattr(pb2_grpc.remote__control__pb2, "Magnet")
PhysicalStatus: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "PhysicalStatus")
Vector: MessageMeta = getattr(pb2_grpc.remote__control__pb2, "Vector")


def convert_vector(vector: Vector) -> seekers.Vector:
    return seekers.Vector(vector.x, vector.y)


def convert_seeker(seeker: SeekerStatus) -> seekers.Seeker:
    out = seekers.Seeker(
        convert_vector(seeker.super.position),
        convert_vector(seeker.super.velocity),
    )

    out.magnet = seeker.magnet
    out.target = convert_vector(seeker.target)
    out.disable_counter = seeker.disable_counter

    return out


def convert_goal(goal: GoalStatus) -> seekers.Goal:
    out = seekers.Goal(
        convert_vector(goal.super.position),
        convert_vector(goal.super.velocity),
    )

    out.scoring_time = goal.time_owned

    return out


def convert_player(player: PlayerStatus) -> seekers.Player:
    out = seekers.Player(player.id, player.camp_id)

    out.seekers = player.seeker_ids

    return out
