# Helicopter Project Alignment Checklist

**Assigned project:** Autonomous Helicopter for Wildfire Reconnaissance and
Precision Fire-Suppressant Delivery

**Source brief:** `Helicopter_Design_project1 (1).docx` supplied by the student.

This checklist follows the assignment brief. The repository began as a
software-only wildfire UAV exploration, so existing components are reusable
groundwork rather than completed helicopter requirements.

## Assignment requirements and current status

| Assignment requirement | Status | What remains |
| --- | --- | --- |
| Select a rotorcraft configuration and define its geometry, mass, powertrain, payload location, centre of gravity, and release mechanism | Partial | A conventional single-main-rotor reference geometry and 6S powertrain have been documented; payload placement, CG, and release design remain open. |
| Analyse thrust, disc and power loading, hover power, rotor efficiency, ground effect, forward-flight drag, wake, and tip speed | Partial | Ideal hover thrust, disk loading, induced velocity, and power are calculated; add tip speed, tail-rotor power, drag, ground effect, and control margin. |
| Evaluate crosswind and gust response, attitude and altitude deviation, recovery time, and control effort | Partial | The integrated route includes a deterministic lateral square gust and tracking/recovery metrics; turbulent gusts, attitude, and validated aircraft performance remain. |
| Design a payload system with secure retention, controlled release, no accidental release, limited CG shift, release confirmation, and stable post-drop flight | Partial | A simulated normally-locked state machine now requires target, geofence, altitude, and stability interlocks, then records a simulated load-sensor confirmation; hardware retention, CG shift, and sensor validation remain. |
| Identify the designated target using vision, a marker, GPS, or a documented combination | Partial groundwork | Local validation results and separate publisher-reported test/field metrics are documented, but the publisher's evaluation images are not available here. The smoke model remains experimental and is not connected to mission control; independent mission-matched labeled imagery is needed before making generalization claims. |
| Complete the mission: vertical takeoff, climb, search, identify, hover, deliver at least 1 kg, return, vertical landing, and abort/return-to-launch | Partial | The simulation runs an outbound and return route, hover, and simulated payload release; target identification is synthetic and the failsafe return is simulation-only. |
| Respect the brief's limits: MTOW at most 7 kg, payload at least 1 kg, rotor diameter at most 1.5 m, electric propulsion, battery at most 6S/12,000 mAh, altitude at most 150 ft AGL, geofence and failsafe | Partial | The mass estimate is unverified and may double-count motor/ESC because the T-REX kit weight basis is ambiguous; the reference airframe has no documented 1 kg payload rating. Payload-rated electric helicopter examples found are above the 7 kg limit. Geofence and return logic remain simulation-only. |

## Reusable work already in this repository

- Grid-based obstacle-aware route planning and patrol coverage.
- A simple mission state flow, step budget, and JSON mission report.
- Smoke-detector evaluation on a validation set, with limitations documented.

The integrated flight profile models altitude, vertical speed, thrust, a
simplified 2D route tracker under a steady assumed crosswind, and the mass
change from a simulated payload release. It is not a full aerodynamic or
attitude model; gust rejection and a real target-identification system remain
unimplemented. The mission cue remains synthetic.

## Build order

1. **Freeze the requirements and simulation scope.** Use this assignment as the
   source of truth; keep all assumed values visible and label simulated results.
2. **Create a feasible conceptual helicopter design.** Select a configuration
   and refine the documented reference-based mass, rotor, motor, battery,
   payload, and centre-of-gravity budget with verified component data.
3. **Add rotor and flight-performance calculations.** Calculate hover and
   forward-flight requirements before implementing a flight simulation.
4. **Improve helicopter disturbance modeling.** Add turbulent gusts, attitude
   response, and validate recovery/control metrics against aircraft data.
5. **Add target identification and mission integration.** Keep the current
   smoke model marked experimental unless independent evaluation supports it.
6. **Refine payload delivery.** Add a payload position/CG model and release
   confirmation fault cases; physical retention and sensor validation remain
   separate hardware work.
7. **Run and document the integrated scenarios.** The nominal, geofence-abort,
   and stronger-gust demonstrations are recorded in
   `docs/FINAL_PROJECT_REPORT.md`; clearly identify the stronger-gust release
   lockout as a failed delivery case and keep all results labeled as simulated.

## Scope note

The brief describes designing, developing, and demonstrating a helicopter and
sets competition-style physical limits. This repository currently has no
helicopter hardware model. The work can first deliver a simulation-based
demonstration, but any required physical prototype or flight test must be
confirmed with the instructor and handled under proper supervision; simulated
results must not be presented as real flight testing.

## Remaining engineering work

The simulation-first academic prototype is documented, but physical design
compliance is not established. Any continuation should first confirm the exact
reference-kit contents and mass, select a rotorcraft with documented payload
capacity that fits the assignment limits, and replace allowances with measured
component data. Higher-fidelity attitude and turbulence models, independent
mission-matched target-identification data, and supervised hardware validation
remain future work. Do not present simulated behavior as flight testing.
