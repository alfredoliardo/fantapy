from typing import Dict, List
from api.remote_participant import RemoteParticipant
from core.auction import Auction


class AuctionRoom:
    def __init__(self, auction:Auction):
        self.auction = auction
        self.connections:List[RemoteParticipant] = []
        self.team_to_participants:Dict[int, List[RemoteParticipant]] = {}  # team_id -> RemoteParticipant

    def join(self, participant:RemoteParticipant):
        self.connections.append(participant)

    def assign_participant(self, participant:RemoteParticipant, team_id:int):
        if team_id not in self.team_to_participants:
            self.team_to_participants[team_id] = []
        self.team_to_participants[team_id].append(participant)
    
    async def broadcast(self, message: dict):
        to_remove = []
        for c in self.connections:
            try:
                await c._ws.send_json(message)
            except Exception:
                to_remove.append(c)
        for pid in to_remove:
            self.connections.remove(pid)