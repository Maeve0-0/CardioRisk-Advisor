import streamlit as st
import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model

# --- Load models ---
with open('risk_classifier2.pkl', 'rb') as f:
    risk_model = pickle.load(f)

bp_model = load_model('cnn_model3.h5')

# --- Streamlit app layout ---
st.set_page_config(page_title="CardioRisk Advisor", layout="centered")
st.title("\U0001F9BE CardioRisk Advisor")
st.markdown("Estimate your **blood pressure** and **10-year heart disease risk**.")

st.header("1. Upload PPG Signal")
uploaded_file = st.file_uploader("Upload your PPG .npy file", type=["npy"])

ppg_valid = False
if uploaded_file is not None:
    try:
        ppg_signal = np.load(uploaded_file)
        if ppg_signal.shape == (125,):
            x_input = ppg_signal.reshape((1, 125, 1))
            bp_pred = bp_model.predict(x_input, verbose=0)
            pred_sbp = round(bp_pred[0][0], 2)
            pred_dbp = round(bp_pred[0][1], 2)
            st.success(f"Predicted Systolic BP: {pred_sbp} mmHg")
            st.success(f"Predicted Diastolic BP: {pred_dbp} mmHg")
            ppg_valid = True
        else:
            st.error("❌ Uploaded .npy file must be 1D with shape (125,)")
    except Exception as e:
        st.error(f"Error reading file: {e}")
else:
    st.info("Please upload a valid .npy PPG signal file.")

# Dummy fallback values
if not ppg_valid:
    pred_sbp = 120.0
    pred_dbp = 80.0

st.header("2. Enter Clinical Information")
col1, col2 = st.columns(2)
with col1:
    age = st.slider("Age", 20, 80, 50)
    male = st.selectbox("Gender", ["Female", "Male"])
    education = st.selectbox("Education Level", [1, 2, 3, 4])
    currentSmoker = st.selectbox("Currently Smokes?", ["No", "Yes"])
    cigsPerDay = st.slider("Cigarettes per Day", 0, 50, 0)
    diabetes = st.selectbox("Has Diabetes?", ["No", "Yes"])
with col2:
    BPMeds = st.selectbox("On BP Medication?", ["No", "Yes"])
    prevalentStroke = st.selectbox("History of Stroke?", ["No", "Yes"])
    prevalentHyp = st.selectbox("Hypertensive?", ["No", "Yes"])
    totChol = st.slider("Total Cholesterol", 100, 400, 200)
    BMI = st.slider("BMI", 10.0, 50.0, 25.0)
    heartRate = st.slider("Heart Rate", 40, 120, 75)
    glucose = st.slider("Glucose", 50, 200, 100)

# --- Predict CHD Risk ---
st.header("3. Heart Disease Risk Prediction")

input_dict = {
    'age': age,
    'cigsPerDay': cigsPerDay,
    'totChol': totChol,
    'BMI': BMI,
    'heartRate': heartRate,
    'glucose': glucose,
    'sysBP': pred_sbp,
    'diaBP': pred_dbp,
    'education': int(education),
    'BPMeds': int(BPMeds == 'Yes'),
    'prevalentStroke': int(prevalentStroke == 'Yes'),
    'prevalentHyp': int(prevalentHyp == 'Yes'),
    'diabetes': int(diabetes == 'Yes'),
    'currentSmoker': int(currentSmoker == 'Yes'),
    'male': int(male == 'Male')
}

input_df = pd.DataFrame([input_dict])
risk_prob = risk_model.predict_proba(input_df)[:, 1][0]
st.subheader(f"\U0001F52E Estimated 10-Year CHD Risk: {risk_prob:.2%}")
# --- Health advice based on risk ---
def get_health_advice(risk):
    if risk < 0.1:
        return "✅ Excellent cardiovascular health. Keep up your current lifestyle!"
    elif risk < 0.2:
        return "👍 Low risk. Maintain a healthy diet, regular exercise, and avoid smoking."
    elif risk < 0.5:
        return "⚠️ Moderate risk. Consider consulting a physician for personalized advice."
    else:
        return "🚨 High risk detected. We strongly recommend medical consultation, lifestyle adjustment, and regular monitoring."
health_advice = get_health_advice(risk_prob)

if risk_prob :
    if st.button("Click to Reveal Your Personalized Health Advice"):
        st.subheader(health_advice)
else:
    st.subheader(health_advice)

# --- Footer ---
st.markdown("""
---
\U0001F4A1 *This app is a prototype for educational purposes only and not a substitute for clinical diagnostics.*
""")