"""Simplified helicopter mission simulation for the wildfire concept.

This is a teaching model, not flight-control software. It models only vertical
translation, a damped altitude controller, and the immediate mass change from
releasing payload. Horizontal navigation is represented by discrete waypoints
from the separate grid planner, not by modeled horizontal flight dynamics.
"""

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from performance import (
    GRAVITY_M_S2,
    SEA_LEVEL_DENSITY_KG_M3,
    calculate_hover,
)

MAX_ALTITUDE_M = 45.72  # Assignment limit: 150 ft AGL
DEFAULT_MASS_KG = 6.088
DEFAULT_ROTOR_DIAMETER_M = 1.248
DEFAULT_PAYLOAD_KG = 1.0
DEFAULT_BATTERY_ENERGY_WH = 115.0
FIGURE_OF_MERIT = 0.74
MAX_THRUST_TO_WEIGHT = 1.5  # Explicit simulation assumption; needs rotor test data
TIME_STEP_S = 0.05
DEFAULT_GRID_CELL_M = 10.0
DEFAULT_CROSSWIND_M_S = 5.0
DEFAULT_GUST_START_S = 90.0
DEFAULT_GUST_DURATION_S = 12.0
DEFAULT_GUST_DELTA_M_S = 0.5
SIDE_AREA_M2 = 0.6  # Explicit teaching-model assumption; not measured airframe data
SIDE_DRAG_COEFFICIENT = 1.0  # Explicit teaching-model assumption
MAX_LATERAL_ACCEL_M_S2 = 2.0


@dataclass
class FlightState:
    time_s: float = 0.0
    altitude_m: float = 0.0
    vertical_speed_m_s: float = 0.0
    mass_kg: float = DEFAULT_MASS_KG
    rotor_thrust_n: float = 0.0
    rotor_energy_wh: float = 0.0
    x_m: float = 0.0
    y_m: float = 0.0
    vx_m_s: float = 0.0
    vy_m_s: float = 0.0


class PayloadReleaseSystem:
    """Simulated normally-locked payload state machine and load confirmation."""

    def __init__(self, payload_mass_kg):
        self.payload_mass_kg = payload_mass_kg
        self.state = "LOCKED"
        self.rejection_reason = None
        self.events = [{"time_s": 0.0, "state": self.state}]

    def arm(self, time_s, *, target_confirmed, geofence_clear, altitude_m,
            vertical_speed_m_s, horizontal_speed_m_s):
        checks = {
            "target confirmed": target_confirmed,
            "geofence clear": geofence_clear,
            "release altitude is within the flight envelope": 0 < altitude_m <= MAX_ALTITUDE_M,
            "vertical speed is below 0.15 m/s": abs(vertical_speed_m_s) <= 0.15,
            "horizontal speed is below 0.3 m/s": horizontal_speed_m_s <= 0.3,
        }
        failed = [label for label, passed in checks.items() if not passed]
        if self.state != "LOCKED":
            self.rejection_reason = "payload is not in the locked state"
            return False
        if failed:
            self.rejection_reason = "; ".join(failed)
            return False
        self.state = "ARMED"
        self.events.append({"time_s": round(time_s, 3), "state": self.state})
        return True

    def release(self, time_s):
        if self.state != "ARMED":
            return False
        self.state = "RELEASED_UNCONFIRMED"
        self.events.append({"time_s": round(time_s, 3), "state": self.state})
        return True

    def confirm(self, time_s):
        if self.state != "RELEASED_UNCONFIRMED":
            return False
        self.state = "RELEASE_CONFIRMED_SIMULATED"
        self.events.append({
            "time_s": round(time_s, 3),
            "state": self.state,
            "source": "simulated payload-load sensor",
        })
        return True


class VerticalFlightSimulation:
    """Run a simple closed-loop vertical profile with a sudden payload release."""

    def __init__(
        self,
        takeoff_mass_kg=DEFAULT_MASS_KG,
        payload_mass_kg=DEFAULT_PAYLOAD_KG,
        rotor_diameter_m=DEFAULT_ROTOR_DIAMETER_M,
        target_altitude_m=25.0,
        hover_time_s=5.0,
        dt_s=TIME_STEP_S,
        max_thrust_to_weight=MAX_THRUST_TO_WEIGHT,
        figure_of_merit=FIGURE_OF_MERIT,
        crosswind_m_s=DEFAULT_CROSSWIND_M_S,
        grid_cell_m=DEFAULT_GRID_CELL_M,
        gust_start_s=DEFAULT_GUST_START_S,
        gust_duration_s=DEFAULT_GUST_DURATION_S,
        gust_delta_m_s=DEFAULT_GUST_DELTA_M_S,
    ):
        inputs = (
            takeoff_mass_kg, payload_mass_kg, rotor_diameter_m,
            target_altitude_m, hover_time_s, dt_s, max_thrust_to_weight,
            figure_of_merit, grid_cell_m, gust_start_s, gust_duration_s,
        )
        if not all(math.isfinite(value) and value > 0 for value in inputs):
            raise ValueError("all mass, geometry, timing, and control inputs must be positive")
        if payload_mass_kg >= takeoff_mass_kg:
            raise ValueError("payload mass must be less than takeoff mass")
        if target_altitude_m > MAX_ALTITUDE_M:
            raise ValueError(
                f"target altitude must not exceed {MAX_ALTITUDE_M:.2f} m (150 ft AGL)"
            )
        if not 0 < figure_of_merit <= 1:
            raise ValueError("figure of merit must be greater than 0 and at most 1")
        if not math.isfinite(crosswind_m_s):
            raise ValueError("crosswind speed must be finite")
        if not math.isfinite(gust_delta_m_s):
            raise ValueError("gust change must be finite")

        self.takeoff_mass_kg = takeoff_mass_kg
        self.payload_mass_kg = payload_mass_kg
        self.dry_mass_kg = takeoff_mass_kg - payload_mass_kg
        self.rotor_diameter_m = rotor_diameter_m
        self.target_altitude_m = target_altitude_m
        self.hover_time_s = hover_time_s
        self.dt_s = dt_s
        self.max_thrust_n = (
            takeoff_mass_kg * GRAVITY_M_S2 * max_thrust_to_weight
        )
        self.figure_of_merit = figure_of_merit
        self.crosswind_m_s = crosswind_m_s
        self.gust_start_s = gust_start_s
        self.gust_duration_s = gust_duration_s
        self.gust_delta_m_s = gust_delta_m_s
        self.gust_was_active = False
        self.gust_recovery_pending = False
        self.gust_end_time_s = None
        self.gust_recovery_time_s = None
        self.peak_gust_tracking_error_m = 0.0
        self.grid_cell_m = grid_cell_m
        self.grid_origin_cell = (0, 0)
        self.horizontal_target_m = (0.0, 0.0)
        self.peak_horizontal_tracking_error_m = 0.0
        self.peak_horizontal_hold_error_m = 0.0
        self.geofence_bounds_m = None
        self.geofence_radius_m = None
        self.geofence_breached = False
        self.geofence_breach_reason = None
        self.geofence_breach_time_s = None
        self.state = FlightState(mass_kg=takeoff_mass_kg)
        self.peak_altitude_after_release_m = 0.0
        self.release_altitude_m = None
        self.payload_released = False
        self.payload_release_confirmed = False
        self.payload_system = PayloadReleaseSystem(payload_mass_kg)
        self.states = []
        self.current_waypoint = None
        self._record("READY")

    def _power_w(self, thrust_n):
        if thrust_n <= 0:
            return 0.0
        hover = calculate_hover(
            self.state.mass_kg,
            self.rotor_diameter_m,
            SEA_LEVEL_DENSITY_KG_M3,
            self.figure_of_merit,
        )
        hover_thrust = hover["weight_thrust_n"]
        # Ideal actuator-disk power varies with thrust to the 3/2 power.
        return hover["hover_power_estimate_w"] * (thrust_n / hover_thrust) ** 1.5

    def _record(self, phase):
        target_x, target_y = self.horizontal_target_m
        horizontal_error = math.hypot(
            target_x - self.state.x_m, target_y - self.state.y_m
        )
        self.peak_horizontal_tracking_error_m = max(
            self.peak_horizontal_tracking_error_m, horizontal_error
        )
        if phase != "WAYPOINT_TRACKING":
            self.peak_horizontal_hold_error_m = max(
                self.peak_horizontal_hold_error_m, horizontal_error
            )
        self.states.append({
            "time_s": round(self.state.time_s, 3),
            "phase": phase,
            "altitude_m": round(self.state.altitude_m, 3),
            "vertical_speed_m_s": round(self.state.vertical_speed_m_s, 3),
            "mass_kg": round(self.state.mass_kg, 3),
            "thrust_n": round(self.state.rotor_thrust_n, 2),
            "x_m": round(self.state.x_m, 3),
            "y_m": round(self.state.y_m, 3),
            "vx_m_s": round(self.state.vx_m_s, 3),
            "vy_m_s": round(self.state.vy_m_s, 3),
            "horizontal_target_m": [round(target_x, 3), round(target_y, 3)],
            "horizontal_tracking_error_m": round(horizontal_error, 3),
            "crosswind_m_s": round(self._crosswind_at(self.state.time_s), 3),
            "gust_active": self._gust_active(self.state.time_s),
            "grid_waypoint": list(self.current_waypoint) if self.current_waypoint is not None else None,
            "geofence_breached": self.geofence_breached,
            "payload_state": self.payload_system.state,
        })

    def _gust_active(self, time_s):
        return self.gust_start_s <= time_s < self.gust_start_s + self.gust_duration_s

    def _crosswind_at(self, time_s):
        return self.crosswind_m_s + (
            self.gust_delta_m_s if self._gust_active(time_s) else 0.0
        )

    def _step_horizontal(self):
        """Track a waypoint against a steady, simplified lateral wind load."""
        state = self.state
        wind_x = self._crosswind_at(state.time_s)
        # Quadratic side-force model using air-relative velocity.
        rel_x = wind_x - state.vx_m_s
        rel_y = -state.vy_m_s
        force_scale = 0.5 * SEA_LEVEL_DENSITY_KG_M3 * SIDE_AREA_M2 * SIDE_DRAG_COEFFICIENT
        aero_x = force_scale * abs(rel_x) * rel_x / state.mass_kg
        aero_y = force_scale * abs(rel_y) * rel_y / state.mass_kg
        error_x = self.horizontal_target_m[0] - state.x_m
        error_y = self.horizontal_target_m[1] - state.y_m
        wind_feedforward_x = (
            force_scale * abs(wind_x) * wind_x / state.mass_kg
        )
        command_x = max(
            -MAX_LATERAL_ACCEL_M_S2,
            min(
                MAX_LATERAL_ACCEL_M_S2,
                0.8 * error_x - 1.8 * state.vx_m_s - wind_feedforward_x,
            ),
        )
        command_y = max(-MAX_LATERAL_ACCEL_M_S2, min(MAX_LATERAL_ACCEL_M_S2, 0.8 * error_y - 1.8 * state.vy_m_s))
        state.vx_m_s += (command_x + aero_x) * self.dt_s
        state.vy_m_s += (command_y + aero_y) * self.dt_s
        state.x_m += state.vx_m_s * self.dt_s
        state.y_m += state.vy_m_s * self.dt_s

    def _step(self, target_altitude_m, phase, hold_thrust_n=None):
        state = self.state
        self._step_horizontal()
        if hold_thrust_n is None:
            altitude_error = target_altitude_m - state.altitude_m
            # PD altitude controller; requested acceleration is deliberately
            # limited to keep the simulated maneuver gentle.
            requested_accel = max(
                -1.5, min(1.5, 0.8 * altitude_error - 1.8 * state.vertical_speed_m_s)
            )
            thrust_n = state.mass_kg * (GRAVITY_M_S2 + requested_accel)
        else:
            thrust_n = hold_thrust_n
        thrust_n = max(0.0, min(self.max_thrust_n, thrust_n))

        vertical_drag_n = 0.8 * state.vertical_speed_m_s
        acceleration_m_s2 = (
            thrust_n - state.mass_kg * GRAVITY_M_S2 - vertical_drag_n
        ) / state.mass_kg
        state.vertical_speed_m_s += acceleration_m_s2 * self.dt_s
        state.altitude_m += state.vertical_speed_m_s * self.dt_s
        if state.altitude_m < 0:
            state.altitude_m = 0.0
            state.vertical_speed_m_s = 0.0
        self._check_geofence()
        state.time_s += self.dt_s
        state.rotor_thrust_n = thrust_n
        state.rotor_energy_wh += self._power_w(thrust_n) * self.dt_s / 3600
        self._update_gust_metrics()
        self._record(phase)

    def _update_gust_metrics(self):
        time_s = self.state.time_s
        active = self._gust_active(time_s)
        error = math.hypot(
            self.horizontal_target_m[0] - self.state.x_m,
            self.horizontal_target_m[1] - self.state.y_m,
        )
        speed = math.hypot(self.state.vx_m_s, self.state.vy_m_s)
        if active:
            self.peak_gust_tracking_error_m = max(
                self.peak_gust_tracking_error_m, error
            )
            self.gust_was_active = True
            self.gust_recovery_pending = False
        elif self.gust_was_active:
            self.gust_was_active = False
            self.gust_recovery_pending = True
            self.gust_end_time_s = time_s
        elif self.gust_recovery_pending and error < 0.1 and speed < 0.1:
            self.gust_recovery_time_s = round(time_s - self.gust_end_time_s, 3)
            self.gust_recovery_pending = False

    def _check_geofence(self):
        if self.geofence_breached or self.geofence_bounds_m is None:
            return
        state = self.state
        if state.altitude_m > MAX_ALTITUDE_M:
            reason = f"altitude exceeded {MAX_ALTITUDE_M:.2f} m limit"
        elif math.hypot(state.x_m, state.y_m) > self.geofence_radius_m:
            reason = "horizontal position left configured mission boundary"
        else:
            return
        self.geofence_breached = True
        self.geofence_breach_reason = reason
        self.geofence_breach_time_s = round(state.time_s, 3)

    def _move_to_altitude(self, target_altitude_m, phase, timeout_s=45.0):
        start = self.state.time_s
        while self.state.time_s - start < timeout_s:
            self._step(target_altitude_m, phase)
            if (
                abs(self.state.altitude_m - target_altitude_m) < 0.05
                and abs(self.state.vertical_speed_m_s) < 0.08
            ):
                if target_altitude_m == 0.0:
                    self.state.altitude_m = 0.0
                    self.state.vertical_speed_m_s = 0.0
                    self._record(phase)
                return
        raise RuntimeError(f"vertical controller did not settle during {phase}")

    def _hold(self, duration_s, phase):
        steps = math.ceil(duration_s / self.dt_s)
        for _ in range(steps):
            self._step(self.target_altitude_m, phase)

    def climb(self):
        self._record("TAKEOFF")
        self._move_to_altitude(self.target_altitude_m, "CLIMB")

    def travel_waypoint(self, waypoint, rtl=False):
        """Track one scaled grid waypoint while controlling altitude."""
        self.current_waypoint = waypoint
        self.horizontal_target_m = (
            (waypoint[0] - self.grid_origin_cell[0]) * self.grid_cell_m,
            (waypoint[1] - self.grid_origin_cell[1]) * self.grid_cell_m,
        )
        start = self.state.time_s
        timeout_s = 300.0 if rtl else 90.0
        while self.state.time_s - start < timeout_s:
            self._step(self.target_altitude_m, "WAYPOINT_TRACKING")
            if self.geofence_breached and not rtl:
                return False
            error = math.hypot(
                self.horizontal_target_m[0] - self.state.x_m,
                self.horizontal_target_m[1] - self.state.y_m,
            )
            speed = math.hypot(self.state.vx_m_s, self.state.vy_m_s)
            final_base_waypoint = waypoint == self.grid_origin_cell
            position_tolerance_m = 0.1 if not rtl or final_base_waypoint else 0.75
            speed_tolerance_m_s = 0.1 if not rtl or final_base_waypoint else 0.5
            if error < position_tolerance_m and speed < speed_tolerance_m_s:
                return True
        raise RuntimeError(
            f"lateral controller did not reach waypoint {waypoint}; "
            f"position=({self.state.x_m:.2f}, {self.state.y_m:.2f}) m, "
            f"velocity=({self.state.vx_m_s:.2f}, {self.state.vy_m_s:.2f}) m/s, "
            f"time={self.state.time_s:.1f} s"
        )

    def release_and_recover(self, target_confirmed=False):
        for _ in range(math.ceil(self.hover_time_s / self.dt_s)):
            self._step(self.target_altitude_m, "SEARCH_AND_HOVER")
            if self.geofence_breached:
                return False

        horizontal_speed = math.hypot(self.state.vx_m_s, self.state.vy_m_s)
        if not self.payload_system.arm(
            self.state.time_s,
            target_confirmed=target_confirmed,
            geofence_clear=not self.geofence_breached,
            altitude_m=self.state.altitude_m,
            vertical_speed_m_s=self.state.vertical_speed_m_s,
            horizontal_speed_m_s=horizontal_speed,
        ):
            return False

        self.release_altitude_m = self.state.altitude_m
        previous_thrust_n = self.state.rotor_thrust_n
        self.payload_system.release(self.state.time_s)
        self.state.mass_kg -= self.payload_mass_kg
        self.payload_released = True
        # Keep the prior rotor thrust for one short step to represent the
        # immediate upward disturbance before the controller responds.
        self._step(self.target_altitude_m, "PAYLOAD_RELEASE", hold_thrust_n=previous_thrust_n)
        self.peak_altitude_after_release_m = self.state.altitude_m
        for _ in range(math.ceil(0.25 / self.dt_s)):
            self._step(self.target_altitude_m, "PAYLOAD_CONFIRMATION")
        self.payload_release_confirmed = self.payload_system.confirm(self.state.time_s)
        self._record("RELEASE_CONFIRMED_SIMULATED")

        start = self.state.time_s
        while self.state.time_s - start < 8.0:
            self._step(self.target_altitude_m, "POST_RELEASE_RECOVERY")
            if self.geofence_breached:
                return True
            self.peak_altitude_after_release_m = max(
                self.peak_altitude_after_release_m, self.state.altitude_m
            )
        return True

    def land(self):
        self._move_to_altitude(0.0, "RETURN_AND_DESCENT")
        self._record("LANDED")

    def run(self):
        self.current_waypoint = (0, 0)
        self.climb()
        self.release_and_recover(target_confirmed=True)
        self.land()

        return self.report()

    def report(self):
        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "simulation_type": "simplified vertical helicopter flight; not 6-DOF",
            "horizontal_motion_model": "2D waypoint tracking with simplified quadratic crosswind load",
            "configuration_reference": "ALIGN T-REX 550X geometry reference; not payload-rated",
            "model_limits": [
                "No attitude dynamics, turbulent gusts, rotor/airframe coupling, or measured aerodynamic coefficients",
                "Crosswind is eastward with a deterministic square gust; assumed side area 0.6 m2 and drag coefficient 1.0",
                "No tail-rotor power, blade profile power, or electrical losses",
                "Maximum thrust is an assumed 1.5 times loaded weight, not a measured value",
                "Payload release and release confirmation are simulated",
            ],
            "status": "landed" if self.state.altitude_m == 0 else "incomplete",
            "target_altitude_m": self.target_altitude_m,
            "altitude_limit_m": MAX_ALTITUDE_M,
            "rotor_diameter_m": self.rotor_diameter_m,
            "payload_mass_kg": self.payload_mass_kg,
            "payload_released": self.payload_released,
            "payload_release_confirmed": self.payload_release_confirmed,
            "payload_state": self.payload_system.state,
            "payload_rejection_reason": self.payload_system.rejection_reason,
            "payload_event_log": self.payload_system.events,
            "payload_release_interlocks": [
                "synthetic target confirmed",
                "geofence clear",
                "altitude within (0, 45.72] m",
                "vertical speed at most 0.15 m/s",
                "horizontal speed at most 0.3 m/s",
            ],
            "takeoff_mass_kg": self.takeoff_mass_kg,
            "post_release_mass_kg": self.dry_mass_kg,
            "release_altitude_m": round(self.release_altitude_m or 0.0, 3),
            "peak_altitude_after_release_m": round(
                self.peak_altitude_after_release_m, 3
            ),
            "peak_deviation_after_release_m": round(
                self.peak_altitude_after_release_m - (self.release_altitude_m or 0.0), 3
            ),
            "idealized_rotor_energy_wh": round(self.state.rotor_energy_wh, 3),
            "reference_battery_energy_wh": DEFAULT_BATTERY_ENERGY_WH,
            "mission_time_s": round(self.state.time_s, 2),
            "crosswind_speed_m_s": self.crosswind_m_s,
            "crosswind_direction": "eastward",
            "wind_profile": {
                "baseline_m_s": self.crosswind_m_s,
                "gust_start_s": self.gust_start_s,
                "gust_duration_s": self.gust_duration_s,
                "gust_delta_m_s": self.gust_delta_m_s,
                "gust_peak_m_s": self.crosswind_m_s + self.gust_delta_m_s,
            },
            "peak_gust_tracking_error_m": round(self.peak_gust_tracking_error_m, 3),
            "gust_recovery_time_s": self.gust_recovery_time_s,
            "gust_recovery_criterion": "time after gust ends until horizontal error <0.1 m and speed <0.1 m/s",
            "geofence_breached": self.geofence_breached,
            "geofence_breach_reason": self.geofence_breach_reason,
            "geofence_breach_time_s": self.geofence_breach_time_s,
            "geofence_bounds_m": list(self.geofence_bounds_m) if self.geofence_bounds_m else None,
            "geofence_radius_m": self.geofence_radius_m,
            "assumed_side_area_m2": SIDE_AREA_M2,
            "assumed_side_drag_coefficient": SIDE_DRAG_COEFFICIENT,
            "grid_cell_spacing_m": self.grid_cell_m,
            "final_horizontal_position_m": [round(self.state.x_m, 3), round(self.state.y_m, 3)],
            "peak_horizontal_tracking_error_m": round(self.peak_horizontal_tracking_error_m, 3),
            "peak_horizontal_hold_error_m": round(self.peak_horizontal_hold_error_m, 3),
            "states": self.states,
        }


def run_integrated_helicopter_mission(
    base=(0, 0), smoke_cue=(4, 3), obstacles=None, grid_size=5,
    max_flight_steps=20, target_altitude_m=25.0,
    payload_mass_kg=DEFAULT_PAYLOAD_KG,
    crosswind_m_s=DEFAULT_CROSSWIND_M_S,
    gust_start_s=DEFAULT_GUST_START_S,
    gust_duration_s=DEFAULT_GUST_DURATION_S,
    gust_delta_m_s=DEFAULT_GUST_DELTA_M_S,
    geofence_radius_m=None,
    report_path="runs/helicopter_flight_report.json",
):
    """Combine vertical flight dynamics with the existing grid route planner."""
    from navigation import find_route

    obstacles = set(obstacles or ())
    route_out = find_route(base, smoke_cue, obstacles, grid_size)
    route_home = find_route(smoke_cue, base, obstacles, grid_size)
    if route_out is None or route_home is None:
        raise ValueError("no safe outbound and return route exists for this scenario")
    route_steps = len(route_out) + len(route_home) - 2
    if route_steps > max_flight_steps:
        raise ValueError(
            f"round trip needs {route_steps} grid steps, exceeding limit {max_flight_steps}"
        )

    sim = VerticalFlightSimulation(
        payload_mass_kg=payload_mass_kg,
        target_altitude_m=target_altitude_m,
        crosswind_m_s=crosswind_m_s,
        gust_start_s=gust_start_s,
        gust_duration_s=gust_duration_s,
        gust_delta_m_s=gust_delta_m_s,
    )
    if geofence_radius_m is None:
        geofence_radius_m = math.hypot(
            (grid_size - 1) * sim.grid_cell_m,
            (grid_size - 1) * sim.grid_cell_m,
        ) + 5.0
    if not math.isfinite(geofence_radius_m) or geofence_radius_m <= 0:
        raise ValueError("geofence radius must be finite and positive")
    sim.geofence_radius_m = geofence_radius_m
    sim.geofence_bounds_m = [-geofence_radius_m, -geofence_radius_m, geofence_radius_m, geofence_radius_m]
    sim.grid_origin_cell = base
    sim.current_waypoint = base
    print("Integrated helicopter mission simulation")
    print(
        f"Wind: {crosswind_m_s:.1f} m/s baseline; +{gust_delta_m_s:.1f} m/s gust "
        f"from {gust_start_s:.1f} to {gust_start_s + gust_duration_s:.1f} s"
    )
    print("Target source: SYNTHETIC SCENARIO (not detector output)")
    print(f"Outbound route: {route_out}")
    print(f"Return route:   {route_home}")
    print(f"Grid step budget: {route_steps}/{max_flight_steps} used")
    print(f"Geofence radius from base: {sim.geofence_radius_m:.1f} m")

    sim.climb()
    trail = [base]
    if sim.geofence_breached:
        print(f"Geofence breach: {sim.geofence_breach_reason}")
    else:
        for waypoint in route_out[1:]:
            if not sim.travel_waypoint(waypoint):
                print(f"Geofence breach: {sim.geofence_breach_reason}")
                break
            trail.append(waypoint)
            print(f"Outbound waypoint reached: {waypoint}")

    delivery_completed = False
    if not sim.geofence_breached:
        print(f"Synthetic target reached at {smoke_cue}; simulated delivery sequence begins")
        delivery_completed = sim.release_and_recover(
            target_confirmed=(sim.current_waypoint == smoke_cue)
        )
        if sim.geofence_breached:
            print(f"Geofence breach: {sim.geofence_breach_reason}")

    if not sim.geofence_breached:
        for waypoint in route_home[1:]:
            if not sim.travel_waypoint(waypoint):
                print(f"Geofence breach: {sim.geofence_breach_reason}")
                break
            trail.append(waypoint)
            print(f"Return waypoint reached: {waypoint}")

    if sim.geofence_breached:
        print("FAILSAFE: canceling mission and retracing last safe waypoints to base")
        if trail[-1] != base:
            sim.travel_waypoint(trail[-1], rtl=True)
            print(f"Failsafe waypoint reached: {trail[-1]}")
        for waypoint in reversed(trail[:-1]):
            if waypoint != sim.current_waypoint:
                sim.travel_waypoint(waypoint, rtl=True)
                print(f"Failsafe waypoint reached: {waypoint}")
        sim.horizontal_target_m = (0.0, 0.0)
        sim.current_waypoint = base
    else:
        delivery_completed = sim.payload_release_confirmed
    sim.land()
    report = sim.report()
    report.update({
        "simulation_type": "vertical dynamics and simplified 2D waypoint tracking; not 6-DOF",
        "mission_mode": "outbound, synthetic-target hover, simulated payload release, return",
        "cue_source": "synthetic scenario; not detector output",
        "base": list(base),
        "synthetic_target": list(smoke_cue),
        "obstacles": [list(cell) for cell in sorted(obstacles)],
        "grid_size": grid_size,
        "max_flight_steps": max_flight_steps,
        "route_steps": route_steps,
        "remaining_grid_steps": max_flight_steps - route_steps,
        "delivery_completed": delivery_completed,
        "mission_outcome": (
            "failsafe_returned_to_base" if sim.geofence_breached
            else "delivery_confirmed_and_returned" if delivery_completed
            else "returned_without_delivery"
        ),
        "route_out": [list(cell) for cell in route_out],
        "route_home": [list(cell) for cell in route_home],
        "model_limits": report["model_limits"] + [
            "Grid cells are assumed 10 m apart for this demo; no real map scale is implied",
            "Target is synthetic; no detector or real suppressant is used",
        ],
    })
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Mission duration (vertical model clock): {report['mission_time_s']:.1f} s")
    if report["payload_release_confirmed"]:
        print(f"Payload released and confirmed (simulated): {report['payload_mass_kg']:.3f} kg")
    elif report["payload_released"]:
        print("Payload released, but simulated confirmation did not complete")
    elif report["payload_rejection_reason"]:
        print(f"Payload stayed locked: {report['payload_rejection_reason']}")
    else:
        print("Payload release: canceled by failsafe")
    print(f"Altitude deviation after release: {report['peak_deviation_after_release_m']:.3f} m")
    print(f"Peak hold position error: {report['peak_horizontal_hold_error_m']:.3f} m")
    print(f"Peak position error during gust: {report['peak_gust_tracking_error_m']:.3f} m")
    print(f"Gust recovery time: {report['gust_recovery_time_s']} s")
    print("Mission state: LANDED (simulation)")
    print(f"Flight report saved: {destination}")
    return report


def run_helicopter_demo(
    takeoff_mass_kg=DEFAULT_MASS_KG,
    payload_mass_kg=DEFAULT_PAYLOAD_KG,
    rotor_diameter_m=DEFAULT_ROTOR_DIAMETER_M,
    target_altitude_m=25.0,
    hover_time_s=5.0,
    report_path="runs/helicopter_flight_report.json",
):
    sim = VerticalFlightSimulation(
        takeoff_mass_kg=takeoff_mass_kg,
        payload_mass_kg=payload_mass_kg,
        rotor_diameter_m=rotor_diameter_m,
        target_altitude_m=target_altitude_m,
        hover_time_s=hover_time_s,
    )
    report = sim.run()
    print("Simplified 1D vertical helicopter flight simulation")
    print("Horizontal routing remains handled by the existing grid planner.")
    print(f"Takeoff mass: {report['takeoff_mass_kg']:.3f} kg")
    print(f"Payload release: {report['payload_mass_kg']:.3f} kg at {report['release_altitude_m']:.2f} m")
    print(f"Post-release mass: {report['post_release_mass_kg']:.3f} kg")
    print(f"Altitude change after release: {report['peak_deviation_after_release_m']:.3f} m")
    print(f"Mission duration: {report['mission_time_s']:.1f} s")
    print(f"Idealized rotor energy: {report['idealized_rotor_energy_wh']:.2f} Wh")
    print("Mission state: LANDED (simulation)")
    destination = Path(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Flight report saved: {destination}")
    return report
