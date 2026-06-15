"""TrackMate trajectory and mean-square-displacement analysis.

This module analyzes uncorrected trajectories.  The companion
``msd_analysis_rd.py`` imports the shared helpers and applies frame-centroid
drift correction before running the same calculation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["TRACK_ID", "FRAME", "POSITION_X", "POSITION_Y"]


def load_trackmate(path: str | Path) -> pd.DataFrame:
    """Load TrackMate CSV/XLSX exports and remove their three metadata rows."""
    path = Path(path)
    if path.suffix.lower() == ".csv":
        # Metadata rows in native TrackMate exports are discarded below by
        # numeric coercion; this also keeps ordinary one-header CSVs readable.
        df = pd.read_csv(path, low_memory=False)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported input format: {path.suffix}")

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing TrackMate columns: {sorted(missing)}")

    for column in REQUIRED_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=REQUIRED_COLUMNS).copy()
    df["TRACK_ID"] = df["TRACK_ID"].astype(int)
    df["FRAME"] = df["FRAME"].astype(int)
    df = df.sort_values(["TRACK_ID", "FRAME"])
    df = df.drop_duplicates(["TRACK_ID", "FRAME"], keep="first")
    return df


def select_tracks(df: pd.DataFrame, min_frames: int) -> pd.DataFrame:
    """Keep tracks long enough for a stable short-lag MSD estimate."""
    lengths = df.groupby("TRACK_ID").size()
    valid_ids = lengths[lengths >= min_frames].index
    selected = df[df["TRACK_ID"].isin(valid_ids)].copy()
    if selected.empty:
        raise ValueError(f"No trajectories contain at least {min_frames} frames")
    return selected


def calculate_ensemble_msd(
    df: pd.DataFrame,
    dt: float,
    pixel_to_um: float,
    max_lag_fraction: float = 1 / 3,
) -> tuple[pd.DataFrame, list[tuple[np.ndarray, np.ndarray]]]:
    """Calculate per-track MSD curves and a displacement-count weighted mean."""
    sums: dict[int, float] = {}
    counts: dict[int, int] = {}
    individual: list[tuple[np.ndarray, np.ndarray]] = []

    for _, track in df.groupby("TRACK_ID"):
        track = track.sort_values("FRAME")
        frames = track["FRAME"].to_numpy(dtype=int)
        coords = (
            track[["POSITION_X", "POSITION_Y"]].to_numpy(dtype=float)
            * pixel_to_um
        )
        max_lag = max(2, int(len(track) * max_lag_fraction))
        track_lags: list[int] = []
        track_msds: list[float] = []

        for lag in range(1, max_lag):
            frame_gap = frames[lag:] - frames[:-lag]
            valid = frame_gap == lag
            if not np.any(valid):
                continue
            delta = coords[lag:] - coords[:-lag]
            squared = np.sum(delta[valid] ** 2, axis=1)
            sums[lag] = sums.get(lag, 0.0) + float(np.sum(squared))
            counts[lag] = counts.get(lag, 0) + int(squared.size)
            track_lags.append(lag)
            track_msds.append(float(np.mean(squared)))

        if track_lags:
            individual.append(
                (np.asarray(track_lags, dtype=float) * dt, np.asarray(track_msds))
            )

    rows = [
        {
            "lag_frames": lag,
            "lag_s": lag * dt,
            "msd_um2": sums[lag] / counts[lag],
            "displacement_count": counts[lag],
        }
        for lag in sorted(sums)
        if counts[lag] > 0
    ]
    msd = pd.DataFrame(rows)
    if len(msd) < 2:
        raise ValueError("Insufficient valid lag points for MSD fitting")
    return msd, individual


def fit_early_msd(msd: pd.DataFrame, fit_points: int) -> dict[str, float | int]:
    """Fit the short-time diffusive region to MSD = slope * tau + intercept."""
    n_fit = min(max(2, fit_points), len(msd))
    fit = msd.iloc[:n_fit]
    x = fit["lag_s"].to_numpy()
    y = fit["msd_um2"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    predicted = slope * x + intercept
    ss_res = float(np.sum((y - predicted) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {
        "fit_points": n_fit,
        "fit_max_lag_s": float(x[-1]),
        "slope_um2_s": float(slope),
        "intercept_um2": float(intercept),
        "diffusion_um2_s": float(slope / 4.0),
        "r_squared": float(r_squared),
    }


def plot_trajectories(
    df: pd.DataFrame, pixel_to_um: float, output_path: Path, title: str
) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    for _, track in df.groupby("TRACK_ID"):
        ax.plot(
            track["POSITION_X"] * pixel_to_um,
            track["POSITION_Y"] * pixel_to_um,
            linewidth=0.7,
            alpha=0.65,
        )
    ax.set_xlabel(r"$x$ ($\mu$m)")
    ax.set_ylabel(r"$y$ ($\mu$m)")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def plot_msd(
    msd: pd.DataFrame,
    individual: list[tuple[np.ndarray, np.ndarray]],
    fit: dict[str, float | int],
    output_path: Path,
    title: str,
) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    for time, values in individual:
        ax.plot(time, values, color="0.65", alpha=0.16, linewidth=0.6)
    ax.plot(
        msd["lag_s"],
        msd["msd_um2"],
        color="#c51b2f",
        linewidth=2.2,
        label="Ensemble average",
    )
    fit_x = msd["lag_s"].iloc[: int(fit["fit_points"])].to_numpy()
    fit_y = float(fit["slope_um2_s"]) * fit_x + float(fit["intercept_um2"])
    ax.plot(
        fit_x,
        fit_y,
        "--",
        color="#2166ac",
        linewidth=2,
        label=(
            rf"Fit: $4D={fit['slope_um2_s']:.3g}$ $\mu$m$^2$/s, "
            rf"$R^2={fit['r_squared']:.3f}$"
        ),
    )
    ax.set_xlabel(r"Lag time $\tau$ (s)")
    ax.set_ylabel(r"MSD ($\mu$m$^2$)")
    ax.set_title(title)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=220)
    plt.close(fig)


def analyze_trackmate_msd(
    input_path: str | Path,
    dt: float,
    pixel_to_um: float,
    output_dir: str | Path,
    label: str,
    min_frames: int = 20,
    fit_points: int = 10,
    corrected: bool = False,
) -> dict[str, float | int | str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    df = select_tracks(load_trackmate(input_path), min_frames)
    msd, individual = calculate_ensemble_msd(df, dt, pixel_to_um)
    fit = fit_early_msd(msd, fit_points)
    mode = "corrected" if corrected else "raw"
    prefix = f"{label}_{mode}"

    plot_trajectories(
        df,
        pixel_to_um,
        output_dir / f"{prefix}_trajectories.png",
        f"{label}: {'drift-corrected' if corrected else 'raw'} trajectories",
    )
    plot_msd(
        msd,
        individual,
        fit,
        output_dir / f"{prefix}_msd.png",
        f"{label}: {'drift-corrected' if corrected else 'raw'} MSD",
    )
    msd.to_csv(output_dir / f"{prefix}_msd.csv", index=False)

    result: dict[str, float | int | str] = {
        "label": label,
        "mode": mode,
        "input": str(Path(input_path)),
        "dt_s": dt,
        "pixel_to_um": pixel_to_um,
        "minimum_track_frames": min_frames,
        "selected_tracks": int(df["TRACK_ID"].nunique()),
        "selected_spots": int(len(df)),
        **fit,
    }
    (output_dir / f"{prefix}_summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--dt", type=float, required=True, help="Frame interval (s)")
    parser.add_argument("--pixel-to-um", type=float, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--min-frames", type=int, default=20)
    parser.add_argument("--fit-points", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = analyze_trackmate_msd(
        args.input,
        args.dt,
        args.pixel_to_um,
        args.output_dir,
        args.label,
        args.min_frames,
        args.fit_points,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
