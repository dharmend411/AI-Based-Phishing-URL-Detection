
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

# Load dataset
df = pd.read_csv("dataset/Dataset.csv")

# Select numerical features
feature_columns = [
    col for col in df.columns
    if col not in ["url", "dom", "tld", "label"]
]

X = df[feature_columns].apply(pd.to_numeric, errors="coerce")
y = df["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Create model
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    ))
])

# Train model
print("Training started...")
model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)

# Calculate performance metrics
accuracy = accuracy_score(y_test, predictions) * 100

precision = precision_score(
    y_test, predictions, zero_division=0
) * 100

recall = recall_score(
    y_test, predictions, zero_division=0
) * 100

f1 = f1_score(
    y_test, predictions, zero_division=0
) * 100

print("\nModel Performance:")
print("Accuracy:", round(accuracy, 2), "%")
print("Precision:", round(precision, 2), "%")
print("Recall:", round(recall, 2), "%")
print("F1-Score:", round(f1, 2), "%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    target_names=["Legitimate", "Phishing"]
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# Save model and performance metrics
joblib.dump({
    "model": model,
    "feature_columns": feature_columns,
    "performance": {
        "accuracy": round(accuracy, 2),
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1_score": round(f1, 2)
    }
}, "model/url_phishing_model.pkl")

print("\nURL Phishing Model saved successfully!")
