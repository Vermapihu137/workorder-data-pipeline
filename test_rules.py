import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from pipeline import tag_text, HARD_EXCLUDE


def test_leak_matches():
    assert "LEAKS" in tag_text("COOLANT LEAK NEAR PUMP")[0]


def test_no_false_positive_on_straight():
    assert tag_text("STRAIGHT PIPE SECTION REPLACED")[0] == ""


def test_misalignment_sheet_not_flagged():
    assert "ALIGNMENT" not in tag_text("MISALIGNMENT TOLERANCE SHEET REVIEWED")[0]


def test_hard_exclusion():
    assert HARD_EXCLUDE.search("TRAINING SESSION FOR NEW STAFF")
    assert not HARD_EXCLUDE.search("PUMP LEAKING")
