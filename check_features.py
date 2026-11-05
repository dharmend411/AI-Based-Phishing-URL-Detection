import pandas as pd
from feature_extraction import extract_features

df = pd.read_csv("dataset/Dataset.csv")

feature_columns = [
    col for col in df.columns
    if col not in ["url", "dom", "tld", "label"]
]

sample = df.head(100)
match_count = {col: 0 for col in feature_columns}
valid_rows = 0

for _, row in sample.iterrows():
    try:
        extracted = extract_features(str(row["url"]))
        valid_rows += 1

        for col in feature_columns:
            actual = float(row[col])
            calculated = float(extracted[col])

            if abs(actual - calculated) < 0.000001:
                match_count[col] += 1

    except Exception:
        continue

print("Valid URLs checked:", valid_rows)
print("\nFeature matching results:")

for col, count in match_count.items():
    print(f"{col}: {count}/{valid_rows}")

print(
    "\nTotal exact feature matches:",
    sum(match_count.values()),
    "/",
    len(feature_columns) * valid_rows
)