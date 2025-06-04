// Connect to the Socket.IO server
const socket = io();

// DOM elements
const currentGestureElement = document.getElementById('current-gesture');
const fpsElement = document.getElementById('fps');
const trackNameElement = document.getElementById('track-name');
const artistNameElement = document.getElementById('artist-name');
const albumNameElement = document.getElementById('album-name');
const playStatusElement = document.getElementById('play-status');
const albumCoverElement = document.getElementById('album-cover');
const noTrackMessage = document.getElementById('no-track-message');
const trackDetails = document.getElementById('track-details');
const playPauseBtn = document.getElementById('play-pause-btn');

// Socket.IO event listeners
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

socket.on('gesture_update', (data) => {
    currentGestureElement.textContent = data.gesture;
});

socket.on('fps_update', (data) => {
    fpsElement.textContent = data.fps;
});

socket.on('track_update', (data) => {
    updateTrackInfo(data);
});

// Function to update track information
function updateTrackInfo(track) {
    if (track) {
        trackNameElement.textContent = track.name;
        artistNameElement.textContent = track.artist;
        albumNameElement.textContent = track.album;
        playStatusElement.textContent = track.is_playing ? 'Playing' : 'Paused';
        
        // Update play/pause button text
        playPauseBtn.textContent = track.is_playing ? 'Pause' : 'Play';
        playPauseBtn.onclick = function() {
            controlSpotify(track.is_playing ? 'pause' : 'play');
        };
        
        // Update album cover if available
        if (track.cover_url) {
            albumCoverElement.src = track.cover_url;
            albumCoverElement.style.display = 'block';
        } else {
            albumCoverElement.style.display = 'none';
        }
        
        // Show track details, hide no track message
        noTrackMessage.style.display = 'none';
        trackDetails.style.display = 'flex';
    } else {
        // No track playing
        noTrackMessage.style.display = 'block';
        trackDetails.style.display = 'none';
        playPauseBtn.textContent = 'Play';
        playPauseBtn.onclick = function() {
            controlSpotify('play');
        };
    }
}

// Function to control Spotify
function controlSpotify(action) {
    fetch(`/control/${action}`)
        .then(response => response.json())
        .then(data => {
            console.log(`${action} action:`, data);
            // Fetch updated track info after action
            setTimeout(fetchTrackInfo, 500);
        })
        .catch(error => {
            console.error('Error controlling Spotify:', error);
        });
}

// Function to fetch current track info
function fetchTrackInfo() {
    fetch('/get_track_info')
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                updateTrackInfo(data);
            } else {
                // No track playing
                noTrackMessage.style.display = 'block';
                trackDetails.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching track info:', error);
        });
}

// Initial fetch of track info when page loads
document.addEventListener('DOMContentLoaded', () => {
    fetchTrackInfo();
});

// Periodically update gesture info as a fallback if socket fails
setInterval(() => {
    fetch('/get_gesture')
        .then(response => response.json())
        .then(data => {
            currentGestureElement.textContent = data.gesture;
        })
        .catch(error => {
            console.error('Error fetching gesture:', error);
        });
}, 1000);

// Function to exit the application
function exitApplication() {
    if (confirm('Are you sure you want to exit the application?')) {
        fetch('/exit')
            .then(response => {
                console.log('Exit command sent to server');
                window.close(); // Attempt to close the browser window
                // Display a message in case window.close() doesn't work
                document.body.innerHTML = '<div style="text-align: center; padding: 50px;"><h1>Application Stopped</h1><p>You can now close this window.</p></div>';
            })
            .catch(error => {
                console.error('Error sending exit command:', error);
            });
    }
}

// Add keyboard shortcut for exit
document.addEventListener('keydown', function(event) {
    // Exit on 'q' or ESC key
    if (event.key === 'q' || event.key === 'Q' || event.keyCode === 27) {
        exitApplication();
    }
});