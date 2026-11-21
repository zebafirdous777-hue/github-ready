"""Preliminary ideal hover sizing for the assigned conventional-helicopter concept.

This uses actuator-disk momentum theory as a lower-bound calculation. It does
not model coaxial wake interference, blade profile power, transmission or
electrical losses, ground effect, forward flight, gusts, or control margin.
"""

import argparse
import math


GRAVITY_M_S2 = 9.80665
SEA_LEVEL_DENSITY_KG_M3 = 1.225
LIPO_NOMINAL_CELL_VOLTAGE_V = 3.7


def calculate_hover(mass_kg, rotor_diameter_m, density_kg_m3,
                    figure_of_merit=None):
    """Return ideal hover requirements and an optional nonideal power estimate.

    ``rotor_diameter_m`` is the main-rotor diameter. A figure of merit must come
    from a stated assumption or rotor data; it is not inferred by this model.
    """
    values = (mass_kg, rotor_diameter_m, density_kg_m3)
    if not all(math.isfinite(value) and value > 0 for value in values):
        raise ValueError("mass, rotor diameter, and air density must be positive")
    if figure_of_merit is not None and not (
        math.isfinite(figure_of_merit) and 0 < figure_of_merit <= 1
    ):
        raise ValueError("figure of merit must be greater than 0 and at most 1")

    thrust_n = mass_kg * GRAVITY_M_S2
    radius_m = rotor_diameter_m / 2
    projected_disk_area_m2 = math.pi * radius_m**2
    disk_loading_n_m2 = thrust_n / projected_disk_area_m2
    ideal_induced_velocity_m_s = math.sqrt(
        thrust_n / (2 * density_kg_m3 * projected_disk_area_m2)
    )
    ideal_hover_power_w = thrust_n * ideal_induced_velocity_m_s
    hover_power_estimate_w = (
        ideal_hover_power_w / figure_of_merit
        if figure_of_merit is not None
        else None
    )

    return {
        "weight_thrust_n": thrust_n,
        "projected_disk_area_m2": projected_disk_area_m2,
        "disk_loading_n_m2": disk_loading_n_m2,
        "ideal_induced_velocity_m_s": ideal_induced_velocity_m_s,
        "ideal_hover_power_lower_bound_w": ideal_hover_power_w,
        "figure_of_merit": figure_of_merit,
        "hover_power_estimate_w": hover_power_estimate_w,
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description="Calculate ideal hover lower-bound values for the helicopter concept."
    )
    parser.add_argument("--mass-kg", type=float, default=6.5)
    parser.add_argument("--rotor-diameter-m", type=float, default=1.4)
    parser.add_argument(
        "--density-kg-m3", type=float, default=SEA_LEVEL_DENSITY_KG_M3,
        help="air density (default: standard sea-level value)",
    )
    parser.add_argument(
        "--figure-of-merit", type=float,
        help="optional assumed or measured rotor figure of merit in (0, 1]",
    )
    parser.add_argument("--battery-series-cells", type=int, default=6)
    parser.add_argument("--battery-capacity-ah", type=float, default=12.0)
    parser.add_argument(
        "--battery-mass-kg", type=float,
        help="optional battery mass for the takeoff-mass budget comparison",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.battery_series_cells <= 0 or args.battery_capacity_ah <= 0:
            raise ValueError("battery cell count and capacity must be positive")
        if args.battery_mass_kg is not None and (
            not math.isfinite(args.battery_mass_kg) or args.battery_mass_kg <= 0
        ):
            raise ValueError("battery mass must be positive")
        result = calculate_hover(
            args.mass_kg,
            args.rotor_diameter_m,
            args.density_kg_m3,
            args.figure_of_merit,
        )
    except ValueError as error:
        parser.error(str(error))

    print(f"Mass: {args.mass_kg:.3f} kg")
    print(f"Required hover thrust: {result['weight_thrust_n']:.2f} N")
    print(
        "Main-rotor disk area: "
        f"{result['projected_disk_area_m2']:.3f} m^2"
    )
    print(f"Disk loading: {result['disk_loading_n_m2']:.2f} N/m^2")
    print(
        "Ideal induced velocity: "
        f"{result['ideal_induced_velocity_m_s']:.2f} m/s"
    )
    print(
        "Ideal hover power lower bound: "
        f"{result['ideal_hover_power_lower_bound_w']:.1f} W"
    )
    nominal_voltage_v = args.battery_series_cells * LIPO_NOMINAL_CELL_VOLTAGE_V
    nominal_energy_wh = nominal_voltage_v * args.battery_capacity_ah
    print(
        f"Battery nominal energy: {nominal_energy_wh:.1f} Wh "
        f"({args.battery_series_cells}S, {args.battery_capacity_ah:.1f} Ah; "
        "3.7 V/cell nominal)"
    )
    power_for_runtime_w = result["hover_power_estimate_w"]
    if power_for_runtime_w is not None:
        idealized_runtime_min = nominal_energy_wh / power_for_runtime_w * 60
        print(
            "Idealized hover runtime ceiling: "
            f"{idealized_runtime_min:.1f} min (all nominal energy usable; "
            "excludes every battery, drive, and mission reserve/loss)"
        )
    else:
        print(
            "Hover runtime: not estimated; power and usable battery energy "
            "are not established."
        )
    if args.battery_mass_kg is not None:
        adjusted_mass_kg = args.mass_kg - 1.0 + args.battery_mass_kg
        print(
            f"Mass if replacing the 1.00 kg draft battery allowance: "
            f"{adjusted_mass_kg:.2f} kg"
        )
    if result["hover_power_estimate_w"] is None:
        print(
            "Nonideal hover power: not estimated; provide a justified or "
            "measured figure of merit."
        )
    else:
        print(
            "Indicative nonideal rotor power using figure of merit "
            f"{args.figure_of_merit:.3f}: "
            f"{result['hover_power_estimate_w']:.1f} W"
        )
    print(
        "Lower-bound only: excludes tail-rotor power, blade profile, "
        "drive/electrical losses, forward flight, and control reserve."
    )


if __name__ == "__main__":
    main()
