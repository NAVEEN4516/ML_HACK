# PathSnap PT-095

Distributed map matching for the supplied PathSnap hackathon dataset.

## Team contributions

Official repository: https://github.com/NAVEEN4516/ML_HACK

- Member 1: Preprocessing and linear model artifacts. Presentation models: Logistic_baseline, LDA_baseline.
- Member 2: Classifier implementation, training and Bayesian optimisation. Presentation models: GaussianNB_baseline, HistogramNB_baseline.
- Member 3: Decoder, evaluation and diagnostics. Presentation models: CART_baseline, Logistic_baseline.
- Member 4: Deployment, API, UI, maps and selected model. Presentation models: CART_search_best, HistogramNB_baseline.

## Installation

Use Python 3.12. From the assembled repository run:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```

Extract the supplied dataset to a sibling directory named `Student folder/Student folder`, containing `train` and `student_test`. Alternatively supply `--data` to prepare.py and set PATHSNAP_TRIPS for inference.

## Reproduce experiments

```powershell
.venv/Scripts/python prepare.py
.venv/Scripts/python experiment.py
.venv/Scripts/python plots.py
.venv/Scripts/python visualize_map.py
.venv/Scripts/python verify.py
```

Training uses up to 300 randomly selected observations from each training trip, including all candidates of those observations. Three folds keep trips together. Validation and student-test scoring use every observation. Seed is 95. The original run completed all 80 training and 10 student-testing trips.

Five independently coded NumPy classifiers are logistic regression, Gaussian naive Bayes, histogram naive Bayes, regularised LDA and a CART-style classification tree. CART tests five quantile thresholds per feature. Eight Gaussian-process Bayesian trials tune the best family. This is a compact CPU baseline. Full configurations and limitations are in docs/METHODOLOGY.md.

## Laptop 1

Set PATHSNAP_TRIPS to the directory containing the ten chosen trip folders.

```powershell
$env:PATHSNAP_TRIPS="C:/path/to/student_test"
.venv/Scripts/python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

For final evaluation, point PATHSNAP_TRIPS at the organiser-provided evaluator trips. PATHSNAP_LABELS may point to a separate directory with matching trip subfolders holding reference files. Predictions finish before reference files are opened for scoring. The UI receives only predicted geometry, GPS observations and aggregate scores.

## Laptop 2

Copy the ui directory to the second laptop and run:

```powershell
$env:PATHSNAP_API="http://LAPTOP_1_IP:8000"
python ui/server.py
```

Open http://127.0.0.1:8501 on Laptop 2. Both laptops must be able to reach port 8000 on Laptop 1. The UI server proxies requests to Laptop 1. Observe Uvicorn logs on Laptop 1 during the demonstration.

## API

GET /trips lists available trip IDs. POST /match/{trip_id} reconstructs one trip. FastAPI documents the endpoints at /docs. Missing labels produce a prediction with null metrics. Unknown IDs return 404.

## Submission and verification

The consolidated technical report records the first integrated run. All ten student trips passed through a browser, the UI proxy and FastAPI on one host. Each POST returned HTTP 200. The four returned metrics agreed with offline scores, and the responses contained 19,160 predictions. Pages 7–8 contain the map, UI and receiving-server evidence. Open the report's `development_map.html` attachment in a PDF viewer that supports embedded files.

The model and CSVs in this checkout come from a separate Windows reproduction. Both runs selected depth-9 CART, adjacency cost 0.65, jump cost 6 and a 10-second restart. Each value below is a mean across ten trips.

| CART + Viterbi | PDF run | This checkout |
|---|---:|---:|
| Aligned point accuracy | 90.03% | 89.97% |
| Road macro F1 | 0.832 | 0.826 |
| Direct road continuity | 97.67% | 97.68% |
| Ordered sequence F1 | 0.812 | 0.808 |

The two runs produced slightly different fitted results. The exact cause has not been established. `results/verification.json` records the independent comparison between this checkout's saved model and its offline CSV for all 19,160 observations. It also records the check that removing the reference file leaves predictions unchanged. The physical two-laptop demonstration and the organiser's reserved trips remain for evaluation day.

### Interactive map

`visualize_map.py` writes `results/development_map.html` for student trip 00000076. It embeds Leaflet during generation and uses local vector layers for the road network, candidates, reference, prediction and GPS. Generating the HTML requires an internet connection to obtain the Leaflet assets. Opening the generated HTML works offline. The map in the PDF is the original report-run export.

### Run the checks

```powershell
.venv/Scripts/python diagnostics.py
.venv/Scripts/python verify.py
.venv/Scripts/python deployment_smoke.py
```

The smoke check starts both web processes on ports 8000 and 8501 using a synthetic trip. Run it before starting the live servers. With both real services running and the student-test dataset selected, run the following in a third terminal:

```powershell
.venv/Scripts/python integration_check.py --ui http://127.0.0.1:8501
```

It checks every proxied response against the offline CSV and writes `results/http_verification.json` after all ten pass. `results/decoder_search.csv` records the six transition settings tested with out-of-fold training emissions. The decoder and classifier settings are saved together in `artifacts/model.json`.

### Assistance

ChatGPT assisted with implementation, execution, verification and report drafting. The team is responsible for presenting its contributions and conducting the physical demonstration.
