"""
BasePanel: generic Dear PyGui panel for displaying and editing a list of tweaks.

Each concrete panel subclass passes its list of panel_name values (matching the
'panel_name' field in the JSON) to the constructor. The base class handles all
rendering, value population, and value collection.
"""

from __future__ import annotations

import contextlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .._dpg import dpg

if TYPE_CHECKING:
    from core.tweak_engine import TweakDef, TweakResult

# Colour constants (RGBA)
COLOR_DISABLED   = (128, 128, 128, 180)
COLOR_LABEL      = (220, 220, 220, 255)
COLOR_SECTION    = (180, 180, 100, 255)
COLOR_WARN       = (220, 160, 60, 255)


@dataclass
class ControlEntry:
    tweak_name: str
    tag: int | str          # dpg item tag for the input widget
    available: bool
    default_value: str
    is_checkbox: bool = False


class BasePanel:
    """
    Renders a scrollable panel of tweaks. Shown/hidden by the app tree nav.
    """

    # Subclasses set this to the list of panel_name strings they own
    PANEL_NAMES: ClassVar[list[str]] = []
    TITLE: str = "Panel"
    DESCRIPTION: str = ""

    def __init__(self, parent_tag: int | str) -> None:
        self._parent = parent_tag
        self._tag = dpg.generate_uuid()
        self._controls: list[ControlEntry] = []
        self._built = False
        self._build_shell()

    def _build_shell(self) -> None:
        with dpg.child_window(
            tag=self._tag,
            parent=self._parent,
            border=False,
            show=False,
        ):
            dpg.add_text(self.TITLE, color=(255, 215, 0, 255))
            dpg.add_separator()
            if self.DESCRIPTION:
                dpg.add_text(
                    self.DESCRIPTION, wrap=700, color=(180, 180, 180, 255)
                )
                dpg.add_spacer(height=6)
            self._content_tag = dpg.add_group()

    def build_controls(self, defs: list[TweakDef]) -> None:
        """
        Create UI controls for all tweaks belonging to this panel.
        Call once after JSON is loaded.
        """
        if self._built:
            return
        self._built = True
        self._controls.clear()

        # Group defs by their panel_name for section headings
        sections: dict[str, list[TweakDef]] = {}
        for td in defs:
            sections.setdefault(td.panel_name, []).append(td)

        with dpg.group(parent=self._content_tag):
            for section_name, tweaks in sections.items():
                # Section heading if more than one section
                if len(sections) > 1:
                    dpg.add_spacer(height=4)
                    dpg.add_text(
                        _panel_name_to_title(section_name), color=COLOR_SECTION
                    )
                    dpg.add_separator()

                for td in tweaks:
                    self._add_control(td)

            dpg.add_spacer(height=20)

    def _add_control(self, td: TweakDef) -> None:
        is_checkbox = _is_checkbox(td)
        tag = dpg.generate_uuid()

        with dpg.group(horizontal=True):
            if is_checkbox:
                dpg.add_checkbox(
                    tag=tag,
                    default_value=td.default_value.lower() in (
                        "1", "true", "yes"
                    ),
                    enabled=td.available,
                )
            else:
                with contextlib.suppress(ValueError):
                    int(float(td.default_value)) if td.default_value else 0
                dpg.add_input_text(
                    tag=tag,
                    default_value=td.default_value,
                    width=90,
                    enabled=td.available,
                    decimal=True,
                )

            label = td.label_text or _humanize_tweak_name(td.tweak_name)
            col = COLOR_LABEL if td.available else COLOR_DISABLED
            lbl_tag = dpg.add_text(label, color=col, wrap=600)

        if not td.available:
            reason = td.unavailable_reason or (
                "Not available for this game version"
            )
            with dpg.tooltip(lbl_tag):
                dpg.add_text(f"Disabled: {reason}", color=COLOR_DISABLED)

        self._controls.append(ControlEntry(
            tweak_name=td.tweak_name,
            tag=tag,
            available=td.available,
            default_value=td.default_value,
            is_checkbox=is_checkbox,
        ))

    def populate(self, results: dict[str, TweakResult]) -> None:
        """Set all control values from live TweakResult data."""
        for ctrl in self._controls:
            result = results.get(ctrl.tweak_name)
            if result is None or not result.available:
                continue
            val = result.current_value
            if ctrl.is_checkbox:
                dpg.set_value(
                    ctrl.tag, val.lower() in ("1", "true", "yes")
                )
            else:
                dpg.set_value(ctrl.tag, val)

    def collect_values(self) -> dict[str, str]:
        """Return {tweak_name: new_value} for all available controls."""
        out: dict[str, str] = {}
        for ctrl in self._controls:
            if not ctrl.available:
                continue
            val = dpg.get_value(ctrl.tag)
            if ctrl.is_checkbox:
                out[ctrl.tweak_name] = "1" if val else "0"
            else:
                out[ctrl.tweak_name] = str(val)
        return out

    def reset_to_defaults(self) -> None:
        for ctrl in self._controls:
            if not ctrl.available:
                continue
            if ctrl.is_checkbox:
                dpg.set_value(
                    ctrl.tag, ctrl.default_value.lower() in ("1", "true", "yes")
                )
            else:
                dpg.set_value(ctrl.tag, ctrl.default_value)

    def show(self) -> None:
        dpg.configure_item(self._tag, show=True)

    def hide(self) -> None:
        dpg.configure_item(self._tag, show=False)

    @property
    def tag(self) -> int | str:
        return self._tag


def _is_checkbox(td: TweakDef) -> bool:
    # The original TweakMB names every CheckBox control with a "chk" prefix and
    # every NumericUpDown with a "num" prefix — match on the prefix so names
    # like "numCompanionMoraleCheckInterval" aren't misclassified.
    return td.control_name.startswith("chk")


def _panel_name_to_title(raw: str) -> str:
    """Convert e.g. 'ucPartySize' → 'Party Size', 'ucAILords' → 'AI Lords'."""
    return _split_camel(raw.removeprefix("uc").removeprefix("pan"))


def _humanize_tweak_name(name: str) -> str:
    """
    Last-resort label for tweaks with no UI control in the original TweakMB.

    Drops the leading category prefix (everything before the first underscore)
    and renders the rest as words, with any further underscores becoming
    em dashes.
    e.g. 'BanditParties_DesertBanditsMax' → 'Desert Bandits Max'
         'Color_PlayerKingdom_Conversation' → 'Player Kingdom — Conversation'
    """
    rest = name.split("_", 1)[1] if "_" in name else name
    return " — ".join(_split_camel(part) for part in rest.split("_"))


_CAMEL_BOUNDARY_1 = re.compile(r"([a-z\d])([A-Z])")
_CAMEL_BOUNDARY_2 = re.compile(r"([A-Z]+)([A-Z][a-z])")


def _split_camel(s: str) -> str:
    """
    CamelCase → space-separated words, keeping acronyms intact
    ('AILords' → 'AI Lords').
    """
    s = _CAMEL_BOUNDARY_1.sub(r"\1 \2", s)
    s = _CAMEL_BOUNDARY_2.sub(r"\1 \2", s)
    return s
