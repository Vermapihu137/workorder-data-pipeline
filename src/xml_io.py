"""Export orders to XML and parse them back with xml.etree.ElementTree."""
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd


def df_to_xml(df: pd.DataFrame, path: Path) -> None:
    root = ET.Element("orders")
    for _, r in df.iterrows():
        o = ET.SubElement(root, "order", id=str(r["order_id"]))
        info = ET.SubElement(o, "info")
        for tag, col in [("type", "order_type"), ("category", "category"),
                         ("site", "site"), ("priority", "priority")]:
            ET.SubElement(info, tag).text = str(r[col])
        ET.SubElement(ET.SubElement(o, "steps"), "step").text = str(r["description"])
        ET.SubElement(ET.SubElement(o, "notes"), "note").text = str(r["action_text"] or "")
        ET.SubElement(o, "opened").text = pd.Timestamp(r["opened_at"]).isoformat()
        ET.SubElement(o, "closed").text = pd.Timestamp(r["closed_at"]).isoformat()
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def xml_to_df(path: Path) -> pd.DataFrame:
    rows = []
    for o in ET.parse(path).getroot().iter("order"):
        rows.append({
            "order_id": o.get("id"),
            "order_type": o.findtext("info/type"),
            "category": o.findtext("info/category"),
            "site": o.findtext("info/site"),
            "priority": o.findtext("info/priority"),
            "text": " ".join([s.text or "" for s in o.findall("steps/step")]
                             + [n.text or "" for n in o.findall("notes/note")]).upper(),
            "opened_at": pd.to_datetime(o.findtext("opened")),
            "closed_at": pd.to_datetime(o.findtext("closed")),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "output"
    df = pd.read_csv(base / "filtered_orders.csv", parse_dates=["opened_at", "closed_at"], dtype={"category": str})
    df_to_xml(df, base / "filtered_orders.xml")
    back = xml_to_df(base / "filtered_orders.xml")
    assert len(df) == len(back), "Round-trip row count mismatch"
    print(f"Exported {len(df)} orders to XML, parsed back {len(back)} (round-trip OK)")
