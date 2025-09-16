class ConfigOption:
    def __init__(self, key: str, values: list[str], required: bool = True):
        self.key = key
        self.values = values
        self.required = required

class AuctionConfigSchema:
    def __init__(self):
        self.modes: dict[str, list[ConfigOption]] = {}

    def register_mode(self, mode: str, options: list[ConfigOption]):
        self.modes[mode] = options

    def export(self):
        return {
            mode: {opt.key: opt.values for opt in opts}
            for mode, opts in self.modes.items()
        }
