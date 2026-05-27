from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from .._dpg import dpg
from .base import BasePanel

if TYPE_CHECKING:
    from core.tweak_engine import TweakDef, TweakResult


class GettingStartedPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = []  # No tweaks — pure info panel
    TITLE = "Getting Started"

    def __init__(self, parent_tag: int | str) -> None:
        self._parent = parent_tag
        self._tag = dpg.generate_uuid()
        self._controls = []
        self._built = True
        self._build_content()

    def _build_content(self) -> None:
        with dpg.child_window(
            tag=self._tag, parent=self._parent, border=False, show=False
        ):
            dpg.add_text("TweakMB Reborn", color=(255, 215, 0, 255))
            dpg.add_text("Warband Native 1.174", color=(180, 180, 100, 255))
            dpg.add_separator()
            dpg.add_spacer(height=8)

            dpg.add_text("How to use:", color=(220, 220, 220, 255))
            dpg.add_text(
                "1. Click 'Load Module' and select your Warband module "
                "folder\n"
                "   (e.g. .../MountBlade Warband/Modules/Native)\n\n"
                "2. Browse the categories in the left tree and adjust "
                "any values.\n"
                "   Greyed-out tweaks are not available for this game "
                "version.\n\n"
                "3. Click 'Save Changes' to apply. A timestamped backup "
                "of every\n"
                "   modified file is automatically created in a "
                "'TweakMB_backups'\n"
                "   folder inside your module directory.\n\n"
                "4. If anything goes wrong, restore the backup files.",
                wrap=660,
                color=(200, 200, 200, 255),
            )
            dpg.add_spacer(height=12)
            dpg.add_separator()
            dpg.add_spacer(height=8)
            dpg.add_text("Notes:", color=(220, 220, 220, 255))
            dpg.add_text(
                "• This tool targets Warband Native 1.174 (the final "
                "Steam version).\n"
                "• Changes take effect the next time you load a save "
                "game.\n"
                "• Most tweaks are save-game compatible (they change "
                "engine constants,\n"
                "  not save data). Tweaks that require a new game are "
                "noted.",
                wrap=660,
                color=(180, 180, 180, 255),
            )

    def build_controls(self, defs: list[TweakDef]) -> None:
        pass  # No tweaks in this panel

    def populate(self, results: dict[str, TweakResult]) -> None:
        pass

    def collect_values(self) -> dict[str, str]:
        return {}
