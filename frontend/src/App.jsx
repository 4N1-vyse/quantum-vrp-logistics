import EarthGlobe from "./components/globe/EarthGlobe";
import { Globe2, Ship, Wind, Activity } from "lucide-react";

function App() {
  return (
    <div className="min-h-screen bg-[#070B14] text-white">
      {/* TOP NAVIGATION */}
      <nav className="flex items-center justify-between border-b border-slate-800 px-8 py-5">
        <div className="flex items-center gap-3">
          <Globe2 className="text-cyan-400" size={30} />

          <div>
            <h1 className="text-2xl font-bold tracking-widest">ROUTEQ</h1>
            <p className="text-xs text-slate-500 tracking-wider">
              FREIGHT INTELLIGENCE SYSTEM
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-green-400"></span>
          <span className="text-xs text-green-400">SYSTEM ONLINE</span>
        </div>
      </nav>

      {/* MAIN CONTENT */}
      <main className="p-8">
        <div className="mb-8">
          <h2 className="text-3xl font-semibold">Global Freight Command</h2>

          <p className="mt-2 text-slate-400">
            Quantum-powered maritime route optimization.
          </p>
        </div>

        {/* STAT CARDS */}
        <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
          <div className="rounded-xl border border-slate-800 bg-[#101B2A] p-6">
            <Ship className="mb-4 text-cyan-400" size={28} />
            <p className="text-sm text-slate-400">Transport Mode</p>
            <h3 className="mt-2 text-xl font-semibold">Maritime</h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#101B2A] p-6">
            <Wind className="mb-4 text-cyan-400" size={28} />
            <p className="text-sm text-slate-400">Environmental Monitoring</p>
            <h3 className="mt-2 text-xl font-semibold">Awaiting Data</h3>
          </div>

          <div className="rounded-xl border border-slate-800 bg-[#101B2A] p-6">
            <Activity className="mb-4 text-purple-400" size={28} />
            <p className="text-sm text-slate-400">Optimization Engine</p>
            <h3 className="mt-2 text-xl font-semibold">Ready</h3>
          </div>
        </div>

        {/* GLOBE PLACEHOLDER */}
        <div className="mt-5 h-[450px] overflow-hidden rounded-2xl border border-slate-800 bg-[#070B14] sm:mt-8 sm:h-[550px] lg:h-[650px]">
          <EarthGlobe />
        </div>
      </main>
    </div>
  );
}

export default App;
