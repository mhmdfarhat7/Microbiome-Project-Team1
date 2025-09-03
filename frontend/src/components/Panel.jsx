export default function Panel({ title, children }) {
    return (
      <section style={{ 
        background: "rgba(255, 255, 255, 0.95)", 
        borderRadius: 16, 
        padding: 20, 
        boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
        backdropFilter: "blur(10px)",
        border: "1px solid rgba(255, 255, 255, 0.2)",
        transition: "transform 0.2s ease, box-shadow 0.2s ease"
      }}>
        <h3 style={{ 
          marginTop: 0, 
          marginBottom: 16, 
          fontSize: 20,
          fontWeight: "600",
          color: "#333",
          borderBottom: "2px solid #f0f0f0",
          paddingBottom: 12
        }}>
          {title}
        </h3>
        {children}
      </section>
    );
  }
  