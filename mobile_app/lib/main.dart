import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'tts_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.blue,
      ),
      home: const TtsDemo(),
    );
  }
}

class TtsDemo extends StatefulWidget {
  const TtsDemo({super.key});

  @override
  State<TtsDemo> createState() => _TtsDemoState();
}

class _TtsDemoState extends State<TtsDemo> {
  final controller = TextEditingController();
  late final TtsService tts;

  bool _isLoading = false;
  bool _isPlaying = false;

  // MODEL
  String _selectedModel = "baseline";
  final List<String> _models = ["baseline", "piper-finetuned"];

  // SPEED
  double _speechRate = 1.0;
  final List<double> _rates = [0.5, 1.0, 1.5, 2.0];

  @override
  void initState() {
    super.initState();
    tts = TtsService(
      "http:192.168.1.26:8000",
    );

    // Player state
    tts.playerStateStream.listen((state) {
      if (!mounted) return;
      setState(() => _isPlaying = state.playing);
    });

    _checkFirstLaunch();
  }


  Future<void> _checkFirstLaunch() async {
    final prefs = await SharedPreferences.getInstance();
    final isFirst = prefs.getBool("first_launch") ?? true;

    if (isFirst) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _showHelpDialog();
      });
      await prefs.setBool("first_launch", false);
    }
  }

  void _showHelpDialog() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text("Hướng dẫn sử dụng"),
        content: const SingleChildScrollView(
          child: Text(
            "1️⃣ Chọn mô hình\n"
            "2️⃣ Chọn tốc độ đọc\n"
            "3️⃣ Nhập văn bản/Upload PDF / Word\n"
            "4️⃣ Xử lý văn bản\n\n\n"
            "❗LƯU Ý: Ấn Xử lý văn bản khi đổi mới MÔ HÌNH/TỐC ĐỘ.",
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("Đã hiểu"),
          ),
        ],
      ),
    );
  }

  // TEXT → TTS
  Future<void> _handleSpeak() async {
    final text = controller.text.trim();
    if (text.isEmpty) return;

    FocusScope.of(context).unfocus();
    setState(() => _isLoading = true);

    try {
      await tts.speak(text, _selectedModel, _speechRate);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Lỗi: $e"), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  // FILE → TTS
  Future<void> _handleUploadFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ["pdf", "docx"],
    );

    if (result == null || result.files.single.path == null) return;

    final file = File(result.files.single.path!);

    setState(() => _isLoading = true);

    try {
      await tts.speakFromFile(
        file: file,
        model: _selectedModel,
        speed: _speechRate,
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Lỗi đọc file: $e"), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    controller.dispose();
    tts.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("DHT – Piper TTS"),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.help_outline),
            onPressed: _showHelpDialog,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [

              // MODEL
              DropdownButtonFormField<String>(
                value: _selectedModel,
                items: _models
                    .map((m) => DropdownMenuItem(value: m, child: Text(m)))
                    .toList(),
                onChanged: (v) => setState(() => _selectedModel = v!),
                decoration: const InputDecoration(
                  labelText: "MÔ HÌNH",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.memory),
                ),
              ),
              const SizedBox(height: 16),

              // SPEED
              DropdownButtonFormField<double>(
                value: _speechRate,
                items: _rates
                    .map((r) => DropdownMenuItem(
                          value: r,
                          child: Text("${r}x"),
                        ))
                    .toList(),
                onChanged: (v) => setState(() => _speechRate = v!),
                decoration: const InputDecoration(
                  labelText: "TỐC ĐỘ",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.speed),
                ),
              ),
              const SizedBox(height: 16),

              // TEXT
              TextField(
                controller: controller,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: "Nhập văn bản tiếng Việt",
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.text_fields),
                ),
              ),
              const SizedBox(height: 20),

              // TEXT BUTTON
              SizedBox(
                height: 48,
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _handleSpeak,
                  icon: const Icon(Icons.auto_fix_high),
                  label: const Text("XỬ LÝ VĂN BẢN"),
                ),
              ),
              const SizedBox(height: 12),

              // FILE BUTTON
              SizedBox(
                height: 48,
                child: OutlinedButton.icon(
                  onPressed: _isLoading ? null : _handleUploadFile,
                  icon: const Icon(Icons.upload_file),
                  label: const Text("UPLOAD PDF / WORD"),
                ),
              ),
              const SizedBox(height: 24),

              // CONTROLS
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  IconButton(
                    icon: const Icon(Icons.replay_5),
                    iconSize: 32,
                    onPressed: () =>
                        tts.seekBy(const Duration(seconds: -5)),
                  ),
                  IconButton(
                    icon: Icon(_isPlaying ? Icons.pause : Icons.play_arrow),
                    iconSize: 36,
                    onPressed: () =>
                        _isPlaying ? tts.pause() : tts.resume(),
                  ),
                  IconButton(
                    icon: const Icon(Icons.forward_5),
                    iconSize: 32,
                    onPressed: () =>
                        tts.seekBy(const Duration(seconds: 5)),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
