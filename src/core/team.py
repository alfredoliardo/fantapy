class Team:
    def __init__(self, team_id:int, name:str, budget:float) -> None:
        self.team_id = team_id
        self.name = name
        self.budget = budget

        self.players = []
    
    def add_player(self, player, price: float):
        # controllo budget
        if price > self.budget:
            raise ValueError("Budget insufficiente")
        self.players.append((player, price))
        self.budget -= price

    def __repr__(self):
        return f"<Team {self.team_id}: {self.name}, budget rimasto {self.budget}>"