# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load the model
model = joblib.load('./utils/house_price_prediction_model.pkl')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        input_data = pd.DataFrame({
            'beds': [float(data['beds'])],
            'baths': [float(data['baths'])],
            'area': [float(data['area'])],

        })

        prediction = model.predict(input_data)[0]

        return jsonify({
            'success': True,
            'predictedPrice': float(prediction)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(port=5000)
