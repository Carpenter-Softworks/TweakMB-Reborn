"""
Loads and saves Mount & Blade Warband module text files.
All files are kept as raw line lists so original whitespace and structure
is preserved; only the specific token being tweaked is changed on save.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .backup import BackupManager

MODULE_FILE_MAP: dict[str, str] = {
    "Conversation":      "conversation.txt",
    "Menus":             "menus.txt",
    "Scripts":           "scripts.txt",
    "Mission_Templates": "mission_templates.txt",
    "Party_Templates":   "party_templates.txt",
    "Troops":            "troops.txt",
    "Triggers":          "triggers.txt",
    "Simple_Triggers":   "simple_triggers.txt",
    "Factions":          "factions.txt",
    "Item_Kinds":        "item_kinds1.txt",
    "Scenes":            "scenes.txt",
    "Presentations":     "presentations.txt",
    "Skills":            "skills.txt",
}


@dataclass
class ModuleFile:
    logical_name: str
    path: str
    lines: list[str] = field(default_factory=list[str])
    modified: bool = False

    def load(self) -> None:
        with open(self.path, encoding="utf-8", errors="replace") as f:
            lines_raw: list[str] = f.readlines()
            self.lines = lines_raw
        self.modified = False

    def save(self, backup_mgr: BackupManager | None = None) -> None:
        if backup_mgr:
            backup_mgr.backup(self)
        with open(self.path, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(self.lines)
        self.modified = False


class ModuleLoadError(Exception):
    pass


class ModuleSet:
    def __init__(self) -> None:
        self._files: dict[str, ModuleFile] = {}
        self.module_path: str = ""

    def load_all(self, module_path: str) -> list[str]:
        """
        Load all module files from module_path.
        Returns a list of warning strings for any files that could not
        be loaded.
        """
        self.module_path = module_path
        self._files.clear()
        warnings: list[str] = []

        for logical_name, filename in MODULE_FILE_MAP.items():
            path = os.path.join(module_path, filename)
            mf = ModuleFile(logical_name=logical_name, path=path)
            if os.path.exists(path):
                try:
                    mf.load()
                except OSError as e:
                    warnings.append(f"Could not read {filename}: {e}")
            else:
                warnings.append(f"File not found: {filename}")
            self._files[logical_name] = mf

        return warnings

    def get_file(self, logical_name: str) -> ModuleFile | None:
        return self._files.get(logical_name)

    def save_all(self, backup_mgr: BackupManager | None = None) -> list[str]:
        """Save all modified files. Returns list of error strings."""
        errors: list[str] = []
        for mf in self._files.values():
            if mf.modified and mf.lines:
                try:
                    mf.save(backup_mgr)
                except OSError as e:
                    errors.append(f"Could not write {mf.path}: {e}")
        return errors

    @property
    def loaded(self) -> bool:
        return bool(self._files)

    def file_names(self) -> list[str]:
        return list(self._files.keys())
