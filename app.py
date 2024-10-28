from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)

# Load and prepare the dataset
data = pd.read_csv('winequality-red.csv', delimiter=';')
X = data.drop('quality', axis=1)
y = data['quality']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/predict', methods=['POST'])
def predict_wine_quality():
    data = request.json
    input_data = np.array([[
        float(data['fixed-acidity']),
        float(data['volatile-acidity']),
        float(data['citric-acid']),
        float(data['residual-sugar']),
        float(data['chlorides']),
        float(data['free-sulfur-dioxide']),
        float(data['total-sulfur-dioxide']),
        float(data['density']),
        float(data['ph']),
        float(data['sulphates']),
        float(data['alcohol'])
    ]])

    # Scale the input data
    input_data_scaled = scaler.transform(input_data)

    # Make prediction
    predicted_quality = model.predict(input_data_scaled)[0]

    # Calculate confidence (using R-squared score as a proxy)
    confidence = model.score(X_test_scaled, y_test)

    return jsonify({
        'predictedQuality': float(predicted_quality),
        'confidence': float(confidence)
    })

if __name__ == '_main_':
    app.run(debug=True)
    