import ports from "../../data/ports";

function PortMarkers(globe) {
  globe
    .pointsData(ports)
    .pointLat((port) => port.lat)
    .pointLng((port) => port.lng)
    .pointColor((port) => (port.id === "jebel-ali" ? "#f59e0b" : "#22d3ee"))
    .pointAltitude(0.025)
    .pointRadius(0.45)
    .pointResolution(16)
    .pointsMerge(false)
    .pointLabel(
      (port) => `
        <div style="
          background: rgba(7, 11, 20, 0.95);
          border: 1px solid #22d3ee;
          border-radius: 8px;
          padding: 10px 12px;
          color: white;
          font-family: Arial;
        ">
          <strong>${port.name}</strong>
          <br />
          <span style="color: #94a3b8; font-size: 12px;">
            ${port.country} · ${port.type}
          </span>
        </div>
      `,
    );

  return ports;
}

export default PortMarkers;
