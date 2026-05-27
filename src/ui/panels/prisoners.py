from typing import ClassVar

from .base import BasePanel


class PrisonersPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucPrisoners",
        "ucEnemyLordEscapeCaptureRates",
        "ucRecruitPrisoners",
    ]
    TITLE = "Prisoners"
    DESCRIPTION = (
        "Maximum prisoners you can hold, enemy lord escape and capture rates, "
        "and the ability to recruit prisoners into your party."
    )
