import os

from core.backup import BackupManager
from core.module_loader import ModuleSet
from core.tweak_engine import TweakEngine


def test_engine_load_tweaks():
    engine = TweakEngine()
    # Path relative to project root since pytest runs from there
    json_path = os.path.join("src", "data", "tweaks_native_1174.json")
    count = engine.load_tweaks(json_path)
    assert count > 0
    assert len(engine.all_defs) == count

def test_module_set_init():
    ms = ModuleSet()
    assert ms.module_path == ""
    assert not ms.loaded

def test_backup_manager_init():
    bm = BackupManager()
    assert bm.backed_up_files == set()
