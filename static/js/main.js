const map = L.map("map").setView([12.9716, 77.5946], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

let routeLayer = null;
let congestionLayers = [];

const output = document.getElementById("output");

function parseCoords(value) {
  return value.split(",").map((item) => parseFloat(item.trim()));
}

function colorForLevel(level) {
  if (level === "Severe") return "#d73027";
  if (level === "Moderate") return "#fc8d59";
  return "#1a9850";
}

async function requestRoute() {
  const start = parseCoords(document.getElementById("start").value);
  const end = parseCoords(document.getElementById("end").value);
  const rainfall = Number(document.getElementById("rain").value || 0);
  const algorithm = document.getElementById("algo").value;

  const res = await fetch("/api/route", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      start,
      end,
      algorithm,
      timestamp: new Date().toISOString(),
      weather: { rainfall_mm: rainfall },
    }),
  });

  const data = await res.json();

  if (routeLayer) {
    map.removeLayer(routeLayer);
  }

  routeLayer = L.polyline(data.path_coordinates, { color: "#2b8cbe", weight: 5 }).addTo(map);
  map.fitBounds(routeLayer.getBounds(), { padding: [20, 20] });
  output.textContent = JSON.stringify(data, null, 2);
}

async function requestPrediction() {
  const segments = document
    .getElementById("segments")
    .value.split(",")
    .map((item) => item.trim())
    .filter(Boolean);
  const rainfall = Number(document.getElementById("rain").value || 0);

  const res = await fetch("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      segment_ids: segments,
      timestamp: new Date().toISOString(),
      weather: { rainfall_mm: rainfall },
    }),
  });

  const data = await res.json();
  output.textContent = JSON.stringify(data, null, 2);

  congestionLayers.forEach((layer) => map.removeLayer(layer));
  congestionLayers = [];

  data.predictions.forEach((prediction) => {
    const marker = L.circleMarker([12.9716 + Math.random() * 0.01, 77.5946 + Math.random() * 0.01], {
      radius: 8,
      color: colorForLevel(prediction.congestion_level),
      fillOpacity: 0.8,
    })
      .bindPopup(
        `${prediction.segment_id}: ${prediction.congestion_level} (risk ${prediction.bottleneck_risk_score})`,
      )
      .addTo(map);
    congestionLayers.push(marker);
  });
}

document.getElementById("routeBtn").addEventListener("click", requestRoute);
document.getElementById("predictBtn").addEventListener("click", requestPrediction);
