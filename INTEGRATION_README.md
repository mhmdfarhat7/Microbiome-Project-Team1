# 🧬 M1-M2-M3 Integration Guide

This project now integrates all three components:
- **M1**: Data cleaning and EDA
- **M2**: Backend analysis and API server  
- **M3**: React frontend with Chart.js visualizations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Install Node.js dependencies (for M3 frontend)
cd frontend
npm install
cd ..
```

### 2. Run M1 Data Cleaning (if needed)
```bash
# Generate cleaned metadata for M2
python3 "M1/load&proccess.py"
```

### 3. Test the Integration
```bash
# Run integration tests
python3 test_integration.py
```

### 4. Start the System
```bash
# Terminal 1: Start M2 API server
python3 src/api_server.py

# Terminal 2: Start M3 frontend
cd frontend
npm run dev
```

### 5. Open Your Browser
- **M3 Frontend**: http://localhost:5173 (or URL shown in terminal)
- **M2 API**: http://localhost:5000/api

## 📁 Project Structure

```
.
├── M1/                          # Data cleaning scripts
│   ├── load&proccess.py        # Generates cleaned metadata
│   └── biorun_eda.py          # EDA on filtered data
├── src/                        # M2 Backend
│   ├── backend.py             # CLI interface (unchanged)
│   ├── utils.py               # Core analysis functions (unchanged)
│   ├── backend_lib.py         # M3 integration library (NEW)
│   └── api_server.py          # Flask API server (NEW)
├── frontend/                   # M3 React Frontend
│   ├── src/
│   │   ├── services/
│   │   │   ├── api.js         # Real API calls to M2 (NEW)
│   │   │   └── api.mock.js    # Mock data (kept for reference)
│   │   └── App.jsx            # Main React component
│   └── package.json
├── data/                       # Processed data
│   └── processed/
│       └── biorun_metadata_clean.parquet  # M1 output
├── Microbe-vis-data/          # Raw data (gitignored)
└── requirements.txt            # Python dependencies
```

## 🔄 Data Flow

```
Raw Data (Microbe-vis-data/) 
    ↓
M1: load&proccess.py 
    ↓
Cleaned Metadata (data/processed/)
    ↓
M2: backend_lib.py + api_server.py
    ↓
REST API (localhost:5000)
    ↓
M3: React Frontend (localhost:5173)
```

## 🌐 API Endpoints

### M2 Backend API Server

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/environments` | GET | List available environments |
| `/api/environments?top=N` | GET | Top N environments by biorun count |
| `/api/composition/<env>` | GET | Get phylum composition for environment |
| `/api/composition/<env>?top=N` | GET | Get top N phyla for environment |
| `/api/stats` | GET | Get data statistics |

### Example API Calls

```bash
# Get all environments
curl http://localhost:5000/api/environments

# Get top 10 environments
curl http://localhost:5000/api/environments?top=10

# Get soil metagenome composition (top 5 phyla)
curl http://localhost:5000/api/composition/soil%20metagenome?top=5

# Check API health
curl http://localhost:5000/api/health
```

## 🧪 Testing

### Test M2 Backend Library
```bash
python3 -c "
from src.backend_lib import get_environments, get_phylum_composition
print('Environments:', get_environments(top=5))
print('Soil composition:', get_phylum_composition('soil metagenome', top=3))
"
```

### Test API Server
```bash
python3 test_integration.py
```

### Test M3 Frontend
1. Start API server: `python3 src/api_server.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser and test dropdown + charts

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Make sure you're in the project root
pwd  # Should show /path/to/Microbiome-Project-Team1
```

**2. "Data file not found" errors**
```bash
# Run M1 data cleaning first
python3 "M1/load&proccess.py"
```

**3. "Port already in use" errors**
```bash
# Kill existing processes on port 5000
lsof -ti:5000 | xargs kill -9
```

**4. Frontend can't connect to API**
```bash
# Check API server is running
curl http://localhost:5000/api/health

# Check CORS is enabled in api_server.py
```

### Debug Mode

```bash
# Start API server with debug info
FLASK_DEBUG=1 python3 src/api_server.py

# Check frontend console for errors
# Open browser dev tools → Console tab
```

## 📊 Available Environments

The system currently supports these environments (from M1 data cleaning):
- `human gut metagenome` (185,541 bioruns)
- `soil metagenome` (41,909 bioruns)  
- `marine metagenome` (15,783 bioruns)
- `mouse gut metagenome` (21,199 bioruns)
- And many more!

## 🎯 Next Steps

1. **Test the integration** with `python3 test_integration.py`
2. **Start both services** (API server + frontend)
3. **Explore different environments** in the M3 frontend
4. **Customize visualizations** in the M3 Chart.js components
5. **Add more analysis levels** (class, order, family) if needed

## 🤝 Team Integration

- **M1 Team**: Data is ready in `data/processed/`
- **M2 Team**: Backend + API server ready
- **M3 Team**: Frontend connected to real data

The integration is complete and ready for production use! 🎉
