# Preliminary Helicopter Concept

## Assignment

Autonomous Helicopter for Wildfire Reconnaissance and Precision
Fire-Suppressant Delivery

This is a **simulation-first concept** for the assigned project. It is not a
fabrication drawing, a selected bill of materials, or evidence that a physical
aircraft can safely meet the requirements. The configuration below is grounded
in published reference-platform specifications where available; added autonomy
and payload masses remain design allowances.

## Configuration choice

- **Rotor layout:** Conventional single main rotor with tail rotor. This is
  allowed by the assignment, which permits conventional/tandem arrangements as
  alternatives to coaxial. An ALIGN T-REX 550X is used as a reference geometry
  and propulsion starting point because its published 6S setup and rotor size
  fit the assignment envelope. It is not assumed to be payload-rated for this
  mission.
- **Propulsion:** Electric, 6S LiPo reference setup.
- **Mission:** Vertical takeoff, climb, search, identify a simulated fire
  target, establish hover, release a simulated suppressant payload, confirm
  release, return to base, and land. Abort/return-to-launch is a required
  alternate path.
- **Targeting:** Vision-assisted identification is the intended AIML component.
  The current smoke detector is experimental and will not be treated as a
  dependable mission trigger. A clearly labelled simulated target/marker will
  be used while detector performance is evaluated separately.

## Constraint ledger

| Item | Assignment limit | Reference / working target | Status |
| --- | ---: | ---: | --- |
| Maximum takeoff mass | 7.0 kg | 6.09 kg provisional estimate | Not demonstrated: base kit contents and integration allowances are unverified; no physical weighing |
| Suppressant payload | At least 1.0 kg | 1.0 kg design target | Not demonstrated: reference airframe has no documented payload rating; release system not built |
| Main rotor diameter | At most 1.5 m | 1.248 m (T-REX 550X) | Manufacturer geometry; payload effects unverified |
| Battery | At most 6S, 12,000 mAh | 6S, 5.2 Ah reference pack | Manufacturer pack is 0.780 kg; current and fit need final integration check |
| Propulsion | Electric | 6S 730MX / RCE-BL100A reference | Published motor/ESC specs; payload duty not validated |
| Flight altitude | At most 150 ft AGL (45.72 m) | Simulated limit 45.72 m | Software limit only; no hardware validation |
| Failsafe | Mandatory | Abort/return-to-launch states | Software simulation implemented; no hardware failsafe |
| Geofence | Mandatory | Configurable bounded area | Software simulation implemented; no hardware geofence |

## Reference component screening

| Component / reference | Published specification used | Design use and limitation |
| --- | --- | --- |
| ALIGN T-REX 550X | Main rotor diameter 1,248 mm; 550 mm blades; 2,590 g weight with kit contents ambiguous; 6S 2,600-5,200 mAh battery range | Geometry and starting platform reference only; manufacturer does not state a 1 kg payload rating or autonomous capability |
| ALIGN 730MX motor | 850 KV, 6S, 380 g, 2,550 W maximum continuous output (manufacturer specification) | Reference powerplant; its published peak rating is not a hover-power measurement for this mission |
| ALIGN RCE-BL100A ESC | 3-6S, 100 A continuous, 138 g | Reference ESC; verify thermal/current margins for the simulated mission profile |
| ALIGN HBP52004 battery | 6S, 5.2 Ah, 115 Wh, 780 g | Reference battery mass/energy; confirm physical tray fit, discharge limits, and usable reserve |

These are screening references, not a purchase list. ALIGN's English page
describes the 2.590 kg figure as excluding the power system, while the product
listing says fully equipped without battery and enumerates motor, ESC, servos,
and flybarless controller among the accessories. The exact mass contents must
be confirmed before using this as a closed aircraft mass. The stock platform
was designed for hobby flight, not firefighting or payload delivery. No source
found establishes a safe 1 kg external payload rating, safe release, or
autonomous flight capability.

## Provisional mass budget

The T-REX 550X weight basis is unresolved. ALIGN's English specification calls
2.590 kg the weight without the power system; its product listing describes
2.590 kg as fully equipped without the battery and lists the motor, ESC,
servos, and flybarless controller as package accessories. Until the exact kit
contents are confirmed, the ledger below keeps the earlier conservative
interpretation that adds the motor and ESC separately. This may double-count
those items. The 0.70 kg autonomy/sensor allowance and 0.50 kg
wiring/mounts/release allowance are not measured. Treat 6.088 kg as a
provisional planning sum, not a verified MTOW.

| Subsystem | Mass used |
| --- | ---: |
| T-REX 550X listed weight basis (contents need confirmation) | 2.590 kg |
| ALIGN 730MX motor (may already be included in kit weight) | 0.380 kg |
| ALIGN RCE-BL100A ESC (may already be included in kit weight) | 0.138 kg |
| ALIGN HBP52004 6S 5.2 Ah battery | 0.780 kg |
| Autopilot, navigation, camera, radio, and sensors (allowance) | 0.700 kg |
| Wiring, mounts, tank, and release mechanism (allowance) | 0.500 kg |
| Suppressant payload | 1.000 kg |
| **Planning takeoff mass** | **6.088 kg** |
| **Arithmetic headroom to 7.0 kg limit** | **0.912 kg** |

The base mass description and included components must be reconciled against
the exact purchased kit before treating this sum as complete. Under the
alternate interpretation that the 2.590 kg already includes the motor and ESC,
the arithmetic subtotal would be 5.570 kg before resolving the other contents
and allowances. Neither subtotal is verified aircraft mass. Also reserve mass
for any missing servo/controller items, guards, payload retention, and
structural reinforcement. Apparent headroom is not a demonstrated design
margin. The concept cannot yet be claimed to meet the 7.0 kg limit, and the
reference airframe has no documented capacity for the required 1.0 kg payload.

## Target mass allocation

To keep design growth inside the 7.0 kg assignment ceiling, the concept uses a
provisional design target of **6.30 kg or less**, leaving **0.70 kg** below the
hard limit. This is an allocation for future component selection, not evidence
that the current T-REX reference meets it.

| Subsystem allocation | Target maximum | Basis / next check |
| --- | ---: | --- |
| Airframe, rotor system, motor, ESC, servos, and flight-control hardware | 3.15 kg | Includes the 2.590 kg ambiguous T-REX kit figure; verify exact included parts and weigh the assembled group |
| Flight battery | 0.80 kg | Reference 6S battery is listed at 0.780 kg; verify exact pack and usable energy |
| Mission computer, navigation, camera, and radio equipment | 0.40 kg | Planning allowance; replace with selected component masses |
| Payload tank, release mechanism, wiring, mounts, and guards | 0.60 kg | Planning allowance; define payload location and weigh hardware |
| Suppressant | 1.00 kg | Assignment minimum |
| Unresolved integration growth allowance | 0.35 kg | Temporary allowance for omitted items; replace with measured components |
| **Design target subtotal** | **6.30 kg** | **Must be verified by a component ledger and scale** |
| **Unallocated distance to 7.0 kg hard limit** | **0.70 kg** | Integration growth margin; not additional subsystem budget |

This target is conditional. If the kit's 2.590 kg excludes the listed motor and
ESC, those three entries already total 3.108 kg before checking what else the
kit mass includes, leaving only 0.042 kg within the 3.15 kg allocation. That
interpretation is not a credible closed mass group until the kit inventory is
verified; a different/lighter configuration or revised allocation may be
needed. The target must not be represented as achieved mass.

## Battery and energy check

The ALIGN HBP52004 pack is specified as 22.2 V, 5.2 Ah, 115 Wh, and 780 g.
This sits below the assignment's 6S / 12 Ah maximum. It is a manufacturer-listed
battery associated with the T-REX 500/600 family; fit and discharge suitability
for the exact 550X assembly still require confirmation.

For the 6.088 kg planning mass and 1.248 m main rotor, the ideal actuator-disk
calculation gives about 266.5 W induced hover power. Applying the generic
helicopter-rotor figure-of-merit range 0.74-0.77 gives about 346-360 W rotor
power and an arithmetic 19-20 minute ceiling from 115 Wh if every nominal
watt-hour were usable and rotor power represented all electrical demand. This
is not mission endurance. It omits battery reserve, tail-rotor power, rotor
profile/drive losses, motor/ESC losses, climb, forward flight, target hover,
payload release, wind, and return.

## First hover sizing result

`src/performance.py` uses ideal actuator-disk momentum theory with sea-level
air density 1.225 kg/m^3. For the 6.088 kg planning mass and 1.248 m main rotor:

- Required hover thrust: **59.70 N** (equal to modeled weight; no control margin).
- Main-rotor disk area: **1.223 m^2**.
- Disk loading: **48.81 N/m^2**.
- Ideal induced velocity: **4.46 m/s**.
- Ideal induced hover power lower bound: **266.5 W**.

This calculation excludes tail-rotor anti-torque power, blade profile power,
forward-flight drag, transmission and electrical losses, ground effect, gust
response, and control/thrust reserve. It does not establish that the reference
motor, ESC, airframe, or battery can safely lift the proposed payload.

## References

- ALIGN, T-REX 550X specifications and recommended 6S battery range:
  https://www.align.com.tw/index.php/helicopter-en/trex550/
- ALIGN, T-REX 550X product listing and package accessories:
  https://shop.align.com.tw/product_info.php?products_id=5898
- ALIGN, 730MX 850KV motor specifications and mass:
  https://shop.align.com.tw/product_info.php?language=eu&products_id=5094
- ALIGN, RCE-BL100A ESC specifications and mass:
  https://shop.align.com.tw/product_info.php?language=en&products_id=5719
- ALIGN, HBP52004 6S 5,200 mAh battery specifications and mass:
  https://shop.align.com.tw/product_info.php?cPath=11_2966_2999&language=en&products_id=5214
- Wayne Johnson, *Rotorcraft Aeromechanics*, Cambridge University Press
  excerpt, ideal hover performance and figure of merit:
  https://assets.cambridge.org/97811070/28074/excerpt/9781107028074_excerpt.pdf
- United Vehicle Robotics, ELECTRON 7 electric helicopter UAV (18 kg empty,
  25 kg MTOW, up to 7 kg load):
  https://uvr.aero/what-we-do/electron/
- Workhorse Aero, Horsefly WA4-100 electric UAS (16.1 kg MTOW, up to 10 lb
  payload depending on delivery system):
  https://workhorse.com/wp-content/uploads/2023/08/WRK_Workhorse_Aero_Horsefly_SpecSheet_Digital_04.pdf

## Decisions still open

1. Confirm whether the instructor requires a physical helicopter or accepts a
   simulation-based demonstration. The brief says “design, develop, and
   demonstrate” and includes competition limits, so a software demo alone may
   not satisfy every interpretation.
2. Define a safe simulated payload container, retention/release logic,
   confirmation method, and post-release mass/CG change.
3. Confirm the exact reference-kit mass contents and select payload-safe hardware
   only if a physical build is approved and properly supervised.
4. Add rotor speed, tip-speed, thrust margin, tail-rotor power, and hover-power
   calculations from the selected configuration's documented data.
5. Define repeatable crosswind/gust cases and measurable recovery criteria.
6. Define the vision target and evaluate it on images not used to choose its
   threshold.

## Integrated simulated flight profile

`src/main.py --helicopter-flight` joins the route planner to vertical flight
dynamics and simplified 2D waypoint tracking. It climbs to 25 m, follows an
outbound route, hovers at a synthetic target, simulates release of 1 kg,
recovers, follows the return route, and lands. The default route is 14 grid
steps round trip. In the current 5 m/s baseline eastward wind with a 0.5 m/s,
12 s square gust, it reaches all waypoints and lands in about 320 seconds of
model time. The peak horizontal error during the gust is about 1.50 m; the
model takes about 49.15 s after the pulse ends to meet its waypoint-recovery
criterion (horizontal error below 0.1 m and speed below 0.1 m/s). Vertical
overshoot after release is about 0.038 m. These are software-model outputs,
not measured aircraft performance.

The model uses a 0.05 s time step, PD altitude and waypoint controllers,
assumed 10 m grid spacing, a 5 m/s baseline eastward wind with a deterministic
0.5 m/s, 12 s square gust, 0.6 m² side area and drag coefficient 1.0 for its
crosswind load, a vertical drag coefficient of 0.8 N/(m/s), and maximum
thrust of 1.5 times loaded weight. Figure of merit is 0.74 for the rotor-energy
estimate. It omits attitude, turbulent gusts, rotor/airframe coupling,
tail-rotor power, electrical losses, and hardware motor/ESC response. These
assumptions must be revised as engineering inputs become available.

The mission also has a software geofence around the grid and a return-to-base
fallback that retraces last reached waypoints if the simulated boundary or
altitude limit is crossed. This behavior has only been exercised in simulation;
it is not a hardware geofence or certified failsafe.

The payload release sequence uses a simulated normally-locked state machine.
It arms only after the synthetic target is confirmed, the fence is clear, the
aircraft is inside the modeled altitude range, and vertical/horizontal speeds
are below their release thresholds. It then removes the payload mass from the
flight model and records a simulated load-sensor confirmation. The payload
mount location is not defined, so CG shift and real retention/release hardware
are not modeled.

## Next engineering step

Confirm the exact kit version and included parts, then replace the ambiguous
base entry with a component-by-component mass ledger that counts each item once
and reserves explicit margin. The manufacturer-published ELECTRON 7 electric
helicopter is rated for up to 7 kg load, but its 18 kg empty weight and 25 kg
MTOW exceed this assignment's mass limit. It is a capability comparison, not a
compliant candidate platform. Keep the T-REX 550X as a geometry reference only
unless documentation establishes safe capacity for the required payload.
