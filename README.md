# Microbe Composition Viewer

A comprehensive web application for visualizing microbial composition data across different taxonomic levels and geographic locations.

## 🌟 Features

- **Multi-level Taxonomic Analysis**: Explore microbial data at phylum, class, order, family, and genus levels
- **Geographic Filtering**: Filter data by specific geographic locations
- **Interactive Visualizations**: Beautiful pie charts and bar charts with Chart.js
- **Real-time Data Processing**: Fast data loading with PyArrow and chunked processing
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Smart Caching**: Intelligent caching system for improved performance

## 🏗️ Architecture

The system consists of three main components:

### Backend (Python/Flask)

- **API Server** (`src/api_server.py`): RESTful API endpoints
- **Data Processing** (`src/backend_lib.py`): Core business logic
- **Utilities** (`src/utils.py`): Data loading and processing functions

### Frontend (React/Vite)

- **Modern React App**: Built with Vite for fast development
- **Interactive Components**: Custom components for data selection and visualization
- **Responsive UI**: Mobile-first design with beautiful gradients

### Data Pipeline

- **M1**: Data cleaning and preprocessing
- **M2**: Statistical analysis and composition calculations
- **M3**: Web interface and visualization
- **M4**: Advanced data analysis and feature extraction
- **M5**: Multi-level taxonomic analysis (class, order, family, genus)

## 📊 Data Flow

1. **Environment Selection**: Choose from available microbial environments
2. **Taxonomic Level**: Select analysis level (phylum → genus)
3. **Geographic Filtering**: Optionally filter by geographic location
4. **Data Processing**: Backend processes large datasets efficiently
5. **Visualization**: Interactive charts display composition results

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd DataScienceProject
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install Frontend dependencies**

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Prepare data files**
   - Ensure data files are in the correct directories:
     - `data/processed/` - Processed metadata files
     - `src/` - Taxonomic composition files (soil.summary.\*.compact.parquet)

### Running the Application

1. **Start the Backend API Server**

   ```bash
   cd src
   python api_server.py
   ```

   The API will be available at `http://localhost:5001`

2. **Start the Frontend Development Server**

   ```bash
   cd frontend
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

3. **Open your browser** and navigate to `http://localhost:5173`

## 📁 Project Structure

```
DataScienceProject/
├── src/                          # Backend Python code
│   ├── api_server.py             # Flask API server
│   ├── backend_lib.py            # Core business logic
│   ├── utils.py                  # Data processing utilities
│   └── soil.summary.*.parquet   # Taxonomic data files
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API services
│   │   └── constants/            # App constants
│   └── package.json
├── data/                         # Data files
│   └── processed/                # Processed metadata
├── M1/                          # Data preprocessing
├── M4/                          # Advanced data analysis
├── M5/                          # Multi-level taxonomic analysis
└── requirements.txt             # Python dependencies
```

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `GET /api/environments` - List available environments
- `GET /api/composition/<env>?level=<level>&top=<n>` - Get composition data
- `GET /api/geographic-locations` - List geographic locations
- `GET /api/location/<location>?level=<level>&top=<n>` - Get location data
- `POST /api/cache/clear` - Clear composition cache
- `GET /api/cache/stats` - Get cache statistics

## 🎨 Usage

1. **Select an Environment**: Choose from the dropdown (e.g., "soil metagenome")
2. **Choose Taxonomic Level**: Select phylum, class, order, family, or genus
3. **Optional Geographic Filter**: Search and select a geographic location
4. **View Results**: Interactive charts show the microbial composition
5. **Switch Views**: Toggle between pie chart and bar chart visualizations

## ⚡ Performance Features

- **Chunked Data Loading**: Large files are processed in chunks using PyArrow
- **Smart Caching**: Results are cached for 5 minutes to improve response times
- **Memory Efficient**: Only loads necessary data for selected filters
- **Background Processing**: Non-blocking data processing

## 🛠️ Development

### Backend Development

```bash
cd src
python api_server.py
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Adding New Taxonomic Levels

1. Add new parquet file to `src/` directory
2. Update `TAXONOMIC_PATHS` in `backend_lib.py`
3. Add level to `LEVELS` array in `LevelSelect.jsx`

## 📝 Data Requirements

The system expects the following data structure:

- **Metadata**: `biorun_metadata_clean.parquet` with columns: `run_accession`, `organism_name`, `biosample`
- **Geographic Data**: `geo_loc_name_with_biosample.csv.gz` with columns: `geo_loc_name`, `biosample`
- **Taxonomic Data**: `soil.summary.{level}.compact.parquet` with biorun as index and taxonomic levels as columns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of a data science course and is for educational purposes.

## 🆘 Troubleshooting

### Common Issues

1. **"Failed to load location composition"**

   - Check if data files are in correct locations
   - Verify file permissions
   - Check server logs for debug information

2. **Frontend not loading**

   - Ensure backend is running on port 5001
   - Check browser console for errors
   - Verify Node.js dependencies are installed

3. **Slow performance**
   - Check if data files are properly indexed
   - Monitor memory usage
   - Consider reducing `top` parameter for fewer results

### Debug Mode

Enable debug logging by checking the server console output when selecting locations. The system provides detailed debug information about data processing steps.

---

**Happy exploring! 🧬🔬**
