// Camera and Media Capture JavaScript

let currentStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let recordingStartTime = null;

// ===== CAMERA FUNCTIONS =====

/**
 * Start camera capture
 */
async function startCamera(videoElementId = 'video') {
    try {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: false
        };

        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        const videoElement = document.getElementById(videoElementId);
        if (videoElement) {
            videoElement.srcObject = currentStream;
            videoElement.play();
        }

        return true;
    } catch (error) {
        console.error('Camera error:', error);
        showToast('Cannot access camera: ' + error.message, 'danger');
        return false;
    }
}

/**
 * Stop camera capture
 */
function stopCamera() {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
        currentStream = null;
    }
}

/**
 * Capture photo from video stream
 */
function capturePhoto(videoElementId = 'video', canvasElementId = 'canvas') {
    try {
        const video = document.getElementById(videoElementId);
        const canvas = document.getElementById(canvasElementId);
        
        if (!video || !canvas) {
            console.error('Video or Canvas element not found');
            return null;
        }

        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0);

        return canvas;
    } catch (error) {
        console.error('Capture error:', error);
        showToast('Failed to capture photo', 'danger');
        return null;
    }
}

/**
 * Convert canvas to file and set to input
 */
function setPhotoToInput(canvasElementId = 'canvas', inputElementId) {
    const canvas = document.getElementById(canvasElementId);
    
    if (!canvas) {
        console.error('Canvas element not found');
        return;
    }

    canvas.toBlob(blob => {
        const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' });
        setFileToInput(inputElementId, file);
    }, 'image/jpeg', 0.95);
}

/**
 * Set file to file input element
 */
function setFileToInput(inputElementId, file) {
    const input = document.getElementById(inputElementId);
    
    if (!input) {
        console.error('Input element not found:', inputElementId);
        return;
    }

    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
    
    // Trigger change event
    const event = new Event('change', { bubbles: true });
    input.dispatchEvent(event);
    
    showToast('File captured successfully', 'success');
}

/**
 * Take photo from camera and set to input
 */
async function takePhotoFromCamera(inputElementId) {
    const canvas = capturePhoto();
    if (canvas) {
        canvas.toBlob(blob => {
            const file = new File([blob], `camera_${Date.now()}.jpg`, { type: 'image/jpeg' });
            setFileToInput(inputElementId, file);
        }, 'image/jpeg', 0.95);
    }
}

// ===== AUDIO RECORDING FUNCTIONS =====

/**
 * Start audio recording
 */
async function startAudioRecording() {
    try {
        const constraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        };

        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        
        mediaRecorder = new MediaRecorder(currentStream);
        recordedChunks = [];
        recordingStartTime = Date.now();

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const recordingLength = Date.now() - recordingStartTime;
            console.log('Recording length:', recordingLength / 1000, 'seconds');
        };

        mediaRecorder.start();
        return true;
    } catch (error) {
        console.error('Audio recording error:', error);
        showToast('Cannot access microphone: ' + error.message, 'danger');
        return false;
    }
}

/**
 * Stop audio recording
 */
function stopAudioRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        return true;
    }
    return false;
}

/**
 * Get recorded audio as blob
 */
function getRecordedAudioBlob(mimeType = 'audio/wav') {
    if (recordedChunks.length === 0) {
        return null;
    }

    return new Blob(recordedChunks, { type: mimeType });
}

/**
 * Set audio file to input
 */
function setAudioToInput(inputElementId, blob) {
    if (!blob) {
        showToast('No audio recorded', 'warning');
        return;
    }

    const file = new File([blob], `audio_${Date.now()}.wav`, { type: 'audio/wav' });
    const input = document.getElementById(inputElementId);
    
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;

    // Show audio preview
    const audioUrl = URL.createObjectURL(blob);
    updateAudioPreview(audioUrl);
    
    showToast('Audio recorded successfully', 'success');
}

/**
 * Update audio preview element
 */
function updateAudioPreview(audioUrl, previewElementId = 'recordedAudio') {
    const audioElement = document.getElementById(previewElementId);
    
    if (audioElement) {
        audioElement.src = audioUrl;
        audioElement.parentElement.style.display = 'block';
    }
}

/**
 * Record audio and set to input (convenience function)
 */
async function recordAndSetAudio(inputElementId, durationSeconds = 30) {
    if (!await startAudioRecording()) {
        return;
    }

    showToast(`Recording for ${durationSeconds} seconds...`, 'info');

    // Auto-stop after duration
    const autoStopTimeout = setTimeout(() => {
        stopAudioRecording();
        const blob = getRecordedAudioBlob();
        setAudioToInput(inputElementId, blob);
        
        // Stop audio stream
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
        
        showToast('Recording stopped', 'success');
    }, durationSeconds * 1000);

    // Allow manual stop
    window.manualStopRecording = function() {
        clearTimeout(autoStopTimeout);
        stopAudioRecording();
        const blob = getRecordedAudioBlob();
        setAudioToInput(inputElementId, blob);
        
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
    };
}

/**
 * Screen Recording (bonus feature)
 */
async function startScreenRecording() {
    try {
        const constraints = {
            video: {
                cursor: 'always'
            },
            audio: false
        };

        currentStream = await navigator.mediaDevices.getDisplayMedia(constraints);
        return true;
    } catch (error) {
        if (error.name !== 'NotAllowedError') {
            console.error('Screen recording error:', error);
            showToast('Cannot start screen recording', 'danger');
        }
        return false;
    }
}

// ===== PERMISSION CHECKING =====

/**
 * Check camera permission
 */
async function checkCameraPermission() {
    try {
        const permission = await navigator.permissions.query({ name: 'camera' });
        return permission.state === 'granted';
    } catch (error) {
        console.log('Permission API not available');
        return null;
    }
}

/**
 * Check microphone permission
 */
async function checkMicrophonePermission() {
    try {
        const permission = await navigator.permissions.query({ name: 'microphone' });
        return permission.state === 'granted';
    } catch (error) {
        console.log('Permission API not available');
        return null;
    }
}

// ===== WEB SPEECH API =====

/**
 * Start speech recognition
 */
async function startSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
        showToast('Speech Recognition not supported', 'danger');
        return null;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.language = 'en-US';

    return recognition;
}

// ===== UTILITY FUNCTIONS =====

/**
 * Check browser support for features
 */
const BrowserSupport = {
    camera: () => !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    microphone: () => !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    geolocation: () => !!navigator.geolocation,
    mediaRecorder: () => !!window.MediaRecorder,
    storage: () => {
        try {
            const test = '__test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch(e) {
            return false;
        }
    }
};

/**
 * Check all browser support
 */
function checkBrowserSupport() {
    const support = {
        camera: BrowserSupport.camera(),
        microphone: BrowserSupport.microphone(),
        geolocation: BrowserSupport.geolocation(),
        mediaRecorder: BrowserSupport.mediaRecorder(),
        storage: BrowserSupport.storage()
    };

    return support;
}

/**
 * Disable user input during capture
 */
function disableInputDuring(callback, duration = 5000) {
    const buttons = document.querySelectorAll('button');
    const inputs = document.querySelectorAll('input, select, textarea');
    
    buttons.forEach(btn => btn.disabled = true);
    inputs.forEach(inp => inp.disabled = true);

    setTimeout(() => {
        buttons.forEach(btn => btn.disabled = false);
        inputs.forEach(inp => inp.disabled = false);
        if (callback) callback();
    }, duration);
}

// Export functions for global use
window.startCamera = startCamera;
window.stopCamera = stopCamera;
window.capturePhoto = capturePhoto;
window.takePhotoFromCamera = takePhotoFromCamera;
window.startAudioRecording = startAudioRecording;
window.stopAudioRecording = stopAudioRecording;
window.recordAndSetAudio = recordAndSetAudio;
window.getRecordedAudioBlob = getRecordedAudioBlob;
window.setFileToInput = setFileToInput;
window.checkCameraPermission = checkCameraPermission;
window.checkMicrophonePermission = checkMicrophonePermission;
window.BrowserSupport = BrowserSupport;
window.checkBrowserSupport = checkBrowserSupport;
