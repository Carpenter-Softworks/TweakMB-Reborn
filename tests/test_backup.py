# pyright: reportPrivateUsage=false
import os
from typing import Any
from unittest.mock import MagicMock, patch

from core.backup import BackupManager


def test_backup_manager_init() -> None:
    bm = BackupManager()
    assert bm.backed_up_files == set()
    assert len(bm._timestamp) > 0

@patch("core.backup.os.path.exists")
@patch("core.backup.os.makedirs")
@patch("core.backup.shutil.copy2")
def test_backup_success(
    mock_copy: MagicMock,
    mock_makedirs: MagicMock,
    mock_exists: MagicMock
) -> None:
    mock_exists.return_value = True

    bm = BackupManager()
    module_file: Any = MagicMock()
    module_file.path = os.path.join("some", "path", "file.txt")

    backup_path = bm.backup(module_file)

    assert backup_path is not None
    assert "TweakMB_backups" in backup_path
    assert "file_" in backup_path
    assert module_file.path in bm.backed_up_files
    mock_copy.assert_called_once()
    mock_makedirs.assert_called_once()

@patch("core.backup.os.path.exists")
def test_backup_already_done(mock_exists: MagicMock) -> None:
    mock_exists.return_value = True

    bm = BackupManager()
    module_file: Any = MagicMock()
    module_file.path = "file.txt"

    bm._backed_up.add("file.txt")
    result = bm.backup(module_file)

    assert result is None

@patch("core.backup.os.path.exists")
def test_backup_file_missing(mock_exists: MagicMock) -> None:
    mock_exists.return_value = False

    bm = BackupManager()
    module_file: Any = MagicMock()
    module_file.path = "ghost.txt"

    result = bm.backup(module_file)

    assert result is None
    assert "ghost.txt" not in bm.backed_up_files

def test_backup_manager_reset() -> None:
    bm = BackupManager()
    bm._backed_up.add("old.txt")

    bm.reset()

    assert bm.backed_up_files == set()
