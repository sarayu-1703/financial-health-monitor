import { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer
} from "recharts";

// Auto-detect API base: same origin on Vercel, localhost in dev
const API_BASE = import.meta.env.VITE_API_URL || "";

function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const COLORS = [
    "#3B82F6",
    "#8B5CF6",
    "#06B6D4",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#EC4899"
  ];

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/run`, { method: "POST" })
      .then((res) => res.json())
      .then((json) => setData(json))
      .catch((err) => setError(err.toString()));
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(to bottom right, #020617, #0f172a, #111827)",
        color: "white",
        padding: "40px",
        fontFamily: "Inter, Arial"
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "20px",
          marginBottom: "40px"
        }}
      >
        <div>
          <h1
            style={{
              fontSize: "64px",
              fontWeight: "900",
              marginBottom: "10px",
              background:
                "linear-gradient(to right, #60A5FA, #A78BFA, #22D3EE)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}
          >
            Financial Health Monitor
          </h1>

          <p style={{ color: "#94A3B8", fontSize: "18px", marginBottom: "25px" }}>
            AI Powered Financial Analytics Dashboard
          </p>

          <div style={{ display: "flex", gap: "15px", flexWrap: "wrap" }}>
            <a
              href={`${API_BASE}/docs`}
              target="_blank"
              style={{
                textDecoration: "none",
                background: "linear-gradient(to right, #2563EB, #7C3AED)",
                padding: "14px 24px",
                borderRadius: "14px",
                color: "white",
                fontWeight: "600",
                boxShadow: "0 8px 20px rgba(59,130,246,0.3)"
              }}
            >
              Open API Docs
            </a>

            <a
              href={`${API_BASE}/api/v1/history`}
              target="_blank"
              style={{
                textDecoration: "none",
                background: "linear-gradient(to right, #059669, #06B6D4)",
                padding: "14px 24px",
                borderRadius: "14px",
                color: "white",
                fontWeight: "600",
                boxShadow: "0 8px 20px rgba(16,185,129,0.3)"
              }}
            >
              View Analysis History
            </a>
          </div>
        </div>

        {data && (
          <div
            style={{
              padding: "22px 34px",
              borderRadius: "22px",
              background:
                data.overall_status === "RED"
                  ? "rgba(239,68,68,0.15)"
                  : data.overall_status === "AMBER"
                  ? "rgba(245,158,11,0.15)"
                  : "rgba(16,185,129,0.15)",
              border:
                data.overall_status === "RED"
                  ? "1px solid #EF4444"
                  : data.overall_status === "AMBER"
                  ? "1px solid #F59E0B"
                  : "1px solid #10B981",
              backdropFilter: "blur(12px)"
            }}
          >
            <h2 style={{ margin: 0, fontSize: "18px", color: "#CBD5E1" }}>
              Overall Financial Status
            </h2>
            <p style={{ margin: 0, marginTop: "10px", fontSize: "42px", fontWeight: "800" }}>
              {data.overall_status}
            </p>
          </div>
        )}
      </div>

      {error && (
        <div
          style={{
            background: "rgba(239,68,68,0.15)",
            border: "1px solid #EF4444",
            padding: 20,
            borderRadius: 18,
            marginBottom: 30
          }}
        >
          {error}
        </div>
      )}

      {!data ? (
        <div
          style={{
            height: "60vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontSize: "34px",
            fontWeight: "700"
          }}
        >
          Loading Financial Dashboard...
        </div>
      ) : (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))",
              gap: "25px",
              marginBottom: "50px"
            }}
          >
            {data.budget_analysis?.map((item) => (
              <div
                key={item.category}
                style={{
                  background: "rgba(255,255,255,0.05)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "26px",
                  padding: "28px",
                  backdropFilter: "blur(14px)",
                  boxShadow: "0 10px 30px rgba(0,0,0,0.35)"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <h3 style={{ fontSize: "26px", margin: 0 }}>{item.category}</h3>
                  <div
                    style={{
                      padding: "8px 14px",
                      borderRadius: "12px",
                      background:
                        item.status === "OVER BUDGET"
                          ? "rgba(239,68,68,0.15)"
                          : "rgba(16,185,129,0.15)",
                      color:
                        item.status === "OVER BUDGET" ? "#F87171" : "#34D399",
                      fontWeight: "600",
                      fontSize: "13px"
                    }}
                  >
                    {item.status}
                  </div>
                </div>

                <div style={{ marginTop: "28px" }}>
                  <p style={{ color: "#94A3B8", marginBottom: "8px" }}>Total Spent</p>
                  <h2 style={{ margin: 0, fontSize: "38px", fontWeight: "800" }}>
                    ₹{item.spent}
                  </h2>
                </div>

                <div style={{ marginTop: "22px" }}>
                  <p style={{ color: "#94A3B8", marginBottom: "8px" }}>Budget Limit</p>
                  <h3 style={{ margin: 0, fontSize: "26px" }}>₹{item.limit}</h3>
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.3fr 1fr",
              gap: "30px",
              marginBottom: "50px"
            }}
          >
            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                borderRadius: "26px",
                padding: "32px",
                border: "1px solid rgba(255,255,255,0.08)"
              }}
            >
              <h2 style={{ marginTop: 0, marginBottom: "30px", fontSize: "34px" }}>
                Spending Distribution
              </h2>
              <div style={{ width: "100%", height: "420px" }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={data.concentration_analysis}
                      dataKey="percentage"
                      nameKey="category"
                      outerRadius={150}
                      innerRadius={70}
                      paddingAngle={3}
                      label
                    >
                      {data.concentration_analysis.map((entry, index) => (
                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div
              style={{
                background: "rgba(255,255,255,0.05)",
                borderRadius: "26px",
                padding: "32px",
                border: "1px solid rgba(255,255,255,0.08)"
              }}
            >
              <h2 style={{ marginTop: 0, marginBottom: "25px", fontSize: "34px" }}>
                Trend Analysis
              </h2>
              {data.trend_analysis?.map((item) => (
                <div
                  key={item.month}
                  style={{
                    background: "rgba(255,255,255,0.04)",
                    padding: "22px",
                    borderRadius: "18px",
                    marginBottom: "20px"
                  }}
                >
                  <h3 style={{ marginTop: 0, fontSize: "24px" }}>{item.month}</h3>
                  <p style={{ color: "#94A3B8", marginBottom: "8px" }}>Total Spending</p>
                  <h2 style={{ margin: 0, fontSize: "36px" }}>₹{item.total_spent}</h2>
                </div>
              ))}
            </div>
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              borderRadius: "26px",
              padding: "36px",
              marginBottom: "40px",
              border: "1px solid rgba(255,255,255,0.08)"
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: "25px", fontSize: "38px" }}>
              AI Financial Insights
            </h2>
            <div style={{ color: "#CBD5E1", lineHeight: 2, fontSize: "18px", whiteSpace: "pre-wrap" }}>
              {data.ai_insights}
            </div>
          </div>

          <div
            style={{
              background: "rgba(255,255,255,0.05)",
              borderRadius: "26px",
              padding: "36px",
              border: "1px solid rgba(255,255,255,0.08)"
            }}
          >
            <h2 style={{ marginTop: 0, marginBottom: "25px", fontSize: "38px" }}>
              Active Analysis Agents
            </h2>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "15px" }}>
              {data.agents_used?.map((agent) => (
                <div
                  key={agent}
                  style={{
                    background: "linear-gradient(to right, #2563EB, #7C3AED)",
                    padding: "15px 24px",
                    borderRadius: "16px",
                    fontWeight: "700",
                    fontSize: "16px",
                    boxShadow: "0 8px 20px rgba(59,130,246,0.35)"
                  }}
                >
                  {agent}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
