import json
import pandas as pd
import joblib

def load_model():
    """Load the trained classifier and scaler."""
    clf = joblib.load("business_classifier.pkl")
    scaler = joblib.load("scaler.pkl")
    return clf, scaler

def predict_from_json(json_data):
    """Predict business expansion status from JSON input."""
    clf, scaler = load_model()
    
    # Convert JSON to DataFrame
    df_input = pd.DataFrame([json_data])
    
    # Apply same transformations as training (scale numerical data)
    df_input_scaled = scaler.transform(df_input)
    
    # Make prediction
    prediction = clf.predict(df_input_scaled)
    
    # Map prediction to readable labels
    expansion_mapping = {0: "No Growth", 1: "Moderate Growth", 2: "High Growth/Franchise"}
    return expansion_mapping[prediction[0]]

if __name__ == "__main__":
    # Load sample JSON input
    with open("sample_data.json", "r") as f:
        json_data = json.load(f)
    
    # Run prediction
    result = predict_from_json(json_data)
    print("Predicted Expansion Status:", result)