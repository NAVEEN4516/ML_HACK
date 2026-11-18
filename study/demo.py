from pathlib import Path
import json
import numpy as np
from models import predict
root = Path(__file__).resolve().parent
example = json.loads((root / "example.json").read_text())
for path in sorted(root.glob("*_*.json")):
    scores = predict(json.loads(path.read_text()), np.array(example["features"]))
    best = scores.argmax()
    print(path.stem, "arc", example["arc_ids"][best], "score", round(float(scores[best]), 3))
