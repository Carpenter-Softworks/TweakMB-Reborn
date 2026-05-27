"""
Main application window and layout.
Manages the sidebar tree, panel switching, module loading, and save flow.
"""

from __future__ import annotations

import os

from core.backup import BackupManager
from core.module_loader import ModuleSet
from core.tweak_engine import TweakEngine, TweakResult

from ._dpg import dpg
from .panels.base import BasePanel
from .panels.battle import BattlePanel
from .panels.economy import EconomyPanel
from .panels.faction_colors import FactionColorsPanel
from .panels.getting_started import GettingStartedPanel
from .panels.parties import PartiesPanel
from .panels.prisoners import PrisonersPanel
from .panels.quests import QuestsPanel
from .panels.reputation import ReputationPanel
from .panels.skills_misc import SkillsMiscPanel
from .panels.towns_villages import TownsVillagesPanel

# Tree structure: (display_label, panel_cls_or_None, children)
# Children are (label, panel_class) pairs
TREE: list[tuple[str, type[BasePanel] |
                 None, list[tuple[str, type[BasePanel]]]]] = [
    ("Getting Started",   GettingStartedPanel,  []),
    ("Battle Options",    BattlePanel,          []),
    ("Parties & Morale",  PartiesPanel,         []),
    ("Economy",           EconomyPanel,         []),
    ("Towns & Villages",  TownsVillagesPanel,   []),
    ("Quests",            QuestsPanel,          []),
    ("Reputation",        ReputationPanel,      []),
    ("Prisoners",         PrisonersPanel,       []),
    ("Skills & Misc",     SkillsMiscPanel,      []),
    ("Faction Colors",    FactionColorsPanel,   []),
]

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_TWEAKS_JSON = os.path.join(_DATA_DIR, "tweaks_native_1174.json")

_DEFAULT_MODULE_PATH = (
    r"C:\Program Files (x86)\Steam\steamapps\common"
    r"\MountBlade Warband\Modules\Native"
)


class App:
    def __init__(self) -> None:
        self._engine = TweakEngine()
        self._module_set = ModuleSet()
        self._backup_mgr = BackupManager()
        self._results: dict[str, TweakResult] = {}
        self._panels: dict[type, BasePanel] = {}
        self._active_panel: BasePanel | None = None
        # panel_cls → selectable tag
        self._selectable_tags: dict[type, int | str] = {}

        # Status bar tags
        self._status_tag = dpg.generate_uuid()
        self._module_label_tag = dpg.generate_uuid()
        self._tweak_count_tag = dpg.generate_uuid()

    def setup(self) -> None:
        """Build the full UI. Call after dpg.create_context()."""
        self._load_tweak_defs()
        self._build_window()

    def _load_tweak_defs(self) -> None:
        if os.path.exists(_TWEAKS_JSON):
            self._engine.load_tweaks(_TWEAKS_JSON)

    def _build_window(self) -> None:
        with dpg.window(tag="primary_window", no_scrollbar=True):
            # ── Top bar ──────────────────────────────────────────────────────
            with dpg.group(horizontal=True):
                dpg.add_text("TweakMB Reborn", color=(255, 215, 0, 255))
                dpg.add_text(
                    "  |  Warband Native 1.174", color=(160, 160, 160, 255)
                )
                dpg.add_spacer(width=20)
                dpg.add_button(
                    label="Load Module",
                    callback=self._on_load_module,
                    width=110
                )
                dpg.add_button(
                    label="Save Changes",
                    callback=self._on_save_changes,
                    width=110
                )
                dpg.add_button(
                    label="Reset Defaults",
                    callback=self._on_reset_defaults,
                    width=120
                )

            dpg.add_separator()

            # Module path + tweak count
            with dpg.group(horizontal=True):
                dpg.add_text("Module: ", color=(160, 160, 160, 255))
                dpg.add_text(
                    "(none loaded)", tag=self._module_label_tag,
                    color=(200, 200, 200, 255)
                )
                dpg.add_spacer(width=30)
                dpg.add_text(
                    "", tag=self._tweak_count_tag, color=(140, 200, 140, 255)
                )

            dpg.add_separator()
            dpg.add_spacer(height=4)

            # ── Main split: sidebar + content ─────────────────────────────
            with dpg.group(horizontal=True):
                # Sidebar
                with dpg.child_window(width=210, border=True):
                    self._build_tree()

                dpg.add_spacer(width=6)

                # Content area (all panels stacked, only one shown)
                with dpg.child_window(border=False, tag="content_area"):
                    self._build_panels()

            # ── Status bar ────────────────────────────────────────────────
            dpg.add_separator()
            dpg.add_text(
                "Ready", tag=self._status_tag, color=(160, 160, 160, 255)
            )

    def _build_tree(self) -> None:
        for label, panel_cls, children in TREE:
            if not children:
                if panel_cls is None:
                    continue
                tag = dpg.generate_uuid()
                self._selectable_tags[panel_cls] = tag
                dpg.add_selectable(
                    tag=tag,
                    label=label,
                    callback=self._make_tree_cb(panel_cls),
                )
            else:
                with dpg.tree_node(label=label, default_open=False):
                    for child_label, child_cls in children:
                        tag = dpg.generate_uuid()
                        self._selectable_tags[child_cls] = tag
                        dpg.add_selectable(
                            tag=tag,
                            label=f"  {child_label}",
                            callback=self._make_tree_cb(child_cls),
                        )

    def _build_panels(self) -> None:
        content = "content_area"
        all_defs = self._engine.all_defs

        for _label, panel_cls, children in TREE:
            if panel_cls is None:
                continue

            if panel_cls is GettingStartedPanel:
                panel = GettingStartedPanel(content)
            else:
                panel = panel_cls(content)

            # Assign tweaks to panel based on PANEL_NAMES
            if panel_cls is not GettingStartedPanel:
                panel_defs = [
                    d for d in all_defs if d.panel_name in panel_cls.PANEL_NAMES
                ]
                panel.build_controls(panel_defs)

            self._panels[panel_cls] = panel

            for _child_label, child_cls in children:
                if child_cls in self._panels:
                    continue
                child_panel = child_cls(content)
                child_defs = [
                    d for d in all_defs if d.panel_name in child_cls.PANEL_NAMES
                ]
                child_panel.build_controls(child_defs)
                self._panels[child_cls] = child_panel

            # Show Getting Started panel by default
            # (also sets its sidebar highlight)
            self._show_panel(GettingStartedPanel)

    def _make_tree_cb(self, panel_cls: type[BasePanel]):
        def callback():
            self._show_panel(panel_cls)
        return callback

    def _show_panel(self, panel_cls: type[BasePanel]) -> None:
        # Deselect all sidebar items, then select the active one
        for cls, tag in self._selectable_tags.items():
            dpg.set_value(tag, cls is panel_cls)

        if self._active_panel is not None:
            self._active_panel.hide()
        panel = self._panels.get(panel_cls)
        if panel:
            panel.show()
            self._active_panel = panel

    def _on_load_module(self) -> None:
        def _pick_callback(_sender: int | str, app_data: dict[str, str]):
            path = (
                app_data.get("file_path_name")
                or app_data.get("current_path", "")
            )
            if path:
                self._load_module(path)

        with dpg.file_dialog(
            label="Select Module Folder",
            directory_selector=True,
            show=True,
            callback=_pick_callback,
            width=700, height=450,
            default_path=(
                _DEFAULT_MODULE_PATH
                if os.path.isdir(_DEFAULT_MODULE_PATH)
                else os.path.expanduser("~")
            ),
        ):
            pass

    def _load_module(self, path: str) -> None:
        self._set_status(f"Loading module from {path}...")
        warnings = self._module_set.load_all(path)

        self._results = self._engine.apply_all(self._module_set)
        self._backup_mgr.reset()

        # Populate all panels
        for panel in self._panels.values():
            panel.populate(self._results)

        total = len(self._results)
        available = sum(1 for r in self._results.values() if r.available)

        dpg.set_value(self._module_label_tag, os.path.basename(path))
        dpg.set_value(
            self._tweak_count_tag,
            f"{available}/{total} tweaks active"
        )

        warn_msg = f" ({len(warnings)} warnings)" if warnings else ""
        self._set_status(f"Module loaded.{warn_msg}")

    def _on_save_changes(self) -> None:
        if not self._module_set.loaded:
            self._set_status("No module loaded.")
            return

        new_values: dict[str, str] = {}
        for panel in self._panels.values():
            new_values.update(panel.collect_values())

        errors = self._engine.save_changes(
            self._module_set, new_values, self._results, self._backup_mgr
        )

        if errors:
            self._set_status(f"Saved with {len(errors)} error(s): {errors[0]}")
        else:
            self._set_status(
                "Changes saved. Backups created in TweakMB_backups/"
            )

    def _on_reset_defaults(self) -> None:
        for panel in self._panels.values():
            panel.reset_to_defaults()
        self._set_status("All values reset to defaults.")

    def _set_status(self, msg: str) -> None:
        dpg.set_value(self._status_tag, msg)
