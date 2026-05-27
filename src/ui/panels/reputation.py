from typing import ClassVar

from .base import BasePanel


class ReputationPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucReputationVillage",
        "ucReputationTown",
        "ucReputationLady",
        "ucReputationLord",
        "ucReputationLord2",
        "ucReputationLord3",
        "ucAssigningFiefs",
        "ucRightToRule",
        "ucHonorQuests",
        "ucHonorOther",
    ]
    TITLE = "Reputation & Honor"
    DESCRIPTION = (
        "Relation gains and losses with villages, towns, ladies, and lords. "
        "Right to Rule and Honor modifiers from various actions."
    )
