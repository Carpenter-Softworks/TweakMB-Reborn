"""
Loads tweak definitions from JSON, applies them to loaded module files,
reads current values, and writes new values back.
"""

import json
from dataclasses import dataclass

from .backup import BackupManager
from .module_loader import ModuleSet


@dataclass
class TweakDef:
    tweak_name: str
    label_text: str
    label_name: str
    panel_name: str
    control_name: str
    row_name: str
    col_current: str
    col_default: str
    module_file: str
    line_id: str
    lines_to_skip: int
    field_id: int
    expected_field_count: int
    actual_field_count: int
    default_value: str
    ignore_line_ids: str
    is_special: bool
    available: bool
    unavailable_reason: str

    @property
    def ignore_list(self) -> list[str]:
        return [x.strip() for x in self.ignore_line_ids.split(",") if x.strip()]


@dataclass
class TweakResult:
    tweak_name: str
    current_value: str
    line_index: int       # index into ModuleFile.lines of the data line
    field_index: int      # index into the split parts array
    available: bool
    reason: str = ""


class TweakEngine:
    def __init__(self) -> None:
        self._defs: list[TweakDef] = []
        self._defs_by_name: dict[str, TweakDef] = {}

    def load_tweaks(self, json_path: str) -> int:
        """Load tweak definitions from JSON. Returns count loaded."""
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        self._defs = []
        self._defs_by_name = {}
        for item in data.get("tweaks", []):
            td = TweakDef(**item)
            self._defs.append(td)
            self._defs_by_name[td.tweak_name] = td
        return len(self._defs)

    @property
    def all_defs(self) -> list[TweakDef]:
        return self._defs

    def get_def(self, tweak_name: str) -> TweakDef | None:
        return self._defs_by_name.get(tweak_name)

    def apply_all(self, module_set: ModuleSet) -> dict[str, TweakResult]:
        """
        Apply all tweak definitions to the loaded module set.
        Returns results keyed by tweak_name.
        """
        results: dict[str, TweakResult] = {}
        for td in self._defs:
            results[td.tweak_name] = self._apply_one(td, module_set)
        return results

    def _apply_one(self, td: TweakDef, module_set: ModuleSet) -> TweakResult:
        if not td.available:
            return TweakResult(
                td.tweak_name, td.default_value, -1, -1, False,
                td.unavailable_reason
            )

        mf = module_set.get_file(td.module_file)
        if mf is None or not mf.lines:
            return TweakResult(td.tweak_name, td.default_value, -1, -1, False,
                               f"Module file '{td.module_file}' not loaded")

        line_idx = self._find_line(td, mf.lines)
        if line_idx < 0:
            return TweakResult(td.tweak_name, td.default_value, -1, -1, False,
                               f"Line ID '{td.line_id}' not found")

        parts = mf.lines[line_idx].split(" ")
        # Locate the field_id-th non-empty token and record its index in parts
        field_index, value = self._find_field(parts, td.field_id)
        if field_index < 0:
            return TweakResult(
                td.tweak_name, td.default_value, line_idx, -1, False,
                f"Field {td.field_id} not found "
                f"(line has {_count_nonempty(parts)} fields)"
            )

        return TweakResult(
            td.tweak_name, value.strip(), line_idx, field_index, True
        )

    def write_value(
        self, module_set: ModuleSet, result: TweakResult, new_value: str
    ) -> bool:
        """
        Write a new value into the module file at the position recorded
        in result. Marks the file as modified. Returns False if result
        is not available.
        """
        if not result.available or result.field_index < 0:
            return False

        td = self._defs_by_name.get(result.tweak_name)
        if td is None:
            return False

        mf = module_set.get_file(td.module_file)
        if mf is None:
            return False

        line = mf.lines[result.line_index]
        parts = line.split(" ")

        # For Simple_Triggers, field 1 requires float format e.g. "1.000000"
        formatted = _format_value(new_value, td.module_file, td.field_id)

        parts[result.field_index] = formatted
        mf.lines[result.line_index] = " ".join(parts)
        mf.modified = True
        return True

    def save_changes(
        self, module_set: ModuleSet, new_values: dict[str, str],
        results: dict[str, TweakResult], backup_mgr: BackupManager | None = None
    ) -> list[str]:
        """
        Write all changed values and save modified files.
        new_values: {tweak_name: new_value_string}
        Returns list of error strings.
        """
        for tweak_name, new_val in new_values.items():
            result = results.get(tweak_name)
            if result and result.available and new_val != result.current_value:
                self.write_value(module_set, result, new_val)

        return module_set.save_all(backup_mgr)

    @staticmethod
    def _find_line(td: TweakDef, lines: list[str]) -> int:
        search = td.line_id if td.line_id.endswith(" ") else td.line_id + " "
        search_exact = td.line_id.strip()
        ignore = td.ignore_list
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (search in line or stripped == search_exact) and not any(
                bad in line for bad in ignore if bad
            ):
                return i + td.lines_to_skip
        return -1

    @staticmethod
    def _find_field(parts: list[str], field_id: int) -> tuple[int, str]:
        """
        Find the field_id-th non-empty token in parts (1-based).
        Returns (index_in_parts, value) or (-1, "") if not found.
        """
        count = 0
        for i, p in enumerate(parts):
            if p.strip():
                count += 1
                if count == field_id:
                    return i, p
        return -1, ""


def _count_nonempty(parts: list[str]) -> int:
    return sum(1 for p in parts if p.strip())


def _format_value(value: str, module_file: str, field_id: int) -> str:
    """
    Trigger interval fields must be written as float strings
    (e.g. '24.000000').
    """
    if module_file in ("Simple_Triggers", "Triggers") and field_id <= 3:
        try:
            f = float(value)
            if "." not in value.strip():
                return f"{int(f)}.000000"
            return value
        except ValueError:
            pass
    return value
