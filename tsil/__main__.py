"""
TSIL REPL — interactive command-line interface.

Run with:  python -m tsil

Provides an interactive prompt for evaluating TSIL expressions,
viewing results, and exploring timeseries data.
"""

from __future__ import annotations

import sys
import traceback

import pandas as pd

from tsil import __version__
from tsil.engine.interpreter import Engine, InterpreterError
from tsil.engine.lexer import LexerError
from tsil.engine.parser import ParseError
from tsil.types.timeseries import series_repr


BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║  TSIL v{__version__}  —  Timeseries Intermediate Language          ║
║  Type 'help' for commands, 'exit' to quit.                  ║
╚══════════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
TSIL Commands:
  help              Show this help message
  vars              List all defined variables
  ast <expr>        Show the AST (JSON) for an expression
  exit / quit       Exit the REPL

TSIL Quick Reference:
  Ticker:   t("SPX")  or  t(["SPX", "SX5E"], WGT_VOL)
  Expiry:   e("3M")   or  e("Z26")  or  e("1Y", "6M")
  Strike:   k("100%") or  k(7500)   or  k("25DC")
  IV:       IV(t("SPX"), e("3M"), k("100%"))
  RV:       RV(t("SPX"), 30)

Operations:
  ts1 + ts2    ts1 - ts2    ts1 * 2    ts1 / ts2    ts1 ** 2
  sqrt(ts)     diff(ts)     pct_change(ts)
  corr(ts1, ts2, 30)        sharpe(ts, 252)
  mean(ts, 30)              std(ts, 30)
  drawdown(ts, 252)

Plotting:
  plot([ts1, ts2])                    # single y-axis
  plot([ts1], [ts2])                  # dual y-axes (y1 left, y2 right)

Examples:
  spx = t("SPX")
  vol = IV(spx, e("3M"), k("100%"))
  rv  = RV(spx, 30)
  slope = IV(spx, e("1Y"), k("100%")) - vol
  plot([vol], [rv])
"""


def main() -> None:
    """Run the TSIL interactive REPL."""
    print(BANNER)
    engine = Engine()

    while True:
        try:
            line = input("tsil> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not line:
            continue

        if line.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if line.lower() == "help":
            print(HELP_TEXT)
            continue

        if line.lower() == "vars":
            user_vars = engine.variables
            if not user_vars:
                print("  (no variables defined)")
            else:
                for name, val in user_vars.items():
                    summary = _summarise(val)
                    print(f"  {name} = {summary}")
            continue

        # AST inspection command
        if line.lower().startswith("ast "):
            expr = line[4:].strip()
            if expr:
                try:
                    json_str = engine.parse_to_json(expr, indent=2)
                    print(json_str)
                except (LexerError, ParseError) as ex:
                    print(f"  Syntax Error: {ex}")
            continue

        # Multi-line: accumulate lines ending with \
        while line.endswith("\\"):
            try:
                continuation = input("...   ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            line = line[:-1] + " " + continuation

        # Evaluate
        try:
            result = engine.eval(line)
            if result is not None:
                if isinstance(result, pd.Series):
                    print(series_repr(result))
                else:
                    print(result)
        except (LexerError, ParseError) as ex:
            print(f"  Syntax Error: {ex}")
        except InterpreterError as ex:
            print(f"  Error: {ex}")
        except Exception as ex:
            print(f"  Unexpected Error: {ex}")
            traceback.print_exc()


def _summarise(val: object) -> str:
    """Create a short summary string for display."""
    if isinstance(val, pd.Series):
        n = len(val)
        meta = val.attrs
        parts = [f"{k}={v}" for k, v in meta.items() if k != "metric"]
        metric = meta.get("metric", "Timeseries")
        return f"{metric}({', '.join(parts)}, {n} rows)"
    return repr(val)


if __name__ == "__main__":
    main()
