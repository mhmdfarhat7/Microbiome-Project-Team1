import { useState, useEffect, useRef } from "react";
import { createPortal } from "react-dom";

// List of values to filter out (non-countries)
const FILTERED_VALUES = [
  "missing",
  "non",
  "unknown",
  "not applicable",
  "na",
  "n/a",
  "none",
  "null",
  "undefined",
  "other",
  "miscellaneous",
];

export default function LocationSelect({
  onLocationSelect,
  selectedLocation,
  locations = [],
  loading = false,
}) {
  const [filteredLocations, setFilteredLocations] = useState([]);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef(null);
  const [dropdownPosition, setDropdownPosition] = useState({
    top: 0,
    left: 0,
    width: 0,
  });

  useEffect(() => {
    const handleResize = () => {
      if (isOpen) {
        updateDropdownPosition();
      }
    };

    window.addEventListener("resize", handleResize);
    window.addEventListener("scroll", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("scroll", handleResize);
    };
  }, [isOpen]);

  useEffect(() => {
    // Filter locations based on search term and remove non-country values
    const filtered = (locations || []).filter((location) => {
      const lowerLocation = location.toLowerCase();
      const lowerSearch = searchTerm.toLowerCase();

      // Filter out non-country values
      if (
        FILTERED_VALUES.some((filtered) => lowerLocation.includes(filtered))
      ) {
        return false;
      }

      // Apply search filter
      return lowerLocation.includes(lowerSearch);
    });

    setFilteredLocations(filtered);
  }, [locations, searchTerm]);

  const handleLocationSelect = (location) => {
    onLocationSelect(location);
    setIsOpen(false);
    setSearchTerm("");
  };

  const handleClearSelection = () => {
    onLocationSelect("");
    setSearchTerm("");
    setIsOpen(false);
  };

  const handleInputChange = (e) => {
    setSearchTerm(e.target.value);
    setIsOpen(true);
  };

  const updateDropdownPosition = () => {
    if (inputRef.current) {
      const rect = inputRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY,
        left: rect.left + window.scrollX,
        width: rect.width,
      });
    }
  };

  const handleInputFocus = () => {
    updateDropdownPosition();
    setIsOpen(true);
  };

  const handleInputBlur = () => {
    // Delay closing to allow for click events
    setTimeout(() => setIsOpen(false), 200);
  };

  if (loading) {
    return (
      <label
        style={{
          display: "block",
          fontSize: 14,
          fontWeight: "500",
          color: "#333",
        }}
      >
        🌍 Geographic Location
        <div
          style={{
            display: "block",
            marginTop: 8,
            padding: "12px 16px",
            width: "100%",
            borderRadius: "8px",
            border: "2px solid #e1e5e9",
            backgroundColor: "#f8f9fa",
            fontSize: "14px",
            color: "#666",
            fontStyle: "italic",
          }}
        >
          Loading locations...
        </div>
      </label>
    );
  }

  if (error) {
    return (
      <label
        style={{
          display: "block",
          fontSize: 14,
          fontWeight: "500",
          color: "#333",
        }}
      >
        🌍 Geographic Location
        <div
          style={{
            display: "block",
            marginTop: 8,
            padding: "12px 16px",
            width: "100%",
            borderRadius: "8px",
            border: "2px solid #e74c3c",
            backgroundColor: "rgba(231, 76, 60, 0.1)",
            fontSize: "14px",
            color: "#e74c3c",
          }}
        >
          Error: {error}
        </div>
      </label>
    );
  }

  return (
    <label
      style={{
        display: "block",
        fontSize: 14,
        fontWeight: "500",
        color: "#333",
      }}
    >
      🌍 Geographic Location
      <div style={{ position: "relative", zIndex: 10 }}>
        <input
          ref={inputRef}
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          placeholder={selectedLocation || "Search for a location..."}
          style={{
            display: "block",
            marginTop: 8,
            padding: "12px 16px",
            width: "100%",
            borderRadius: "8px",
            border: "2px solid #e1e5e9",
            backgroundColor: "white",
            fontSize: "14px",
            color: "#333",
            cursor: "pointer",
            transition: "border-color 0.2s ease, box-shadow 0.2s ease",
            outline: "none",
            boxSizing: "border-box",
          }}
          onFocus={(e) => {
            handleInputFocus();
            e.target.style.borderColor = "#667eea";
            e.target.style.boxShadow = "0 0 0 3px rgba(102, 126, 234, 0.1)";
          }}
          onBlur={(e) => {
            handleInputBlur();
            e.target.style.borderColor = "#e1e5e9";
            e.target.style.boxShadow = "none";
          }}
        />

        {isOpen &&
          filteredLocations.length > 0 &&
          createPortal(
            <div
              style={{
                position: "absolute",
                top: dropdownPosition.top,
                left: dropdownPosition.left,
                width: dropdownPosition.width,
                backgroundColor: "white",
                border: "2px solid #e1e5e9",
                borderTop: "none",
                borderRadius: "0 0 8px 8px",
                maxHeight: "200px",
                overflowY: "auto",
                zIndex: 9999,
                boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
              }}
            >
              {filteredLocations.map((location, index) => (
                <div
                  key={index}
                  onClick={() => handleLocationSelect(location)}
                  style={{
                    padding: "12px 16px",
                    cursor: "pointer",
                    borderBottom: "1px solid #f0f0f0",
                    transition: "background-color 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = "#f8f9fa";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = "white";
                  }}
                >
                  {location}
                </div>
              ))}
            </div>,
            document.body
          )}

        {isOpen &&
          filteredLocations.length === 0 &&
          searchTerm &&
          createPortal(
            <div
              style={{
                position: "absolute",
                top: dropdownPosition.top,
                left: dropdownPosition.left,
                width: dropdownPosition.width,
                backgroundColor: "white",
                border: "2px solid #e1e5e9",
                borderTop: "none",
                borderRadius: "0 0 8px 8px",
                padding: "12px 16px",
                color: "#666",
                fontStyle: "italic",
                zIndex: 9999,
              }}
            >
              No locations found
            </div>,
            document.body
          )}
      </div>
      {selectedLocation && (
        <div
          style={{
            marginTop: 8,
            padding: "8px 12px",
            background: "rgba(102, 126, 234, 0.1)",
            border: "1px solid rgba(102, 126, 234, 0.3)",
            borderRadius: "6px",
            fontSize: "13px",
            color: "#667eea",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>
            📍 Selected: <strong>{selectedLocation}</strong>
          </span>
          <button
            onClick={handleClearSelection}
            style={{
              background: "none",
              border: "none",
              color: "#667eea",
              cursor: "pointer",
              fontSize: "16px",
              padding: "4px",
              borderRadius: "4px",
              transition: "background-color 0.2s ease",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = "rgba(102, 126, 234, 0.2)";
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = "transparent";
            }}
            title="Clear selection"
          >
            ✕
          </button>
        </div>
      )}
    </label>
  );
}
