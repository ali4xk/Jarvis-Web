from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

def handle_command(command):
    command = command.lower().strip()

    if "what time" in command or "current time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {current_time}"

    return "I did not understand that command"

@app.route("/api/command", methods=["POST"])
def process_command():
    data = request.get_json()
    command = data.get("command", "")

    if not command:
        return jsonify({"error": "No command provided"}), 400

    response = handle_command(command)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)