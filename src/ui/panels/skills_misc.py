from typing import ClassVar

from .base import BasePanel


class SkillsMiscPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucSkills",
        "ucMisc",
        "ucCattle",
        "ucFoodConsumption",
        "ucResting",
    ]
    TITLE = "Skills & Misc"
    DESCRIPTION = (
        "Skill effect magnitudes, miscellaneous gameplay constants, "
        "cattle behavior, food consumption rates, and resting/camping "
        "settings."
    )
