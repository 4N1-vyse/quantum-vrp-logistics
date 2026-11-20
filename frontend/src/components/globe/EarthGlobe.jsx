import RouteLayer from "./RouteLayer";
import PortMarkers from "./PortMarkers";
import { useEffect, useRef, useState } from "react";
import { RotateCcw } from "lucide-react";
import CountryLayer from "./CountryLayer";
import Globe from "globe.gl";

function EarthGlobe() {
  const globeContainerRef = useRef(null);
  const globeInstanceRef = useRef(null);
  const zoomToIndiaRef = useRef(null);
  const [isIndiaView, setIsIndiaView] = useState(false);

  const zoomToIndia = () => {
    const globe = globeInstanceRef.current;

    if (!globe) return;

    globe.pointOfView(
      {
        lat: 22,
        lng: 82,
        altitude: 1.15,
      },
      1800,
    );

    setIsIndiaView(true);
  };

  const resetGlobe = () => {
    const globe = globeInstanceRef.current;

    if (!globe) return;

    globe.pointOfView(
      {
        lat: 20,
        lng: 78,
        altitude: 2.5,
      },
      1800,
    );

    setIsIndiaView(false);
  };

  useEffect(() => {
    const container = globeContainerRef.current;

    if (!container) return;

    zoomToIndiaRef.current = zoomToIndia;

    // Clear any previous canvas before creating the globe
    container.innerHTML = "";

    // Create the 3D Earth
    const globe = Globe({
      animateIn: true,
      waitForGlobeReady: true,
    })(container);

    globeInstanceRef.current = globe;

    // Apply Earth textures
    globe
      .globeImageUrl("/textures/earth-blue-marble.jpg")
      .bumpImageUrl("/textures/earth-topology.png")
      .backgroundImageUrl("/textures/night-sky.png")
      .backgroundColor("#070B14");
    CountryLayer(globe, () => zoomToIndiaRef.current?.());
    PortMarkers(globe);
    RouteLayer(globe);
    // Configure the atmosphere
    globe
      .showAtmosphere(true)
      .atmosphereColor("#38bdf8")
      .atmosphereAltitude(0.18);

    // Center the initial camera around India
    globe.pointOfView(
      {
        lat: 20,
        lng: 78,
        altitude: 2.5,
      },
      0,
    );

    // Enable automatic rotation
    const controls = globe.controls();
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.35;
    controls.enableZoom = true;
    controls.enablePan = false;

    // Make the globe responsive
    const resizeObserver = new ResizeObserver(() => {
      if (!container) return;

      globe.width(container.clientWidth).height(container.clientHeight);
    });

    resizeObserver.observe(container);

    // Set initial dimensions
    globe.width(container.clientWidth).height(container.clientHeight);

    // Cleanup when the component unmounts
    return () => {
      resizeObserver.disconnect();
      globe.pauseAnimation();
      container.innerHTML = "";
      globeInstanceRef.current = null;
    };
  }, []);

  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl bg-[#070B14]">
      <div ref={globeContainerRef} className="h-full w-full" />

      {/* Globe information overlay */}
      <div className="pointer-events-none absolute left-4 top-4 z-10 sm:left-6 sm:top-6">
        <p className="text-xs font-semibold tracking-[0.25em] text-cyan-400">
          {isIndiaView ? "INDIA VIEW" : "GLOBAL VIEW"}
        </p>

        <h2 className="mt-1 text-lg font-semibold text-white sm:mt-2 sm:text-xl">
          {isIndiaView ? "Indian Subcontinent" : "Earth Explorer"}
        </h2>

        <p className="mt-1 text-xs text-slate-400">
          {isIndiaView
            ? "India selected · Regional exploration"
            : "Interactive 3D visualization"}
        </p>
      </div>
      {isIndiaView && (
        <button
          onClick={resetGlobe}
          className="absolute right-3 top-3 z-20 flex items-center gap-2 rounded-lg border border-cyan-400/30 bg-slate-900/90 px-3 py-2 text-xs text-cyan-300 transition duration-300 hover:border-cyan-400 hover:bg-cyan-400/10 sm:right-5 sm:top-5 sm:px-4 sm:text-sm"
        >
          <RotateCcw size={16} />
          Global View
        </button>
      )}

      {/* Interaction hint */}
      <div className="pointer-events-none absolute bottom-5 left-5 z-10">
        <p className="text-xs text-slate-400">
          DRAG TO ROTATE · SCROLL TO ZOOM
        </p>
      </div>
    </div>
  );
}

export default EarthGlobe;
