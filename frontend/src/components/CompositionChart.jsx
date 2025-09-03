import { useMemo } from "react";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function CompositionChart({ data, kind = "pie" }) {
  const chartData = useMemo(() => {
    // Generate unique colors for any number of categories
    const generateColors = (count) => {
      const baseColors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
        '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#82E0AA', '#F1948A', '#D7BDE2', '#F9E79F',
        '#D5A6BD', '#A9CCE3', '#FAD7A0', '#ABEBC6', '#E74C3C',
        '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6', '#1ABC9C',
        '#E67E22', '#34495E', '#16A085', '#8E44AD', '#27AE60'
      ];
      
      // If we need more colors than base colors, generate additional ones
      if (count <= baseColors.length) {
        return baseColors.slice(0, count);
      }
      
      // Generate additional colors using HSL for better distribution
      const additionalColors = [];
      for (let i = baseColors.length; i < count; i++) {
        const hue = (i * 137.508) % 360; // Golden angle approximation for good distribution
        const saturation = 65 + (i % 25); // Vary saturation between 65-90%
        const lightness = 45 + (i % 25); // Vary lightness between 45-70%
        additionalColors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
      }
      
      return [...baseColors, ...additionalColors];
    };

    const numCategories = data?.labels?.length || 0;
    const colors = generateColors(numCategories);

    return {
      labels: data?.labels ?? [],
      datasets: [
        {
          label: "Relative abundance (%)",
          data: data?.values ?? [],
          backgroundColor: colors,
          borderColor: colors.map(color => color + '80'),
          borderWidth: 2,
          hoverBackgroundColor: colors.map(color => color + 'CC'),
          hoverBorderColor: colors,
          hoverBorderWidth: 3,
        },
      ],
    };
  }, [data]);

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: kind === "pie" ? "right" : "top",
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 14,
            weight: '500'
          },
          color: '#333'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: '#667eea',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed || context.raw;
            return `${label}: ${value.toFixed(2)}%`;
          }
        }
      }
    },
    scales: kind === "bar" ? {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          },
          font: {
            size: 12
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      x: {
        ticks: {
          font: {
            size: 12
          }
        },
        grid: {
          display: false
        }
      }
    } : undefined,
    animation: {
      animateRotate: kind === "pie",
      animateScale: true,
      duration: 1000,
      easing: 'easeInOutQuart'
    }
  }), [kind]);

  if (!data) return null;

  return (
    <div style={{ 
      background: "rgba(255, 255, 255, 0.95)", 
      borderRadius: 16, 
      padding: 24, 
      boxShadow: "0 8px 32px rgba(0,0,0,0.1)",
      backdropFilter: "blur(10px)",
      border: "1px solid rgba(255, 255, 255, 0.2)",
      height: "100%",
      display: "flex",
      flexDirection: "column"
    }}>
      <div style={{ 
        marginBottom: 16, 
        textAlign: "center",
        borderBottom: "2px solid #f0f0f0",
        paddingBottom: 16
      }}>
        <h3 style={{ 
          margin: 0, 
          color: "#333", 
          fontSize: "1.4rem",
          fontWeight: "600"
        }}>
          {kind === "pie" ? "Microbial Composition" : "Abundance Distribution"}
        </h3>
        <p style={{ 
          margin: "8px 0 0 0", 
          color: "#666", 
          fontSize: "0.9rem"
        }}>
          {data.labels?.length || 0} different {data.labels?.length === 1 ? 'organism' : 'organisms'} found
        </p>
      </div>
      
      <div style={{ flex: 1, minHeight: 0 }}>
        {kind === "bar" ? (
          <Bar data={chartData} options={chartOptions} />
        ) : (
          <Pie data={chartData} options={chartOptions} />
        )}
      </div>
    </div>
  );
}
