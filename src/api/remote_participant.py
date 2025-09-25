import asyncio
import uuid
from typing import Dict, List, Optional

from fastapi import WebSocket

from core.bid import Bid
from core.bidder import IBidder
from core.bidding_strategies import BiddingStrategy, FreeBiddingStrategy
from core.caller import ICaller
from core.player import Player
from core.team import Team


class RemoteParticipant(ICaller, IBidder):
    """Partecipante remoto che si connette via WebSocket."""

    def __init__(self, participant_id: str, username: str, ws: WebSocket):
        self._id = participant_id
        self._name = username
        self._ws = ws
        self._team: Optional[Team] = None
        self._connected = True
        self._pending_requests: Dict[str, asyncio.Future] = {}

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def get_label(self) -> str:
        return f"Remote: {self._name}"

    @property
    def team(self) -> Optional[Team]:
        return self._team

    @team.setter
    def team(self, value: Team):
        self._team = value

    def disconnect(self) -> None:
        if not self._connected:
            return
        self._connected = False
        for future in list(self._pending_requests.values()):
            if not future.done():
                future.set_exception(ConnectionError("Participant disconnected"))
        self._pending_requests.clear()

    def push_message(self, message: dict) -> None:
        if not self._connected:
            return
        request_id = message.get("request_id")
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests.pop(request_id)
            if not future.done():
                future.set_result(message)

    async def _await_response(self, request_id: str, expected_type: str) -> Optional[dict]:
        if not self._connected:
            raise ConnectionError("Participant disconnected")
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        self._pending_requests[request_id] = future
        try:
            response = await future
        finally:
            self._pending_requests.pop(request_id, None)
        if response is None:
            return None
        if response.get("type") != expected_type:
            raise ValueError(f"Unexpected response type: {response.get('type')} (expected {expected_type})")
        return response

    async def _request(self, payload: dict, expected_response: str) -> Optional[dict]:
        if not self._connected:
            raise ConnectionError("Participant disconnected")
        request_id = uuid.uuid4().hex
        payload = {
            **payload,
            "request_id": request_id,
            "participant_id": self.id,
        }
        await self._ws.send_json(payload)
        try:
            return await self._await_response(request_id, expected_response)
        except ConnectionError:
            return None

    async def get_bid(self, player: Player) -> Optional[float]:
        team = self.team
        response = await self._request(
            {
                "type": "place_bid_request",
                "player": {
                    "player_id": player.player_id,
                    "name": player.name,
                    "role": player.role.name,
                    "real_team": player.realTeam,
                },
                "team": {
                    "id": team.id if team else None,
                    "name": team.name if team else None,
                },
            },
            "place_bid_response",
        )
        if not response:
            return None
        amount = response.get("amount")
        if amount is None:
            return None
        try:
            bid_value = float(amount)
        except (TypeError, ValueError):
            return None
        if bid_value <= 0:
            return None
        if team is not None and not team.can_afford(bid_value):
            return None
        return bid_value

    def place_bid(self, player: Player, amount: float) -> Bid:
        if self.team is None:
            raise Exception("Bidder has no team assigned")
        return Bid(player=player, amount=amount, team=self.team)

    async def choose_player(self, player_pool: List[Player]) -> Optional[Player]:
        response = await self._request(
            {
                "type": "choose_player_request",
                "player_pool": [
                    {
                        "player_id": p.player_id,
                        "name": p.name,
                        "role": p.role.name,
                        "real_team": p.realTeam,
                    }
                    for p in player_pool
                ],
            },
            "choose_player_response",
        )
        if not response:
            return None
        player_id = response.get("player_id")
        for player in player_pool:
            if player.player_id == player_id:
                return player
        return None

    async def choose_bidding_strategy(self) -> BiddingStrategy:
        await self._request(
            {
                "type": "choose_bidding_strategy_request",
            },
            "choose_bidding_strategy_response",
        )
        # Placeholder: ritorna sempre la strategia "free"
        return FreeBiddingStrategy(market_rule=None)  # type: ignore[arg-type]
