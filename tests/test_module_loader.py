# pyright: reportPrivateUsage=false
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

from core.module_loader import MODULE_FILE_MAP, ModuleFile, ModuleSet


def test_module_file_load() -> None:
    content = "line1\nline2\n"
    with patch("builtins.open", mock_open(read_data=content)):
        mf = ModuleFile(logical_name="Test", path="test.txt")
        mf.load()
        assert mf.lines == ["line1\n", "line2\n"]
        assert not mf.modified

def test_module_file_save() -> None:
    mock_backup: Any = MagicMock()
    mf = ModuleFile(
        logical_name="Test", path="test.txt", lines=["new\n"], modified=True
    )

    with patch("builtins.open", mock_open()) as mocked_file:
        mf.save(backup_mgr=mock_backup)
        mocked_file.assert_called_once_with(
            "test.txt", "w", encoding="utf-8", newline="\n"
        )
        mocked_file().writelines.assert_called_once_with(["new\n"])
        assert not mf.modified
        mock_backup.backup.assert_called_once_with(mf)

def test_module_set_init() -> None:
    ms = ModuleSet()
    assert ms.module_path == ""
    assert not ms.loaded
    assert ms.file_names() == []

@patch("core.module_loader.os.path.exists")
@patch("core.module_loader.ModuleFile.load")
def test_module_set_load_all(
    mock_load: MagicMock, mock_exists: MagicMock
) -> None:
    # Simulate some files existing, some missing
    def exists_side_effect(path: str) -> bool:
        return "conversation.txt" in path

    mock_exists.side_effect = exists_side_effect

    ms = ModuleSet()
    warnings = ms.load_all("dummy_path")

    assert ms.module_path == "dummy_path"
    assert ms.loaded
    assert "Conversation" in ms.file_names()
    # Check that we have warnings for the missing files
    assert len(warnings) == len(MODULE_FILE_MAP) - 1
    assert any("File not found: menus.txt" in w for w in warnings)
    mock_load.assert_called_once()

@patch("core.module_loader.os.path.exists")
@patch("core.module_loader.ModuleFile.load")
def test_module_set_load_all_oserror(
    mock_load: MagicMock, mock_exists: MagicMock
) -> None:
    mock_exists.return_value = True
    mock_load.side_effect = OSError("Read error")

    ms = ModuleSet()
    warnings = ms.load_all("dummy_path")

    assert len(warnings) == len(MODULE_FILE_MAP)
    assert all("Could not read" in w for w in warnings)

def test_module_set_get_file() -> None:
    ms = ModuleSet()
    mf = ModuleFile(logical_name="Test", path="test.txt")
    ms._files["Test"] = mf

    assert ms.get_file("Test") == mf
    assert ms.get_file("NonExistent") is None

def test_module_set_save_all_success() -> None:
    ms = ModuleSet()
    mf1: Any = MagicMock(spec=ModuleFile)
    mf1.modified = True
    mf1.lines = ["data"]
    mf2: Any = MagicMock(spec=ModuleFile)
    mf2.modified = False

    ms._files = {"f1": mf1, "f2": mf2}

    errors = ms.save_all()
    assert not errors
    mf1.save.assert_called_once()
    mf2.save.assert_not_called()

def test_module_set_save_all_oserror() -> None:
    ms = ModuleSet()
    mf: Any = MagicMock(spec=ModuleFile)
    mf.modified = True
    mf.lines = ["data"]
    mf.path = "fail.txt"
    mf.save.side_effect = OSError("Write error")

    ms._files = {"f": mf}

    errors = ms.save_all()
    assert len(errors) == 1
    assert "Could not write fail.txt: Write error" in errors[0]
