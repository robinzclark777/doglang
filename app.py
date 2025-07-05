# doglang_webapp/app.py
from flask import Flask, request, render_template, redirect, url_for
import whisper
import os
import uuid
import string
from collections import Counter

app = Flask(__name__)
model = whisper.load_model("base")

CUES = {"sit", "down", "wait", "come", "here", "place", "circle", "spin", "stand"}
REWARD_MARKERS = {"yes", "good"}
NO_REWARD_MARKERS = {"nope", "uh", "uh uh", "wrong", "try again"}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audio"]
        if not file:
            return redirect(url_for("index"))

        filename = f"{uuid.uuid4()}.m4a"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        result = model.transcribe(filepath, language="en")
        text = result["text"]
        report = analyze_transcript(text)

        return render_template("report.html", text=text, report=report)

    return render_template("index.html")

def analyze_transcript(text):
    clean = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
    report = Counter()
    for word in clean:
        if word in CUES:
            report["commands"] += 1
        elif word in REWARD_MARKERS:
            report["reward_markers"] += 1
        elif word in NO_REWARD_MARKERS:
            report["no_reward_markers"] += 1
        else:
            report["unknown"] += 1
    return report

if __name__ == "__main__":
    app.run(debug=True)
