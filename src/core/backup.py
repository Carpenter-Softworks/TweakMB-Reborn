"""
Creates timestamped backups of module files before the first write per session.
Backups go into <module_dir>/TweakMB_backups/.
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .module_loader import ModuleFile


class BackupManager:
    def __init__(self) -> None:
        self._backed_up: set[str] = set()
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    @property
    def backed_up_files(self) -> set[str]:
        return self._backed_up

    def backup(self, module_file: ModuleFile) -> str | None:
        """
        Copy module_file to the backups folder if not already backed up
        this session. Returns the backup path, or None if file doesn't
        exist or already backed up.
        """
        path = module_file.path
        if path in self._backed_up:
            return None
        if not os.path.exists(path):
            return None

        backup_dir = os.path.join(os.path.dirname(path), "TweakMB_backups")
        os.makedirs(backup_dir, exist_ok=True)

        basename = os.path.basename(path)
        name, ext = os.path.splitext(basename)
        backup_path = os.path.join(backup_dir, f"{name}_{self._timestamp}{ext}")

        shutil.copy2(path, backup_path)
        self._backed_up.add(path)
        return backup_path

    def reset(self) -> None:
        """Call at the start of a new session to allow fresh backups."""
        self._backed_up.clear()
        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
