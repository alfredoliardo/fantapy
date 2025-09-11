import random
import tkinter as tk
from tkinter import messagebox
import uuid

from core.auction import Auction
from core.caller import Caller, SystemCaller, TeamCaller
from core.enums import PlayerRole
from core.player import Player

class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auction Manager")

        # Frame impostazioni iniziali
        self.setup_frame = tk.Frame(root)
        self.setup_frame.pack(padx=10, pady=10)

        tk.Label(self.setup_frame, text="Partecipanti (separati da virgola):").pack(anchor="w")
        self.entry_teams = tk.Entry(self.setup_frame, width=40)
        self.entry_teams.pack(pady=5)

        tk.Label(self.setup_frame, text="Budget iniziale:").pack(anchor="w")
        self.entry_budget = tk.Entry(self.setup_frame, width=20)
        self.entry_budget.insert(0, "500")
        self.entry_budget.pack(pady=5)

        self.start_button = tk.Button(self.setup_frame, text="Crea Asta", command=self.create_auction)
        self.start_button.pack(pady=10)

        # Frame gestione asta
        self.auction_frame = tk.Frame(root)

        self.next_turn_button = tk.Button(self.auction_frame, text="Prossimo Turno", command=self.next_turn)
        self.next_turn_button.pack(pady=5)

        self.text_area = tk.Text(self.auction_frame, width=50, height=15, state="disabled")
        self.text_area.pack(pady=5)

        self.auction = None

    def create_auction(self):
        teams = [t.strip() for t in self.entry_teams.get().split(",") if t.strip()]
        budget = self.entry_budget.get()

        if not teams:
            messagebox.showerror("Errore", "Inserisci almeno un partecipante.")
            return

        # Caller: tutti i team + system
        callers = [TeamCaller(team) for team in teams]
        callers.append(SystemCaller())

        # Lista giocatori demo
        players = [Player(player_id=i,name=f"Giocatore {i}", role=random.choice(list(PlayerRole)), realTeam="Team {i}") for i in range(1, 11)]

        # Crea asta
        self.auction = Auction(auction_id=str(uuid.uuid4()), name="FANTAVALLONE 2025/26",players=players)
        self.auction.subscribe(self.handle_event)

        # Switch UI
        self.setup_frame.pack_forget()
        self.auction_frame.pack(padx=10, pady=10)

        self.log(f"Asta creata con {len(teams)} team e budget {budget}")

    def next_turn(self):
        if self.auction:
            self.auction.next_turn()
        else:
            messagebox.showerror("Errore", "Crea prima un'asta.")

    def handle_event(self, event):
        self.log(f"EVENTO: {event.type} → {event.payload}")

    def log(self, message):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()