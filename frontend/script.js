// API Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? `http://${window.location.hostname}:8000`
  : window.location.origin;

// DOM Elements
const languageSelect = document.getElementById('language');
const voiceSelect = document.getElementById('voice');
const speedSlider = document.getElementById('speed');
const speedValue = document.getElementById('speed-value');
const qualitySelect = document.getElementById('quality');
const formatSelect = document.getElementById('format');
const downloadLabel = document.getElementById('download-label');
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const playBtn = document.getElementById('play-btn');
const downloadBtn = document.getElementById('download-btn');
const stopBtn = document.getElementById('stop-btn');
const clearBtn = document.getElementById('clear-btn');
const statusMessage = document.getElementById('status-message');
const progressBar = document.getElementById('progress-bar');
const playerSection = document.getElementById('player-section');
const audioPlayer = document.getElementById('audio-player');
const helpBtn = document.getElementById('help-btn');
const helpModal = document.getElementById('help-modal');
const modalClose = document.getElementById('modal-close');

// State
let languages = {};
let currentAudio = null;
let isPlaying = false;


// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadLanguages();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    languageSelect.addEventListener('change', onLanguageChange);
    voiceSelect.addEventListener('change', onVoiceChange);
    speedSlider.addEventListener('input', onSpeedChange);
    formatSelect.addEventListener('change', updateDownloadLabel);
    textInput.addEventListener('input', onTextInput);
    playBtn.addEventListener('click', onPlayClick);
    downloadBtn.addEventListener('click', onDownloadClick);
    stopBtn.addEventListener('click', onStopClick);
    clearBtn.addEventListener('click', onClearClick);
    helpBtn.addEventListener('click', () => showModal(true));
    modalClose.addEventListener('click', () => showModal(false));
    helpModal.addEventListener('click', (e) => {
        if (e.target === helpModal) showModal(false);
    });

    // Load example text if empty
    if (!textInput.value.trim()) {
        loadExampleText();
    }
    updateCharCount();
    updateDownloadLabel();
}

// Update download button label based on format selection
function updateDownloadLabel() {
    const format = formatSelect.value.toUpperCase();
    const quality = qualitySelect.value === 'high' ? ' (HQ)' : '';
    downloadLabel.textContent = `Download ${format}${quality}`;

    // Show info about WAV format
    if (formatSelect.value === 'wav') {
        showStatus('💡 WAV selected: Lossless audio format, larger file size. Perfect quality!', 'info');
    }
}

// Load Languages
async function loadLanguages() {
    try {
        console.log('Loading languages from:', `${API_BASE_URL}/languages`);
        showStatus('Loading languages...', 'loading');

        const response = await fetch(`${API_BASE_URL}/languages`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        languages = data.languages;

        console.log('Languages loaded:', Object.keys(languages).length);

        // Populate language dropdown
        languageSelect.innerHTML = '<option value="">Select a language...</option>';
        Object.entries(languages).forEach(([code, lang]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = lang.name;
            languageSelect.appendChild(option);
        });

        // Set default language to British English with Ryan voice
        languageSelect.value = 'en-GB';
        onLanguageChange();
        voiceSelect.value = 'Ryan (Male)';

        showStatus('✅ Ready! Select a language to start', 'success');
    } catch (error) {
        console.error('Error loading languages:', error);
        showStatus(`❌ Failed to load languages: ${error.message}`, 'error');
        languageSelect.innerHTML = '<option value="">Error loading languages</option>';
    }
}

// Language Selection
function onLanguageChange() {
    const selectedLang = languageSelect.value;
    voiceSelect.innerHTML = '<option value="">Select a voice...</option>';
    voiceSelect.disabled = !selectedLang;

    if (selectedLang && languages[selectedLang]) {
        const voices = languages[selectedLang].voices;
        Object.keys(voices).forEach(voiceName => {
            const option = document.createElement('option');
            option.value = voiceName;
            option.textContent = voiceName;
            voiceSelect.appendChild(option);
        });
    }
}

// Voice Selection
function onVoiceChange() {
    // Just update UI, no special action needed
}

// Speed Control
function onSpeedChange() {
    const speed = parseInt(speedSlider.value);
    speedValue.textContent = `${speed > 0 ? '+' : ''}${speed}%`;
}


// Text Input
function onTextInput() {
    updateCharCount();
}

function updateCharCount() {
    const text = textInput.value;
    // Count only visible characters (without pause tags)
    const cleanText = text.replace(/<pause\s*[\d.]*\s*(?:s|ms)?\s*>/g, '');
    charCount.textContent = cleanText.length;
}

// Play Button
async function onPlayClick() {
    const text = textInput.value.trim();
    if (!text) {
        showStatus('Please enter some text', 'error');
        return;
    }

    if (!languageSelect.value) {
        showStatus('Please select a language', 'error');
        return;
    }

    if (!voiceSelect.value) {
        showStatus('Please select a voice', 'error');
        return;
    }

    await synthesizeAndPlay();
}

// Download Button
async function onDownloadClick() {
    const text = textInput.value.trim();
    if (!text) {
        showStatus('Please enter some text', 'error');
        return;
    }

    if (!languageSelect.value) {
        showStatus('Please select a language', 'error');
        return;
    }

    if (!voiceSelect.value) {
        showStatus('Please select a voice', 'error');
        return;
    }

    await synthesizeAndDownload();
}

// Stop Button
function onStopClick() {
    if (audioPlayer.paused) {
        return;
    }

    audioPlayer.pause();
    audioPlayer.currentTime = 0;
    isPlaying = false;
    updatePlayStopButtons();
    showStatus('Playback stopped', 'info');
}

// Clear Button
function onClearClick() {
    textInput.value = '';
    updateCharCount();
    showStatus('Text cleared', 'info');
}

// Synthesize and Play
async function synthesizeAndPlay() {
    try {
        // Check if WAV format is selected
        if (formatSelect.value === 'wav') {
            showStatus('⚠️ WAV format is best for downloading. Use Download button to save as WAV.', 'info');
            // Still allow synthesis for download
        }

        const blob = await synthesizeAudio();
        if (!blob) return;

        // Only play if MP3 format (WAV has limited browser support)
        if (formatSelect.value === 'mp3') {
            // Create blob URL
            const url = URL.createObjectURL(blob);
            audioPlayer.src = url;

            // Show player section
            playerSection.style.display = 'block';

            // Play audio
            audioPlayer.play();
            isPlaying = true;
            updatePlayStopButtons();
            showStatus('🎵 Now playing...', 'success');

            // Update status when finished
            audioPlayer.onended = () => {
                isPlaying = false;
                updatePlayStopButtons();
                showStatus('✅ Playback completed', 'success');
            };
        } else {
            // For WAV, show download prompt instead
            showStatus('📥 Use "Download WAV" button to save the audio file', 'info');
        }
    } catch (error) {
        console.error('Error playing audio:', error);
        showStatus(`Error: ${error.message}`, 'error');
    }
}

// Synthesize and Download
async function synthesizeAndDownload() {
    try {
        const blob = await synthesizeAudio();
        if (!blob) return;

        // Create download link with proper handling
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Determine filename based on format
        const format = formatSelect.value;
        const quality = qualitySelect.value === 'high' ? '-hq' : '';
        const timestamp = new Date().getTime();
        a.download = `tts-${timestamp}${quality}.${format}`;

        // Ensure the link is in DOM for click to work
        document.body.appendChild(a);

        // Log for debugging
        console.log(`Downloading: ${a.download}`);
        console.log(`Blob size: ${blob.size} bytes`);
        console.log(`Content type: ${blob.type}`);

        // Trigger download
        a.click();

        // Cleanup
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);

        const formatName = format.toUpperCase();
        showStatus(`✅ ${formatName} downloaded! (${(blob.size/1024).toFixed(1)}KB)`, 'success');
    } catch (error) {
        console.error('Error downloading audio:', error);
        showStatus(`❌ Download failed: ${error.message}`, 'error');
    }
}

// Synthesize Audio
async function synthesizeAudio() {
    try {
        progressBar.style.display = 'block';
        playBtn.disabled = true;
        downloadBtn.disabled = true;

        const payload = {
            text: textInput.value,
            language: languageSelect.value,
            voice: voiceSelect.value,
            speed: parseInt(speedSlider.value),
            quality: qualitySelect.value,
            format: formatSelect.value
        };

        const response = await fetch(`${API_BASE_URL}/synthesize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to synthesize audio');
        }

        const blob = await response.blob();
        showStatus('✅ Audio generated successfully!', 'success');
        progressBar.style.display = 'none';

        return blob;
    } catch (error) {
        console.error('Error synthesizing audio:', error);
        showStatus(`Error: ${error.message}`, 'error');
        progressBar.style.display = 'none';
        return null;
    } finally {
        playBtn.disabled = false;
        downloadBtn.disabled = false;
    }
}

// Update Play/Stop Buttons
function updatePlayStopButtons() {
    if (isPlaying && !audioPlayer.paused) {
        playBtn.style.display = 'none';
        stopBtn.style.display = 'flex';
    } else {
        playBtn.style.display = 'flex';
        stopBtn.style.display = 'none';
    }
}

// Show Status Message
function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;

    // Clear error messages after 5 seconds
    if (type === 'error' || type === 'success') {
        setTimeout(() => {
            statusMessage.textContent = '';
            statusMessage.className = 'status-message';
        }, 5000);
    }
}

// Show Help Modal
function showModal(show) {
    helpModal.style.display = show ? 'flex' : 'none';
}

// Load Example Text
function loadExampleText() {
    const exampleText = `Hello, this is a test of the text-to-speech system.

I will now pause for one second.<pause 1s>

The pause above was one second long.

Here's an example with speed control. <slow>This part will be spoken slowly.</slow><pause 500>And <fast>this part will be spoken quickly.</fast>

You can combine pauses and speed tags:
<slow>Important message here.</slow><pause 1s>
Then continue at normal speed.

Both pause tags and speed tags work together in the same text.`;

    textInput.value = exampleText;
    updateCharCount();
}


// Audio player event listeners
audioPlayer.addEventListener('play', () => {
    isPlaying = true;
    updatePlayStopButtons();
});

audioPlayer.addEventListener('pause', () => {
    isPlaying = false;
    updatePlayStopButtons();
});

// Handle text input focus/blur for iOS
if (/iPhone|iPad|iPod/.test(navigator.userAgent)) {
    textInput.addEventListener('focus', () => {
        document.body.style.position = 'fixed';
    });

    textInput.addEventListener('blur', () => {
        document.body.style.position = 'static';
    });
}
