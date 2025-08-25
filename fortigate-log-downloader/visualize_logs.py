import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Folder containing daily log files
LOG_DIR = "logs"

# Regex to extract fields from log lines
pattern = re.compile(
    r'date=(\d{4}-\d{2}-\d{2})\s+time=(\d{2}:\d{2}:\d{2}).*?user="([^"]+)".*?action="([^"]+)"'
)

# Load all logs
data = []
for file in sorted(os.listdir(LOG_DIR)):
    if file.startswith("fortigate-auth-") and file.endswith(".log"):
        with open(os.path.join(LOG_DIR, file), "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    log_date, log_time, user, action = match.groups()
                    data.append([log_date, log_time, user.upper(), action])

# Convert to DataFrame
df = pd.DataFrame(data, columns=["Date", "Time", "User", "Action"])
df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
df.sort_values("Datetime", inplace=True)

if df.empty:
    print("⚠ No valid log entries found.")
    exit()

# Split logons and logouts
logons = df[df["Action"] == "auth-logon"].copy()
logouts = df[df["Action"] == "auth-logout"].copy()

# Merge sessions: find nearest logout after each logon
sessions = []
for _, logon in logons.iterrows():
    logout = logouts[
        (logouts["User"] == logon["User"]) &
        (logouts["Datetime"] >= logon["Datetime"])
    ].head(1)
    if not logout.empty:
        logout = logout.iloc[0]
        sessions.append({
            "User": logon["User"],
            "Start": logon["Datetime"],
            "End": logout["Datetime"]
        })

sessions_df = pd.DataFrame(sessions)

# --- Visualization 1: Session Timeline ---
fig, ax = plt.subplots(figsize=(12, 6))
for i, row in sessions_df.iterrows():
    ax.plot([row["Start"], row["End"]], [row["User"], row["User"]], marker="o")

ax.set_xlabel("Time")
ax.set_ylabel("User")
ax.set_title("FortiGate 2FA Sessions Timeline")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("sessions_timeline.png", dpi=200)
print("📊 Saved: sessions_timeline.png")

# --- Visualization 2: Daily Login Count ---
daily_counts = logons.groupby(["Date", "User"]).size().reset_index(name="Logins")
pivot_counts = daily_counts.pivot(index="Date", columns="User", values="Logins").fillna(0)

pivot_counts.plot(kind="bar", figsize=(12, 6))
plt.ylabel("Login Count")
plt.title("Daily Logins per User")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("daily_logins.png", dpi=200)
print("📊 Saved: daily_logins.png")
