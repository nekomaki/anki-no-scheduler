from functools import lru_cache

from aqt import mw

addon_identifier = mw.addonManager.addonFromModule(__name__)


class Config(object):
    def __init__(self):
        self.data = mw.addonManager.getConfig(addon_identifier)

    @property
    def reorder_cards(self):
        return self.data.get("reorder_cards")

    @reorder_cards.setter
    def reorder_cards(self, value):
        self.data["reorder_cards"] = value
        self.save()

    @property
    def disable_same_day_reviews(self):
        return self.data.get("disable_same_day_reviews")

    @disable_same_day_reviews.setter
    def disable_same_day_reviews(self, value):
        self.data["disable_same_day_reviews"] = value
        self.save()

    @property
    def display_status(self):
        return self.data.get("display_status")

    @display_status.setter
    def display_status(self, value):
        self.data["display_status"] = value
        self.save()

    def save(self):
        mw.addonManager.writeConfig(addon_identifier, self.data)


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
