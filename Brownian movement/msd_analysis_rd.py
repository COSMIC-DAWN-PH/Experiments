"""TrackMate MSD analysis with frame-centroid drift correction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from msd_analysis import (
    analyze_trackmate_msd,
    load_trackmate,
    select_tracks,
)


def correct_frame_centroid_drift(input_path: str | Path, min_frames: int):
    """Subtract cumulative mean displacement of tracks shared by adjacent frames.

    Comparing absolute frame centroids is biased when tracks enter or leave the
    field of view.  The mean displacement of particles linked across each frame
    pair is the corresponding centroid shift for a stable particle population.
    """
    df = select_tracks(load_trackmate(input_path), min_frames)
    frames = sorted(df["FRAME"].unique())
    cumulative_x = 0.0
    cumulative_y = 0.0
    drift_rows = [{"FRAME": frames[0], "DRIFT_X": 0.0, "DRIFT_Y": 0.0}]

    indexed = {
        frame: group.set_index("TRACK_ID")[["POSITION_X", "POSITION_Y"]]
        for frame, group in df.groupby("FRAME")
    }
    for previous_frame, frame in zip(frames[:-1], frames[1:]):
        previous = indexed[previous_frame]
        current = indexed[frame]
        common = previous.index.intersection(current.index)
        if frame - previous_frame == 1 and len(common) > 0:
            step = current.loc[common].to_numpy() - previous.loc[common].to_numpy()
            cumulative_x += float(step[:, 0].mean())
            cumulative_y += float(step[:, 1].mean())
        drift_rows.append(
            {"FRAME": frame, "DRIFT_X": cumulative_x, "DRIFT_Y": cumulative_y}
        )

    import pandas as pd

    shifts = pd.DataFrame(drift_rows).set_index("FRAME")
    corrected = df.join(shifts, on="FRAME")
    corrected["POSITION_X"] = corrected["POSITION_X"] - corrected["DRIFT_X"]
    corrected["POSITION_Y"] = corrected["POSITION_Y"] - corrected["DRIFT_Y"]
    return corrected.drop(columns=["DRIFT_X", "DRIFT_Y"])


def analyze_trackmate_msd_drift_corrected(
    input_path: str | Path,
    dt: float,
    pixel_to_um: float,
    output_dir: str | Path,
    label: str,
    min_frames: int = 20,
    fit_points: int = 10,
) -> dict[str, float | int | str]:
    """Correct drift, save a temporary cleaned CSV, then use the shared analyzer."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    corrected = correct_frame_centroid_drift(input_path, min_frames)
    corrected_csv = output_dir / f"{label}_centroid_corrected_input.csv"
    corrected.to_csv(corrected_csv, index=False)
    result = analyze_trackmate_msd(
        corrected_csv,
        dt,
        pixel_to_um,
        output_dir,
        label,
        min_frames,
        fit_points,
        corrected=True,
    )
    result["drift_method"] = (
        "cumulative centroid displacement of tracks shared by adjacent frames"
    )
    summary_path = output_dir / f"{label}_corrected_summary.json"
    summary_path.write_text(
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
    result = analyze_trackmate_msd_drift_corrected(
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
