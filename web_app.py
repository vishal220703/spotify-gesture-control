import os
import sys
import webbrowser
import time
from threading import Timer
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_server_ready():
    try:
        response = requests.get('http://127.0.0.1:5000/health')
        if response.status_code == 200:
            webbrowser.open('http://127.0.0.1:5000')
            return
    except requests.exceptions.ConnectionError:
        pass
    
    # If we get here, the server isn't ready yet, try again in 1 second
    Timer(1.0, check_server_ready).start()

if __name__ == "__main__":
    # Add the current directory to the path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    logging.info("Starting Spotify Gesture Control Web App")
    
    # Start checking if the server is ready
    Timer(2.0, check_server_ready).start()
    
    # Import and run the Flask app
    from web.app import app, socketio, start_gesture_controller
    
    # Add a health check endpoint
    @app.route('/health')
    def health_check():
        return "OK"
    
    # Start the gesture controller in a separate thread
    logging.info("Starting gesture controller thread")
    from threading import Thread
    gesture_thread = Thread(target=start_gesture_controller)
    gesture_thread.daemon = True
    gesture_thread.start()
    
    logging.info("Starting web server")
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)