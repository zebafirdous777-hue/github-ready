"""Evaluate the smoke detector on a declared dataset split.

The default split is `test` so threshold selection on validation data is not
mistaken for an independent performance estimate.
"""

import argparse
import json
from pathlib import Path

import yaml
from ultralytics import YOLO


def resolve_split(data_yaml, split):
    config = yaml.safe_load(data_yaml.read_text(encoding="utf-8")) or {}
    split_value = config.get(split)
    if not split_value:
        raise ValueError(
            f"{data_yaml} has no '{split}' split. Add a separate labeled split "
            "before running an independent evaluation."
        )
    dataset_root = Path(config.get("path", data_yaml.parent))
    if not dataset_root.is_absolute():
        dataset_root = (data_yaml.parent / dataset_root).resolve()
    split_paths = split_value if isinstance(split_value, list) else [split_value]
    missing = []
    for item in split_paths:
        image_path = Path(item)
        if not image_path.is_absolute():
            image_path = dataset_root / image_path
        if not image_path.exists():
            missing.append(str(image_path))
    if missing:
        raise ValueError("dataset split path(s) do not exist: " + ", ".join(missing))
    return config


def build_parser():
    parser = argparse.ArgumentParser(
        description="Evaluate a YOLO smoke detector on a declared dataset split."
    )
    parser.add_argument("--weights", default="models/SAINet_v11.1.pt")
    parser.add_argument("--data", default="datasets/SAINetset_v8.0/data.yaml")
    parser.add_argument("--split", choices=("train", "val", "test"), default="test")
    parser.add_argument("--confidence", type=float, default=0.082)
    parser.add_argument("--image-size", type=int, default=320)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--output", default="runs/detector_test_metrics.json")
    return parser


def main():
    args = build_parser().parse_args()
    data_yaml = Path(args.data).resolve()
    weights = Path(args.weights).resolve()
    if not data_yaml.is_file():
        raise SystemExit(f"Dataset YAML not found: {data_yaml}")
    if not weights.is_file():
        raise SystemExit(f"Model weights not found: {weights}")
    if not 0 <= args.confidence <= 1:
        raise SystemExit("--confidence must be between 0 and 1")
    if args.image_size < 1 or args.batch < 1:
        raise SystemExit("--image-size and --batch must be positive")

    try:
        resolve_split(data_yaml, args.split)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(weights))
    result = model.val(
        data=str(data_yaml),
        split=args.split,
        conf=args.confidence,
        imgsz=args.image_size,
        batch=args.batch,
        workers=0,
        plots=True,
        project=str(output.parent),
        name=f"{output.stem}_plots",
        exist_ok=True,
    )
    metrics = {
        "precision": float(result.box.mp),
        "recall": float(result.box.mr),
        "map50": float(result.box.map50),
        "map50_95": float(result.box.map),
    }
    report = {
        "model_weights": str(weights),
        "dataset_yaml": str(data_yaml),
        "split": args.split,
        "confidence_threshold": args.confidence,
        "image_size": args.image_size,
        "batch_size": args.batch,
        "metrics": metrics,
        "plots_directory": str(result.save_dir),
        "warning": (
            "Validation split results are not an independent final estimate if "
            "the threshold was selected using that same split."
            if args.split == "val"
            else "Results apply only to this test split and do not establish operational safety."
        ),
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Evaluation report saved: {output}")


if __name__ == "__main__":
    main()
