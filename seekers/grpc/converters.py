from google._upb._message import MessageMeta

from seekers.grpc import seekers_pb2_grpc as pb2_grpc
from seekers.grpc import types
import seekers

SessionRequest: MessageMeta = getattr(pb2_grpc.seekers__pb2, "SessionRequest")
PropertiesRequest: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PropertiesRequest")
PropertiesReply: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PropertiesReply")
SessionReply: MessageMeta = getattr(pb2_grpc.seekers__pb2, "SessionReply")
EntityRequest: MessageMeta = getattr(pb2_grpc.seekers__pb2, "EntityRequest")
EntityReply: MessageMeta = getattr(pb2_grpc.seekers__pb2, "EntityReply")
PlayerRequest: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PlayerRequest")
PlayerReply: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PlayerReply")
CommandRequest: MessageMeta = getattr(pb2_grpc.seekers__pb2, "CommandRequest")
CommandReply: MessageMeta = getattr(pb2_grpc.seekers__pb2, "CommandReply")
GoalStatus: MessageMeta = getattr(pb2_grpc.seekers__pb2, "GoalStatus")
PlayerStatus: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PlayerStatus")
CampStatus: MessageMeta = getattr(pb2_grpc.seekers__pb2, "CampStatus")
SeekerStatus: MessageMeta = getattr(pb2_grpc.seekers__pb2, "SeekerStatus")
PhysicalStatus: MessageMeta = getattr(pb2_grpc.seekers__pb2, "PhysicalStatus")
Vector: MessageMeta = getattr(pb2_grpc.seekers__pb2, "Vector")


def convert_vector(vector: types._Vector) -> seekers.Vector:
    return seekers.Vector(vector.x, vector.y)


def convert_vector_back(vector: seekers.Vector) -> Vector:
    return Vector(x=vector.x, y=vector.y)


def convert_seeker(seeker: types._SeekerStatus, props: dict[str, str]) -> seekers.Seeker:
    out = seekers.Seeker(
        seeker.super.id,
        convert_vector(seeker.super.position),
        convert_vector(seeker.super.velocity),
        float(props["seeker.mass"]),
        float(props["seeker.radius"])
    )

    out.magnet.strength = seeker.magnet
    out.target = convert_vector(seeker.target)
    out.disable_counter = seeker.disable_counter

    return out


def convert_physical_back(physical: seekers.Physical) -> PhysicalStatus:
    return PhysicalStatus(
        id=physical.id,
        acceleration=convert_vector_back(physical.acceleration),
        velocity=convert_vector_back(physical.velocity),
        position=convert_vector_back(physical.position)
    )


def convert_seeker_back(seeker: seekers.InternalSeeker) -> SeekerStatus:
    out = SeekerStatus(
        super=convert_physical_back(seeker),
        player_id=seeker.owner.id,
        magnet=seeker.magnet.strength,
        target=convert_vector_back(seeker.target),
        disable_counter=seeker.disabled_counter
    )

    return out


def convert_goal(goal: types._GoalStatus, props: dict[str, str], camps: list[seekers.Camp]) -> seekers.Goal:
    out = seekers.Goal(
        goal.super.id,
        convert_vector(goal.super.position),
        convert_vector(goal.super.velocity),
        float(props["goal.mass"]),
        float(props["goal.radius"])
    )

    out.owned_for = goal.time_owned
    out.owned_by = next((camp for camp in camps if camp.owner.id == goal.camp_id), None)

    return out


def convert_goal_back(goal: seekers.InternalGoal) -> GoalStatus:
    return GoalStatus(
        super=convert_physical_back(goal),
        camp_id=goal.owner.id,
        time_owned=goal.owned_for
    )


def convert_color(color: str):
    return tuple(int(color[i:i + 2], base=16) for i in (2, 4, 6))


def convert_color_back(color: tuple[int, int, int]):
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def convert_player(player: types._PlayerStatus, all_seekers: dict[str, seekers.Seeker]) -> seekers.Player:
    out = seekers.Player(
        player.id,
        f"<{player.id}>",
        player.score,
        [all_seekers[seeker_id] for seeker_id in player.seeker_ids],
    )

    out._color = convert_color(player.color)

    return out


def convert_player_back(player: seekers.Player) -> PlayerStatus:
    return PlayerStatus(
        id=player.id,
        camp_id=player.camp.id,
        color=convert_color_back(player.color),
        score=player.score,
        seeker_ids=[seeker.id for seeker in player.seekers.values()]
    )


def convert_camp(camp: types._CampStatus, all_players: dict[str, seekers.Player]) -> seekers.Camp:
    out = seekers.Camp(
        camp.id,
        all_players[camp.player_id],
        convert_vector(camp.position),
        camp.width,
        camp.height
    )

    return out
