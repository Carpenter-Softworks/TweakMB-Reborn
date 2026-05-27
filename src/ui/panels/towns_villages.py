from typing import ClassVar

from .base import BasePanel


class TownsVillagesPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucVillageImprovements",
        "ucImprovementEffects",
        "ucProsperityGeneral",
        "ucProsperityVillage",
        "ucTroopRecruitment",
        "ucBanditInfestations",
        "ucHowFiefsAreAwarded",
    ]
    TITLE = "Towns & Villages"
    DESCRIPTION = (
        "Village improvement costs and effects, fief prosperity, troop "
        "recruitment rates, bandit infestation mechanics, and fief "
        "awarding rules."
    )
