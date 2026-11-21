# Autonomous Helicopter for Wildfire Reconnaissance and Precision Fire-Suppressant Delivery

A simulation-first implementation of the assigned wildfire helicopter project. It reuses earlier smoke-detection and grid-navigation work as groundwork; it does not claim physical flight capability or a reliable fire alarm.

## Current progress

- [x] Assignment requirements and limitations mapped in [docs/ASSIGNMENT_ALIGNMENT.md](docs/ASSIGNMENT_ALIGNMENT.md)
- [x] Conventional 6S helicopter reference concept, provisional mass ledger, and target mass allocation in [docs/CONCEPTUAL_DESIGN.md](docs/CONCEPTUAL_DESIGN.md)
- [x] Simulation results and remaining assignment gaps in [docs/FINAL_PROJECT_REPORT.md](docs/FINAL_PROJECT_REPORT.md) and the [submission-ready PDF](output/pdf/FINAL_PROJECT_REPORT.pdf)
- [x] Ideal hover sizing calculator in `src/performance.py`
- [ ] Verify exact reference-kit contents and replace the provisional mass
      ledger; document a payload-rated design within the 7 kg limit
- [x] Simulate helicopter vertical motion, waypoint tracking, steady crosswind, and simulated payload release
- [x] Add a software geofence and return-to-base failsafe demonstration
- [x] Add a repeatable square-gust scenario and report tracking/recovery metrics
- [x] Add simulated payload release interlocks and confirmation state
- [ ] Add attitude dynamics and more realistic turbulent gusts
- [ ] Validate payload retention/release logic and aircraft mass with hardware data

## Earlier groundwork reused

- [x] Python project starts successfully
- [x] Grid navigation and a basic route/patrol mission demonstration
- [x] Detection experiments and their limitations are documented
- [ ] Select and evaluate the mission target-identification method; the smoke model remains experimental

## Run the helicopter flight simulation

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe .\src\main.py --helicopter-flight
```

This connects the grid planner to a simplified helicopter profile: the
simulated aircraft climbs, tracks outbound waypoints to a synthetic target,
hovers, checks simulated payload-release interlocks, releases a simulated 1 kg
payload if conditions pass, records simulated release confirmation, recovers,
follows the return route, and lands. It checks the route against the grid-step
budget and writes `runs/helicopter_flight_report.json`.

The model includes vertical altitude control and simplified 2D waypoint
tracking under 5 m/s eastward baseline wind, with a repeatable 0.5 m/s increase
from 90 to 102 seconds. The assumed side area (0.6 m²), drag coefficient
(1.0), and grid-cell spacing (10 m) are teaching assumptions, not measured
aircraft data or a scale-accurate map. This simplified square gust omits
turbulence, attitude, rotor/airframe coupling, and electrical losses. The
target and payload release are simulated. This is not flight control software
or evidence that the reference helicopter can carry the payload.

Release stays locked unless the synthetic target is reached, the geofence is
clear, altitude is within the modeled flight envelope, and vertical and
horizontal speeds are below the configured thresholds. Release confirmation
is a simulated load-sensor event; payload retention hardware, CG shift, and
real release sensing are not modeled.

The helicopter mission also checks a configurable circular boundary around
base.
If the simulated position or altitude leaves the allowed area, it cancels the
delivery and retraces its last safe waypoints to base. The default horizontal
radius covers the full grid; use `--geofence-radius-m 15` to see an early
boundary breach trigger the return-to-base path. This is a software failsafe
demonstration, not a certified geofence.

The default command below still runs the earlier grid mission demonstration.

## Run the mission simulation

From the project folder, run:

```powershell
.\.venv\Scripts\python.exe .\src\main.py
```

The basic simulation prints a grid map of the base, synthetic smoke cue,
obstacles, and planned route. It uses a **synthetic smoke cue** at a fixed grid location;
this is a demonstration of route planning and mission states, not a real camera
detection or an operational flight plan. Obstacles are blocked grid cells, and
the simulation checks that the planned round trip fits within its step limit
and reports the remaining flight-step reserve.

You can change the scenario from PowerShell without editing the source. For
example, this changes the base, cue, and blocked cells:

```powershell
.\.venv\Scripts\python.exe .\src\main.py --base 0,0 --smoke-cue 4,3 --obstacle 2,0 --obstacle 2,1 --obstacle 2,2 --grid-size 5 --max-flight-steps 20
```

Run the program with `--help` to see all options. If no `--obstacle` options
are supplied, the default three blocked cells are used.
For the helicopter mission, change the steady crosswind assumption with
`--crosswind-m-s`, and adjust the gust with `--gust-start-s`,
`--gust-duration-s`, and `--gust-delta-m-s`.

Add `--patrol --max-flight-steps 60` to sweep all reachable cells before
returning. The patrol route uses a simple nearest-cell heuristic and may not be
the shortest possible coverage route. The smoke cue remains synthetic. Each run
writes a JSON mission report to `runs/mission_report.json`; use the `--report`
option to choose another path, such as `somewhere/report.json`. The `runs/`
folder is ignored by Git. Invalid grid sizes, out-of-grid coordinates, and
base/cue placements on obstacles are rejected with a clear command-line error.

## Detection experiments

The SAI-Net model (`models/SAINet_v11.1.pt`) returned no detections on labeled
smoke images `187661.jpg` and `187957.jpg` at confidence 0.05. At image size
1280 and confidence 0.001, it produced a box overlapping the visible plume in
`187957.jpg` at confidence 0.00100650. This score is too low to count as a
reliable detection.

The original checkpoint was also evaluated at image size 320 on the dataset's
validation split: 1,134 images containing 49 labeled smoke instances. It scored
precision 0.448, recall 0.531, mAP50 0.380, and mAP50-95 0.199. These results
show that the model detects some smoke in aggregate, but it still misses many
instances and makes false detections. Together with the missed sample images,
this is not enough to treat it as a reliable fire alarm.

The validation F1-confidence curve peaked at about 0.48 near confidence 0.082.
This is only a candidate threshold selected on the validation split; it needs
evaluation on independent images and is not a safety-ready alarm setting.
At confidence 0.082, the same validation split gave precision 0.456, recall
0.531, mAP50 0.347, and mAP50-95 0.185. Because this threshold was chosen from
the same split, these threshold-specific results are preliminary and may be
optimistic; they do not establish reliable alarm performance.

The model publisher separately reports SAINet v11.1 results on its test split
(precision 0.833, recall 0.797, mAP50 0.842) and on its La Rancherita in-situ
evaluation (precision 0.859, recall 0.861, mAP50 0.906). These are
[publisher-reported results](https://github.com/AlterMundi/sai-sainet-latest),
not results reproduced in this project. The publisher repository provides the
checkpoint and configuration but not those evaluation images, so we cannot
independently verify or compare them with our local validation results. The
publisher also recommends held-out, deployment-matched evaluation and
temporal consensus. Those external figures do not establish that this model is
reliable for our mission.

A quick fine-tuning trial used one epoch on 2% of the training set. It produced
many boxes across the hillside and sky in the two sample images; validation
precision, recall, and mAP were all zero. This trial is not a usable detector.
The full CPU training attempt was interrupted because it was too slow.

Do not use the current model or trial for real fire alerts. A reliable detector
needs proper training, validation, and testing on representative data.

The published [SAINetset v8.0 dataset card](https://huggingface.co/datasets/SAINetset/SAINetset_v8.0)
lists only train and validation splits, with no independent test split. The
current confidence threshold was selected on validation, so those results
cannot serve as an unbiased final test. `src/evaluate_detector.py` is ready to
run when a separate labeled test split is available; it defaults to `--split
test` and stops with a clear message if that split is missing. Do not move or
reuse the current validation images as test data.

The example images `data/187661.jpg` and `data/187957.jpg` are from SAINetset
v8.0 by AlterMundi and are shared under the dataset's CC BY 4.0 license. See
the [dataset card](https://huggingface.co/datasets/SAINetset/SAINetset_v8.0)
for attribution and license terms.
