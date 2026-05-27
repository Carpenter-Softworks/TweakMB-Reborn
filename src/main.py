"""TweakMB Reborn — entry point."""

from ui._dpg import dpg
from ui.app import App


def main() -> None:
    dpg.create_context()

    with dpg.font_registry():
        pass  # Use DPG's built-in default font

    dpg.create_viewport(
        title="TweakMB Reborn v1.0 - Warband Native 1.174",
        width=1100,
        height=750,
        min_width=800,
        min_height=500,
    )
    dpg.setup_dearpygui()

    app = App()
    app.setup()

    dpg.set_primary_window("primary_window", True)
    dpg.show_viewport()

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()

    dpg.destroy_context()


if __name__ == "__main__":
    main()
