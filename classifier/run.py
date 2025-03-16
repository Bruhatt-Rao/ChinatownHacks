import json
import pandas as pd
import joblib
import os

# Define required features at module level
REQUIRED_FEATURES = [
    'Years in Business',
    'Annual Revenue (3 Years Ago)',
    'Annual Revenue (2 Years Ago)',
    'Annual Revenue (Last Year)',
    'Review Rating',
    'Number of Reviews',
    'Social Media Followers',
    'Competitor Density',
    'Lease Price'
]

def load_model():
    """Load the trained model and scaler."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model = joblib.load(os.path.join(current_dir, "chinatown_business_model.pkl"))
        scaler = joblib.load(os.path.join(current_dir, "scaler.pkl"))
        with open(os.path.join(current_dir, 'feature_columns.json'), 'r') as f:
            feature_columns = json.load(f)
        return model, scaler, feature_columns
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"Looking in directory: {current_dir}")
        raise Exception("Model files not found. Please run train.py first.") from e

def predict_from_json(json_data):
    """Predict market demand score from JSON input."""
    model, scaler, feature_columns = load_model()
    
    # Convert JSON to DataFrame with specific features
    try:
        df_input = pd.DataFrame([json_data])[feature_columns]
        
        # Ensure correct data types
        df_input = df_input.astype({
            'Years in Business': int,
            'Annual Revenue (3 Years Ago)': float,
            'Annual Revenue (2 Years Ago)': float,
            'Annual Revenue (Last Year)': float,
            'Review Rating': int,
            'Number of Reviews': int,
            'Social Media Followers': int,
            'Competitor Density': int,
            'Lease Price': int
        })
        
        # Scale features
        df_input_scaled = scaler.transform(df_input)
        
        # Make prediction
        prediction = model.predict(df_input_scaled)[0]
        
        return {
            "market_demand_score": round(prediction, 1)
        }
        
    except KeyError as e:
        missing_features = set(feature_columns) - set(json_data.keys())
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        raise e
    except Exception as e:
        raise Exception(f"Error processing input data: {str(e)}") from e

def validate_input(json_data):
    """Validate the input data format and types."""
    missing = set(REQUIRED_FEATURES) - set(json_data.keys())
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    
    # Validate types and ranges
    if not isinstance(json_data['Years in Business'], (int, float)) or json_data['Years in Business'] < 0:
        raise ValueError("Years in Business must be a non-negative number")
    
    for revenue_field in ['Annual Revenue (3 Years Ago)', 'Annual Revenue (2 Years Ago)', 'Annual Revenue (Last Year)']:
        if not isinstance(json_data[revenue_field], (int, float)) or json_data[revenue_field] < 0:
            raise ValueError(f"{revenue_field} must be a non-negative number")
    
    if not (0 <= json_data['Review Rating'] <= 5):
        raise ValueError("Review Rating must be between 0 and 5")
    
    if not isinstance(json_data['Number of Reviews'], (int, float)) or json_data['Number of Reviews'] < 0:
        raise ValueError("Number of Reviews must be a non-negative number")
        
    if not isinstance(json_data['Social Media Followers'], (int, float)) or json_data['Social Media Followers'] < 0:
        raise ValueError("Social Media Followers must be a non-negative number")
        
    if not isinstance(json_data['Competitor Density'], (int, float)) or json_data['Competitor Density'] < 0:
        raise ValueError("Competitor Density must be a non-negative number")
        
    if not isinstance(json_data['Lease Price'], (int, float)) or json_data['Lease Price'] < 0:
        raise ValueError("Lease Price must be a non-negative number")

def predict_from_dict(data):
    print("Received data:", data)
    print("Data types:")
    for key, value in data.items():
        print(f"{key}: {type(value)} = {value}")
    
    # Convert string values to appropriate numeric types
    numeric_fields = {
        'Years in Business': int,
        'Annual Revenue (3 Years Ago)': float,
        'Annual Revenue (2 Years Ago)': float,
        'Annual Revenue (Last Year)': float,
        'Review Rating': float,
        'Number of Reviews': int,
        'Social Media Followers': int,
        'Competitor Density': int,
        'Lease Price': float
    }
    
    for field, convert_type in numeric_fields.items():
        if field in data and isinstance(data[field], str):
            try:
                data[field] = convert_type(data[field])
            except ValueError:
                raise ValueError(f"Invalid value for {field}: {data[field]}")
    
    validate_input(data)
    return predict_from_json(data)['market_demand_score']

if __name__ == "__main__":
    try:
        # Load sample JSON input
        with open("sample_data.json", "r") as f:
            json_data = json.load(f)
        
        # Remove any non-feature fields
        json_data = {k: v for k, v in json_data.items() if k in REQUIRED_FEATURES}
        
        # Validate input
        validate_input(json_data)
        
        # Run prediction
        result = predict_from_json(json_data)
        print("\nPrediction Results:")
        print("-----------------")
        print(f"Predicted Market Demand Score: {result['market_demand_score']}")
        
    except FileNotFoundError:
        print("Error: sample_data.json not found")
    except ValueError as e:
        print(f"Error: Invalid input data - {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")