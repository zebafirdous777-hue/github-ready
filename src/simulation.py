"""A small grid-based UAV mission demonstration.

The smoke cue in this simulation is synthetic. It is not produced by the
project's experimental smoke detector.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from navigation import find_coverage_route, find_route


def _print_map(grid_size, base, smoke_cue, obstacles, route_cells):
    """Print the grid from top to bottom with the planned round trip."""
    print("Grid map (* route, # obstacle, B base, S synthetic cue):")
    for y in range(grid_size - 1, -1, -1):
        row = []
        for x in range(grid_size):
            cell = (x, y)
            if cell == base:
                marker = "B"
            elif cell == smoke_cue:
                marker = "S"
            elif cell in obstacles:
                marker = "#"
            elif cell in route_cells:
                marker = "*"
            else:
                marker = "."
            row.append(marker)
        print(f"y={y} " + " ".join(row))
    print("    " + " ".join(str(x) for x in range(grid_size)) + "  x")


def _save_report(
    report_path, status, base, smoke_cue, obstacles, grid_size, max_flight_steps,
    patrol, route_out=None, route_home=None, total_steps=None, summary="",
):
    """Write a JSON record of the simulated mission."""
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "mode": "patrol" if patrol else "direct",
        "cue_source": "synthetic scenario; not model detection",
        "base": list(base),
        "synthetic_smoke_cue": list(smoke_cue),
        "grid_size": grid_size,
        "obstacles": [list(cell) for cell in sorted(obstacles)],
        "max_flight_steps": max_flight_steps,
        "route_out": [list(cell) for cell in route_out] if route_out else [],
        "route_home": [list(cell) for cell in route_home] if route_home else [],
        "flight_steps": total_steps,
        "remaining_steps": (
            max_flight_steps - total_steps if total_steps is not None else None
        ),
        "summary": summary,
    }
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Mission report saved: {destination}")


def run_mission(
    base, smoke_cue, obstacles, grid_size=5, max_flight_steps=20, patrol=False,
    report_path="runs/mission_report.json",
):
    """Plan and print a mission for a synthetic smoke cue."""
    print("Mission state: READY")
    print(f"UAV base: {base}; simulated smoke cue: {smoke_cue}")
    print("Smoke cue source: SYNTHETIC SCENARIO (not model detection)")

    cue_route = find_route(base, smoke_cue, obstacles, grid_size)
    route_out = (
        find_coverage_route(base, obstacles, grid_size)
        if patrol
        else cue_route
    )
    patrol_end = route_out[-1] if route_out else smoke_cue
    route_home = find_route(patrol_end, base, obstacles, grid_size)

    if cue_route is None or route_out is None or route_home is None:
        print("Mission state: ABORTED — no safe round-trip route")
        _save_report(
            report_path, "aborted", base, smoke_cue, obstacles, grid_size,
            max_flight_steps, patrol, route_out, route_home,
            summary="No safe round-trip route was found.",
        )
        return False

    total_steps = len(route_out) + len(route_home) - 2
    if total_steps > max_flight_steps:
        print(
            "Mission state: ABORTED — planned round trip needs "
            f"{total_steps} steps; limit is {max_flight_steps}"
        )
        _save_report(
            report_path, "aborted", base, smoke_cue, obstacles, grid_size,
            max_flight_steps, patrol, route_out, route_home, total_steps,
            summary="Planned round trip exceeds the flight-step budget.",
        )
        return False

    route_cells = set(route_out) | set(route_home)
    _print_map(grid_size, base, smoke_cue, obstacles, route_cells)

    mission_type = "PATROL" if patrol else "SEARCHING"
    print(f"Mission state: {mission_type} — planned flight distance {total_steps} steps")
    print(
        f"Flight-step budget: {total_steps}/{max_flight_steps} used; "
        f"{max_flight_steps - total_steps} steps remain"
    )
    for position in route_out[1:]:
        print(f"UAV position: {position}")
        if patrol and position == smoke_cue:
            print(f"Synthetic smoke cue encountered at {position}")

    if patrol:
        print("Patrol complete: all reachable grid cells were visited.")
    print("Mission state: INVESTIGATING")
    print("Synthetic smoke cue reached; no real-world fire alarm was generated.")
    print("Mission state: RETURNING")
    for position in route_home[1:]:
        print(f"UAV position: {position}")

    print(f"Mission state: LANDED — returned to base {base}")
    _save_report(
        report_path, "landed", base, smoke_cue, obstacles, grid_size,
        max_flight_steps, patrol, route_out, route_home, total_steps,
        summary="Simulation landed at base; the smoke cue was synthetic.",
    )
    return True
