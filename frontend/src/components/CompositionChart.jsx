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
    const colors = [
      '#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe',
      '#43e97b', '#38f9d7', '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3',
      '#d299c2', '#fef9d7', '#667eea', '#764ba2', '#f093fb', '#f5576c'
    ];

    return {
      labels: data?.labels ?? [],
      datasets: [
        {
          label: "Relative abundance (%)",
          data: data?.values ?? [],
          backgroundColor: colors.slice(0, data?.labels?.length || 0),
          borderColor: colors.slice(0, data?.labels?.length || 0).map(color => color + '80'),
          borderWidth: 2,
          hoverBackgroundColor: colors.slice(0, data?.labels?.length || 0).map(color => color + 'CC'),
          hoverBorderColor: colors.slice(0, data?.labels?.length || 0),
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
