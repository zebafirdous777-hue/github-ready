import cv2

image = cv2.imread("data/187661.jpg")

height, width = image.shape[:2]

# The smoke box from this image's dataset label
center_x = 0.815784 * width
center_y = 0.238749 * height
box_width = 0.368170 * width
box_height = 0.438273 * height

x1 = int(center_x - box_width / 2)
y1 = int(center_y - box_height / 2)
x2 = int(center_x + box_width / 2)
y2 = int(center_y + box_height / 2)
crop = image[y1:y2, x1:x2]
cv2.imshow("Labeled smoke crop", cv2.resize(crop, None, fx=2, fy=2)) 
crop = image[y1:y2, x1:x2]
cv2.imshow("Labeled smoke crop", crop)
cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
cv2.imshow("Dataset smoke label", cv2.resize(image, (1200, 675)))
cv2.waitKey(0)
cv2.destroyAllWindows()