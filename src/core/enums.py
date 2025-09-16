from enum import Enum, auto

class PlayerRole(Enum):
    GOALKEEPER = P = Gk = Pt = auto()
    DEFENDER = D = Df = auto()
    MIDFIELDER = C = Md = Cc = auto()
    FORWARD = A = Fw = auto()

class AuctionMode(str, Enum):
    TEAM_DRIVEN = "team_driven"
    HOST_DRIVEN = "host_driven"
    SYSTEM_DRIVEN = "system_driven"