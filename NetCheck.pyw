from __future__ import annotations

import ctypes


def main() -> int:
    try:
        from netcheck.webui import run_ui_from_args

        return run_ui_from_args([])
    except Exception as exc:
        ctypes.windll.user32.MessageBoxW(0, str(exc), "NetCheck", 0x10)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
