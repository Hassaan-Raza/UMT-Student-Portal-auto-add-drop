import cv2
import numpy as np
import pyautogui
import time
import sys
import subprocess
import pygetwindow as gw

# Function to detect if an image (button or error) is present on the screen
def detect_image(image_path, confidence_threshold=0.5):
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")

    target_img = cv2.imread(image_path)
    screen_img = cv2.imread("screenshot.png")

    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    screen_gray = cv2.cvtColor(screen_img, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screen_gray, target_gray, cv2.TM_CCOEFF_NORMED)
    loc = cv2.minMaxLoc(result)
    confidence = loc[1]

    threshold = 0.7
    yloc, xloc = np.where(result >= threshold)
    for (x, y) in zip(xloc, yloc):
        cv2.rectangle(screen_img, (x, y), (x + target_img.shape[1], y + target_img.shape[0]), (0, 255, 0), 2)

    cv2.imwrite("matched_result.png", screen_img)

    if confidence >= confidence_threshold:
        print(f"Image found with confidence: {confidence}")
        return loc[3]  # Returns the position of the top-left corner of the match

    print(f"Image '{image_path}' not found with sufficient confidence.")
    return None

# Function to click at a specific position on the screen
def click_at_position(pos):
    if pos:
        pyautogui.click(pos[0] + 10, pos[1] + 10)  # Add offset to click at the center
        print("Clicked at position:", pos)
        return True
    return False

# Paths to the images
button1_img_path = base_dir / "button.png"
button2_img_path = base_dir / "2ndstep.png"
error_img_path = base_dir / "error.png"
success_img_path = base_dir / "success.png"


try:
    while True:
        # Check if the success message is detected
        success_position = detect_image(success_img_path)
        if success_position:
            print("Success message detected. Sending Discord notification.")

        # Detect and click the first button
        button1_position = detect_image(button1_img_path)
        if button1_position and click_at_position(button1_position):
            print("First button clicked. Proceeding to click the second button.")

            # Detect and click the second button
            button2_position = detect_image(button2_img_path)
            if button2_position and click_at_position(button2_position):
                print("Second button clicked. Checking for error message.")

                # Check for error message
                error_position = detect_image(error_img_path)
                if error_position:
                    print("Error message detected. Retrying...")
                    continue  # Retry the entire process

        # Wait before the next iteration
        time.sleep(2)

except Exception as e:
    print("An error occurred:", str(e))
    sys.exit(1)
