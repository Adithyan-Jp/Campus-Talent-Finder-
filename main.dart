import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(MaterialApp(
      theme: ThemeData(primarySwatch: Colors.indigo),
      home: CampusMatchHome(),
    ));

class CampusMatchHome extends StatefulWidget {
  @override
  _CampusMatchHomeState createState() => _CampusMatchHomeState();
}

class _CampusMatchHomeState extends State<CampusMatchHome> {
  List matches = [];
  bool isLoading = true;

  // 10.0.2.2 is the special alias to your laptop's localhost for Android emulators
  final String apiUrl = "http://10.0.2.2:8000/match/1";

  Future<void> fetchMatches() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        setState(() {
          matches = json.decode(response.body);
          isLoading = false;
        });
      }
    } catch (e) {
      print("Connection error: $e");
    }
  }

  @override
  void initState() {
    super.initState();
    fetchMatches();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Campus Partner Finder")),
      body: isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: matches.length,
              itemBuilder: (context, index) {
                return Card(
                  margin: EdgeInsets.all(10),
                  child: ListTile(
                    title: Text(matches[index]['Title'], 
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(matches[index]['Description']),
                    trailing: CircleAvatar(
                      backgroundColor: Colors.indigo,
                      child: Text(
                        matches[index]['matched_skills'].toString(),
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ),
                );
              },
            ),
    );
  }
}