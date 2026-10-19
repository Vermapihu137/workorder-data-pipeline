"""Simple analysis + charts on the filtered orders."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

base = Path(__file__).resolve().parent.parent / "output"
df = pd.read_csv(base / "filtered_orders.csv", parse_dates=["opened_at", "closed_at"])

monthly = df.set_index("opened_at").resample("MS").size()
by_priority = df["priority"].value_counts().reindex(["P1", "P2", "P3", "OTHER"]).fillna(0)
avg_close = df.groupby("priority")["hours_to_close"].mean().round(1)
top_site = df["site"].value_counts()

print("Average hours to close by priority:\n", avg_close.to_string())

fig, ax = plt.subplots(2, 2, figsize=(11, 7))
monthly.plot(ax=ax[0, 0], title="Orders opened per month")
by_priority.plot.bar(ax=ax[0, 1], title="Orders by priority", rot=0)
avg_close.plot.bar(ax=ax[1, 0], title="Avg hours to close by priority", rot=0)
top_site.plot.bar(ax=ax[1, 1], title="Orders by site", rot=0)
plt.tight_layout()
fig.savefig(base / "summary.png", dpi=120)
print("Saved", base / "summary.png")
