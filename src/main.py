"""Run the configurable software-only wildfire UAV mission scenario."""

import argparse

from simulation import run_mission
from helicopter import (
    DEFAULT_CROSSWIND_M_S,
    DEFAULT_GUST_DELTA_M_S,
    DEFAULT_GUST_DURATION_S,
    DEFAULT_GUST_START_S,
    MAX_ALTITUDE_M,
    run_integrated_helicopter_mission,
)


def parse_cell(value):
    """Parse a grid coordinate written as x,y."""
    try:
        x, y = value.split(",", maxsplit=1)
        return int(x), int(y)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"{value!r} must be two integers written as x,y (example: 2,3)"
        ) from error


def build_parser():
    parser = argparse.ArgumentParser(
        description="Simulate a grid-based UAV mission (the smoke cue is synthetic)."
    )
    parser.add_argument("--base", type=parse_cell, default=(0, 0), metavar="X,Y")
    parser.add_argument(
        "--smoke-cue", type=parse_cell, default=(4, 3), metavar="X,Y",
        help="synthetic cue location (default: 4,3)",
    )
    parser.add_argument(
        "--obstacle", type=parse_cell, action="append", metavar="X,Y",
        help="blocked grid cell; repeat this option for each obstacle",
    )
    parser.add_argument("--grid-size", type=int, default=5)
    parser.add_argument("--max-flight-steps", type=int, default=20)
    parser.add_argument(
        "--helicopter-flight", action="store_true",
        help="run a route-connected helicopter mission with simulated payload release",
    )
    parser.add_argument("--target-altitude-m", type=float, default=25.0)
    parser.add_argument("--payload-kg", type=float, default=1.0)
    parser.add_argument("--crosswind-m-s", type=float, default=DEFAULT_CROSSWIND_M_S)
    parser.add_argument("--gust-start-s", type=float, default=DEFAULT_GUST_START_S)
    parser.add_argument("--gust-duration-s", type=float, default=DEFAULT_GUST_DURATION_S)
    parser.add_argument("--gust-delta-m-s", type=float, default=DEFAULT_GUST_DELTA_M_S)
    parser.add_argument("--geofence-radius-m", type=float,
                        help="circular mission boundary radius in metres (default covers grid)")
    parser.add_argument(
        "--flight-report", default="runs/helicopter_flight_report.json",
        help="JSON report path for --helicopter-flight",
    )
    parser.add_argument(
        "--patrol", action="store_true",
        help="sweep every reachable cell before returning to base",
    )
    parser.add_argument(
        "--report", default="runs/mission_report.json",
        help="JSON report path (default: runs/mission_report.json)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    obstacles = set(args.obstacle) if args.obstacle is not None else {
        (2, 0), (2, 1), (2, 2)
    }

    if args.grid_size < 1:
        parser.error("--grid-size must be at least 1")
    if args.max_flight_steps < 1:
        parser.error("--max-flight-steps must be at least 1")

    named_cells = [("--base", args.base), ("--smoke-cue", args.smoke_cue)]
    named_cells.extend(("--obstacle", cell) for cell in obstacles)
    for option, (x, y) in named_cells:
        if not (0 <= x < args.grid_size and 0 <= y < args.grid_size):
            parser.error(
                f"{option} coordinate {x},{y} is outside the "
                f"{args.grid_size}x{args.grid_size} grid"
            )
    if args.base in obstacles:
        parser.error("the base cannot be placed on an obstacle")
    if args.smoke_cue in obstacles:
        parser.error("the synthetic smoke cue cannot be placed on an obstacle")

    if args.helicopter_flight:
        if args.target_altitude_m <= 0 or args.target_altitude_m > MAX_ALTITUDE_M:
            parser.error(f"--target-altitude-m must be >0 and at most {MAX_ALTITUDE_M:.2f}")
        if args.payload_kg <= 0:
            parser.error("--payload-kg must be positive")
        try:
            run_integrated_helicopter_mission(
                base=args.base,
                smoke_cue=args.smoke_cue,
                obstacles=obstacles,
                grid_size=args.grid_size,
                max_flight_steps=args.max_flight_steps,
                target_altitude_m=args.target_altitude_m,
                payload_mass_kg=args.payload_kg,
                crosswind_m_s=args.crosswind_m_s,
                gust_start_s=args.gust_start_s,
                gust_duration_s=args.gust_duration_s,
                gust_delta_m_s=args.gust_delta_m_s,
                geofence_radius_m=args.geofence_radius_m,
                report_path=args.flight_report,
            )
        except ValueError as error:
            parser.error(str(error))
        return

    run_mission(
        base=args.base,
        smoke_cue=args.smoke_cue,
        obstacles=obstacles,
        grid_size=args.grid_size,
        max_flight_steps=args.max_flight_steps,
        patrol=args.patrol,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
