from typing import ClassVar

from .base import BasePanel


class BattlePanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucArena", "ucTournamentFrequency",
        "ucAmmo",
        "ucReinforcements",
        "ucSieges",
        "ucBattleMisc",
        "ucBattleMapSize",
    ]
    TITLE = "Battle Options"
    DESCRIPTION = (
        "Tweaks affecting combat, arenas, reinforcement waves, "
        "siege mechanics, ammunition, and battle map size."
    )
