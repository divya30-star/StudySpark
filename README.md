# StudySpark — Quiz & Flashcard Learning Platform

A beginner-friendly Python mini project built with Flask, SQLite, HTML, CSS and JavaScript.

## Features
- User registration, login and logout
- Password hashing
- Quiz questions loaded from SQLite
- Server-side quiz scoring
- Quiz attempt history and average score
- Flashcards with flip, previous and next
- Add personal flashcards
- JSON API routes using GET, POST and DELETE

## 1. Install Python and VS Code
Install Python 3.10 or newer and Visual Studio Code. During Python installation on Windows, select "Add Python to PATH".

## 2. Open the project
Extract the ZIP file. In VS Code choose File → Open Folder and select `quiz_flashcard_platform`.

## 3. Create a virtual environment

Windows:
```bash
py -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install packages
```bash
pip install -r requirements.txt
```

## 5. Run the website
```bash
python app.py
```
If `python` does not work on Windows, try `py app.py`.

Open http://127.0.0.1:5000 in your browser.

The SQLite database `platform.db` is created automatically on first run and populated with a sample Python quiz and sample flashcards.

## 6. Try the project
1. Click Sign up and create an account.
2. Log in.
3. Open the Python Basics quiz and answer all questions.
4. Submit and view your score.
5. Open Dashboard to see your attempt history.
6. Open Flashcards, flip the sample cards and add your own.

## 7. API routes to demonstrate

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/quizzes` | List available quizzes |
| GET | `/api/quiz/1` | Get questions for quiz 1 (login required) |
| POST | `/api/submit` | Submit answers and calculate score (login required) |
| GET | `/api/flashcards` | Get available flashcards (login required) |
| POST | `/api/flashcards` | Add a personal flashcard (login required) |
| DELETE | `/api/flashcards/ID` | Delete your own flashcard |
| GET | `/api/my-stats` | Get your quiz statistics |

Example POST body for `/api/submit`:
```json
{
  "quiz_id": 1,
  "answers": {
    "1": "B",
    "2": "C"
  }
}
```

Example POST body for `/api/flashcards`:
```json
{
  "subject": "Physics",
  "front": "What is wavelength?",
  "back": "The distance between two successive points in the same phase."
}
```

## 8. Important notes before deployment
- This is a learning/demo project. Add CSRF protection, rate limiting, stronger validation and production logging before public use.
- Do not deploy with the default SECRET_KEY. Set a long random `SECRET_KEY` environment variable on your hosting provider.
- For a hosted production app, use a persistent database/storage solution. The local SQLite file may not persist on some free hosting instances.
- Run with Flask's development server only on your own computer, not as a public production server.
