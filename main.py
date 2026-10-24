from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        from netcheck.webui import run_ui_from_args

        return run_ui_from_args([])
    if args[0] == "ui":
        from netcheck.webui import run_ui_from_args

        return run_ui_from_args(args[1:])
    from netcheck.cli import main as cli_main

    return cli_main(args)


if __name__ == "__main__":
    raise SystemExit(main())
