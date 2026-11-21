# Autonomous Helicopter for Wildfire Reconnaissance and Precision Fire Suppressant Delivery

## Project summary

This project delivers a reproducible software simulation and preliminary engineering study for the assigned wildfire helicopter mission. The integrated demonstration plans a route, models vertical flight and simplified horizontal waypoint tracking, applies wind and a gust, checks a geofence, simulates an interlocked 1 kg payload release, and returns to base. A separate smoke detector was evaluated on the available validation split. The detector is not connected to mission control because its measured performance does not justify using it to trigger a delivery.

The result is a simulation prototype, not a built or flight-tested aircraft. The reference T-REX 550X has no documented rating for the required 1 kg payload, the mass budget remains uncertain, and the flight model omits attitude dynamics and several major aerodynamic and electrical effects. Accordingly, this report distinguishes simulated behavior, calculated estimates, manufacturer specifications, and unresolved design assumptions.

## 1. Assignment and project scope

The assignment requires a rotorcraft under 7 kg MTOW with at least 1 kg of suppressant, rotor diameter no greater than 1.5 m, electric propulsion and a battery no larger than 6S / 12,000 mAh. The mission calls for vertical takeoff and landing, target identification, controlled hover, payload delivery, stable post-release flight, return-to-base, emergency abort, and geofence protection. The design stages also call for rotor and hover analysis, gust/disturbance response analysis, payload retention and release design, and vision-assisted target identification.

This project addresses those requirements in software where possible. Physical payload capability, airworthiness, flight testing, and fire response are outside the demonstrated scope. All mission targets in the simulator are synthetic coordinates. No real fire alarm or suppressant release is generated.

## 2. Conceptual configuration

The reference concept uses a conventional single-main-rotor helicopter with a tail rotor and electric 6S propulsion. The ALIGN T-REX 550X is used as a geometry and component reference: its published main rotor diameter is 1.248 m, within the assignment limit. The manufacturer does not publish a safe 1 kg payload rating or autonomous capability for this hobby platform, so it is not represented as a mission-ready aircraft.

The concept carries a 1 kg simulated suppressant payload. The simulated release system remains locked until the synthetic target is confirmed, the geofence is clear, altitude is within the modeled flight envelope, vertical speed is at most 0.15 m/s, and horizontal speed is at most 0.3 m/s. The release and load-sensor confirmation are simulated states only. Payload retention hardware, payload location, and centre-of-gravity shift have not been designed or tested.

### 2.1 Mass budget and feasibility

The provisional takeoff-mass sum is 6.088 kg: a 2.590 kg T-REX kit figure, 0.380 kg motor, 0.138 kg ESC, 0.780 kg battery, 0.700 kg autonomy/sensor allowance, 0.500 kg wiring and release allowance, and 1.000 kg payload. However, ALIGN's English specification calls the 2.590 kg figure a weight without the power system, while its product listing describes a fully equipped weight without battery and lists the motor, ESC, servos, and flybarless controller among the accessories. The motor and ESC may therefore be counted twice. If they are already included, the arithmetic subtotal is 5.570 kg before resolving the remaining kit contents and allowances.

Neither subtotal is verified aircraft mass. The exact kit contents must be reconciled and the proposed assembly weighed. A target allocation of 6.30 kg or less is recorded in the conceptual design, leaving 0.70 kg below the 7 kg assignment limit. It is a design target, not an achieved result. No source found for the T-REX establishes a 1 kg payload rating. A manufacturer-published electric helicopter with a documented 7 kg load rating, the ELECTRON 7, lists 18 kg empty weight and 25 kg MTOW, so it exceeds this assignment's mass limit and serves only as a capability comparison.

## 3. Preliminary performance analysis

The hover calculation uses ideal actuator-disk momentum theory at standard sea-level density, 1.225 kg/m^3. For mass m = 6.088 kg and rotor diameter D = 1.248 m:

- Rotor disk area: A = pi D^2 / 4 = 1.223 m^2.
- Hover thrust: T = mg = 59.70 N.
- Disk loading: T / A = 48.81 N/m^2.
- Ideal induced velocity: vi = sqrt(T / (2 rho A)) = 4.46 m/s.
- Ideal induced hover power lower bound: Pi = T vi = 266.5 W.
- At an assumed figure of merit of 0.74 to 0.77, indicative rotor power is about 346 to 360 W.

The reference 6S, 5.2 Ah battery is listed as 115 Wh and 0.780 kg. Dividing nominal energy by the indicative rotor power gives an idealized hover ceiling of roughly 19 to 20 minutes if every nominal watt-hour were usable. This is not a flight-endurance prediction. It excludes battery reserve, tail-rotor power, blade profile power, transmission and electrical losses, climb, forward flight, wind, and mission-specific energy use.

The calculation does not establish available thrust margin or prove that the motor, ESC, battery, or airframe can lift the mission payload. A measured bill of materials, motor/rotor performance data, rotor speed, tip-speed calculation, tail-rotor power estimate, and ground-effect analysis remain necessary for a physical design.

## 4. Simulation design

The integrated program joins a grid-based obstacle-aware route planner to a simplified helicopter model. The model includes vertical altitude and speed, a damped altitude controller, simplified 2D waypoint tracking, a quadratic crosswind force, a deterministic square gust, a circular geofence, return-to-base behavior, a payload-release state machine, and a JSON mission report. The default grid has 10 m assumed spacing; that spacing is only a visualization assumption and does not represent surveyed terrain.

The nominal wind assumption is a 5.0 m/s eastward crosswind with a 0.5 m/s increase from 90 to 102 seconds. The simplified model uses a side area of 0.6 m^2, drag coefficient 1.0, time step 0.05 seconds, and maximum thrust of 1.5 times loaded weight. These are teaching assumptions, not measured properties of a real helicopter.

The model does not include roll/pitch/yaw attitude states, rotor/airframe coupling, turbulent or fire-generated flow, blade and tail-rotor power, motor/ESC response, electrical losses, terrain effects, visual degradation, or physical payload dynamics. The detector output is not used as a mission cue.

## 5. Demonstration scenarios and results

| Scenario | Conditions | Outcome | Recorded results |
| --- | --- | --- | --- |
| Nominal mission | 5.0 m/s wind; +0.5 m/s gust for 12 s; 14 of 20 grid steps used | Synthetic target reached; simulated 1 kg release confirmed; return and landing completed | 319.95 s model time; 0.038 m peak altitude deviation after release; 1.504 m peak position error during gust; 49.15 s recovery to error and speed below 0.1 |
| Geofence abort | 15 m radius | Boundary breach detected; delivery canceled; last safe route retraced; landing completed | 80.0 s model time; payload remained locked; returned to base |
| Stronger gust | 5.0 m/s wind; +1.5 m/s gust for 12 s | Route completed and aircraft landed; release interlock rejected delivery because horizontal speed exceeded 0.3 m/s | 17.854 m peak error during gust; 31.75 s recovery by the model's criterion; no payload release |

These results demonstrate software control flow and expose a weakness: the stronger gust allows a large simulated displacement, and the release interlock correctly refuses delivery while the aircraft is moving too quickly. This is a useful failure case, not evidence of acceptable real-world gust tolerance. The model's distance and time values should not be interpreted as field performance.

The nominal report also records 26.692 Wh of idealized rotor energy over the simulated mission. The energy model uses the simplified thrust-power relationship and omits key aircraft and electrical loads, so this value is not a battery endurance or reserve guarantee.

## 6. Target identification and AIML results

The project retains an experimental pretrained smoke detector as an AIML component. On the available validation split at image size 320, the original checkpoint produced precision 0.448, recall 0.531, mAP50 0.380, and mAP50-95 0.199. A confidence threshold of 0.082 was selected from the same validation split; at that threshold, precision was 0.456, recall 0.531, mAP50 0.347, and mAP50-95 0.185. Because the same split informed threshold selection, these threshold-specific results are preliminary. The split contains 1,134 images and 49 labeled smoke instances.

The detector missed both previously inspected sample images at confidence 0.05. A short fine-tuning trial on only 2% of training data produced false detections and zero validation precision, recall, and mAP. The quick trial is rejected. The available dataset card lists train and validation splits but no independent test split, so validation cannot be relabeled as a final test set. A separate evaluation runner is ready for a genuine held-out labeled split.

The model publisher reports higher SAINet v11.1 scores on its own test and La Rancherita in-situ evaluations. Those figures are publisher-reported and were not reproduced here; the published repository does not provide those evaluation images. They are not directly comparable to this project's local validation. The local smoke detector is not a reliable fire alarm and is not connected to simulated mission control. The current synthetic target marker supplies the mission cue.

## 7. Safety and limitations

This repository contains simulation and preliminary design analysis only. It is not a flight controller, airworthiness assessment, certified geofence, validated payload-drop device, fire alarm, or permission to operate an aircraft. No physical aircraft was built or flown. A physical prototype would require a payload-rated platform, verified mass and centre of gravity, engineered retention and release hardware, independent safety review, instructor supervision, and controlled tests before any flight.

NASA wildfire-rotorcraft work identifies gaps in handling qualities, turbulence-response modeling, and mission subsystems. NASA external-load research also finds that suspended loads can affect handling qualities; whether that finding applies directly depends on the payload mounting arrangement, which this concept has not yet defined. These sources support treating the stronger-gust and payload-release cases as important engineering concerns; they do not validate this project's simplified model.

## 8. Reproduction

Run the nominal integrated mission from the project folder:

```powershell
.\.venv\Scripts\python.exe .\src\main.py --helicopter-flight --flight-report .\runs\final_nominal.json
```

Run the geofence abort demonstration:

```powershell
.\.venv\Scripts\python.exe .\src\main.py --helicopter-flight --geofence-radius-m 15 --flight-report .\runs\final_geofence.json
```

Run the stronger gust case:

```powershell
.\.venv\Scripts\python.exe .\src\main.py --helicopter-flight --gust-delta-m-s 1.5 --gust-duration-s 12 --flight-report .\runs\final_stronger_gust.json
```

Each command writes a detailed JSON report under `runs/`; that folder is ignored by Git. Additional commands and parameter descriptions are in the project README.

## 9. Completion status

The software demonstration, detector evaluation notes, preliminary hover sizing, conceptual configuration, mass-target allocation, simulated payload interlocks, and geofence abort path are documented. The nominal, abort, and stronger-gust scenarios have been run successfully as software demonstrations. The stronger-gust case also shows the simulated release lockout.

The project is complete as a simulation-first academic prototype and preliminary design study. It is not complete as a physically compliant helicopter design: exact kit mass, payload capability, component selection, centre of gravity, attitude/gust response, independent target-identification validation, and hardware safety remain unresolved. These limits should be stated during any presentation.

## References

1. Helicopter Design Project 1 assignment brief, supplied by the student.
2. ALIGN, T-REX 550X specifications: https://www.align.com.tw/index.php/helicopter-en/trex550/
3. ALIGN, T-REX 550X product listing and package accessories: https://shop.align.com.tw/product_info.php?products_id=5898
4. ALIGN, HBP52004 6S battery listing: https://shop.align.com.tw/product_info.php?cPath=11_2966_2999&language=en&products_id=5214
5. Johnson, W. *Rotorcraft Aeromechanics*, Cambridge University Press excerpt: https://assets.cambridge.org/97811070/28074/excerpt/9781107028074_excerpt.pdf
6. NASA, *VAERA: Identifying Technology Gaps for Wildfire Relief Rotorcraft Missions*: https://ntrs.nasa.gov/citations/20240000476
7. NASA, *Development of Handling Qualities Criteria for Rotorcraft with Externally Slung Loads*: https://ntrs.nasa.gov/citations/20070009837
8. United Vehicle Robotics, ELECTRON 7 specifications: https://uvr.aero/what-we-do/electron/
9. SAINetset v8.0 dataset card: https://huggingface.co/datasets/SAINetset/SAINetset_v8.0
10. SAINet model publisher repository and reported results: https://github.com/AlterMundi/sai-sainet-latest
