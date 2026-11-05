
from flask import Flask, render_template, request, send_file
import joblib
import pandas as pd
import csv
import os
from datetime import datetime

from feature_extraction import extract_features

app = Flask(__name__)

# Load trained model
saved_data = joblib.load("model/url_phishing_model.pkl")
model = saved_data["model"]
feature_columns = saved_data["feature_columns"]
performance = saved_data["performance"]

# History file path
HISTORY_FILE = "history.csv"


# Save scan history
def save_history(url, prediction, confidence):
    file_exists = os.path.isfile(HISTORY_FILE)

    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists or os.path.getsize(HISTORY_FILE) == 0:
            writer.writerow([
                "Date",
                "URL",
                "Prediction",
                "Confidence"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            url,
            prediction,
            confidence
        ])


# Homepage and URL detection
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    submitted_url = ""

    if request.method == "POST":
        submitted_url = request.form.get("url", "").strip()

        try:
            if not submitted_url:
                raise ValueError("Please enter a URL.")

            features = extract_features(submitted_url)

            input_data = pd.DataFrame(
                [[features[col] for col in feature_columns]],
                columns=feature_columns
            )

            prediction = int(model.predict(input_data)[0])

            probabilities = model.predict_proba(input_data)[0]
            confidence = round(
                float(probabilities[prediction]) * 100, 2
            )

            if prediction == 1:
                prediction_label = "Phishing"
                result = (
                    f"Warning: This URL may be Phishing! "
                    f"(Confidence: {confidence}%)"
                )
            else:
                prediction_label = "Legitimate"
                result = (
                    f"This URL is predicted to be Legitimate. "
                    f"(Confidence: {confidence}%)"
                )

            save_history(
                submitted_url,
                prediction_label,
                confidence
            )

        except Exception as error:
            result = f"Error: {error}"

    return render_template(
        "index.html",
        result=result,
        submitted_url=submitted_url
    )


# Prediction history page
@app.route("/history")
def history():
    records = []

    if os.path.exists(HISTORY_FILE):
        with open(
            HISTORY_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            records = list(reader)

    return render_template(
        "history.html",
        records=records
    )


# Dashboard page
@app.route("/dashboard")
def dashboard():
    records = []

    if os.path.exists(HISTORY_FILE):
        with open(
            HISTORY_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:
            reader = csv.DictReader(file)
            records = list(reader)

    total_scans = len(records)

    phishing_count = sum(
        1 for record in records
        if record["Prediction"] == "Phishing"
    )

    legitimate_count = sum(
        1 for record in records
        if record["Prediction"] == "Legitimate"
    )

    if total_scans > 0:
        legitimate_percentage = round(
            (legitimate_count / total_scans) * 100, 2
        )
        phishing_percentage = round(
            (phishing_count / total_scans) * 100, 2
        )
    else:
        legitimate_percentage = 0
        phishing_percentage = 0

    recent_records = records[-5:][::-1]

    return render_template(
        "dashboard.html",
        total_scans=total_scans,
        phishing_count=phishing_count,
        legitimate_count=legitimate_count,
        legitimate_percentage=legitimate_percentage,
        phishing_percentage=phishing_percentage,
        recent_records=recent_records,
        performance=performance
    )


# Export scan history as CSV
@app.route("/export-history")
def export_history():

    if not os.path.exists(HISTORY_FILE):
        return "No scan history available to export.", 404

    if os.path.getsize(HISTORY_FILE) == 0:
        return "Scan history is empty.", 404

    return send_file(
        HISTORY_FILE,
        mimetype="text/csv",
        as_attachment=True,
        download_name="Phishing_Scan_History.csv"
    )


# Run Flask application
if __name__ == "__main__":
    app.run(debug=True)
