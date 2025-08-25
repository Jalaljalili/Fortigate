import os
import re
import pandas as pd

# Folder containing daily log files (same as your script)
LOG_DIR = "logs"

# Regex to extract fields from log lines
pattern = re.compile(
    r'date=(\d{4}-\d{2}-\d{2})\s+time=(\d{2}:\d{2}:\d{2}).*?user="([^"]+)".*?action="([^"]+)"',
    re.IGNORECASE
)

records = []
for file in sorted(os.listdir(LOG_DIR)):
    if file.startswith("fortigate-auth-") and file.endswith(".log"):
        with open(os.path.join(LOG_DIR, file), "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    d, t, user, action = m.groups()
                    records.append((d, t, user.strip().upper(), action.strip().lower()))

if not records:
    print("⚠ No valid log entries found.")
    raise SystemExit(0)

df = pd.DataFrame(records, columns=["Date", "Time", "User", "Action"])
df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
df.sort_values("Datetime", inplace=True)

# Split by action
logins = df[df["Action"] == "auth-logon"].copy()
logouts = df[df["Action"] == "auth-logout"].copy()

# Aggregations
login_count = logins.groupby("User").size().rename("Login_Count")
first_login = logins.groupby("User")["Datetime"].min().rename("First_Login")
last_logout = logouts.groupby("User")["Datetime"].max().rename("Last_Logout")

# Combine into one per-user summary
summary = pd.concat([login_count, first_login, last_logout], axis=1).reset_index()

# Optional: sort users by name or by most logins
summary.sort_values(["Login_Count", "User"], ascending=[False, True], inplace=True)

# Write Excel
out_file = "fortigate_user_summary.xlsx"
with pd.ExcelWriter(out_file, engine="openpyxl", datetime_format="yyyy-mm-dd hh:mm:ss") as writer:
    summary.to_excel(writer, index=False, sheet_name="User_Summary")

print(f"✅ Excel report saved: {out_file}")
