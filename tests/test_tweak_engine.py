# pyright: reportPrivateUsage=false
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

from core.tweak_engine import (
    TweakDef,
    TweakEngine,
    TweakResult,
    _count_nonempty,
    _format_value,
)


def test_tweak_def_ignore_list() -> None:
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="", line_id="", lines_to_skip=0, field_id=0,
        expected_field_count=0, actual_field_count=0, default_value="",
        ignore_line_ids="ignore1, ignore2 ", is_special=False, available=True,
        unavailable_reason=""
    )
    assert td.ignore_list == ["ignore1", "ignore2"]

def test_tweak_engine_load_tweaks() -> None:
    engine = TweakEngine()
    data = (
        '{"tweaks": [{"tweak_name": "test_tweak", "label_text": "", '
        '"label_name": "", "panel_name": "", "control_name": "", '
        '"row_name": "", "col_current": "", "col_default": "", '
        '"module_file": "", "line_id": "", "lines_to_skip": 0, '
        '"field_id": 0, "expected_field_count": 0, "actual_field_count": 0, '
        '"default_value": "", "ignore_line_ids": "", "is_special": false, '
        '"available": true, "unavailable_reason": ""}]}'
    )

    with patch("builtins.open", mock_open(read_data=data)):
        count = engine.load_tweaks("tweaks.json")
        assert count == 1
        assert engine.get_def("test_tweak") is not None
        assert engine.get_def("non_existent") is None

def test_tweak_engine_apply_all() -> None:
    engine = TweakEngine()
    td: Any = MagicMock(spec=TweakDef)
    td.tweak_name = "t1"
    engine._defs = [td]

    mock_ms: Any = MagicMock()
    with patch.object(TweakEngine, "_apply_one") as mock_apply:
        result = MagicMock(spec=TweakResult)
        mock_apply.return_value = result
        results = engine.apply_all(mock_ms)
        assert results["t1"] == result
        mock_apply.assert_called_once_with(td, mock_ms)

def test_apply_one_not_available() -> None:
    engine = TweakEngine()
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="", line_id="", lines_to_skip=0, field_id=0,
        expected_field_count=0, actual_field_count=0, default_value="default",
        ignore_line_ids="", is_special=False, available=False,
        unavailable_reason="Reason"
    )
    mock_ms: Any = MagicMock()
    res = engine._apply_one(td, mock_ms)
    assert not res.available
    assert res.reason == "Reason"

def test_apply_one_file_missing() -> None:
    engine = TweakEngine()
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="MissingFile", line_id="", lines_to_skip=0, field_id=0,
        expected_field_count=0, actual_field_count=0, default_value="default",
        ignore_line_ids="", is_special=False, available=True,
        unavailable_reason=""
    )
    mock_ms: Any = MagicMock()
    mock_ms.get_file.return_value = None
    res = engine._apply_one(td, mock_ms)
    assert not res.available
    assert "not loaded" in res.reason

def test_apply_one_line_not_found() -> None:
    engine = TweakEngine()
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="f1", line_id="SEARCH", lines_to_skip=0, field_id=0,
        expected_field_count=0, actual_field_count=0, default_value="default",
        ignore_line_ids="", is_special=False, available=True,
        unavailable_reason=""
    )
    mock_ms: Any = MagicMock()
    mf: Any = MagicMock()
    mf.lines = ["line 1", "line 2"]
    mock_ms.get_file.return_value = mf

    with patch.object(TweakEngine, "_find_line", return_value=-1):
        res = engine._apply_one(td, mock_ms)
        assert not res.available
        assert "not found" in res.reason

def test_apply_one_field_not_found() -> None:
    engine = TweakEngine()
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="f1", line_id="SEARCH", lines_to_skip=0, field_id=5,
        expected_field_count=0, actual_field_count=0, default_value="default",
        ignore_line_ids="", is_special=False, available=True,
        unavailable_reason=""
    )
    mock_ms: Any = MagicMock()
    mf: Any = MagicMock()
    mf.lines = ["SEARCH 1 2 3"]
    mock_ms.get_file.return_value = mf

    with patch.object(TweakEngine, "_find_line", return_value=0):
        res = engine._apply_one(td, mock_ms)
        assert not res.available
        assert "Field 5 not found" in res.reason

def test_apply_one_success() -> None:
    engine = TweakEngine()
    td = TweakDef(
        tweak_name="t1", label_text="", label_name="", panel_name="",
        control_name="", row_name="", col_current="", col_default="",
        module_file="f1", line_id="SEARCH", lines_to_skip=0, field_id=2,
        expected_field_count=0, actual_field_count=0, default_value="default",
        ignore_line_ids="", is_special=False, available=True,
        unavailable_reason=""
    )
    mock_ms: Any = MagicMock()
    mf: Any = MagicMock()
    mf.lines = ["SEARCH  VAL2  3"]
    mock_ms.get_file.return_value = mf

    res = engine._apply_one(td, mock_ms)
    assert res.available
    assert res.current_value == "VAL2"
    assert res.line_index == 0
    assert res.field_index == 2 # "SEARCH" is index 0, "" is 1, "VAL2" is 2

def test_write_value_invalid_result() -> None:
    engine = TweakEngine()
    res = TweakResult("t1", "old", 0, -1, False)
    assert not engine.write_value(MagicMock(), res, "new")

def test_write_value_missing_def() -> None:
    engine = TweakEngine()
    res = TweakResult("missing", "old", 0, 1, True)
    assert not engine.write_value(MagicMock(), res, "new")

def test_write_value_missing_file() -> None:
    engine = TweakEngine()
    td: Any = MagicMock()
    td.module_file = "f1"
    engine._defs_by_name["t1"] = td
    res = TweakResult("t1", "old", 0, 1, True)

    mock_ms: Any = MagicMock()
    mock_ms.get_file.return_value = None
    assert not engine.write_value(mock_ms, res, "new")

def test_write_value_success() -> None:
    engine = TweakEngine()
    td: Any = MagicMock()
    td.module_file = "f1"
    td.field_id = 2
    engine._defs_by_name["t1"] = td
    res = TweakResult("t1", "old", 0, 2, True)

    mock_ms: Any = MagicMock()
    mf: Any = MagicMock()
    mf.lines = ["SEARCH  VAL2  3"]
    mock_ms.get_file.return_value = mf

    assert engine.write_value(mock_ms, res, "NEWVAL")
    assert mf.lines[0] == "SEARCH  NEWVAL  3"
    assert mf.modified

def test_save_changes() -> None:
    engine = TweakEngine()
    mock_ms: Any = MagicMock()

    results = {
        "t1": TweakResult("t1", "old", 0, 1, True),
        "t2": TweakResult("t2", "old", 0, 1, True)
    }
    new_values = {"t1": "new", "t2": "old"} # t2 hasn't changed

    with patch.object(engine, "write_value") as mock_write:
        engine.save_changes(mock_ms, new_values, results)
        mock_write.assert_called_once_with(mock_ms, results["t1"], "new")
        mock_ms.save_all.assert_called_once()

def test_find_line() -> None:
    lines = [
        "not this",
        "IGNORE SEARCH",
        "SEARCH 100",
        "EXACT"
    ]
    td: Any = MagicMock()
    td.line_id = "SEARCH"
    td.ignore_list = ["IGNORE"]
    td.lines_to_skip = 1

    # Matches line 2 ("SEARCH 100"), then skips 1 to return 3
    assert TweakEngine._find_line(td, lines) == 3

    td.line_id = "EXACT"
    td.lines_to_skip = 0
    assert TweakEngine._find_line(td, lines) == 3

    td.line_id = "MISSING"
    assert TweakEngine._find_line(td, lines) == -1

def test_format_value() -> None:
    assert _format_value("10", "Simple_Triggers", 1) == "10.000000"
    assert _format_value("10.5", "Simple_Triggers", 1) == "10.5"
    assert _format_value("abc", "Simple_Triggers", 1) == "abc"
    assert _format_value("10", "Other", 1) == "10"

def test_count_nonempty() -> None:
    assert _count_nonempty(["", "a", " ", "b"]) == 2
