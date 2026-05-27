from typing import ClassVar

from .base import BasePanel


class EconomyPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = [
        "ucTroopWages",
        "ucFiefIncome",
        "ucTaxInefficiency",
        "ucMerchants",
        "ucEnterpriseDetail",
        "ucEnterprisePrices",
        "ucEnterpriseStart",
    ]
    TITLE = "Economy"
    DESCRIPTION = (
        "Troop wages, fief income, tax inefficiency thresholds, merchant gold, "
        "and enterprise production/overhead values."
    )
