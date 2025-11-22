import React, { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";

// --- Fix default marker icons ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// --- Fix Canvas readback warnings (must run before heatmap) ---
(function patchCanvas() {
  const orig = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, attrs) {
    if (type === "2d") {
      attrs = Object.assign({ willReadFrequently: true }, attrs || {});
    }
    return orig.call(this, type, attrs);
  };
})();

function GeoMap({ articles, heatmap = true }) {
  const mapContainer = useRef(null);
  const mapInstance = useRef(null);
  const heatLayerRef = useRef(null);
  const markerLayerRef = useRef(null);

  useEffect(() => {
    if (!mapContainer.current) return;

    // ---------------------------
    // Initialize the map ONCE
    // ---------------------------
    if (!mapInstance.current) {
      mapInstance.current = L.map(mapContainer.current, {
        center: [20, 0],
        zoom: 2,
        worldCopyJump: true,
      });

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
        maxZoom: 19,
      }).addTo(mapInstance.current);

      // Force proper size after first render
      setTimeout(() => mapInstance.current.invalidateSize(), 300);
    }

    const map = mapInstance.current;

    // ---------------------------
    // Clear old layers safely
    // ---------------------------
    if (markerLayerRef.current) map.removeLayer(markerLayerRef.current);
    if (heatLayerRef.current) map.removeLayer(heatLayerRef.current);

    // ---------------------------
    // Filter valid points
    // ---------------------------
    const valid = articles.filter(
      (a) =>
        a.lat &&
        a.lon &&
        !isNaN(parseFloat(a.lat)) &&
        !isNaN(parseFloat(a.lon))
    );

    if (valid.length === 0) return;

    // ---------------------------
    // Marker Layer
    // ---------------------------
    const markerGroup = L.layerGroup();
    const bounds = L.latLngBounds();

    valid.forEach((article) => {
      const lat = parseFloat(article.lat);
      const lon = parseFloat(article.lon);

      if (isNaN(lat) || isNaN(lon)) return;

      const marker = L.marker([lat, lon]).bindPopup(`
        <div style="max-width: 250px;">
          <h4 style="margin-bottom: 6px; font-size: 14px;">${article.title || "Article"}</h4>

          <p style="margin: 0 0 6px; font-size: 12px; color: #666;">
            ${
              article.description
                ? article.description.substring(0, 100) + "..."
                : "No description"
            }
          </p>

          <p style="margin: 0; font-size: 12px; font-weight: bold;">
            📍 ${article.location || "Unknown Location"}
          </p>
        </div>
      `);

      marker.addTo(markerGroup);
      bounds.extend([lat, lon]);
    });

    markerGroup.addTo(map);
    markerLayerRef.current = markerGroup;

    // ---------------------------
    // HEATMAP (with safe delay)
    // ---------------------------
    if (heatmap) {
      setTimeout(() => {
        const size = map.getSize();
        if (size.x === 0 || size.y === 0) {
          map.invalidateSize();
          return;
        }

        const heatPoints = valid.map((a) => [
          parseFloat(a.lat),
          parseFloat(a.lon),
          0.6,
        ]);

        heatLayerRef.current = L.heatLayer(heatPoints, {
          radius: 22,
          blur: 25,
          maxZoom: 11,
        });

        heatLayerRef.current.addTo(map);
      }, 350);
    }

    // ---------------------------
    // Fit map to markers
    // ---------------------------
    if (bounds.isValid()) {
      setTimeout(() => {
        map.fitBounds(bounds, { padding: [40, 40] });
        map.invalidateSize();
      }, 300);
    }
  }, [articles, heatmap]);

  return (
    <div
      ref={mapContainer}
      style={{
        width: "100%",
        height: "500px",
        borderRadius: "10px",
        overflow: "hidden",
        boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
      }}
    />
  );
}

export default GeoMap;
