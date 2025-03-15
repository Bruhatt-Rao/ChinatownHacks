import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load dataset
df = pd.read_csv("fake_chinatown_restaurant_data.csv")

# Separate features and target
# Drop non-feature columns (business name and target)
X = df.drop(columns=["Business Name", "Business Type", "Expansion Status"])
y = df["Expansion Status"]

# Scale numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save the scaler
joblib.dump(scaler, "scaler.pkl")
print("Scaler saved successfully!")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train classifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Save the trained model
joblib.dump(clf, "chinatown_business_classifier.pkl")
print("Model saved successfully!")

# Make predictions and evaluate
y_pred = clf.predict(X_test)
print("\nModel Evaluation:")
print("----------------")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred))

# Print feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': clf.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
print("------------------")
print(feature_importance)
