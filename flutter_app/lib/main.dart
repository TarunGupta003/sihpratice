import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';

const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:8000',
);

void main() {
  runApp(const OrcaApp());
}

class OrcaApp extends StatelessWidget {
  const OrcaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ORCA Fisher',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xff006d77),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xfff4f7f5),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class OrcaApi {
  Future<Map<String, dynamic>> get(String path) async {
    final client = HttpClient();
    try {
      final request = await client.getUrl(Uri.parse('$apiBaseUrl$path'));
      request.headers.set(HttpHeaders.acceptHeader, 'application/json');
      final response = await request.close();
      final body = await response.transform(utf8.decoder).join();
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw Exception('Server returned ${response.statusCode}');
      }
      return jsonDecode(body) as Map<String, dynamic>;
    } finally {
      client.close(force: true);
    }
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final api = OrcaApi();
  Map<String, dynamic>? advisory;
  Map<String, dynamic>? health;
  String? error;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final results = await Future.wait([
        api.get('/api/v1/advisory?lat=20.9&lon=70.37'),
        api.get('/api/v1/health'),
      ]);
      if (!mounted) return;
      setState(() {
        advisory = results[0];
        health = results[1];
        loading = false;
      });
    } catch (exception) {
      if (!mounted) return;
      setState(() {
        error = 'Could not reach ORCA Box. Check the server address.';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final verdict = _text(advisory?['verdict'] ?? advisory?['status'], 'WAIT');
    final reason = _text(
      advisory?['plain_en'] ?? advisory?['headline_en'],
      'Connect to ORCA Box for the latest sea advisory.',
    );
    final operational = health != null;

    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('ORCA', style: TextStyle(fontWeight: FontWeight.w800)),
            Text('Fisher safety desk', style: TextStyle(fontSize: 12)),
          ],
        ),
        actions: [
          IconButton(
            onPressed: loading ? null : refresh,
            tooltip: 'Refresh advisory',
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: refresh,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
          children: [
            Text('VERAVAL HARBOUR', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Card(
              elevation: 0,
              color: _verdictColor(verdict).withAlpha(28),
              child: Padding(
                padding: const EdgeInsets.all(22),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('CAN I GO?', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 10),
                    if (loading)
                      const Center(child: CircularProgressIndicator())
                    else
                      Text(
                        verdict.toUpperCase(),
                        style: TextStyle(
                          color: _verdictColor(verdict),
                          fontSize: 38,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 0,
                        ),
                      ),
                    const SizedBox(height: 10),
                    Text(reason, style: Theme.of(context).textTheme.bodyLarge),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 14),
            if (error != null)
              Card(
                elevation: 0,
                color: const Color(0xffffeadf),
                child: ListTile(
                  leading: const Icon(Icons.cloud_off, color: Color(0xffa8441f)),
                  title: Text(error!),
                  subtitle: Text('API: $apiBaseUrl'),
                  trailing: IconButton(onPressed: refresh, icon: const Icon(Icons.refresh)),
                ),
              ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _InfoTile(icon: Icons.waves, label: 'Sea check', value: operational ? 'Updated' : 'Offline')),
                const SizedBox(width: 12),
                Expanded(child: _InfoTile(icon: Icons.location_on_outlined, label: 'Location', value: '20.90, 70.37')),
              ],
            ),
            const SizedBox(height: 20),
            Text('Before you leave', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 10),
            const _SafetyRow(icon: Icons.wb_sunny_outlined, text: 'Check the latest advisory at the harbour.'),
            const _SafetyRow(icon: Icons.phone_outlined, text: 'Carry a charged phone and life jacket.'),
            const _SafetyRow(icon: Icons.groups_outlined, text: 'Tell someone your route and return time.'),
          ],
        ),
      ),
    );
  }

  String _text(Object? value, String fallback) => value?.toString().trim().isNotEmpty == true ? value.toString() : fallback;

  Color _verdictColor(String value) {
    final lower = value.toLowerCase();
    if (lower.contains('go') || lower.contains('safe') || lower.contains('operational')) return const Color(0xff087f5b);
    if (lower.contains('no') || lower.contains('danger') || lower.contains('avoid')) return const Color(0xffb42318);
    return const Color(0xffa15c00);
  }
}

class _InfoTile extends StatelessWidget {
  const _InfoTile({required this.icon, required this.label, required this.value});
  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Card(
        elevation: 0,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Icon(icon, color: Theme.of(context).colorScheme.primary),
            const SizedBox(height: 10),
            Text(label, style: Theme.of(context).textTheme.labelMedium),
            const SizedBox(height: 3),
            Text(value, style: const TextStyle(fontWeight: FontWeight.w700)),
          ]),
        ),
      );
}

class _SafetyRow extends StatelessWidget {
  const _SafetyRow({required this.icon, required this.text});
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) => ListTile(
        contentPadding: EdgeInsets.zero,
        leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
        title: Text(text),
      );
}
