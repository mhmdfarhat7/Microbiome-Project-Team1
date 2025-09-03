import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5001/api';

export default function LocationData({ selectedLocation }) {
  const [locationData, setLocationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (selectedLocation) {
      fetchLocationData(selectedLocation);
    } else {
      setLocationData(null);
    }
  }, [selectedLocation]);

  const fetchLocationData = async (location) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`${API_BASE_URL}/location/${encodeURIComponent(location)}`);
      
      if (response.data.success) {
        setLocationData(response.data.data);
      } else {
        setError(response.data.error || 'Failed to fetch location data');
      }
    } catch (err) {
      setError('Error connecting to API server');
      console.error('Error fetching location data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedLocation) {
    return (
      <div className="location-data">
        <div className="no-selection">
          🌍 Select a geographic location to view microbiome data
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="location-data">
        <div className="loading">
          🔄 Loading data for <strong>{selectedLocation}</strong>...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="location-data">
        <div className="error">
          ❌ Error: {error}
          <button onClick={() => fetchLocationData(selectedLocation)} className="retry-btn">
            🔄 Retry
          </button>
        </div>
      </div>
    );
  }

  if (!locationData) {
    return null;
  }

  return (
    <div className="location-data">
      <div className="location-summary">
        <h3>🌍 {locationData.location}</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-number">{locationData.biosample_count.toLocaleString()}</span>
            <span className="stat-label">Biosamples</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{locationData.biorun_count.toLocaleString()}</span>
            <span className="stat-label">Bioruns</span>
          </div>
        </div>
      </div>

      {locationData.sample_locations && locationData.sample_locations.length > 0 && (
        <div className="sample-locations">
          <h4>📍 Sample Locations</h4>
          <div className="locations-list">
            {locationData.sample_locations.slice(0, 10).map((sample, index) => (
              <div key={index} className="sample-item">
                <div className="sample-biosample">{sample.biosample}</div>
                <div className="sample-coords">{sample.lat_lon || 'No coordinates'}</div>
                <div className="sample-date">{sample.collection_date || 'No date'}</div>
              </div>
            ))}
            {locationData.sample_locations.length > 10 && (
              <div className="more-samples">
                ... and {locationData.sample_locations.length - 10} more samples
              </div>
            )}
          </div>
        </div>
      )}

      {locationData.biorun_data && locationData.biorun_data.length > 0 && (
        <div className="biorun-data">
          <h4>🔬 Biorun Data</h4>
          <div className="biorun-list">
            {locationData.biorun_data.slice(0, 10).map((biorun, index) => (
              <div key={index} className="biorun-item">
                <div className="biorun-accession">{biorun.run_accession}</div>
                <div className="biorun-biosample">{biorun.biosample}</div>
                <div className="biorun-organism">{biorun.organism_name}</div>
              </div>
            ))}
            {locationData.biorun_data.length > 10 && (
              <div className="more-bioruns">
                ... and {locationData.biorun_data.length - 10} more bioruns
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
