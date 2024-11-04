<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Home Price Predictor - README</title>
</head>
<body>

<h1>Home Price Predictor</h1>
<p>A machine learning-based web application that predicts home prices based on input features such as location, size, number of bedrooms and bathrooms..</p>

<h2>Table of Contents</h2>
<ol>
  <li><a href="#features">Features</a></li>
  <li><a href="#demo">Demo</a></li>
  <li><a href="#installation">Installation</a></li>
  <li><a href="#usage">Usage</a></li>
  <li><a href="#model-training">Model Training</a></li>
  <li><a href="#data">Data</a></li>
  <li><a href="#technologies-used">Technologies Used</a></li>
  <li><a href="#contributing">Contributing</a></li>
  <li><a href="#license">License</a></li>
</ol>

<h2 id="features">Features</h2>
<ul>
  <li>Predicts home prices based on key factors like location, size, and amenities.</li>
  <li>Web-based interface for easy user input and prediction display.</li>
  <li>Trained on real home price data, ensuring a high level of accuracy.</li>
  <li>Interactive visualizations of the predicted prices against actual market values.</li>
  <li>Search favorite home on specific location by Mapbox.</li>
</ul>

<h2 id="demo">Demo</h2>
<p>To see a live demo of the application, visit <a href="https://home-pirce-predictor-web.vercel.app">here</a>.</p>

<h2 id="installation">Installation</h2>
<h3>Prerequisites</h3>
<ul>
  <li>Python 3.8+</li>
  <li><a href="https://scikit-learn.org/">scikit-learn</a></li>
  <li>Flask (for web app deployment)</li>
</ul>

<h3>Steps</h3>
<ol>
  <li>Clone this repository:
    <pre><code>git clone https://github.com/home-price-predictor.git
cd home-price-predictor
</code></pre>
  </li>
  <li>Install the dependencies:
    <pre><code>pip install -r requirements.txt
</code></pre>
  </li>
  <li>Set up your Hugging Face API credentials if needed.</li>
  <li>Run the application locally:
    <pre><code>python app.py
</code></pre>
  </li>
  <li>Open your browser and navigate to <code>http://localhost:5000</code> to use the app.</li>
</ol>

<h2 id="usage">Usage</h2>
<ol>
  <li>Enter the location, size, and other relevant details for the property.</li>
  <li>Click <strong>Predict</strong> to get an estimated home price.</li>
</ol>

<h2 id="model-training">Model Training</h2>
<p>The model is trained using a dataset of over 200k home prices. It uses features such as:</p>
<ul>
  <li>Location (e.g., city, neighborhood)</li>
  <li>Size</li>
  <li>Number of bedrooms and bathrooms</li>
</ul>

<h2 id="data">Data</h2>
<p>The data used in this project includes:</p>
<ul>
  <li>Home price dataset sourced from redfin, realestate and jamesedition</li>
  <li>Additional neighborhood information for better location-based predictions</li>
</ul>
<p>The data is preprocessed and split into training and testing sets.</p>

<h2 id="technologies-used">Technologies Used</h2>
<ul>
  <li><strong>Flask</strong>: Web framework for building the app</li>
  <li><strong>scikit-learn</strong>: Machine learning algorithms and evaluation metrics</li>
  <li><strong>pandas</strong>: Data manipulation and cleaning</li>
  <li><strong>matplotlib/plotly</strong>: Data visualization</li>
</ul>

<h2 id="contributing">Contributing</h2>
<p>Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.</p>

<h2 id="license">License</h2>
<p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>

</body>
</html>
