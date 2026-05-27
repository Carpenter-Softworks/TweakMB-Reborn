from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from .._dpg import dpg
from .base import COLOR_DISABLED, COLOR_LABEL, BasePanel, ControlEntry

if TYPE_CHECKING:
    from core.tweak_engine import TweakDef, TweakResult


class FactionColorsPanel(BasePanel):
    PANEL_NAMES: ClassVar[list[str]] = ["ucFactionColors"]
    TITLE = "Faction Colors"
    DESCRIPTION = (
        "Customize the map color of each faction. Values are stored as "
        "packed 32-bit integers (the upper byte is preserved)."
    )

    def __init__(self, parent_tag: int | str) -> None:
        # tweak_name → upper byte of original value
        self._upper_bytes: dict[str, int] = {}
        super().__init__(parent_tag)

    def _add_control(self, td: TweakDef) -> None:
        tag = dpg.generate_uuid()

        # Parse default hex color; record upper byte for faithful round-trip
        self._upper_bytes[td.tweak_name] = _upper_byte(td.default_value)
        default_color = _int_to_rgb(td.default_value)

        with dpg.group(horizontal=True):
            dpg.add_color_edit(
                tag=tag,
                default_value=(*default_color, 255),
                no_alpha=True,
                enabled=td.available,
                width=120,
            )
            label = td.label_text or td.tweak_name
            col = COLOR_LABEL if td.available else COLOR_DISABLED
            dpg.add_text(label, color=col)

        self._controls.append(ControlEntry(
            tweak_name=td.tweak_name,
            tag=tag,
            available=td.available,
            default_value=td.default_value,
            is_checkbox=False,
        ))

    def populate(self, results: dict[str, TweakResult]) -> None:
        for ctrl in self._controls:
            result = results.get(ctrl.tweak_name)
            if result is None or not result.available:
                continue
            self._upper_bytes[ctrl.tweak_name] = _upper_byte(
                result.current_value
            )
            rgb = _int_to_rgb(result.current_value)
            dpg.set_value(ctrl.tag, (*rgb, 255))

    def collect_values(self) -> dict[str, str]:
        out: dict[str, str] = {}
        for ctrl in self._controls:
            if not ctrl.available:
                continue
            rgba = dpg.get_value(ctrl.tag)  # [r, g, b, a] 0-255
            upper = self._upper_bytes.get(ctrl.tweak_name, 0)
            packed = (
                (upper << 24)
                | (int(rgba[0]) << 16)
                | (int(rgba[1]) << 8)
                | int(rgba[2])
            )
            # Re-encode as signed 32-bit to match original format
            if packed >= 0x80000000:
                packed -= 0x100000000
            out[ctrl.tweak_name] = str(packed)
        return out


def _upper_byte(value: str) -> int:
    """
    Extract the upper (alpha/flags) byte from a possibly-signed 32-bit
    color integer.
    """
    try:
        n = int(float(value)) & 0xFFFFFFFF  # treat as unsigned 32-bit
        return (n >> 24) & 0xFF
    except (ValueError, TypeError):
        return 0


def _int_to_rgb(value: str) -> tuple[int, int, int]:
    try:
        n = int(float(value)) & 0xFFFFFFFF  # treat as unsigned 32-bit
        r = (n >> 16) & 0xFF
        g = (n >> 8) & 0xFF
        b = n & 0xFF
        return r, g, b
    except (ValueError, TypeError):
        return 128, 128, 128
