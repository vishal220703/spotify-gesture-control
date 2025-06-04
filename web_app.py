import os
import sys
import webbrowser
import time
from threading import Timer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    logging.info("Starting Spotify Gesture Control Web App")
    
    # Start the browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Import and run the Flask app
    from web.app import app, socketio, start_gesture_controller
    
    # Start the gesture controller in a separate thread
    logging.info("Starting gesture controller thread")
    from threading import Thread
    gesture_thread = Thread(target=start_gesture_controller)
    gesture_thread.daemon = True
    gesture_thread.start()
    
    logging.info("Starting web server")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)