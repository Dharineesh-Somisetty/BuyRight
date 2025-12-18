import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'api_service.dart';

class CameraScreen extends StatefulWidget {
  final List<CameraDescription> cameras;

  const CameraScreen({super.key, required this.cameras});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  final TextRecognizer _textRecognizer = TextRecognizer();
  final ApiService _apiService = ApiService();
  bool _isScanning = false;

  @override
  void initState() {
    super.initState();
    // Initialize with the first camera (rear camera usually)
    _controller = CameraController(widget.cameras.first, ResolutionPreset.high);
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() {
    _controller.dispose();
    _textRecognizer.close();
    super.dispose();
  }

  Future<void> _scanImage() async {
    if (_isScanning) return;

    try {
      setState(() {
        _isScanning = true;
      });

      String rawText = "";

      if (kIsWeb) {
        // ML Kit doesn't support Web. Simulate a scan for testing the connection.
        await Future.delayed(const Duration(seconds: 1));
        rawText = "Sugar, Whey Protein, Cocoa Butter, Milk Solids"; // Mock data
        print("Web Mode: Mocking OCR result: $rawText");
      } else {
        await _initializeControllerFuture;

        // 1. Take Picture
        final image = await _controller.takePicture();

        // 2. Create InputImage
        final inputImage = InputImage.fromFilePath(image.path);

        // 3. Process Image
        final RecognizedText recognizedText = await _textRecognizer
            .processImage(inputImage);

        rawText = recognizedText.text;
      }

      print("Extracted Text: $rawText");

      // Simple processing: Split by commas or newlines to mock ingredient list logic
      List<String> ingredients = rawText
          .split(RegExp(r'[,\n]'))
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList();

      if (ingredients.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('No text found. Try again.')),
          );
        }
        return;
      }

      // 4. API Call
      final result = await _apiService.scanProduct(ingredients, 'BULK');

      // 5. Show Feedback
      if (!mounted) return;
      _showResultSheet(result);
    } catch (e) {
      print('Error scanning: $e');
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) {
        setState(() {
          _isScanning = false;
        });
      }
    }
  }

  void _showResultSheet(Map<String, dynamic> result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true, // Allow taller sheet
      backgroundColor: Colors.black,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        final double score = (result['final_score'] as num).toDouble();
        final String verdict = result['verdict'] ?? 'Unknown';
        final List<String> goodIngredients = List<String>.from(
          result['good_ingredients'] ?? [],
        );
        final List<String> badIngredients = List<String>.from(
          result['bad_ingredients'] ?? [],
        );

        // Determine Color
        Color scoreColor = Colors.redAccent;
        if (score >= 80) {
          scoreColor = Colors.greenAccent;
        } else if (score >= 50) {
          scoreColor = Colors.orangeAccent;
        }

        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          minChildSize: 0.4,
          maxChildSize: 0.9,
          expand: false,
          builder: (context, scrollController) {
            return Padding(
              padding: const EdgeInsets.all(24.0),
              child: ListView(
                controller: scrollController,
                children: [
                  // 1. Score Circle
                  Center(
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: scoreColor, width: 4),
                        color: Colors.grey[900],
                      ),
                      child: Center(
                        child: Text(
                          score.toStringAsFixed(0),
                          style: TextStyle(
                            color: scoreColor,
                            fontSize: 48,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  // 2. Verdict
                  Text(
                    verdict,
                    style: TextStyle(
                      color: scoreColor,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 32),

                  // 3. Good Ingredients
                  if (goodIngredients.isNotEmpty) ...[
                    const Text(
                      'The Good Stuff',
                      style: TextStyle(
                        color: Colors.green,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...goodIngredients.map(
                      (ing) => ListTile(
                        leading: const Icon(
                          Icons.check_circle,
                          color: Colors.green,
                          size: 20,
                        ),
                        title: Text(
                          ing,
                          style: const TextStyle(color: Colors.white70),
                        ),
                        contentPadding: EdgeInsets.zero,
                        dense: true,
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],

                  // 4. Bad Ingredients
                  if (badIngredients.isNotEmpty) ...[
                    const Text(
                      'Watch Out',
                      style: TextStyle(
                        color: Colors.redAccent,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    ...badIngredients.map(
                      (ing) => ListTile(
                        leading: const Icon(
                          Icons.warning,
                          color: Colors.redAccent,
                          size: 20,
                        ),
                        title: Text(
                          ing,
                          style: const TextStyle(color: Colors.white70),
                        ),
                        contentPadding: EdgeInsets.zero,
                        dense: true,
                      ),
                    ),
                    const SizedBox(height: 24),
                  ],

                  if (goodIngredients.isEmpty && badIngredients.isEmpty)
                    const Text(
                      "No key ingredients identified.",
                      style: TextStyle(color: Colors.grey),
                      textAlign: TextAlign.center,
                    ),

                  const SizedBox(height: 32),
                  ElevatedButton(
                    onPressed: () => Navigator.pop(context),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: scoreColor,
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text(
                      'Close',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan Ingredients'),
        backgroundColor: Colors.black,
        foregroundColor: Colors.greenAccent,
      ),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return Stack(
              children: [
                // Camera Preview
                Positioned.fill(child: CameraPreview(_controller)),

                // Scan Button
                Positioned(
                  bottom: 32,
                  left: 0,
                  right: 0,
                  child: Center(
                    child: _isScanning
                        ? const CircularProgressIndicator(
                            color: Colors.greenAccent,
                          )
                        : FloatingActionButton.extended(
                            onPressed: _scanImage,
                            backgroundColor: Colors.greenAccent,
                            label: const Text(
                              'SCAN',
                              style: TextStyle(
                                color: Colors.black,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            icon: const Icon(
                              Icons.camera_alt,
                              color: Colors.black,
                            ),
                          ),
                  ),
                ),
              ],
            );
          } else {
            return const Center(
              child: CircularProgressIndicator(color: Colors.greenAccent),
            );
          }
        },
      ),
    );
  }
}
