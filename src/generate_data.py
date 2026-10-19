"""Generate a fully synthetic work-order dataset (no real company data)."""
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

SITES = ["SITE-A", "SITE-B", "SITE-C", "SITE-D", "SITE-E"]
ORDER_TYPES = ["C", "P", "R"]  # corrective, preventive, routine
CATEGORIES = ["10", "20", "30", "40", "50", "60", "70", "80"]

# Generic free-text snippets (invented, not taken from any real system)
DEFECT_TEXT = [
    "Pump housing leaking, gasket replaced",
    "Belt worn, tension adjusted",
    "Bracket loose, retightened",
    "Coolant leak near heat exchanger",
    "Shaft misaligned, realigned and tested",
    "Paint scratch on outer casing",
    "Fan bearing noise, replaced unit",
    "Filter cleaning completed, flow restored",
    "Cable damaged, rerouted and secured",
    "Valve stuck, cleaned and lubricated",
    "Straight pipe section replaced",             # tests word-boundary logic (STRAIGHT != ALIGN-type words)
    "Misalignment tolerance sheet reviewed",      # tests word-boundary logic
    "Routine check, no defect found",
]
ADMIN_TEXT = [
    "Training session for new staff",
    "Drill exercise, dummy entry",
    "Test entry created for system demo",
]
TITLES_SCHEDULED = [
    "Quarterly cleaning", "Belt inspection", "Routine lubrication",
    "Filter replacement", "Annual calibration", "Visual walk-around",
]


def make_orders(n: int = 8000) -> pd.DataFrame:
    start = datetime(2025, 1, 1)
    rows = []
    for i in range(1, n + 1):
        opened = start + timedelta(hours=random.randint(0, 24 * 540))
        closed = opened + timedelta(hours=random.randint(1, 24 * 20))
        otype = random.choices(ORDER_TYPES, weights=[50, 20, 30])[0]
        is_admin = random.random() < 0.04
        text = random.choice(ADMIN_TEXT) if is_admin else random.choice(DEFECT_TEXT)
        rows.append(
            {
                "order_id": f"WO{i:06d}",
                "order_type": otype,
                "category": random.choice(CATEGORIES),
                "site": random.choice(SITES),
                "title": random.choice(TITLES_SCHEDULED) if otype == "R" else "",
                "description": text,
                "action_text": random.choice(DEFECT_TEXT + [""]),
                "opened_at": opened,
                "closed_at": closed,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "output"
    out.mkdir(exist_ok=True)
    df = make_orders()
    df.to_csv(out / "synthetic_orders.csv", index=False)
    print(f"Wrote {len(df)} synthetic orders -> {out / 'synthetic_orders.csv'}")
