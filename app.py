# doglang_webapp/app.py
from flask import Flask, request, render_template, redirect, url_for
import whisper
import os
import uuid
import string
from collections import Counter

app = Flask(__name__)
model = whisper.load_model("base")

CUES = {"sit", "down", "wait", "come", "here", "place", "spin", "circle"}
REWARD_MARKERS = {"yes", "good", "get it", "strike"}
NO_REWARD_MARKERS = {"no"}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["audio"]
        if not file:
            return redirect(url_for("index"))

        filename = f"{uuid.uuid4()}.webm"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        result = model.transcribe(filepath, language="en")
        text = result.get("text", "").strip()
        if not text:
            return render_template("report.html", words_with_tags=[], report={})

        words_with_tags, report = analyze_transcript(text)
                # pad report keys before render
        for key in ["commands", "reward_markers", "no_reward_markers", "unknown"]:
            report.setdefault(key, 0)

        return render_template("report.html", words_with_tags=words_with_tags, report=report)

    return render_template("index.html")

def analyze_transcript(text):
    clean = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
    words_with_tags = []
    report = Counter()

    for word in clean:
        if word in CUES:
            tag = "cue"
            report["commands"] += 1
        elif word in REWARD_MARKERS:
            tag = "reward"
            report["reward_markers"] += 1
        elif word in NO_REWARD_MARKERS:
            tag = "no_reward"
            report["no_reward_markers"] += 1
        else:
            tag = "unknown"
            report["unknown"] += 1
        words_with_tags.append((word, tag))
    return words_with_tags, report

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
