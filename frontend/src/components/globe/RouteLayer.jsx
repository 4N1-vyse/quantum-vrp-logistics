const shippingRoute = [
  {
    startLat: 18.95,
    startLng: 72.95,
    endLat: 24.985,
    endLng: 55.027,
    name: "Nhava Sheva → Jebel Ali",
  },
];

const portRings = [
  {
    lat: 18.95,
    lng: 72.95,
    color: "#22d3ee",
  },
  {
    lat: 24.985,
    lng: 55.027,
    color: "#f59e0b",
  },
];

function RouteLayer(globe) {
  // Shipping route
  globe
    .arcsData(shippingRoute)
    .arcStartLat((d) => d.startLat)
    .arcStartLng((d) => d.startLng)
    .arcEndLat((d) => d.endLat)
    .arcEndLng((d) => d.endLng)
    .arcColor(() => "#22d3ee")
    .arcAltitude(0.22)
    .arcStroke(0.5)
    .arcDashLength(0.4)
    .arcDashGap(0.15)
    .arcDashInitialGap(() => Math.random())
    .arcDashAnimateTime(2500);

  // Pulsing rings at both ports
  globe
    .ringsData(portRings)
    .ringLat((d) => d.lat)
    .ringLng((d) => d.lng)
    .ringColor((d) => d.color)
    .ringMaxRadius(3)
    .ringPropagationSpeed(2)
    .ringRepeatPeriod(1800);

  return shippingRoute;
}

export default RouteLayer;
