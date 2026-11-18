"""Generate the development-only Folium map from one labelled trip."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

import numpy as np
from geometry import reference
from prepare import DEFAULT_DATA, ROOT
from service import reconstruct


def map_layers(folder):
    artifact = json.loads((ROOT / "artifacts/model.json").read_text())
    trip, ids, _, _, choices = reconstruct(folder, artifact)
    route, _ = reference(folder, trip)
    prediction = ids[np.arange(len(choices)), choices]
    gps = trip.track[:, :2][:, ::-1]
    lower, upper = gps.min(axis=0) - .001, gps.max(axis=0) + .001
    roads = trip.nodes[trip.arcs][:, :, ::-1]
    visible = ((roads.max(axis=1) >= lower) & (roads.min(axis=1) <= upper)).all(axis=1)
    return {
        "trip": folder.name, "gps": gps.round(7).tolist(),
        "network": roads[visible].round(7).tolist(),
        "candidates": roads[np.unique(ids)].round(7).tolist(),
        "reference": roads[np.unique(route)].round(7).tolist(),
        "prediction": roads[np.unique(prediction)].round(7).tolist(),
    }


def render(layers, dest):
    import folium

    gps = np.asarray(layers["gps"])
    chart = folium.Map(location=gps.mean(axis=0).tolist(), tiles=None,
                       control_scale=True, prefer_canvas=True)
    # The view uses vector layers and native Leaflet controls only.
    chart.default_js = []
    chart.default_css = []
    from branca.element import Element
    leaflet = "https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet"
    header = chart.get_root().header
    for extension, tag in (("css","style"),("js","script")):
        with urlopen(f"{leaflet}.{extension}", timeout=30) as source:
            asset = source.read().decode("utf-8")
        header.add_child(Element(f"<{tag}>{asset}</{tag}>"))
    for key, name, color, width in [
        ("network", "Road network", "#d2d7da", 1),
        ("candidates", "Candidate roads", "#8a999d", 2),
        ("reference", "Reference route", "#c95624", 7),
        ("prediction", "Predicted route", "#16755c", 3),
    ]:
        group = folium.FeatureGroup(name=name).add_to(chart)
        folium.PolyLine(layers[key], color=color, weight=width, opacity=.85).add_to(group)
    points = folium.FeatureGroup(name="GPS observations").add_to(chart)
    features = {"type":"FeatureCollection", "features":[
        {"type":"Feature","geometry":{"type":"Point","coordinates":[lon,lat]},"properties":{}}
        for lat,lon in layers["gps"]]}
    folium.GeoJson(features, marker=folium.CircleMarker(radius=1.5,color="#3359a6",
                   weight=1,fill=True)).add_to(points)
    folium.LayerControl(collapsed=False).add_to(chart)
    chart.fit_bounds([gps.min(axis=0).tolist(),gps.max(axis=0).tolist()])
    dest.parent.mkdir(parents=True,exist_ok=True)
    chart.save(str(dest))


def main(folder, dest):
    render(map_layers(folder), dest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trip", type=Path, default=DEFAULT_DATA/"student_test"/"00000076")
    parser.add_argument("--out", type=Path, default=ROOT/"results/development_map.html")
    args = parser.parse_args()
    main(args.trip, args.out)
