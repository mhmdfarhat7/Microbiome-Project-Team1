// temporary mock data so UI works without backend

const ENVIRONMENTS = [
    "soil metagenome",
    "marine metagenome",
    "gut metagenome",
    "freshwater metagenome",
  ];
  
  const MOCK_BY_LEVEL = {
    phylum: {
      labels: ["d__Bacteria", "d__Archaea", "unassigned"],
      values: [63, 35, 2],
    },
    class: {
      labels: ["Gammaproteobacteria", "Bacilli", "Cyanobacteriia", "others"],
      values: [28, 21, 14, 37],
    },
    genus: {
      labels: ["Escherichia", "Bacillus", "Microcystis", "Other"],
      values: [12, 9, 5, 74],
    },
  };
  
  export async function fetchEnvironments() {
    // simulate network delay
    await new Promise(r => setTimeout(r, 300));
    return ENVIRONMENTS;
  }
  
  export async function fetchComposition(env, level = "phylum") {
    await new Promise(r => setTimeout(r, 300));
    return MOCK_BY_LEVEL[level] ?? MOCK_BY_LEVEL["phylum"];
  }
  