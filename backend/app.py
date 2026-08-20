from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import requests
import json
import os
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TASKS_FILE = "tasks.json"
STOCK_SYMBOLS = ["AAPL", "TSLA", "MSFT", "NVDA", "GOOGL"]

def get_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if response.status_code != 200:
            print(f"Weather API error: {response.status_code} - {data}")
            return f"I could not find weather for {city}"
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"It is currently {temp} degrees Celsius with {description} in {city}"
    except requests.exceptions.RequestException:
        return "I could not reach the weather service"

def get_location():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()
        if data.get("status") != "success":
            return None
        return {
            "ip": data.get("query"),
            "city": data.get("city"),
            "region": data.get("regionName"),
            "country": data.get("country"),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "isp": data.get("isp")
        }
    except requests.exceptions.RequestException:
        return None

def get_stocks():
    results = []
    for symbol in STOCK_SYMBOLS:
        try:
            url = "https://finnhub.io/api/v1/quote"
            params = {"symbol": symbol, "token": FINNHUB_API_KEY}
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            current_price = data.get("c")
            prev_close = data.get("pc")

            if current_price is None or prev_close is None:
                print(f"Stock fetch issue for {symbol}: {data}")
                continue

            change = current_price - prev_close
            direction = "up" if change >= 0 else "down"

            results.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "direction": direction
            })
        except requests.exceptions.RequestException:
            continue
    return results

def get_news(country="us", page_size=5):
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {"country": country, "pageSize": page_size, "apiKey": NEWS_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("status") != "ok":
            print(f"News API error: {data}")
            return None

        articles = []
        for article in data.get("articles", []):
            title = article.get("title")
            source = article.get("source", {}).get("name")
            if title:
                articles.append({"title": title, "source": source})
        return articles
    except requests.exceptions.RequestException:
        return None

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(task_text):
    tasks = load_tasks()
    tasks.append(task_text)
    save_tasks(tasks)
    return f"Added task: {task_text}"

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        return "You have no tasks"
    if len(tasks) == 1:
        return f"You have one task: {tasks[0]}"
    return f"You have {len(tasks)} tasks: {', '.join(tasks)}"

def clear_tasks():
    save_tasks([])
    return "All tasks cleared"

FILLER_WORDS = ["today", "please", "now", "right now", "for me", "sir"]

def clean_extracted(text):
    text = text.strip().strip("?.!,")
    words = text.split()
    while words and words[-1].lower() in FILLER_WORDS:
        words.pop()
    return " ".join(words).strip()

def extract_after(command, phrases):
    for phrase in phrases:
        if phrase in command:
            result = command.split(phrase, 1)[1]
            result = clean_extracted(result)
            if result:
                return result
    return ""

def handle_command(command):
    command = command.lower().strip()

    if "hello" in command or "hey jarvis" in command or "hi jarvis" in command:
        return {"response": "Hello, how can I help you?"}

    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return {"response": f"The time is {current_time}"}

    if "search" in command or "google" in command:
        query = extract_after(command, ["search for", "search", "google"])
        if query:
            return {
                "response": f"Searching for {query}",
                "action": "open_url",
                "url": f"https://www.google.com/search?q={quote(query)}"
            }
        return {"response": "What do you want me to search for?"}

    if "weather" in command:
        city = extract_after(command, ["weather in", "weather for", "weather"])
        if city:
            return {"response": get_weather(city)}
        return {"response": "Which city do you want the weather for?"}

    if "task" in command and ("clear" in command or "delete" in command or "remove" in command):
        return {"response": clear_tasks()}

    if "task" in command and ("add" in command or "new" in command or "remind" in command):
        task_text = extract_after(command, ["add task", "add a task", "new task", "remind me to", "remind me"])
        if task_text:
            return {"response": add_task(task_text)}
        return {"response": "What is the task?"}

    if "task" in command and ("my" in command or "list" in command or "what" in command or "show" in command):
        return {"response": list_tasks()}

    return {"response": "I did not understand that command"}

@app.route("/api/weather", methods=["GET"])
def weather():
    city = request.args.get("city")

    if not city:
        location_data = get_location()
        city = location_data.get("city") if location_data else None

    if not city:
        return jsonify({"error": "Could not determine city"}), 502

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if response.status_code != 200:
            print(f"Weather API error: {response.status_code} - {data}")
            return jsonify({"error": "Could not fetch weather"}), response.status_code

        return jsonify({
            "city": data.get("name", city),
            "temperature": round(data["main"]["temp"]),
            "condition": data["weather"][0]["description"].upper(),
            "humidity": data["main"]["humidity"],
            "wind": round(data["wind"]["speed"] * 3.6)
        })
    except requests.exceptions.RequestException:
        return jsonify({"error": "Could not reach weather service"}), 502

@app.route("/api/news", methods=["GET"])
def news():
    articles = get_news()
    if articles is None:
        return jsonify({"error": "Could not fetch news"}), 502
    return jsonify({"articles": articles})

@app.route("/api/location", methods=["GET"])
def location():
    result = get_location()
    if result is None:
        return jsonify({"error": "Could not determine location"}), 502
    return jsonify(result)

@app.route("/api/stocks", methods=["GET"])
def stocks():
    return jsonify({"stocks": get_stocks()})

@app.route("/api/command", methods=["POST"])
def process_command():
    data = request.get_json()
    command = data.get("command", "")

    if not command:
        return jsonify({"error": "No command provided"}), 400

    result = handle_command(command)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)