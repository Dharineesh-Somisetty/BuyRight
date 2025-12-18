import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'camera_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Fetch available cameras
  // We wrap this in a try-catch to handle platforms without cameras (like simulator sometimes) gracefully-ish
  List<CameraDescription> cameras = [];
  try {
    cameras = await availableCameras();
  } on CameraException catch (e) {
    debugPrint('Error: $e.code\nError Message: $e.description');
  }

  runApp(ApexScannerApp(cameras: cameras));
}

class ApexScannerApp extends StatelessWidget {
  final List<CameraDescription> cameras;

  const ApexScannerApp({super.key, required this.cameras});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Apex Scanner',
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.black,
        scaffoldBackgroundColor: Colors.black,
        colorScheme: const ColorScheme.dark(
          primary: Colors.greenAccent,
          secondary: Colors.green,
        ),
        useMaterial3: true,
      ),
      home: cameras.isNotEmpty
          ? CameraScreen(cameras: cameras)
          : const Scaffold(body: Center(child: Text("No cameras found"))),
    );
  }
}
