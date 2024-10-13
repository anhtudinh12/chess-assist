import cv2
import numpy as np
import pyautogui

def captureScreen():
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    return screenshot_cv

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def detect_chessboard(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    largest_contour = None
    max_area = 0

    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area > max_area:
                largest_contour = approx
                max_area = area

    # Order the points
    if largest_contour is not None:
        ordered_points = order_points(largest_contour.reshape(4, 2))
        return ordered_points  # Return the ordered points of the chessboard

    return None

def crop_chessboard(image, points):
    # Get the width and height of the new image
    width = 400  # Desired width of the output chessboard image
    height = 400  # Desired height of the output chessboard image
    destination_points = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1]
    ], dtype="float32")

    # Get the perspective transform
    M = cv2.getPerspectiveTransform(points, destination_points)

    # Apply the perspective warp to obtain the cropped chessboard
    cropped_chessboard = cv2.warpPerspective(image, M, (width, height))

    return cropped_chessboard
def getChessBoard():
    screen = captureScreen()
    chessboard_positions = detect_chessboard(screen)
    return crop_chessboard(screen, chessboard_positions)
if __name__ == "__main__":
    # image = cv2.imread('./frame_0013.jpg')
    image = captureScreen()
    chessboard_positions = detect_chessboard(image)
    if chessboard_positions is not None:
        print("Chessboard detected! Corner positions:")
        print(chessboard_positions)
        cropped_chessboard = crop_chessboard(image, chessboard_positions)
        # Save or show the cropped chessboard image
        cv2.imshow('Cropped Chessboard', cropped_chessboard)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No chessboard detected.")