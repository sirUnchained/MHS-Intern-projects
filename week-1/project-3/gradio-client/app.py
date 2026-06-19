import gradio as gr
import joblib
import numpy as np
import os
import requests

# Model URL and local filename
MODEL_URL = "https://huggingface.co/sirunchained/diabet-analysis/resolve/main/diabet-analysis.joblib?download=true"
MODEL_FILE = "diabet-analysis.joblib"


def download_model():
    """Download the model from Hugging Face if not already present."""
    if os.path.exists(MODEL_FILE):
        print(f"Model '{MODEL_FILE}' already exists locally.")
        return

    print(f"Downloading model from {MODEL_URL}...")
    try:
        response = requests.get(MODEL_URL, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(MODEL_FILE, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"Download progress: {percent:.1f}%", end="\r")

        print(f"\nModel downloaded successfully to '{MODEL_FILE}'")
    except Exception as e:
        raise RuntimeError(f"Failed to download model: {e}")


# Download the model if needed
download_model()

# Load the trained pipeline
try:
    pipeline = joblib.load(MODEL_FILE)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")


def predict_diabetes(
    pregnancies,
    glucose,
    blood_pressure,
    skin_thickness,
    insulin,
    bmi,
    diabetes_pedigree,
    age,
):
    """
    Predict diabetes outcome based on patient features.
    Returns prediction (0 or 1) and probability.
    """
    # Prepare input array in the same order as training features
    input_data = np.array(
        [
            [
                pregnancies,
                glucose,
                blood_pressure,
                skin_thickness,
                insulin,
                bmi,
                diabetes_pedigree,
                age,
            ]
        ]
    )

    # Predict class and probabilities
    prediction = pipeline.predict(input_data)[0]
    probabilities = pipeline.predict_proba(input_data)[0]

    # Format output
    outcome = "Diabetic" if prediction == 1 else "Non-Diabetic"
    confidence = probabilities[prediction] * 100

    return {
        "Prediction": outcome,
        "Confidence (%)": round(confidence, 2),
        "Probability (Non-Diabetic)": round(probabilities[0], 4),
        "Probability (Diabetic)": round(probabilities[1], 4),
    }


# Define input components
inputs = [
    gr.Number(label="Pregnancies", value=1),
    gr.Number(label="Glucose (mg/dL)", value=120),
    gr.Number(label="Blood Pressure (mm Hg)", value=70),
    gr.Number(label="Skin Thickness (mm)", value=20),
    gr.Number(label="Insulin (mu U/ml)", value=80),
    gr.Number(label="BMI (kg/m²)", value=30.0),
    gr.Number(label="Diabetes Pedigree Function", value=0.5),
    gr.Number(label="Age (years)", value=30),
]

# Output components
outputs = [gr.Label(label="Result"), gr.JSON(label="Detailed Probabilities")]

# Create Gradio interface
iface = gr.Interface(
    fn=predict_diabetes,
    inputs=inputs,
    outputs=outputs,
    title="Diabetes Prediction App",
    description="Enter patient health metrics to predict diabetes risk.",
    examples=[
        [1, 85, 66, 29, 0, 26.6, 0.351, 31],  # Non-diabetic example
        [6, 148, 72, 35, 0, 33.6, 0.627, 50],  # Diabetic example
        [8, 183, 64, 0, 0, 23.3, 0.672, 32],
        [0, 137, 40, 35, 168, 43.1, 2.288, 33],
    ],
    theme="default",
)

if __name__ == "__main__":
    iface.launch()
