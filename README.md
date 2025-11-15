# Speech Studio

Enhanced Microsoft Edge TTS - free professional text-to-speech with natural-sounding audio. Generate unlimited voiceovers in 19 languages with 50+ voices without API costs or quotas. Perfect for YouTubers, content creators, and educators.

## Why Speech Studio?

Unlike standard TTS, we enhanced audio quality by:
- **Studio room tone in pauses** - pauses filled with authentic studio ambience instead of silence, making audio sound like a professional recording
- **Flexible pause control** - add custom pauses with tags to match your speech timing exactly
- **Quality selection** - choose between normal (128 kbps) or high quality (320 kbps) based on your needs
- **Speed control** - adjust voice speed -50% to +50% with automatic bitrate optimization for clarity


## Supported Languages

English (British, American), Russian, German, French, Spanish, Italian, Dutch, Polish, Swedish, Danish, Norwegian, Ukrainian, Portuguese (Portugal & Brazil), Czech, Hungarian, Romanian, Greek

## Usage Tips & Recommendations

**For YouTube videos:**
- Use Normal quality (faster, smaller files)
- Speed: 0% to +10% (natural speaking pace)
- Add pauses: `<pause 1s>` between thoughts for better pacing

**For audiobooks/long content:**
- Use High quality (better audio fidelity)
- Speed: -5% to 0% (easier to listen to)
- Natural pauses keep listeners engaged

**For fast-paced content:**
- Speed: +15% to +30%
- Use High quality to maintain clarity at fast speeds
- Shorter pauses: `<pause 500>`

## Quick Start

1. Select language and voice
2. Paste your text
3. Adjust speed and quality
4. Click Play to preview, Download to save

### Pause Syntax

```
Normal pause (500ms):       <pause>
Custom milliseconds:        <pause 800>
Custom seconds:             <pause 1.5s>
```

Example: `Hello<pause 1s>how are you?`

## Setup

### Clone the Repository

```bash
git clone https://github.com/yourusername/speech-studio.git
cd speech-studio
```

### Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

The app will start on http://0.0.0.0:8000 - open it in your browser to begin synthesizing.

### Requirements
- Python 3.8+
- pip (Python package manager)
- FFmpeg (required for audio processing)

## 100% Free

No limits on synthesis count, text length, or downloads.

## Disclaimer

This project uses Microsoft Edge TTS through an open-source library. It's designed for **personal, educational, and non-commercial use only**.

For commercial projects and production use, please use the official **Microsoft Azure Speech Services API**, which requires a paid subscription. This ensures proper licensing and reliability.

The edge-tts library is community-maintained and not officially supported by Microsoft.
