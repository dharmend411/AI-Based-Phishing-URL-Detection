
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# 1. Load dataset
data_path = Path("dataset/PhishingData.csv/PhishingData.csv")

df = pd.read_csv(data_path)

print("Dataset loaded successfully!")
print("Original shape:", df.shape)

# 2. Clean column names
df.columns = df.columns.astype(str).str.strip()

# Remove duplicate columns, if any
df = df.loc[:, ~df.columns.duplicated()]

# 3. Remove unnecessary index column
df = df.drop(columns=["index"], errors="ignore")

# 4. Separate features and target
if "Result" not in df.columns:
    raise ValueError("Target column 'Result' not found!")

X = df.drop(columns=["Result"])
y = df["Result"]

# Convert features into numeric values
X = X.apply(pd.to_numeric, errors="coerce")

# Remove rows with missing target values
valid_rows = y.notna()
X = X.loc[valid_rows]
y = y.loc[valid_rows]

print("\nFeatures:", X.shape[1])
print("Target distribution:")
print(y.value_counts())

# 5. Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))

# 6. Create Random Forest pipeline
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("classifier", RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    ))
])

# 7. Train model
print("\nTraining model...")
model.fit(X_train, y_train)

# 8. Evaluate model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("\nModel Training Completed!")
print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    predictions,
    zero_division=0
))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

# 9. Save trained model
Path("model").mkdir(exist_ok=True)

joblib.dump(
    {
        "model": model,
        "feature_columns": X.columns.tolist(),
        "labels": {
            -1: "Phishing",
            1: "Legitimate"
        }
    },
    "model/phishing_model.pkl"
)

print("\nModel saved successfully!")
