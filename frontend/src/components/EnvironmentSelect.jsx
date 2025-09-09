export default function EnvironmentSelect({
  options,
  value,
  onChange,
  disabled,
}) {
  return (
    <label
      style={{
        display: "block",
        fontSize: 14,
        fontWeight: "500",
        color: "#333",
      }}
    >
      Environment
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        style={{
          display: "block",
          marginTop: 8,
          padding: "12px 16px",
          width: "100%",
          borderRadius: "8px",
          border: "2px solid #e1e5e9",
          backgroundColor: disabled ? "#f8f9fa" : "white",
          fontSize: "14px",
          color: "#333",
          cursor: disabled ? "not-allowed" : "pointer",
          transition: "border-color 0.2s ease, box-shadow 0.2s ease",
          outline: "none",
        }}
        onFocus={(e) => {
          if (!disabled) {
            e.target.style.borderColor = "#667eea";
            e.target.style.boxShadow = "0 0 0 3px rgba(102, 126, 234, 0.1)";
          }
        }}
        onBlur={(e) => {
          e.target.style.borderColor = "#e1e5e9";
          e.target.style.boxShadow = "none";
        }}
      >
        <option value="">Select an environment…</option>
        {options.map((env) => (
          <option key={env} value={env}>
            {env}
          </option>
        ))}
      </select>
    </label>
  );
}
