import cv2
import time

def test_camera(index):
    print(f"Testing camera index {index}...")
    cap = cv2.VideoCapture(index)
    
    if not cap.isOpened():
        print(f"Failed to open camera with index {index}")
        return False
    
    print(f"Successfully opened camera with index {index}")
    ret, frame = cap.read()
    
    if not ret:
        print(f"Failed to read frame from camera with index {index}")
        cap.release()
        return False
    
    print(f"Successfully read frame from camera with index {index}")
    cv2.imshow(f"Camera {index} Test", frame)
    key = cv2.waitKey(2000)  # Show for 2 seconds or until key press
    
    # Check if 'q' or ESC key was pressed
    if key == ord('q') or key == 27:  # 27 is the ASCII code for ESC
        print("Exit requested by user")
        cap.release()
        cv2.destroyAllWindows()
        return "exit"
        
    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    print("Press 'q' or ESC key to exit at any time")
    # Test camera indices 0-3
    for i in range(4):
        result = test_camera(i)
        if result == "exit":
            print("Exiting program")
            break
        elif result:
            print(f"Camera index {i} is working!")
        time.sleep(1)  # Wait between tests