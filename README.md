# Work-Order Data Pipeline (synthetic data)

A small, end-to-end data project: generate messy work-order data, clean and filter it with **pandas** using business rules, export/parse **XML**, and analyse the result.

> All data and rules are **synthetic and invented**. No real company data, systems or specifications are used.

## Problem
Operational teams receive thousands of work orders with free-text descriptions. Only a subset is relevant for a given review, so orders must be filtered by rules, tagged, and prioritised before analysis.

## What it does
| Stage | File | Description |
|---|---|---|
| 0 | `src/generate_data.py` | Creates 8,000 synthetic orders (IDs, category, free text, open/close dates) |
| 1-4 | `src/pipeline.py` | Cleans text, applies hard exclusions, category whitelist, regex text rules (word boundaries), and P1/P2/P3 priority tiers |
| XML | `src/xml_io.py` | Exports orders to XML and parses them back (round-trip check) |
| Analysis | `src/analysis.py` | Monthly trend, priority split, average time to close, orders by site -> `output/summary.png` |
| Tests | `tests/test_rules.py` | Unit tests for rule matching and false positives |

## Run
```bash
pip install -r requirements.txt
python src/generate_data.py
python src/pipeline.py
python src/xml_io.py
python src/analysis.py
pytest tests
```

## Example result (seed 42)
- 8,000 input orders -> ~5,300 kept after exclusions and rules
- XML export and re-import give identical row counts
- Word-boundary regex avoids false positives (e.g. `STRAIGHT`, `MISALIGNMENT SHEET`)

## Key learnings
- Using `\b` word boundaries in regex instead of plain `LIKE '%TEXT%'` removes many false positives.
- Concatenating all free-text fields before matching avoids missing keywords that appear in only one field.
- A round-trip test (export -> parse -> compare) is a cheap way to validate XML handling.

## Tech
Python, pandas, matplotlib, xml.etree.ElementTree, pytest
