from abc import ABC, abstractmethod


class IBidder(ABC):
    @abstractmethod
    async def make_bid(self, amount:float):...

