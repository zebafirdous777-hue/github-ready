from ultralytics import YOLO

model = YOLO("models/SAINet_v11.1.pt")
results = model.predict("data/187957.jpg", conf=0.05)

for result in results:
    print(result.verbose())
    result.save("data/187957_result.jpg")
    

print("Annotated image saved in data.")

