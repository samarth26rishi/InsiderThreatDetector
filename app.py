import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from glob import glob
import shap
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🔐 Insider Threat Detection Dashboard")

# =====================================================
# DETECT MONTHS
# =====================================================

def parse_month(folder):
    return int(folder.split("_")[1])

email_months = sorted(glob("month_*_email"), key=parse_month)

if not email_months:
    st.error("No month folders found.")
    st.stop()

# =====================================================
# SESSION STATE
# =====================================================

for key in ["month_index","day","baseline_exists","final_df","alerts","X_scaled","drift_ratio"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key in ["month_index","day"] else None

if st.session_state.day == 0:
    st.session_state.day = 1

current_month_folder = email_months[st.session_state.month_index]
current_month = current_month_folder.replace("_email","")
usb_folder = f"{current_month}_usbfiles"

st.markdown(f"### Month: {current_month}")
st.markdown(f"### Day: {st.session_state.day}")

# =====================================================
# PROCESS NEXT DAY
# =====================================================

if st.button("➡️ Process Next Day"):

    day = st.session_state.day

    email_file = os.path.join(current_month_folder, f"email_{day}.csv")
    usb_file = os.path.join(usb_folder, f"usbfile_{day}.csv")

    # Month finished
    if not os.path.exists(email_file):

        if os.path.exists("email_cumulative.csv"):
            os.system("python make_model_repeated.py")
            st.session_state.baseline_exists = True

        st.session_state.month_index += 1
        st.session_state.day = 1

        for f in ["email_cumulative.csv","usb_cumulative.csv"]:
            if os.path.exists(f):
                os.remove(f)

        st.rerun()

    # Load daily
    email_daily = pd.read_csv(email_file)
    usb_daily = pd.read_csv(usb_file)

    email_cum = pd.read_csv("email_cumulative.csv") if os.path.exists("email_cumulative.csv") else pd.DataFrame()
    usb_cum = pd.read_csv("usb_cumulative.csv") if os.path.exists("usb_cumulative.csv") else pd.DataFrame()

    email_cum = pd.concat([email_cum,email_daily])
    usb_cum = pd.concat([usb_cum,usb_daily])

    email_cum.to_csv("email_cumulative.csv", index=False)
    usb_cum.to_csv("usb_cumulative.csv", index=False)

    if not st.session_state.baseline_exists:
        st.warning("Building baseline month...")
        st.session_state.day += 1
        st.rerun()

    # =====================================================
    # LOAD MODEL
    # =====================================================

    model = joblib.load("baseline_model.pkl")
    scaler = joblib.load("baseline_scaler.pkl")
    feature_columns = joblib.load("baseline_features.pkl")
    org_stats = np.load("org_baseline_stats.npy", allow_pickle=True).item()
    personal_baseline = pd.read_csv("personal_baseline.csv")
    psy_df = pd.read_csv("psychometric.csv").rename(columns={"user_id":"user"})

    # =====================================================
    # DAILY NORMALIZED AGGREGATION
    # =====================================================

    days_so_far = st.session_state.day

    usb_agg = usb_cum.groupby("user").sum().reset_index()
    email_agg = email_cum.groupby("user").sum().reset_index()

    final_df = usb_agg.merge(email_agg,on="user",how="outer").fillna(0)

    for col in final_df.columns:
        if col!="user":
            final_df[col] /= days_so_far

    # Add psychometrics
    final_df = final_df.merge(psy_df,on="user",how="left").fillna(0)
    final_df["C"] = 100-final_df["C"]
    final_df["A"] = 100-final_df["A"]

    # =====================================================
    # ANOMALY DETECTION
    # =====================================================

    X = final_df[feature_columns]
    X_scaled = scaler.transform(X)

    scores = model.decision_function(X_scaled)
    preds = model.predict(X_scaled)

    final_df["anomaly_score"] = scores
    final_df["ANOMALY_FLAG"] = preds==-1

    # =====================================================
    # PERSONAL DEVIATION
    # =====================================================

    merged = final_df.merge(personal_baseline,on="user",suffixes=("","_base"))
    merged.fillna(0,inplace=True)

    merged["PERSONAL_FLAG"] = (
        merged["sensitive_files_accessed"] >
        1.8 * merged["sensitive_files_accessed_base"]
    )

    final_df["PERSONAL_FLAG"] = merged["PERSONAL_FLAG"]

    # =====================================================
    # ORG DRIFT
    # =====================================================

    today_mean = final_df["sensitive_files_accessed"].mean()
    drift_ratio = today_mean/(org_stats["mean_sensitive"]+1e-6)

    st.session_state.drift_ratio = drift_ratio

    # =====================================================
    # FINAL FLAG
    # =====================================================

    final_df["FINAL_FLAG"] = (
        final_df["ANOMALY_FLAG"] |
        final_df["PERSONAL_FLAG"]
    )

    st.session_state.final_df = final_df
    st.session_state.alerts = final_df[final_df["FINAL_FLAG"]]
    st.session_state.day += 1

# =====================================================
# DISPLAY DASHBOARD
# =====================================================

if st.session_state.final_df is not None:

    final_df = st.session_state.final_df
    alerts = st.session_state.alerts
    drift_ratio = st.session_state.drift_ratio

    col1,col2,col3 = st.columns(3)
    col1.metric("Users",len(final_df))
    col2.metric("Alerts",len(alerts))
    col3.metric("Drift Ratio",round(drift_ratio,2))

    # Gauge
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=drift_ratio,
        title={'text':"Drift Ratio"},
        gauge={'axis':{'range':[0,3]},
               'steps':[{'range':[0,1.2],'color':"green"},
                        {'range':[1.2,1.5],'color':"yellow"},
                        {'range':[1.5,3],'color':"red"}]}
    ))
    st.plotly_chart(fig_gauge,use_container_width=True)

    st.markdown("---")

    # Scatter
    fig_scatter = px.scatter(
        final_df,
        x="external_emails",
        y="sensitive_files_accessed",
        color="FINAL_FLAG",
        hover_data=["user"],
        template="plotly_dark"
    )
    st.plotly_chart(fig_scatter,use_container_width=True)

    # SHAP for flagged
    if len(alerts)>0:

        st.subheader("Top Risk Users")
        top_users = alerts.sort_values("anomaly_score").head(5)
        st.dataframe(top_users)

        selected_user = st.selectbox("Explain User", top_users["user"])

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_scaled)

        user_index = final_df.index[final_df["user"]==selected_user][0]
        user_shap = shap_values[user_index]

        shap_df = pd.DataFrame({
            "Feature":feature_columns,
            "Impact":user_shap
        }).sort_values("Impact",key=abs)

        fig_shap = px.bar(
            shap_df.tail(10),
            x="Impact",
            y="Feature",
            orientation="h",
            color="Impact",
            template="plotly_dark"
        )
        st.plotly_chart(fig_shap,use_container_width=True)

# =====================================================
# RESET
# =====================================================

if st.button("Reset Simulation"):
    st.session_state.clear()
    for f in ["email_cumulative.csv","usb_cumulative.csv",
              "baseline_model.pkl","baseline_scaler.pkl",
              "baseline_features.pkl","org_baseline_stats.npy",
              "personal_baseline.csv"]:
        if os.path.exists(f):
            os.remove(f)