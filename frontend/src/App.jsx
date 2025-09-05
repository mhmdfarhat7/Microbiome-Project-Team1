import { useEffect, useState } from "react";
import EnvironmentSelect from "./components/EnvironmentSelect";
import LevelSelect from "./components/LevelSelect";
import CompositionChart from "./components/CompositionChart";
import LocationSelect from "./components/LocationSelect";
import LocationData from "./components/LocationData";
import Panel from "./components/Panel";
import LoadingModal from "./components/LoadingModal";
import {
  fetchComposition,
  fetchGeographicLocations,
  fetchLocationComposition,
} from "./services/api"; // Real M2 backend API
import { STATIC_ENVIRONMENTS } from "./constants/environments";

export default function App() {
  const [envs, setEnvs] = useState([]);
  const [env, setEnv] = useState("");
  const [level, setLevel] = useState("phylum");
  const [data, setData] = useState(null);
  const [loadingEnv, setLoadingEnv] = useState(true);
  const [loadingData, setLoadingData] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Loading...");
  const [error, setError] = useState("");
  const [chartType, setChartType] = useState("pie");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [geographicLocations, setGeographicLocations] = useState([]);
  const [loadingLocations, setLoadingLocations] = useState(true);

  // load environment list and geographic locations
  useEffect(() => {
    (async () => {
      try {
        // Use static environments list - no need to fetch from server
        setEnvs(STATIC_ENVIRONMENTS);
        setLoadingEnv(false);

        // Only fetch geographic locations from server
        const locations = await fetchGeographicLocations();
        setGeographicLocations(locations);
      } catch (e) {
        setError("Failed to load geographic locations");
        console.error("Error loading geographic locations:", e);
      } finally {
        setLoadingLocations(false);
      }
    })();
  }, []);

  // handle window resize for responsive design
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // fetch composition when env or level changes (and env selected)
  useEffect(() => {
    if (!env) return;
    setLoadingData(true);
    setLoadingMessage(`Loading ${level} composition for ${env}...`);
    setError("");
    (async () => {
      try {
        const res = await fetchComposition(env, level);
        setData(res);
      } catch (e) {
        setError("Failed to load composition");
        setData(null);
      } finally {
        setLoadingData(false);
      }
    })();
  }, [env, level]);

  // fetch location composition when selectedLocation or level changes
  useEffect(() => {
    if (!selectedLocation || selectedLocation.trim() === "") {
      // If no location selected, clear data and return to environment view
      setData(null);
      setError("");
      setLoadingData(false);
      return;
    }

    setLoadingData(true);
    setLoadingMessage(
      `Loading ${level} composition for ${selectedLocation}...`
    );
    setError("");
    (async () => {
      try {
        const res = await fetchLocationComposition(selectedLocation, level, 50);
        setData(res);
      } catch (e) {
        setError("Failed to load location composition");
        setData(null);
      } finally {
        setLoadingData(false);
      }
    })();
  }, [selectedLocation, level]);

  // When location is cleared, try to load environment data if available
  useEffect(() => {
    if ((!selectedLocation || selectedLocation.trim() === "") && env) {
      setLoadingData(true);
      setLoadingMessage(`Loading ${level} composition for ${env}...`);
      setError("");
      (async () => {
        try {
          const res = await fetchComposition(env, level);
          setData(res);
        } catch (e) {
          setError("Failed to load composition");
          setData(null);
        } finally {
          setLoadingData(false);
        }
      })();
    }
  }, [selectedLocation, env, level]);

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
      }}
    >
      <header
        style={{
          padding: isMobile ? "16px 20px" : "20px 30px",
          background: "rgba(255, 255, 255, 0.1)",
          backdropFilter: "blur(10px)",
          borderBottom: "1px solid rgba(255, 255, 255, 0.2)",
        }}
      >
        <h1
          style={{
            margin: 0,
            color: "white",
            fontSize: isMobile ? "1.8rem" : "2.5rem",
            fontWeight: "700",
            textShadow: "0 2px 4px rgba(0,0,0,0.3)",
          }}
        >
          Microbe Composition Viewer
        </h1>
        <p
          style={{
            marginTop: 8,
            color: "rgba(255, 255, 255, 0.9)",
            fontSize: isMobile ? "0.9rem" : "1.1rem",
            textShadow: "0 1px 2px rgba(0,0,0,0.3)",
          }}
        >
          Choose an environment and level to explore microbial composition.
        </p>
      </header>

      <div
        style={{
          flex: 1,
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "350px 1fr",
          gridTemplateRows: isMobile ? "auto 1fr" : "1fr",
          gap: 20,
          padding: isMobile ? 16 : 20,
          overflow: "hidden",
        }}
      >
        {/* left column: controls */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
            height: "fit-content",
          }}
        >
          <Panel title="Filters">
            {loadingEnv || loadingLocations ? (
              <p>Loading data…</p>
            ) : (
              <>
                <EnvironmentSelect
                  options={envs}
                  value={env}
                  onChange={setEnv}
                />
                <div style={{ height: 16 }} />
                <LevelSelect
                  value={level}
                  onChange={setLevel}
                  disabled={!env}
                />
                <div style={{ height: 16 }} />
                <LocationSelect
                  selectedLocation={selectedLocation}
                  onLocationSelect={setSelectedLocation}
                  locations={geographicLocations}
                  loading={loadingLocations}
                />
              </>
            )}
          </Panel>

          <Panel title="View Options">
            <div style={{ display: "flex", gap: 10, marginBottom: 10 }}>
              <button
                onClick={() => setChartType("pie")}
                style={{
                  padding: "8px 16px",
                  borderRadius: "6px",
                  border: "1px solid #ddd",
                  background: chartType === "pie" ? "#667eea" : "white",
                  color: chartType === "pie" ? "white" : "#333",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                Pie Chart
              </button>
              <button
                onClick={() => setChartType("bar")}
                style={{
                  padding: "8px 16px",
                  borderRadius: "6px",
                  border: "1px solid #ddd",
                  background: chartType === "bar" ? "#667eea" : "white",
                  color: chartType === "bar" ? "white" : "#333",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                Bar Chart
              </button>
            </div>
            <small style={{ color: "#666" }}>
              Switch between chart types to explore your data differently.
            </small>
          </Panel>

          {selectedLocation && (
            <Panel title="🌍 Location Data">
              <LocationData selectedLocation={selectedLocation} />
            </Panel>
          )}
        </div>

        {/* right column: chart */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            // height: "100%",
            overflow: "hidden",
            paddingBottom: isMobile ? 0 : 50,
          }}
        >
          {error && (
            <div
              style={{
                color: "#ff6b6b",
                marginBottom: 16,
                padding: "12px 16px",
                background: "rgba(255, 107, 107, 0.1)",
                borderRadius: "8px",
                border: "1px solid rgba(255, 107, 107, 0.3)",
              }}
            >
              {error}
            </div>
          )}
          {!env && !selectedLocation && (
            <div
              style={{
                color: "rgba(255, 255, 255, 0.8)",
                textAlign: "center",
                padding: "40px",
                fontSize: "1.2rem",
              }}
            >
              Select an environment or geographic location to see results.
            </div>
          )}
          {!env && selectedLocation && selectedLocation.trim() === "" && (
            <div
              style={{
                color: "rgba(255, 255, 255, 0.8)",
                textAlign: "center",
                padding: "40px",
                fontSize: "1.2rem",
              }}
            >
              Select an environment or geographic location to see results.
            </div>
          )}
          {data && (
            <div style={{ flex: 1, minHeight: 0 }}>
              <CompositionChart data={data} kind={chartType} />
            </div>
          )}
        </div>
      </div>

      {/* Loading Modal */}
      <LoadingModal isVisible={loadingData} message={loadingMessage} />
    </div>
  );
}
