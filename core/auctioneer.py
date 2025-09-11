# core/auctioneer.py
import threading
import time
from typing import Callable, Optional

from core.player import Player
from core.team import Team

class Auctioneer:
    def __init__(self, countdown_seconds: int = 10, tick_callback: Optional[Callable] = None):
        """
        countdown_seconds: durata di un turno d'asta per un giocatore
        tick_callback: funzione richiamata ogni secondo, utile per notifiche UI/WebSocket
        """
        self.countdown_seconds = countdown_seconds
        self.tick_callback = tick_callback
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.on_finish: Optional[Callable[[Player, Team, int], None]] = None

    def start(self, player: Player, best_bid):
        """Avvia countdown sul giocatore corrente"""
        self._stop_event.clear()

        def run():
            remaining = self.countdown_seconds
            while remaining > 0 and not self._stop_event.is_set():
                if self.tick_callback:
                    self.tick_callback(remaining)
                time.sleep(1)
                remaining -= 1

            if not self._stop_event.is_set() and self.on_finish:
                # Alla fine assegna il giocatore al miglior offerente
                if best_bid:
                    self.on_finish(player, best_bid.team, best_bid.amount)
                else:
                    self.on_finish(player, None, 0)

        self._timer_thread = threading.Thread(target=run, daemon=True)
        self._timer_thread.start()

    def stop(self):
        """Ferma il countdown (es. se arriva nuovo rilancio)"""
        self._stop_event.set()
