from flask import Flask, render_template, request, redirect, url_for
from gtts import gTTS
import os
import json
import uuid

app = Flask(__name__)
DATA_FILE = "hearthstone_data.json"
AUDIO_FOLDER = "static/audio"
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Load or create data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "parent_name": "Mom/Dad",
        "memories_stories": [],
        "life_lessons": {},
        "advice_scenarios": {},
        "comfort_phrases": ["I'm here for you.", "It's okay to feel this way.", "You're strong and you'll get through this."]
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def speak(text):
    tts = gTTS(text=text)
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)
    tts.save(filepath)
    return f"/static/audio/{filename}"

@app.route("/")
def index():
    data = load_data()
    return render_template("index.html", data=data)

@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    item_type = request.form["type"]
    if item_type == "memory":
        title = request.form["title"]
        content = request.form["content"]
        data["memories_stories"].append({"title": title, "content": content})
    elif item_type == "lesson":
        topic = request.form["topic"].lower()
        lesson = request.form["content"]
        data["life_lessons"][topic] = lesson
    elif item_type == "advice":
        trigger = request.form["trigger"].lower()
        advice = request.form["content"]
        data["advice_scenarios"][trigger] = advice
    elif item_type == "comfort":
        phrase = request.form["content"]
        data["comfort_phrases"].append(phrase)
    save_data(data)
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    data = load_data()
    mode = request.form["mode"]
    response = "I don't know how to answer that."
    if mode == "story":
        if data["memories_stories"]:
            story = data["memories_stories"][-1]
            response = f"Here's a story: {story['title']}. {story['content']}"
    elif mode == "lesson":
        if data["life_lessons"]:
            topic, lesson = next(iter(data["life_lessons"].items()))
            response = f"About {topic}, I remember being taught: {lesson}"
    elif mode == "advice":
        if data["advice_scenarios"]:
            trigger, advice = next(iter(data["advice_scenarios"].items()))
            response = advice
    elif mode == "comfort":
        if data["comfort_phrases"]:
            response = data["comfort_phrases"][-1]
    audio_path = speak(response)
    return render_template("response.html", response=response, audio_path=audio_path)

if __name__ == "__main__":
    app.run(debug=True)