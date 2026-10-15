# StudySprint — A Tiny Study Tracker

StudySprint is a standard-library-only command-line tool for recording study sessions in a local JSON file. It is a beginner-friendly project in data modelling, input validation, file handling, and CLI design.

## Requirements

- Python 3.10+
- No third-party packages

## Usage

    python studysprint.py add "Linux networking" 35
    python studysprint.py add "Python testing" 25 --note "Practised unittest"
    python studysprint.py list
    python studysprint.py summary

The data file defaults to studysprint.json in the current directory. Use --data PATH to select another file.

## Features

- Record a topic, duration in minutes, timestamp, and optional note
- List sessions in reverse chronological order
- Summarise total minutes and time per topic
- Validate durations and handle missing or malformed data safely

## Ideas to extend

1. Add weekly summaries.
2. Export to CSV.
3. Add goals and streaks.
4. Write unit tests for malformed JSON and invalid durations.
