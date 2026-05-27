from typing import ClassVar

from .base import BasePanel


class PartiesPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucPartySize",
        "ucAILords",
        "ucBanditMaxParties",
        "ucPartySizeBandits",
        "ucCompanionManagement",
    ]
    TITLE = "Parties & Morale"
    DESCRIPTION = (
        "Party size limits, morale modifiers, AI lord party sizes, "
        "bandit spawn limits, and companion management settings."
    )
