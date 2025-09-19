from fastapi import WebSocket


class RemoteParticipant:
    """Partecipante remoto che si connette via WebSocket."""
    
    def __init__(self, id:str, username: str, ws:WebSocket):
        self._id = id
        self._name = username
        self._ws = ws
    
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    def get_label(self) -> str:
        return "Remote: {self._name}"
