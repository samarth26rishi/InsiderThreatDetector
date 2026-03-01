import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import joblib

print("🔄 Retraining Baseline Model (Email-Weighted + Psychometrics)...")

# =====================================================
# LOAD DATA
# =====================================================

email_df = pd.read_csv("email_cumulative.csv")
usb_df = pd.read_csv("usb_cumulative.csv")
psy_df = pd.read_csv("psychometric.csv")

psy_df.columns = psy_df.columns.str.strip()
psy_df = psy_df.rename(columns={"user_id": "user"})

# =====================================================
# DETERMINE NUMBER OF DAYS
# =====================================================

num_users = email_df["user"].nunique()
days = int(len(email_df) / num_users)

print(f"📅 Baseline built over {days} days")

# =====================================================
# AGGREGATE DAILY AVERAGES
# =====================================================

usb_agg = usb_df.groupby("user").sum().reset_index()
email_agg = email_df.groupby("user").sum().reset_index()

final_df = usb_agg.merge(email_agg, on="user", how="outer")
final_df.fillna(0, inplace=True)

for col in final_df.columns:
    if col != "user":
        final_df[col] = final_df[col] / days

# =====================================================
# MERGE PSYCHOMETRICS
# =====================================================

final_df = final_df.merge(
    psy_df[["user", "O", "C", "E", "A", "N"]],
    on="user",
    how="left"
)

final_df.fillna(0, inplace=True)

# Flip C and A
final_df["C"] = 100 - final_df["C"]
final_df["A"] = 100 - final_df["A"]

# =====================================================
# EMAIL WEIGHTING (STRONGER)
# =====================================================

email_weight = 1.5
psy_weight = 0.6

email_features = [
    "external_emails",
    "attachments_sent",
    "bcc_in_email",
    "total_emails"
]

psy_features = ["O", "C", "E", "A", "N"]

for col in email_features:
    if col in final_df.columns:
        final_df[col] *= email_weight

for col in psy_features:
    if col in final_df.columns:
        final_df[col] *= psy_weight

# =====================================================
# SAVE PERSONAL BASELINE
# =====================================================

final_df.to_csv("personal_baseline.csv", index=False)
print("✅ Personal baseline saved")

# =====================================================
# TRAIN ISOLATION FOREST
# =====================================================

feature_columns = [col for col in final_df.columns if col != "user"]

X = final_df[feature_columns]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=350,
    contamination=0.05,
    random_state=42
)

model.fit(X_scaled)

# =====================================================
# SAVE ORG BASELINE
# =====================================================

org_stats = {
    "mean_sensitive": final_df["sensitive_files_accessed"].mean(),
    "std_sensitive": final_df["sensitive_files_accessed"].std()
}

np.save("org_baseline_stats.npy", org_stats)

joblib.dump(model, "baseline_model.pkl")
joblib.dump(scaler, "baseline_scaler.pkl")
joblib.dump(feature_columns, "baseline_features.pkl")

print("✅ Baseline Model Retrained Successfully")