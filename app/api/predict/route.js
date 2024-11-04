import { NextResponse } from "next/server";
import path from "path";
import joblib from "joblib-node";

export async function POST(req) {
  try {
    const body = await req.json();
    const { beds, baths, area, city } = body;

    // Load the model
    const modelPath = path.join(
      process.cwd(),
      "public",
      "models",
      "house_price_prediction_model.pkl"
    );
    const model = await joblib.load(modelPath);

    // Prepare input data
    const inputData = {
      beds: parseFloat(beds),
      baths: parseFloat(baths),
      area: parseFloat(area),
    };

    // Make prediction
    const prediction = await model.predict([
      [inputData.beds, inputData.baths, inputData.area],
    ]);

    return NextResponse.json({
      predictedPrice: prediction[0],
      success: true,
    });
  } catch (error) {
    console.error("Prediction error:", error);
    return NextResponse.json(
      {
        error: "Failed to make prediction",
        success: false,
      },
      { status: 500 }
    );
  }
}
