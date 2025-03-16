import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Load dataset
print("Loading and preprocessing data...")
df = pd.read_csv("updated_chinatown_restaurant_data.csv")

# Ensure column names match exactly with sample_data.json
expected_columns = [
    'Years in Business',
    'Annual Revenue (3 Years Ago)',
    'Annual Revenue (2 Years Ago)',
    'Annual Revenue (Last Year)',
    'Review Rating',
    'Number of Reviews',
    'Social Media Followers',
    'Competitor Density',
    'Lease Price',
    'Market Demand Score'
]

# Verify all required columns exist
missing_columns = set(expected_columns) - set(df.columns)
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Select features for the model
feature_columns = [
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

# Prepare features and target
X = df[feature_columns]
y = df['Market Demand Score']

# Ensure data types match sample_data.json
X = X.astype({
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
print("Scaling features...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save the scaler
joblib.dump(scaler, "scaler.pkl")
print("Scaler saved successfully!")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train regressor
print("\nTraining Random Forest Regressor...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=2,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42
)
model.fit(X_train, y_train)

# Save the trained model
joblib.dump(model, "chinatown_business_model.pkl")
print("Model saved successfully!")

# Make predictions and evaluate
y_pred = model.predict(X_test)
print("\nModel Evaluation:")
print("----------------")
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")
print(f"R² Score: {r2_score(y_test, y_pred):.2f}")

# Print feature importance
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
print("------------------")
print(feature_importance)

# Save feature importance plot
try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 6))
    plt.bar(feature_importance['feature'], feature_importance['importance'])
    plt.xticks(rotation=45, ha='right')
    plt.title('Feature Importance in Predicting Market Demand Score')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    print("\nFeature importance plot saved as 'feature_importance.png'")
except:
    print("\nCouldn't save feature importance plot (matplotlib might not be installed)")

# Save feature columns for prediction
import json
with open('feature_columns.json', 'w') as f:
    json.dump(feature_columns, f)