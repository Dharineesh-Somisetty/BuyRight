import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiService {
  // Use 10.0.2.2 for Android emulator, 127.0.0.1 for iOS/Web
  String get baseUrl {
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    // Simple check: if not web, assume Android for this demo or fallback to localhost for iOS
    // Ideally we check Platform.isAndroid but dart:io breaks web builds.
    // For a robust solution we'd use conditional imports, but for this demo let's assume
    // if not web, try 10.0.2.2 (Android Emulator) primarily.
    return 'http://10.0.2.2:8000';
  }

  Future<Map<String, dynamic>> scanProduct(
    List<String> ingredients,
    String mode,
  ) async {
    final url = Uri.parse('$baseUrl/scan');

    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'ingredients': ingredients, 'mode': mode}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to load score: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error connecting to backend: $e');
    }
  }

  Future<Map<String, dynamic>> fetchProductByBarcode(String barcode) async {
    final url = Uri.parse('$baseUrl/product/$barcode');
    try {
      final response = await http.get(url);
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Product not found or error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching product: $e');
    }
  }
}
