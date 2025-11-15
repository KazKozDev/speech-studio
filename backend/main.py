import edge_tts
import asyncio
import re
import tempfile
import os
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging

# Try to import pydub for pause support
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠️ Warning: pydub not installed. Pause tags will be ignored.")
    print("   Install it with: pip install pydub")

app = FastAPI(title="TTS Web API", version="1.0.0")

# Load background audio file for pauses
BACKGROUND_AUDIO = None
BACKGROUND_AUDIO_PATH = "studio-room-tone.wav"

def load_background_audio():
    global BACKGROUND_AUDIO
    try:
        if os.path.exists(BACKGROUND_AUDIO_PATH):
            BACKGROUND_AUDIO = AudioSegment.from_wav(BACKGROUND_AUDIO_PATH)
            logger_placeholder = logging.getLogger(__name__)
            logger_placeholder.info(f"✅ Loaded background audio: {len(BACKGROUND_AUDIO)}ms")
        else:
            print(f"⚠️ Warning: {BACKGROUND_AUDIO_PATH} not found. Using silence for pauses.")
    except Exception as e:
        print(f"⚠️ Warning: Could not load background audio: {e}")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pause tag regex pattern
PAUSE_TAG_REGEX = r'<pause\s*(\d*\.?\d*)\s*(s|ms)?\s*>'

# Supported voices by language
SUPPORTED_VOICES = {
    "ru": {
        "name": "🇷🇺 Русский",
        "voices": {
            "Dmitry (Male)": "ru-RU-DmitryNeural",
            "Svetlana (Female)": "ru-RU-SvetlanaNeural",
            "Ekaterina (Female)": "ru-RU-EkaterinaNeural",
        }
    },
    "en-GB": {
        "name": "🇬🇧 English (British)",
        "voices": {
            "Ryan (Male)": "en-GB-RyanNeural",
            "Sonia (Female)": "en-GB-SoniaNeural",
            "Libby (Female)": "en-GB-LibbyNeural",
            "Thomas (Male)": "en-GB-ThomasNeural",
        }
    },
    "en-US": {
        "name": "🇺🇸 English (American)",
        "voices": {
            "Guy (Male)": "en-US-GuyNeural",
            "Jenny (Female)": "en-US-JennyNeural",
            "Aria (Female)": "en-US-AriaNeural",
            "Christopher (Male)": "en-US-ChristopherNeural",
        }
    },
    "de": {
        "name": "🇩🇪 Deutsch",
        "voices": {
            "Stefan (Male)": "de-DE-StefanNeural",
            "Katja (Female)": "de-DE-KatjaNeural",
            "Amala (Female)": "de-DE-AmalaNeural",
        }
    },
    "fr": {
        "name": "🇫🇷 Français",
        "voices": {
            "Henri (Male)": "fr-FR-HenriNeural",
            "Denise (Female)": "fr-FR-DeniseNeural",
            "Alain (Male)": "fr-FR-AlainNeural",
            "Brigitte (Female)": "fr-FR-BrigetteNeural",
        }
    },
    "es": {
        "name": "🇪🇸 Español",
        "voices": {
            "Alvaro (Male)": "es-ES-AlvaroNeural",
            "Consuelo (Female)": "es-ES-ConsualoNeural",
            "Enrique (Male)": "es-ES-EnriqueNeural",
            "Lucia (Female)": "es-ES-LuciaNeural",
        }
    },
    "it": {
        "name": "🇮🇹 Italiano",
        "voices": {
            "Diego (Male)": "it-IT-DiegoNeural",
            "Elsa (Female)": "it-IT-ElsaNeural",
            "Isabella (Female)": "it-IT-IsabellaNeural",
        }
    },
    "nl": {
        "name": "🇳🇱 Nederlands",
        "voices": {
            "Frank (Male)": "nl-NL-FrankNeural",
            "ColetteNeural (Female)": "nl-NL-ColetteNeural",
            "MaartenNeural (Male)": "nl-NL-MaartenNeural",
        }
    },
    "pl": {
        "name": "🇵🇱 Polski",
        "voices": {
            "Jakub (Male)": "pl-PL-JakubNeural",
            "Zofia (Female)": "pl-PL-ZofiaNeural",
        }
    },
    "sv": {
        "name": "🇸🇪 Svenska",
        "voices": {
            "Marcus (Male)": "sv-SE-MarcusNeural",
            "Sofia (Female)": "sv-SE-SofiaNeural",
        }
    },
    "da": {
        "name": "🇩🇰 Dansk",
        "voices": {
            "Jeppe (Male)": "da-DK-JeppeNeural",
            "ChristelNeural (Female)": "da-DK-ChristelNeural",
        }
    },
    "nb": {
        "name": "🇳🇴 Norsk (Bokmål)",
        "voices": {
            "Finn (Male)": "nb-NO-FinnNeural",
            "Pernille (Female)": "nb-NO-PernilleNeural",
        }
    },
    "uk": {
        "name": "🇺🇦 Українська",
        "voices": {
            "Ostap (Male)": "uk-UA-OstapNeural",
            "Oxana (Female)": "uk-UA-OxanaNeural",
        }
    },
    "pt": {
        "name": "🇵🇹 Português (Portugal)",
        "voices": {
            "Duarte (Male)": "pt-PT-DuarteNeural",
            "Fernanda (Female)": "pt-PT-FernandaNeural",
        }
    },
    "pt-BR": {
        "name": "🇧🇷 Português (Brasil)",
        "voices": {
            "Antonio (Male)": "pt-BR-AntonioNeural",
            "Francisca (Female)": "pt-BR-FranciscaNeural",
        }
    },
    "cs": {
        "name": "🇨🇿 Čeština",
        "voices": {
            "Anton (Male)": "cs-CZ-AntonNeural",
            "Zuzana (Female)": "cs-CZ-ZuzanaNeural",
        }
    },
    "hu": {
        "name": "🇭🇺 Magyar",
        "voices": {
            "Tamas (Male)": "hu-HU-TamasNeural",
            "Noemi (Female)": "hu-HU-NoemiNeural",
        }
    },
    "ro": {
        "name": "🇷🇴 Română",
        "voices": {
            "Andrei (Male)": "ro-RO-AndreiNeural",
            "AmeliaNeuralNeural (Female)": "ro-RO-AmeliaNeural",
        }
    },
    "gr": {
        "name": "🇬🇷 Ελληνικά",
        "voices": {
            "Themis (Male)": "el-GR-ThemisNeural",
            "Athinandria (Female)": "el-GR-AthinandriaNeural",
        }
    },
}


class TTSRequest(BaseModel):
    text: str
    language: str
    voice: str
    speed: int = 0  # -50 to 50
    quality: str = "normal"  # normal or high
    format: str = "mp3"  # mp3 or wav


class LanguagesResponse(BaseModel):
    languages: dict


class TTSStatus(BaseModel):
    status: str
    message: str


def parse_pauses(text: str) -> List[tuple]:
    """Parse text into parts with pause tags"""
    parts = []
    last_end = 0

    for match in re.finditer(PAUSE_TAG_REGEX, text, re.IGNORECASE):
        start, end = match.span()

        # Add text before pause tag
        if start > last_end:
            text_part = text[last_end:start].strip()
            if text_part:
                parts.append(('text', text_part))

        # Parse pause duration
        value = match.group(1)
        unit = match.group(2) or 'ms'

        if value:
            duration = float(value)
            if unit == 's':
                duration_ms = int(duration * 1000)
            else:  # ms
                duration_ms = int(duration)
        else:
            duration_ms = 500  # Default pause

        parts.append(('pause', duration_ms))
        last_end = end

    # Add remaining text
    if last_end < len(text):
        text_part = text[last_end:].strip()
        if text_part:
            parts.append(('text', text_part))

    return parts if parts else [('text', text)]


def format_rate(speed: int) -> str:
    """Format speed for Edge TTS"""
    if speed >= 0:
        return f"+{speed}%"
    else:
        return f"{speed}%"


def get_background_segment(duration_ms: int) -> AudioSegment:
    """Get random segment of background audio with specified duration"""
    if BACKGROUND_AUDIO is None or len(BACKGROUND_AUDIO) == 0:
        return AudioSegment.silent(duration=duration_ms)

    max_start = max(0, len(BACKGROUND_AUDIO) - duration_ms)
    start_pos = random.randint(0, max_start) if max_start > 0 else 0
    end_pos = start_pos + duration_ms

    segment = BACKGROUND_AUDIO[start_pos:end_pos]

    # If segment is shorter than requested duration, pad with silence
    if len(segment) < duration_ms:
        silence = AudioSegment.silent(duration=duration_ms - len(segment))
        segment = segment + silence

    return segment


def normalize_audio(audio: AudioSegment) -> AudioSegment:
    """Normalize audio to improve quality, especially for slow speeds"""
    # Normalize loudness
    loudness = audio.dBFS
    if loudness != 0:
        # Normalize to -20dBFS for consistent volume
        audio = audio.apply_gain(min(0, -20 - loudness))

    # Add slight compression effect for clarity
    return audio


def get_bitrate(quality: str, speed: int) -> str:
    """Determine bitrate based on quality and speed"""
    # Lower speeds benefit from higher bitrates for clarity
    if speed < -20:
        # Very slow speech needs high bitrate
        return "320k" if quality == "high" else "192k"
    elif speed < 0:
        # Slow speech
        return "320k" if quality == "high" else "160k"
    else:
        # Normal or fast speech
        return "320k" if quality == "high" else "128k"


@app.get("/")
async def root():
    return {"message": "TTS Web API", "version": "1.0.0"}


@app.get("/languages", response_model=LanguagesResponse)
async def get_languages():
    """Get list of supported languages and voices"""
    return {"languages": SUPPORTED_VOICES}


@app.post("/synthesize")
async def synthesize_tts(request: TTSRequest):
    """Synthesize text to speech with quality and format options"""
    try:
        # Validate inputs
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if request.language not in SUPPORTED_VOICES:
            raise HTTPException(status_code=400, detail=f"Language '{request.language}' not supported")

        if request.voice not in SUPPORTED_VOICES[request.language]["voices"]:
            raise HTTPException(status_code=400, detail=f"Voice '{request.voice}' not found for language '{request.language}'")

        # Validate speed
        if not (-50 <= request.speed <= 50):
            raise HTTPException(status_code=400, detail="Speed must be between -50 and 50")

        # Get voice code and determine bitrate
        voice_code = SUPPORTED_VOICES[request.language]["voices"][request.voice]
        rate = format_rate(request.speed)
        bitrate = get_bitrate(request.quality, request.speed)

        # Determine content type based on format
        if request.format == "wav":
            content_type = "audio/wav"
            output_format = "wav"
        else:
            content_type = "audio/mpeg"
            output_format = "mp3"

        logger.info(f"Generating TTS: {request.language}/{request.voice}, speed={request.speed}, quality={request.quality}, format={request.format}")

        # Parse text for pauses
        parts = parse_pauses(request.text)

        # If no pauses or pydub unavailable, use simple method
        if not any(p[0] == 'pause' for p in parts) or not PYDUB_AVAILABLE:
            communicate = edge_tts.Communicate(
                text=request.text,
                voice=voice_code,
                rate=rate
            )

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
            temp_file.close()

            await communicate.save(temp_file.name)

            # Load, normalize, and re-export with quality settings
            if PYDUB_AVAILABLE:
                audio = AudioSegment.from_mp3(temp_file.name)
                audio = normalize_audio(audio)

                export_params = {"format": output_format}
                if output_format == "mp3":
                    export_params["bitrate"] = bitrate

                audio.export(temp_file.name, **export_params)

            return FileResponse(
                path=temp_file.name,
                media_type=content_type,
                filename=f"audio.{output_format}"
            )

        # Build audio with pauses
        final_audio = AudioSegment.empty()

        for part_type, content in parts:
            if part_type == 'text':
                if not content.strip():
                    continue

                communicate = edge_tts.Communicate(
                    text=content,
                    voice=voice_code,
                    rate=rate
                )

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
                temp_file.close()

                await communicate.save(temp_file.name)

                segment = AudioSegment.from_mp3(temp_file.name)
                final_audio += segment

                os.unlink(temp_file.name)

            elif part_type == 'pause':
                pause_segment = get_background_segment(content)
                final_audio += pause_segment

        # Normalize the final audio
        final_audio = normalize_audio(final_audio)

        # Save final audio with appropriate format and quality
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}')
        temp_file.close()

        export_params = {"format": output_format}
        if output_format == "mp3":
            export_params["bitrate"] = bitrate

        final_audio.export(temp_file.name, **export_params)

        return FileResponse(
            path=temp_file.name,
            media_type=content_type,
            filename=f"audio.{output_format}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in synthesize_tts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating speech: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pydub_available": PYDUB_AVAILABLE,
        "languages_supported": len(SUPPORTED_VOICES)
    }


# Mount static files (frontend)
try:
    # Try current structure first (local development)
    frontend_dir = "../frontend"
    if not os.path.exists(frontend_dir):
        # Try Docker structure
        frontend_dir = "./frontend"
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")


# Load background audio on startup
@app.on_event("startup")
async def startup_event():
    load_background_audio()


if __name__ == "__main__":
    import uvicorn
    load_background_audio()
    uvicorn.run(app, host="0.0.0.0", port=8000)
