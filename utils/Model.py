import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor
import joblib

# Load the data from the CSV file
data = pd.read_csv("./selected_house_data.csv")

# Convert the 'price' column to numeric
data['price'] = data['price'].replace('[$,]', '', regex=True).astype(float)

# Preprocess the data (handle missing values, encode categorical variables, etc.)

# Define features and target variable
X = data[['beds', 'baths', 'area']]  # Features
y = data['price']  # Target variable

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Initialize the XGBoost Regressor
model = XGBRegressor()

print("Training the model...")
# Train the model
model.fit(X_train, y_train)
print("Model training completed.")

# Save the trained model
joblib.dump(model, 'house_price_prediction_model.pkl')
print("Model saved as house_price_prediction_model.pkl.")
