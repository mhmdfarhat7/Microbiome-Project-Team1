// Real API service for M3 frontend to connect to M2 backend

const API_BASE_URL = "http://localhost:5001/api";

export async function fetchEnvironments(top = null) {
  try {
    const url = top
      ? `${API_BASE_URL}/environments?top=${top}`
      : `${API_BASE_URL}/environments`;

    const response = await fetch(url);
    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Failed to fetch environments");
    }

    return data.environments;
  } catch (error) {
    console.error("Error fetching environments:", error);
    throw error;
  }
}

export async function fetchComposition(env, level = "phylum", top = 50) {
  try {
    // For now, we only support phylum level
    if (level !== "phylum") {
      throw new Error("Only phylum level is currently supported");
    }

    const url = `${API_BASE_URL}/composition/${encodeURIComponent(
      env
    )}?top=${top}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Failed to fetch composition");
    }

    // Transform M2 backend data to M3 frontend format
    const composition = data.data;

    // Extract labels and values for Chart.js
    const labels = composition.composition.map((item) => {
      // Clean up phylum names for display
      let cleanName = item.taxon;
      if (cleanName.startsWith("d__Bacteria;p__")) {
        cleanName = cleanName.replace("d__Bacteria;p__", "");
      } else if (cleanName.startsWith("d__Archaea;p__")) {
        cleanName = cleanName.replace("d__Archaea;p__", "");
      }
      return cleanName;
    });

    const values = composition.composition.map((item) => item.mean_percent);

    return {
      labels,
      values,
      metadata: {
        environment: composition.env,
        level: composition.level,
        n_runs: composition.n_runs,
        unassigned_included: composition.unassigned_included,
      },
    };
  } catch (error) {
    console.error("Error fetching composition:", error);
    throw error;
  }
}

export async function fetchStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/stats`);
    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Failed to fetch stats");
    }

    return data.stats;
  } catch (error) {
    console.error("Error fetching stats:", error);
    throw error;
  }
}

export async function fetchGeographicLocations() {
  try {
    const response = await fetch(`${API_BASE_URL}/geographic-locations`);
    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || "Failed to fetch geographic locations");
    }

    return data.geo_locations;
  } catch (error) {
    console.error("Error fetching geographic locations:", error);
    throw error;
  }
}

export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    const data = await response.json();
    return data.status === "healthy";
  } catch (error) {
    console.error("Health check failed:", error);
    return false;
  }
}
