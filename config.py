from functools import lru_cache

from aqt import mw

addon_identifier = mw.addonManager.addonFromModule(__name__)


class Config(object):
    def __init__(self):
        self.data = mw.addonManager.getConfig(addon_identifier)
        if not self.data:
            self.data = dict()

    @property
    def sort_cards(self):
        return self.data.get("sort_cards", True)

    @sort_cards.setter
    def sort_cards(self, value):
        self.data["sort_cards"] = value
        self.save()

    @property
    def display(self):
        return self.data.get("display", True)

    @display.setter
    def display(self, value):
        self.data["display"] = value
        self.save()

    def save(self):
        mw.addonManager.writeConfig(addon_identifier, self.data)


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
