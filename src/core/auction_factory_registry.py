from core.enums import AuctionMode


class AuctionFactoryRegistry:
    def __init__(self):
        self._factories = {}

    def register(self, mode: AuctionMode, factory_cls):
        self._factories[mode.value] = factory_cls

    def list_modes(self):
        return list(self._factories.keys())

    def create(self, mode: str, **kwargs):
        if mode not in self._factories:
            raise ValueError(f"Unsupported auction mode: {mode}")
        factory_cls = self._factories[mode]
        return factory_cls(**kwargs)
