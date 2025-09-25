from typing import Dict, List
from api.remote_participant import RemoteParticipant
from core.auction import Auction


class AuctionRoom:
    def __init__(self, auction:Auction):
        self.auction = auction
        self.participants:Dict[str,RemoteParticipant] = {}
        self.team_to_participants:Dict[int, List[RemoteParticipant]] = {}  # team_id -> RemoteParticipant

    def join(self, participant:RemoteParticipant):
        self.participants[participant.id] = participant

    def assign_participant(self, participant:RemoteParticipant, team_id:int):
        # remove existing association
        for participants in self.team_to_participants.values():
            if participant in participants:
                participants.remove(participant)
        if team_id not in self.team_to_participants:
            self.team_to_participants[team_id] = []
        if participant not in self.team_to_participants[team_id]:
            self.team_to_participants[team_id].append(participant)
        team = self.auction.teams.get(team_id)
        if team:
            participant.team = team
        return team

    def get_participant_team_ids(self, participant_id: str) -> List[int]:
        team_ids: List[int] = []
        for team_id, participants in self.team_to_participants.items():
            if any(p.id == participant_id for p in participants):
                team_ids.append(team_id)
        return team_ids

    def leave(self, participant_id: str) -> None:
        participant = self.participants.pop(participant_id, None)
        if participant is None:
            return
        participant.disconnect()
        for team_id, members in list(self.team_to_participants.items()):
            self.team_to_participants[team_id] = [p for p in members if p.id != participant_id]
            if not self.team_to_participants[team_id]:
                del self.team_to_participants[team_id]
    
    async def broadcast(self, message: dict):
        to_remove = []
        for c in self.participants.values():
            try:
                await c._ws.send_json(message)
            except Exception:
                to_remove.append(c.id)
        for pid in to_remove:
            self.leave(pid)
