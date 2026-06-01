"""
TSIL plotting — dual-axis timeseries chart.

Plots one or more timeseries on a primary y-axis (left) and an
optional set on a secondary y-axis (right).

Usage:
    from tsil.operations.plot import plot

    plot([vol_1m, vol_3m])                           # single axis
    plot([vol_1m, vol_3m], y2=[spot])                 # dual axes
    plot([vol_1m], y2=[spot], title="Vol vs Spot")
"""

from __future__ import annotations

from typing import Optional, Sequence

import pandas as pd


def plot(
    y1: Sequence[pd.Series],
    y2: Optional[Sequence[pd.Series]] = None,
    title: Optional[str] = None,
    y1_label: Optional[str] = None,
    y2_label: Optional[str] = None,
    figsize: tuple[int, int] = (14, 6),
) -> object:
    """Plot timeseries on dual y-axes.

    Args:
        y1:       List of pd.Series to plot on the left (primary) y-axis.
        y2:       Optional list of pd.Series for the right (secondary) y-axis.
        title:    Chart title.  Defaults to auto-generated from series names.
        y1_label: Label for the left y-axis.
        y2_label: Label for the right y-axis.
        figsize:  Figure size as (width, height) in inches.

    Returns:
        The matplotlib Figure object.

    Examples:
        >>> from tsil import t, e, k, IV, RV
        >>> from tsil.operations.plot import plot
        >>> vol = IV(t("SPX"), e("3M"), k("100%"))
        >>> rv  = RV(t("SPX"), 30)
        >>> fig = plot([vol], y2=[rv], title="Implied vs Realised")
    """
    # Lazy import so matplotlib is optional
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        raise ImportError(
            "matplotlib is required for plotting. "
            "Install with:  pip install tsil[plot]"
        )

    fig, ax1 = plt.subplots(figsize=figsize)

    # ── Styling ─────────────────────────────────────────────────────────
    fig.patch.set_facecolor("#0f0f14")
    ax1.set_facecolor("#0f0f14")
    ax1.tick_params(colors="#a0a0b0")
    ax1.xaxis.label.set_color("#a0a0b0")
    ax1.yaxis.label.set_color("#a0a0b0")
    for spine in ax1.spines.values():
        spine.set_color("#2a2a3a")

    # Colour palettes — y1 uses cool tones, y2 uses warm tones
    y1_colors = ["#4fc3f7", "#81d4fa", "#b3e5fc", "#e1f5fe", "#80deea"]
    y2_colors = ["#ffb74d", "#ffd54f", "#fff176", "#ffcc80", "#ffe0b2"]

    # ── Plot y1 (left axis) ─────────────────────────────────────────────
    for i, s in enumerate(y1):
        label = _label(s, i)
        color = y1_colors[i % len(y1_colors)]
        ax1.plot(s.index, s.values, label=label, color=color, linewidth=1.3)

    ax1.set_ylabel(y1_label or _axis_label(y1), color="#4fc3f7", fontsize=11)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.3,
               facecolor="#1a1a2e", edgecolor="#2a2a3a", labelcolor="#c0c0d0")

    # ── Plot y2 (right axis) ───────────────────────────────────────────
    if y2:
        ax2 = ax1.twinx()
        ax2.set_facecolor("#0f0f14")
        ax2.tick_params(colors="#a0a0b0")
        ax2.yaxis.label.set_color("#a0a0b0")
        for spine in ax2.spines.values():
            spine.set_color("#2a2a3a")

        for i, s in enumerate(y2):
            label = _label(s, i)
            color = y2_colors[i % len(y2_colors)]
            ax2.plot(s.index, s.values, label=label, color=color,
                     linewidth=1.3, linestyle="--")

        ax2.set_ylabel(y2_label or _axis_label(y2), color="#ffb74d", fontsize=11)
        ax2.legend(loc="upper right", fontsize=9, framealpha=0.3,
                   facecolor="#1a1a2e", edgecolor="#2a2a3a", labelcolor="#c0c0d0")

    # ── Title & formatting ──────────────────────────────────────────────
    chart_title = title or "TSIL Timeseries"
    ax1.set_title(chart_title, color="#e0e0e8", fontsize=14, fontweight="bold",
                  pad=12)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    fig.autofmt_xdate(rotation=30)

    ax1.grid(True, alpha=0.15, color="#4a4a5a")

    plt.tight_layout()
    plt.show()
    return fig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _label(s: pd.Series, idx: int) -> str:
    """Build a legend label from series name or attrs."""
    if s.name:
        return str(s.name)
    meta = s.attrs
    if "metric" in meta:
        parts = [meta["metric"]]
        for k in ("ticker", "expiry", "strike", "window"):
            if k in meta:
                parts.append(str(meta[k]))
        return " ".join(parts)
    return f"series_{idx}"


def _axis_label(series_list: Sequence[pd.Series]) -> str:
    """Auto-generate an axis label from the first series' metric."""
    if series_list:
        metric = series_list[0].attrs.get("metric", "")
        if metric:
            return metric
    return "Value"
