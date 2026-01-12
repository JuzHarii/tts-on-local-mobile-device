# Piper TTS for Mobile Application

Vietnamese Text-to-Speech (TTS) using **Piper ONNX Models** + **FastAPI** for Android mobile applications (Flutter).

This project provides a complete solution for running offline neural text-to-speech on mobile devices with a local backend server, eliminating the need for cloud-based TTS services.

---

## 🚀 Quick Start

### For Backend Server Users
```bash
# 1. Create and activate virtual environment
cd backend
py -3.10 -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000

# 4. Visit http://localhost:8000/docs
```

### For Mobile App Users
```bash
# 1. Install Flutter dependencies
cd mobile_app
flutter pub get

# 2. Update backend IP in lib/tts_service.dart
# Change: final String serverUrl = "http://192.168.1.YOUR_IP:8000";

# 3. Run on device/emulator
flutter run
```

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Backend Setup Guide](#backend-setup-guide)
- [API Endpoints](#api-endpoints)
- [Mobile App Setup](#mobile-app-setup)
- [Model Evaluation](#model-evaluation)
- [Troubleshooting](#troubleshooting)
- [Performance Optimization](#performance-optimization)
- [Contributing](#contributing)

---

## System Requirements

### Backend (FastAPI Server)

**Minimum Requirements:**
- **Python 3.10 – 3.11** (Recommended: 3.10.11)
- **4GB RAM**
- **2GB storage** for models
- **Windows 10/11**, Linux, or macOS

**Recommended:**
- **8GB+ RAM** for smooth multi-user handling
- **SSD** for faster model loading
- **NVIDIA GPU** (CUDA) for real-time synthesis
- **2Mbps+ network** for mobile streaming

⚠️ **Python Version Warning:** Do not use Python > 3.12. Several core dependencies (piper-tts, onnxruntime) are not yet fully compatible.

### Mobile App (Flutter)

- **Flutter SDK 3.0+**
- **Android:** SDK level 21+ (minimum), 28+ (recommended)
- **iOS:** iOS 12+
- **Device RAM:** 2GB minimum, 4GB recommended
- **Network:** Same WiFi or LAN as backend server

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│   Mobile Application (Flutter)      │
│  ┌───────────────────────────────┐  │
│  │  Text Input → TTS Service     │  │
│  │  Audio Playback               │  │
│  └───────────────┬───────────────┘  │
└──────────────────┼──────────────────┘
                   │
                   │ HTTP/REST
                   │ JSON Request
                   ▼
┌──────────────────────────────────────┐
│   Backend Server (FastAPI/Uvicorn)   │
│  ┌──────────────────────────────────┐│
│  │  /synthesize (POST)              ││
│  │  /synthesize_batch (POST)        ││
│  │  /health (GET)                   ││
│  └──────────┬───────────────────────┘│
│             │                         │
│  ┌──────────┴─────────────────────┐  │
│  │                                │  │
│  ▼                                ▼  │
│ ┌──────────────┐          ┌──────────┐
│ │ Text Services│          │  Piper   │
│ │ • Chunking   │          │  TTS     │
│ │ • Normalize  │          │  Engine  │
│ │ • Validate   │          │  (ONNX)  │
│ └──────────────┘          └──────────┘
│              │                │       │
│              └────────┬───────┘       │
│                       ▼               │
│              ┌─────────────────┐      │
│              │ Audio Generation│      │
│              │ & Streaming     │      │
│              └─────────────────┘      │
└──────────────────────────────────────┘
                   ▲
                   │ WAV Audio Stream
                   │
                   ▼
         Mobile App Plays Audio
```

**Data Flow:**
1. User types text in Flutter app
2. App sends HTTP POST to `/synthesize` endpoint
3. Backend validates and chunks long text
4. Piper TTS engine synthesizes speech (ONNX model)
5. Backend streams audio back to app
6. App receives and plays audio using native player

---

## Project Structure

```
tts-on-local-mobile-device/
│
├── backend/                           # FastAPI Server (Python)
│   │
│   ├── models/                        # ONNX Model Directory
│   │   ├── piper_model.onnx           # Main TTS model (150-300MB)
│   │   └── piper_model.json           # Model config & metadata
│   │
│   ├── evaluation/                    # Model Evaluation Suite
│   │   ├── audio/
│   │   │   ├── baseline/              # Baseline model audio outputs
│   │   │   └── finetuned/             # Fine-tuned model outputs
│   │   ├── test_case.py               # Sample Vietnamese test sentences
│   │   ├── generate_test_case.py      # Auto-generate diverse test cases
│   │   ├── generate_audio.py          # Batch synthesis script
│   │   ├── asr_whisper.py             # Audio-to-text validation (ASR)
│   │   ├── eval_wer.py                # Word Error Rate calculator
│   │   └── eval_rtf.py                # Real-Time Factor measurement
│   │
│   ├── services/                      # Core Business Logic
│   │   ├── tts_engine.py              # Piper TTS wrapper
│   │   ├── text_chunker.py            # Split long text intelligently
│   │   ├── text_extractor.py          # Extract text from files
│   │   └── audio_processor.py         # Audio post-processing
│   │
│   ├── routes/                        # API Endpoints
│   │   ├── synthesis.py               # /synthesize endpoints
│   │   ├── health.py                  # /health endpoint
│   │   └── models.py                  # /models endpoint
│   │
│   ├── uploads/                       # Temporary file storage (auto-cleanup)
│   ├── outputs/                       # Generated audio outputs
│   ├── logs/                          # Server logs
│   │
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Configuration & constants
│   ├── requirements.txt               # Python dependencies
│   └── .env                           # Environment variables (ignored)
│
├── mobile_app/                        # Flutter Application
│   │
│   ├── lib/
│   │   ├── main.dart                  # App entry point & main screen
│   │   ├── tts_service.dart           # API client & service layer
│   │   │
│   │   ├── models/                    # Data models
│   │   │   ├── synthesis_request.dart
│   │   │   └── synthesis_response.dart
│   │   │
│   │   ├── screens/                   # UI Screens
│   │   │   ├── home_screen.dart       # Main interface
│   │   │   └── settings_screen.dart   # Configuration
│   │   │
│   │   ├── widgets/                   # Reusable UI components
│   │   │   ├── text_input_widget.dart
│   │   │   └── audio_player_widget.dart
│   │   │
│   │   ├── utils/                     # Utilities
│   │   │   ├── constants.dart
│   │   │   ├── logger.dart
│   │   │   └── validators.dart
│   │   │
│   │   └── providers/                 # State management (if using Provider)
│   │       └── tts_provider.dart
│   │
│   ├── assets/
│   │   ├── images/                    # App icons, logos
│   │   │   ├── app_icon.png
│   │   │   └── logo.png
│   │   └── fonts/                     # Custom fonts
│   │
│   ├── android/                       # Android native config
│   │   ├── app/src/main/AndroidManifest.xml
│   │   └── build.gradle
│   │
│   ├── ios/                           # iOS native config
│   │   ├── Runner.xcworkspace
│   │   └── Podfile
│   │
│   ├── pubspec.yaml                   # Flutter dependencies
│   ├── pubspec.lock                   # Locked package versions
│   ├── analysis_options.yaml          # Dart linter rules
│   └── .gitignore
│
├── README.md                          # This file
├── .gitignore                         # Git ignore patterns
└── LICENSE                            # Project license
```

---

## Backend Setup Guide

### Step 1: Install Python 3.10

**Windows:** Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

### Step 2: Create Virtual Environment

```bash
cd backend
py -3.10 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

After activation, your prompt should show `(venv)`.

### Step 4: Upgrade pip and Install Dependencies

```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Key Dependencies:**
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **piper-tts** - TTS engine
- **onnxruntime** - ONNX model inference
- **librosa** - Audio processing
- **numpy** - Numerical computing

### Step 5: Download & Prepare Models

Create `backend/models/` directory:
```bash
mkdir models
```

**Option A: Download Pre-trained Models**

Download Vietnamese Piper models from [Hugging Face](https://huggingface.co/rhasspy/piper-voices):

1. Visit: https://huggingface.co/rhasspy/piper-voices
2. Navigate to: `vi_VN-` folder
3. Download:
   - `vi_VN-vios-medium.onnx` (~230MB)
   - `vi_VN-vios-medium.onnx.json` (~2KB)

Place files in `backend/models/`:
```
backend/models/
├── vi_VN-vios-medium.onnx
└── vi_VN-vios-medium.onnx.json
```

**Option B: Use Piper CLI (Auto-download)**

```bash
# Install piper directly (includes model management)
pip install piper-tts

# Models auto-download to ~/.local/share/piper/models/
# Or specify custom location in config
```

### Step 6: Configuration

Edit `backend/config.py`:

```python
# Server Configuration
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 8000
DEBUG = False  # Set True only in development

# Model Configuration
MODEL_PATH = "models/vi_VN-vios-medium.onnx"
MODEL_CONFIG = "models/vi_VN-vios-medium.onnx.json"

# TTS Settings
SAMPLE_RATE = 22050  # Hz
SPEAKER_ID = 0  # Default speaker
SPEED = 1.0  # Synthesis speed (0.5-2.0)

# Text Processing
MAX_TEXT_LENGTH = 1000  # Characters per request
CHUNK_SIZE = 200  # Characters per synthesis chunk

# Performance
NUM_THREADS = 4  # CPU threads for inference
ENABLE_GPU = False  # Set True if CUDA available
```

### Step 7: Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Optional flags:**
```bash
# Without auto-reload (production)
uvicorn main:app --host 0.0.0.0 --port 8000

# With worker threads (handle concurrent requests)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Custom log level
uvicorn main:app --log-level debug
```

### Step 8: Verify Server Status

**Method 1: Browser**
- Open: `http://localhost:8000/docs`
- Should see interactive Swagger UI

**Method 2: curl**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "running",
  "version": "1.0.0",
  "models": ["vi_VN-vios-medium"],
  "timestamp": "2026-01-12T12:56:00Z"
}
```

---

## API Endpoints

### 1. Health Check
```
GET /health
```
Returns server status and available models.

**Response (200):**
```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": 3600,
  "models": ["vi_VN-vios-medium"],
  "gpu_available": false
}
```

### 2. List Available Models
```
GET /models
```

**Response:**
```json
{
  "models": [
    {
      "name": "vi_VN-vios-medium",
      "language": "Vietnamese",
      "quality": "medium",
      "file_size": "230MB"
    }
  ]
}
```

### 3. Synthesize Speech (Single)
```
POST /synthesize
Content-Type: application/json

{
  "text": "Xin chào, Thế giới.",
  "model": "vi_VN-vios-medium",
  "speaker": 0,
  "speed": 1.0
}
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| text | string | required | Text to synthesize (max 1000 chars) |
| model | string | "vi_VN-vios-medium" | Model to use |
| speaker | integer | 0 | Speaker ID (0-3 depending on model) |
| speed | float | 1.0 | Synthesis speed (0.5-2.0) |

**Response (200):**
```
Content-Type: audio/wav
Binary WAV audio data
```

**Error (400):**
```json
{
  "detail": "Text must not exceed 1000 characters"
}
```

### 4. Synthesize Batch
```
POST /synthesize_batch
Content-Type: application/json

{
  "texts": [
    "Câu thứ nhất",
    "Câu thứ hai",
    "Câu thứ ba"
  ],
  "model": "vi_VN-vios-medium",
  "speed": 1.0
}
```

**Response (200):**
```json
{
  "status": "completed",
  "count": 3,
  "files": [
    "audio_0.wav",
    "audio_1.wav",
    "audio_2.wav"
  ],
  "download_url": "/download_batch/batch_123456"
}
```

### 5. Advanced Options
```
POST /synthesize_advanced

{
  "text": "Vietnamese text here",
  "model": "vi_VN-vios-medium",
  "speaker": 0,
  "speed": 1.2,
  "noise_scale": 0.667,
  "length_scale": 1.0,
  "output_format": "wav"
}
```

---

## Mobile App Setup

### Prerequisites

1. **Install Flutter SDK**
   - Download: https://docs.flutter.dev/get-started
   - Add to PATH
   - Verify: `flutter doctor`

2. **Android Setup** (if targeting Android)
   - Android SDK 21+ required
   - Android Studio recommended for emulator

3. **iOS Setup** (if targeting iOS, macOS only)
   - Xcode 12+
   - iOS 12+ deployment target

### Step 1: Navigate to Mobile App

```bash
cd mobile_app
```

### Step 2: Install Dependencies

```bash
flutter pub get
```

This installs packages from `pubspec.yaml`:
- `http` - HTTP client for API calls
- `audioplayers` - Audio playback
- `intl` - Internationalization

### Step 3: Update Backend URL

**File:** `lib/tts_service.dart`

```dart
class TtsService {
  // IMPORTANT: Replace with your backend server IP
  // Use computer IP address (e.g., 192.168.1.100), not localhost
  final String baseUrl = "http://192.168.1.100:8000";
  
  final http.Client _httpClient = http.Client();
  
  Future<File> synthesize(String text) async {
    final response = await _httpClient.post(
      Uri.parse('$baseUrl/synthesize'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'text': text}),
    );
    
    if (response.statusCode == 200) {
      // Save audio file and return
      return File(path);
    } else {
      throw Exception('Synthesis failed: ${response.statusCode}');
    }
  }
}
```

**Finding Your Backend IP:**
```bash
# Windows
ipconfig

# Linux/macOS
ifconfig
# or
hostname -I
```

Look for IPv4 address like `192.168.x.x` or `10.x.x.x`

### Step 4: Configure App Icon (Optional)

Edit `pubspec.yaml`:
```yaml
flutter_launcher_icons:
  android: "launcher_icon"
  ios: true
  image_path: "assets/images/app_icon.png"
  min_sdk_android: 21
```

Generate icons:
```bash
flutter pub run flutter_launcher_icons
```

### Step 5: Run App

**List connected devices:**
```bash
flutter devices
```

**Run on Android Emulator:**
```bash
flutter run
```

**Run on specific device:**
```bash
flutter run -d emulator-5554
```

**Run in release mode (optimized):**
```bash
flutter run --release
```

### Step 6: Build for Distribution

**Build APK for Android:**
```bash
# Split APKs by architecture (smaller download)
flutter build apk --release --split-per-abi

# Single universal APK (larger)
flutter build apk --release

# App Bundle for Play Store
flutter build appbundle --release
```

**Output locations:**
```
build/app/outputs/flutter-apk/
├── app-armeabi-v7a-release.apk        # ARM 32-bit
├── app-arm64-v8a-release.apk          # ARM 64-bit
└── app-x86_64-release.apk             # x86 64-bit
```

**Build for iOS (macOS only):**
```bash
flutter build ios --release
```

---

## Model Evaluation

### Purpose
Evaluate TTS model quality using standard metrics:
- **WER** (Word Error Rate) - Accuracy via ASR
- **CER** (Character Error Rate) - Character-level accuracy  
- **RTF** (Real-Time Factor) - Synthesis speed

### Step 1: Prepare Test Dataset

Create `backend/evaluation/test_cases.txt`:
```
Đây là câu kiểm tra số một.
Công nghệ trí tuệ nhân tạo đang phát triển nhanh chóng.
Tiếng Việt là ngôn ngữ của dân tộc Kinh.
Hôm nay thời tiết rất đẹp.
Tôi thích học lập trình Python.
```

Or auto-generate:
```bash
cd backend/evaluation
python generate_test_case.py --count 1000
```

### Step 2: Generate Audio Files

```bash
python generate_audio.py
```

This will:
1. Synthesize each test sentence using the model
2. Save to `audio/` directory
3. Create separate folders for baseline and fine-tuned models
4. Generate metadata files

**Output structure:**
```
audio/
├── baseline/
│   ├── 0.wav (audio file)
│   ├── 0.json (metadata)
│   └── ...
└── finetuned/
    ├── 0.wav
    ├── 0.json
    └── ...
```

### Step 3: Calculate WER/CER

This uses Whisper ASR to transcribe generated audio and compare with original text:

```bash
python eval_wer.py
```

### Step 4: Measure Real-Time Factor

Measures how fast the model synthesizes compared to audio playback:

```bash
python eval_rtf.py
```
**RTF Interpretation:**
- RTF = 0.1 → 10x faster than real-time (excellent)
- RTF = 0.5 → 2x faster than real-time (good)
- RTF = 1.0 → Real-time capability (minimum acceptable)
- RTF > 1.0 → Slower than real-time (not suitable for live)

---

## Troubleshooting

### Backend Issues

#### Problem: "Port 8000 already in use"

**Windows:**
```bash
# Find process using port
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID 1234 /F

# Or use different port
uvicorn main:app --port 8001
```

**Linux/macOS:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### Problem: "ModuleNotFoundError: No module named 'piper_tts'"

```bash
# Ensure you're in the virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Reinstall dependencies
pip install -r requirements.txt

# Verify piper installation
python -c "import piper_tts; print(piper_tts.__version__)"
```

#### Problem: "ONNX model not found"

```bash
# Check model directory structure
ls backend/models/

# Should contain:
# - piper_model.onnx (or your model file)
# - piper_model.json

# Verify model files exist
python -c "import os; print(os.path.exists('models/piper_model.onnx'))"
```

#### Problem: "OSError: libsndfile not found" (Linux)

```bash
# Ubuntu/Debian
sudo apt install libsndfile1

# Fedora
sudo dnf install libsndfile

# Arch
sudo pacman -S libsndfile
```

### Mobile App Issues

#### Problem: "Connection refused" or "Cannot reach backend"

**Checklist:**
1. Backend server running: `http://192.168.1.100:8000/health`
2. Correct IP in `lib/tts_service.dart` (not localhost)
3. Both devices on same WiFi network
4. Firewall allows port 8000
5. Mobile device can ping backend PC

**Debug:**
```dart
// Add to tts_service.dart
void debugConnection() async {
  try {
    final response = await http.get(
      Uri.parse('http://192.168.1.100:8000/health'),
    ).timeout(const Duration(seconds: 5));
    
    print('Status: ${response.statusCode}');
    print('Body: ${response.body}');
  } on SocketException catch (e) {
    print('Network error: $e');
  } on TimeoutException {
    print('Connection timeout - backend not reachable');
  }
}
```

#### Problem: "No audio playing"

- Check device volume
- Verify audio permissions in `AndroidManifest.xml`
- Test with local audio file first
- Check logcat: `flutter logs`

#### Problem: "Flutter build fails"

```bash
# Clean everything
flutter clean

# Clear pub cache (if needed)
flutter pub cache clean

# Get dependencies fresh
flutter pub get

# Try building again
flutter run
```

#### Problem: "Android build error: gradle"

```bash
# Update Flutter
flutter upgrade

# Repair pub cache
flutter pub cache repair

# Rebuild from scratch
flutter clean
cd android
./gradlew clean
cd ..
flutter run
```

#### Problem: "App keeps disconnecting from backend"

Implement retry logic in `tts_service.dart`:

```dart
Future<File> synthesizeWithRetry(String text, {int maxRetries = 3}) async {
  for (int i = 0; i < maxRetries; i++) {
    try {
      return await synthesize(text);
    } catch (e) {
      if (i == maxRetries - 1) rethrow;
      await Future.delayed(Duration(seconds: 2 * (i + 1)));
    }
  }
}
```

---

## Performance Optimization

### Backend

**1. Enable GPU Acceleration:**
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu  # Requires CUDA 11.8+
```

**2. Batch Processing:**
Use `/synthesize_batch` endpoint instead of multiple single requests.

**3. Increase Worker Threads:**
```bash
uvicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**4. Enable Caching:**
```python
# In config.py
ENABLE_CACHE = True
CACHE_DIR = "cache/"
```

### Mobile App

**1. Cache Generated Audio:**
```dart
final Map<String, File> audioCache = {};

Future<File> getCachedAudio(String text) async {
  if (audioCache.containsKey(text)) {
    return audioCache[text]!;
  }
  final file = await synthesize(text);
  audioCache[text] = file;
  return file;
}
```

**2. Pre-buffer Audio:**
Generate audio in background before user requests playback.

**3. Memory Management:**
```dart
// Clear old cached audio periodically
void clearOldCache() {
  audioCache.clear();
  // Rebuild UI to release references
}
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/tts-on-local-mobile-device.git
   cd tts-on-local-mobile-device
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open Pull Request** on GitHub

---

## Acknowledgments

- **[Rhasspy Piper](https://github.com/rhasspy/piper)** - Open-source TTS engine
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[Flutter](https://flutter.dev/)** - Cross-platform mobile framework
- **[ONNX Runtime](https://onnxruntime.ai/)** - Model inference engine
- **Vietnamese TTS Community** - For voice models and guidance
---
