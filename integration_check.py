"""Check the running browser proxy and compare all ten responses to offline scores."""
import argparse
import csv
import json
import math
from urllib.request import Request, urlopen

from prepare import ROOT


def verify_proxy(base):
    def fetch(path, method="GET"):
        with urlopen(Request(base.rstrip("/") + path, method=method), timeout=180) as response:
            assert response.status == 200
            return response.read()

    assert b"Route explorer" in fetch("/")
    with (ROOT / "results/decoder_by_trip.csv").open() as source:
        expected = {row["trip"]:row for row in csv.DictReader(source) if row["method"] == "viterbi"}
    trips = json.loads(fetch("/trips"))["trips"]
    assert len(trips) == 10 and sorted(trips) == sorted(expected)
    checks = []
    for trip in trips:
        result = json.loads(fetch("/match/" + trip, "POST"))
        count = result["observations"]
        assert result["trip"] == trip and len(result["arc_ids"]) == len(result["gps"]) == count
        assert not {"reference", "route", "labels"}.intersection(result)
        for key in ("top1", "macro_f1", "continuity", "sequence_f1"):
            assert math.isclose(result["metrics"][key], float(expected[trip][key]), rel_tol=0, abs_tol=1e-12)
        checks.append({"trip":trip, "observations":count, "status":200, "metrics_match":True})
    assert sum(row["observations"] for row in checks) == 19160
    (ROOT / "results/http_verification.json").write_text(json.dumps(checks, indent=2))
    print("Verified 10 UI-proxy responses and four metrics for every trip (19,160 fixes).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", default="http://127.0.0.1:8501")
    verify_proxy(parser.parse_args().ui)
