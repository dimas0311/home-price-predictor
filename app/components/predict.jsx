import React, { useState } from "react";

const FLASK_API_URL = "http://localhost:5000/predict";

const PricePredictionComponent = () => {
  const [predictionInput, setPredictionInput] = useState({
    beds: "",
    baths: "",
    area: "",
    city: "",
  });
  const [predictedPrice, setPredictedPrice] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPredictionInput((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateInputs = () => {
    if (
      !predictionInput.beds ||
      !predictionInput.baths ||
      !predictionInput.area ||
      !predictionInput.city
    ) {
      return "All fields are required";
    }
    if (predictionInput.beds < 1 || predictionInput.baths < 1) {
      return "Beds and baths must be at least 1";
    }
    if (predictionInput.area < 100) {
      return "Area must be at least 100 sq ft";
    }
    return null;
  };

  const handlePredict = async () => {
    const validationError = validateInputs();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(FLASK_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(predictionInput),
      });

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Prediction failed");
      }

      setPredictedPrice(data.predictedPrice);
    } catch (error) {
      setError(error.message || "An error occurred");
      console.error("Prediction failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyle = {
    fontFamily: "Helvetica",
    height: "45px",
    fontSize: "26px",
  };

  return (
    <div className="w-full bg-zinc-900 rounded-lg p-6">
      <h2
        className="text-4xl font-semibold text-white mb-6"
        style={{ fontFamily: "Helvetica" }}
      >
        Predict House Price
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <input
            type="number"
            name="beds"
            value={predictionInput.beds}
            onChange={handleInputChange}
            placeholder="Number of beds"
            className="w-full bg-black text-white rounded-lg px-4 focus:outline-none focus:ring-2 focus:ring-green-400"
            style={inputStyle}
          />
          <input
            type="number"
            name="baths"
            value={predictionInput.baths}
            onChange={handleInputChange}
            placeholder="Number of baths"
            className="w-full bg-black text-white rounded-lg px-4 focus:outline-none focus:ring-2 focus:ring-green-400"
            style={inputStyle}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <input
            type="number"
            name="area"
            value={predictionInput.area}
            onChange={handleInputChange}
            placeholder="Area (sq ft)"
            className="w-full bg-black text-white rounded-lg px-4 focus:outline-none focus:ring-2 focus:ring-green-400"
            style={inputStyle}
          />
          <input
            type="text"
            name="city"
            value={predictionInput.city}
            onChange={handleInputChange}
            placeholder="City"
            className="w-full bg-black text-white rounded-lg px-4 focus:outline-none focus:ring-2 focus:ring-green-400"
            style={inputStyle}
          />
        </div>
        <button
          onClick={handlePredict}
          disabled={isLoading}
          className="w-full bg-green-400 text-black px-10 py-2 rounded-lg text-3xl font-semibold hover:bg-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ fontFamily: "Helvetica" }}
        >
          {isLoading ? "Predicting..." : "Predict Price"}
        </button>

        {predictedPrice && (
          <div className="mt-4 p-4 bg-gray-800 rounded-lg">
            <p
              className="text-2xl text-white"
              style={{ fontFamily: "Helvetica" }}
            >
              Predicted Price:{" "}
              <span className="font-semibold bg-yellow-400 text-black px-2 rounded-lg">
                ${predictedPrice.toLocaleString()}
              </span>
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default PricePredictionComponent;
