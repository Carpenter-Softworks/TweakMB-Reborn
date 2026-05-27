"""
Typed re-export of dearpygui.

dearpygui ships without a ``py.typed`` marker, so pyright treats every
attribute access on the imported module as ``Unknown`` under strict mode.
Importing through this wrapper localizes the suppression to a single file
and gives callers a plainly ``Any``-typed handle.
"""

from typing import Any

import dearpygui.dearpygui as _dpg  # type: ignore[reportMissingTypeStubs]

dpg: Any = _dpg
