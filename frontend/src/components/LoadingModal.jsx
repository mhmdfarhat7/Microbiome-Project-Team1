import React from "react";

export default function LoadingModal({ isVisible, message = "Loading..." }) {
  if (!isVisible) return null;

  return (
    <>
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.7)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
          backdropFilter: "blur(5px)",
          animation: "fadeIn 0.3s ease-out",
        }}
      >
        <div
          style={{
            backgroundColor: "white",
            borderRadius: "20px",
            padding: "50px 70px",
            boxShadow: "0 25px 50px rgba(0, 0, 0, 0.3)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "30px",
            minWidth: "350px",
            maxWidth: "550px",
            textAlign: "center",
            animation: "modalSlideIn 0.4s ease-out",
            border: "1px solid rgba(255, 255, 255, 0.2)",
          }}
        >
          {/* Animated Spinner */}
          <div
            style={{
              width: "80px",
              height: "80px",
              border: "6px solid #f0f0f0",
              borderTop: "6px solid #667eea",
              borderRadius: "50%",
              animation: "spin 1.2s linear infinite",
            }}
          />

          {/* Loading message */}
          <div
            style={{
              fontSize: "20px",
              fontWeight: "700",
              color: "#333",
              margin: 0,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            {message}
          </div>

          {/* Subtitle with dots animation */}
          <div
            style={{
              fontSize: "15px",
              color: "#666",
              margin: 0,
              lineHeight: "1.5",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <span>Processing data</span>
            <span
              style={{
                animation: "dots 1.5s infinite",
              }}
            >
              ...
            </span>
          </div>

          {/* Progress bar */}
          <div
            style={{
              width: "100%",
              height: "4px",
              backgroundColor: "#f0f0f0",
              borderRadius: "2px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: "100%",
                height: "100%",
                background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                borderRadius: "2px",
                animation: "progress 2s ease-in-out infinite",
              }}
            />
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes spin {
          0% {
            transform: rotate(0deg);
          }
          100% {
            transform: rotate(360deg);
          }
        }

        @keyframes modalSlideIn {
          from {
            opacity: 0;
            transform: scale(0.7) translateY(-30px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        @keyframes dots {
          0%,
          20% {
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
          100% {
            opacity: 0;
          }
        }

        @keyframes progress {
          0% {
            transform: translateX(-100%);
          }
          50% {
            transform: translateX(0%);
          }
          100% {
            transform: translateX(100%);
          }
        }
      `}</style>
    </>
  );
}
