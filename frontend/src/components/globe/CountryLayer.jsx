import { feature } from "topojson-client";
import worldData from "world-atlas/countries-110m.json";

// India has country ID 356 in this dataset.
const countries = feature(worldData, worldData.objects.countries).features;

const india = countries.filter((country) => country.id === "356");

function CountryLayer(globe, onIndiaClick) {
  globe
    .polygonsData(india)
    .polygonCapColor(() => "rgba(34, 211, 238, 0.25)")
    .polygonSideColor(() => "rgba(34, 211, 238, 0.08)")
    .polygonStrokeColor(() => "#22d3ee")
    .polygonAltitude(0.012)
    .polygonLabel(() => "India")
    .onPolygonClick((country) => {
      console.log("Clicked country:", country);

      if (String(country.id) === "356") {
        console.log("India selected! Zooming...");
        onIndiaClick();
      }
    });

  return india;
}

export default CountryLayer;
