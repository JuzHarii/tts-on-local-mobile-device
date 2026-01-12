import 'package:just_audio/just_audio.dart';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TtsService {
  final String baseUrl;

  final AudioPlayer _player = AudioPlayer();

  File? _lastAudioFile;

  TtsService(this.baseUrl);

  void dispose() {
    _player.dispose();
  }

  //  TEXT → TTS (model + speed)
  Future<void> speak(String text, String model, double speed) async {
    if (text.trim().isEmpty) return;

    try {
      await _player.stop();

      final response = await http
          .post(
            Uri.parse("$baseUrl/tts"),
            headers: {
              "Content-Type": "application/json",
              "ngrok-skip-browser-warning": "true",
            },
            body: jsonEncode({
              "text": text,
              "model": model,
              "speed": speed,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode != 200) {
        throw Exception(
          "Server error ${response.statusCode}: ${response.body}",
        );
      }

      await _saveAndPlay(response.bodyBytes);
    } catch (e) {
      print("❌ Lỗi TTS text: $e");
      rethrow;
    }
  }

  //  UPLOAD PDF / DOCX → TTS
  Future<void> speakFromFile({
    required File file,
    required String model,
    required double speed,
  }) async {
    try {
      await _player.stop();

      final uri = Uri.parse("$baseUrl/tts/upload");
      final request = http.MultipartRequest("POST", uri);

      request.fields["model"] = model;
      request.fields["speed"] = speed.toString();

      request.files.add(
        await http.MultipartFile.fromPath(
          "file",
          file.path,
        ),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode != 200) {
        throw Exception(
          "Upload TTS error ${response.statusCode}: ${response.body}",
        );
      }

      await _saveAndPlay(response.bodyBytes);
    } catch (e) {
      print("❌ Lỗi TTS upload: $e");
      rethrow;
    }
  }

  //  SAVE WAV + PLAY
  Future<void> _saveAndPlay(List<int> bytes) async {
    final tempDir = await getTemporaryDirectory();
    final fileName =
        "tts_${DateTime.now().millisecondsSinceEpoch}.wav";
    final file = File("${tempDir.path}/$fileName");

    await file.writeAsBytes(bytes);
    _lastAudioFile = file;

    await _player.setFilePath(file.path);
    await _player.play();
  }

  //  COPY WAV RA DOCUMENTS (nếu muốn dùng sau)
  Future<String?> saveWavToDocuments() async {
    if (_lastAudioFile == null) return null;

    final docDir = await getApplicationDocumentsDirectory();
    final targetPath =
        "${docDir.path}/${_lastAudioFile!.path.split('/').last}";

    final targetFile = await _lastAudioFile!.copy(targetPath);
    return targetFile.path;
  }

  //  STOP
  Future<void> stop() async {
    await _player.stop();
  }

  // PAUSE
  Future<void> pause() async {
    if (_player.playing) {
      await _player.pause();
    }
  }

  //  RESUME
  Future<void> resume() async {
    if (!_player.playing) {
      await _player.play();
    }
  }

  //  SEEK
  Future<void> seekBy(Duration offset) async {
    final current = _player.position;
    final duration = _player.duration;

    if (duration == null) return;

    final target = current + offset;

    if (target < Duration.zero) {
      await _player.seek(Duration.zero);
    } else if (target > duration) {
      await _player.seek(duration);
    } else {
      await _player.seek(target);
    }
  }

  //  PLAYER STATE
  Stream<PlayerState> get playerStateStream =>
      _player.playerStateStream;

  bool get isPlaying => _player.playing;
}
