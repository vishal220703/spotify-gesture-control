import cv2
import time

def test_camera(camera_index):
    print(f"Testing camera with index {camera_index}...")
    start_time = time.time()
    cap = cv2.VideoCapture(camera_index)
    init_time = time.time() - start_time
    print(f"Camera initialization took {init_time:.2f} seconds")
    
    if not cap.isOpened():
        print(f"Failed to open camera with index {camera_index}")
        return False
    
    # Try to read a frame
    ret, frame = cap.read()
    if not ret:
        print(f"Failed to read frame from camera with index {camera_index}")
        cap.release()
        return False
    
    # Display the frame for 2 seconds
    cv2.imshow(f"Camera {camera_index} Test", frame)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()
    
    cap.release()
    print(f"Camera with index {camera_index} is working properly")
    return True

if __name__ == "__main__":
    # Test cameras with indices 0 to 3
    for i in range(4):
        if test_camera(i):
            print(f"Camera index {i} is available and working")
        else:
            print(f"Camera index {i} is not available or not working")
        print("---")