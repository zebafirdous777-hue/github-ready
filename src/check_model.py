from ultralytics import YOLO

model = YOLO("models/SAINet_v11.1.pt")

print("Model loaded!")
print("Classes:", model.names)
