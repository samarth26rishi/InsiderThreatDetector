import pandas as pd
import numpy as np
import os

# =====================================================
# SETTINGS
# =====================================================

NUM_USERS = 100
MONTHS = 3
DAYS_PER_MONTH = 30

# Coordinated attack happens in Month 1 (after baseline)
COORDINATED_ATTACK_MONTH = 1
ATTACK_START_DAY = 5
ATTACK_PERCENT = 0.5  # 50% users participate

np.random.seed(42)

users = [f"user_{i}" for i in range(NUM_USERS)]

# =====================================================
# NORMAL BEHAVIOR
# =====================================================

def normal_behavior():
    total_emails = np.random.randint(10, 35)
    external = int(total_emails * np.random.uniform(0.05, 0.2))
    attachments = int(total_emails * np.random.uniform(0.05, 0.25))
    bcc = int(total_emails * np.random.uniform(0.0, 0.05))

    usb = np.random.randint(0, 3)
    sensitive = np.random.randint(1, 10)
    files = sensitive + np.random.randint(1, 10)

    return total_emails, external, attachments, bcc, usb, files, sensitive

# =====================================================
# COORDINATED ATTACK BEHAVIOR
# =====================================================

def coordinated_behavior():
    # Strong malicious email pattern
    total_emails = np.random.randint(60, 120)
    external = int(total_emails * np.random.uniform(0.7, 0.95))
    attachments = int(total_emails * np.random.uniform(0.5, 0.8))
    bcc = int(total_emails * np.random.uniform(0.3, 0.6))

    # Heavy USB extraction
    usb = np.random.randint(8, 20)
    sensitive = np.random.randint(40, 100)
    files = sensitive + np.random.randint(20, 60)

    return total_emails, external, attachments, bcc, usb, files, sensitive

# =====================================================
# GENERATE MONTHS
# =====================================================

for month in range(MONTHS):

    email_folder = f"month_{month}_email"
    usb_folder = f"month_{month}_usbfiles"

    os.makedirs(email_folder, exist_ok=True)
    os.makedirs(usb_folder, exist_ok=True)

    print(f"\n📆 Generating Month {month}")

    for day in range(1, DAYS_PER_MONTH + 1):

        email_rows = []
        usb_rows = []

        attackers = []

        # Coordinated attack trigger
        if month == COORDINATED_ATTACK_MONTH and day >= ATTACK_START_DAY:
            attackers = np.random.choice(
                users,
                int(NUM_USERS * ATTACK_PERCENT),
                replace=False
            )

        for user in users:

            if user in attackers:
                total_emails, external, attachments, bcc, usb, files, sensitive = coordinated_behavior()
            else:
                total_emails, external, attachments, bcc, usb, files, sensitive = normal_behavior()

            email_rows.append({
                "user": user,
                "total_emails": total_emails,
                "external_emails": external,
                "attachments_sent": attachments,
                "bcc_in_email": bcc,
                "avg_email_size": np.random.uniform(50, 300)
            })

            usb_rows.append({
                "user": user,
                "usb_insertions": usb,
                "files_accessed": files,
                "sensitive_files_accessed": sensitive
            })

        pd.DataFrame(email_rows).to_csv(
            f"{email_folder}/email_{day}.csv", index=False
        )

        pd.DataFrame(usb_rows).to_csv(
            f"{usb_folder}/usbfile_{day}.csv", index=False
        )

print("\n🎉 Strong Coordinated Attack Simulation Generated")