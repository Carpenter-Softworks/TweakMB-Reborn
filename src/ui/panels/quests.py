from typing import ClassVar

from .base import BasePanel


class QuestsPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucQuestsVillage",
        "ucQuestsMayor",
        "ucQuestsLady",
        "ucQuestsLord",
    ]
    TITLE = "Quests"
    DESCRIPTION = (
        "Quest repeat intervals for village elder, guild master, lady, "
        "and lord quests. Lower intervals allow quests to reappear "
        "more quickly."
    )
