import asyncio
from typing import Callable, Dict, List, Optional
from core.bid import Bid
from core.bidder import IBidder
from core.caller import ICaller
from core.calling_strategy.base import CallingStrategy
from core.events import AuctionEvent, BidPlaced
from core.player_pool import PlayerPool
from core.team import Team
from core.turn import Turn


class Auction:
    def __init__(
        self,
        auction_id:str,
        auction_name:str,
        teams:int = 8     
    ) -> None:
    
        self.auction_id = auction_id
        self.name = auction_name

        self.teams:Dict[int, Team] = self._generate_teams(teams)

        self.player_pool:PlayerPool = PlayerPool()

        self.turns:List[Turn] = []
 
        self.started = False

        self.current_turn:Optional[Turn] = None
        # lista di callback sottoscritte
        self._subscribers: Dict[str, List[Callable[[AuctionEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[AuctionEvent], None]) -> None:
        """
        Sottoscrivi una callback ad un tipo di evento.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[AuctionEvent], None]) -> None:
        """
        Rimuovi una sottoscrizione.
        """
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]

    def _publish(self, event: AuctionEvent) -> None:
        """
        Pubblica un evento a tutti i sottoscrittori registrati.
        """
        # notifica sottoscrittori specifici per tipo
        if event.type in self._subscribers:
            for cb in list(self._subscribers[event.type]):
                cb(event)

        # notifica sottoscrittori "wildcard" (se registrati con "*")
        if "*" in self._subscribers:
            for cb in list(self._subscribers["*"]):
                cb(event)

    def _generate_teams(self, n: int) -> dict[int, Team]:
        return {
            i: Team(
                id=i,
                name=f"Team {i}"
            )
            for i in range(1, n + 1)
        }


    async def start(self):
        if self.started:
            raise ValueError("Auction already started")
        self.started = True
        await self._next_turn()


        return
    
    async def _next_turn(self):
        # Ottieni i possibili caller dalla strategia
        callers: List[ICaller] = self.calling_strategy.next_caller()
        bidders: List[IBidder] = []  # qui popolerai i bidder ammessi

        # Lancia in parallelo la richiesta a tutti i caller
        tasks = {
            asyncio.create_task(c.choose_player(self.player_pool.get_available())): c
            for c in callers
        }

        # Aspetta il primo che risponde
        done, pending = await asyncio.wait(
            tasks.keys(), return_when=asyncio.FIRST_COMPLETED
        )

        # Prendi il risultato del primo completato
        first_task = done.pop()
        chosen_player = first_task.result()
        chosen_caller = tasks[first_task]

        # Cancella gli altri (non servono più)
        for task in pending:
            task.cancel()

        # Crea il nuovo turno
        turn_number = len(self.turns) + 1

        

    async def bid(self, bid:Bid):
        if not self.current_turn:
            raise Exception("Auction not started")
        
        self.current_turn.bid(bid)

        event = BidPlaced(
            team_id=bid.team.id,
            team_name=bid.team.name,
            amount=bid.amount
        )

        return event
        

    def set_calling_strategy(self,strategy:CallingStrategy):
        self.calling_strategy = strategy

    