# 0. Piper TTS for Mobile Application

Text-to-Speech (TTS) tiếng Việt sử dụng **Piper TTS** + **FastAPI**, phục vụ cho ứng dụng di động Android (Flutter).
---

## 1. Yêu cầu hệ thống

### 1.1. Phần mềm bắt buộc

- **Python 3.10 – 3.11** (Khuyến nghị 3.10.11)
- **pip** (đi kèm Python)
- Hệ điều hành:
  - Windows 10 / 11 (đã test)
  - Linux / macOS (chưa test, nhưng có thể chạy)

⚠️ Không sử dụng Python > 3.12 vì một số thư viện chưa tương thích ổn định.
---

## 2. Cấu trúc thư mục 

DHT-TTS/
├── backend/                       
│   ├── models/                     # Lưu trữ các file trọng số mô hình ONNX và cấu hình
│   │   ├── nagiya_ver_1.onnx       # Mô hình baseline
│   │   ├── nagiya_ver_1.onnx.json  
│   │   ├── piper_model.onnx        # Mô hình Piper finetuned 
│   │   └── piper_model.json          
│   ├── evaluation/                 
│   │   ├── audio/                 
│   │   │   ├── baseline/           # Audio sinh ra từ mô hình gốc
│   │   │   └── finetuned/          # Audio sinh ra từ mô hình đã tinh chỉnh
│   │   ├── test_case.py            # Chứa các danh sách câu mẫu để kiểm thử
│   │   ├── genarate_test_case.py   # Script tự động tạo 1000 câu test đa dạng
│   │   ├── generate_audio.py       # Script gọi API để sinh audio hàng loạt từ test case
│   │   ├── asr_whisper.py          # Chuyển đổi audio ngược lại thành văn bản dùng Whisper
│   │   ├── eval_wer.py             # Tính toán tỉ lệ lỗi từ (WER) và ký tự (CER)
│   │   └── eval_rtf.py             # Đo lường tốc độ tổng hợp âm thanh (Real-Time Factor)
│   ├── outputs/                    # Lưu trữ kết quả đầu ra sau khi xử lý thực tế
│   ├── services/                  
│   │   ├── text_chunker.py         # Chia nhỏ văn bản dài để tối ưu hóa tổng hợp
│   │   └── text_extractor.py       # Trích xuất nội dung văn bản từ các định dạng file
│   ├── uploads/                    # Thư mục tạm chứa file người dùng tải lên
│   ├── main.py                     # File chạy chính của server (FastAPI/Flask)
│   └── requirements.txt            # Danh sách các thư viện Python cần cài đặt
├── mobile_app/                    
│   ├── android/                    # Cấu hình dự án cho hệ điều hành Android
│   ├── assets/                     # Chứa hình ảnh, font chữ và tài nguyên ứng dụng
│   ├── ios/                        # Cấu hình dự án cho hệ điều hành iOS
│   ├── lib/                       
│   │   ├── main.dart               # Điểm khởi chạy và giao diện chính của App
│   │   └── tts_service.dart        # Logic kết nối và gọi API từ backend
│   ├── analysis_options.yaml       # Quy tắc kiểm tra lỗi code Dart (Linter)
│   ├── pubspec.lock                # Danh sách chi tiết các phiên bản package đã cài
│   └── pubspec.yaml                # Khai báo thư viện và tài nguyên của dự án Flutter
└── README.md                       
---


# 1. Cài đặt môi trường Python-Backend

## 1.1. Tạo môi trường ảo (Virtual Environment)
cd F:\DHT_TTS\backend

py -3.10 -m venv venv

### 1.2. Kích hoạt virtual environment
- **windows**

venv\Scripts\activate

- **Linux/macOS**

source venv/bin/activate
---


## 2. Cài đặt thư viện Python 


### 2.1. Nâng cấp pip 

python -m pip install --upgrade pip

### 2.2. Cài toàn bộ thư viện cần thiết 

pip install -r requirements.txt
---

## 3. Chuẩn bị mô hình TTS 

### 3.1 Đặt mô hình ONNX vào models/
models/
├── model.onnx
└── model.onnx.json
---

## 4. Chạy backend FastAPI 

### 4.1. Kiểm tra server 

**Cấu hình API backend**
Trong lib/main.dart : 

tts = TtsService(
  "http://<IP_MAY_CHAY_BACKEND>:8000",
);


### 4.2. Chạy server 

uvicorn main:app --host 0.0.0.0 --port 8000

**Mở trình duyệt:** http://localhost:8000 

**Kết quả**
{
  "status": "ok",
  "models": ["baseline", "piper-finetuned"]
}

==> Backend chạy thành công 

**Xử lý lỗi thường gặp**
ModuleNotFoundError
Port 8000 already in use
App không gọi được backend
Firewall chặn 
---

# 2. Cài Flutter - APK APP (New terminal)

**Link tải**
https://docs.flutter.dev/get-started

**Kiểm tra**
flutter doctor 

## 1. Cấu hình Mobile App

cd F:\DHT_TTS\mobile_app 

**Cài package** 
flutter pub get 

**Load Icon App**

flutter pub run flutter_launcher_icons
---

## 2. Run App 

**Android**

flutter run 

**Build APK**

flutter build apk --release --split-per-abi


# 3. Đánh giá mô hình (WER/RTF)

## 3.1. Chuẩn bị test case

evaluation/test_case.txt

Mỗi dòng là 1 ground truth

## 3.2. Sinh audio đánh giá 

python evaluation/generate_audio.py

## 3.3 Tính WER/CER

python evaluation/eval_wer.py

**Kết quả**
=== BASELINE ===
WER: 0.8068
CER: 0.4994

=== FINETUNED ===
WER: 0.4100
CER: 0.2119

## 3.4 Tính RTF 

python evaluation/eval_rtf.py

**Kết quả** 
=== RTF: BASELINE ===
Total synth time: 2704.02s
Total audio time: 14119.04s 
RTF = 0.192 

=== RTF: PIPER-FINETUNED ===
Total synth time: 2692.98s
Total audio time: 13988.58s 
RTF = 0.190 