import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from "recharts";

export default function ResultCard({ data }) {
  if (!data) {
    return (
      <div className="result-card empty-state">
        <h3>Results</h3>
        <p>Ask a question to see analytics.</p>
      </div>
    );
  }

  if (!data.success) {
    return (
      <div className="result-card error-state">
        <h3>Error</h3>
        <p>{data.message}</p>
      </div>
    );
  }

  const firstRow = Array.isArray(data.results) && data.results[0] ? data.results[0] : {};
  const hasResults = Array.isArray(data.results) && data.results.length > 0;

  // Detect header names dynamically
  let locationHeader = "Location";
  if ("municipality_name" in firstRow || "municipality_code" in firstRow) {
    locationHeader = "Municipality";
  } else if ("district_name" in firstRow || "district_code" in firstRow) {
    locationHeader = "District";
  } else if ("state_name" in firstRow || "state_code" in firstRow) {
    locationHeader = "State";
  } else if ("name" in firstRow) {
    // Fallback if backend just uses generic "name"
    locationHeader = "Location";
  }

  const metricKey = Object.keys(firstRow).find(k => k.includes("accident") || k.includes("count") || k === "value") || "fatal_accidents";
  const metricHeader = metricKey.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");

  const chartData = hasResults 
    ? data.results.map(row => ({
        displayName: row.municipality_name || row.district_name || row.state_name || row.name || row.district_code || "Unknown",
        metricValue: Number(row[metricKey]) || 0
      }))
    : [];

  // 💡 Check if every single returned value is 0 (or if we explicitly filtered for zeroes)
  const isZeroValueQuery = hasResults && chartData.every(item => item.metricValue === 0);

  const CHART_COLORS = ["#3b82f6", "#2563eb", "#1d4ed8", "#1e40af", "#1e3a8a"];

  return (
    <div className="result-card functional-result-card">
      {data.title && <div className="result-title">{data.title}</div>}

      {data.message && <div className="result-summary-text">{data.message}</div>}

      {hasResults && (
        <>
          {isZeroValueQuery ? (
            /* 🌟 ZERO-VALUE LAYOUT: Clean Grid of Location Cards (No full zeroes column, No (undefined)) */
            <div style={{ marginTop: "20px" }}>
              <div style={{ fontSize: "12px", textTransform: "uppercase", color: "#10b981", fontWeight: "600", marginBottom: "14px", letterSpacing: "0.5px", display: "flex", alignItems: "center", gap: "6px" }}>
                <span>🟢</span> Zero Accidents Registered (Perfect Safety Record)
              </div>
              
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "10px" }}>
                {data.results.map((row, index) => {
                  const nameVal = row.municipality_name || row.district_name || row.state_name || row.name;
                  const codeVal = row.municipality_code || row.district_code || row.state_code;
                  
                  // Strict check to completely ignore code indicators if they are null, missing, or undefined strings
                  const hasValidCode = codeVal && codeVal !== "undefined" && codeVal !== "null";

                  return (
                    <div 
                      key={codeVal || index} 
                      style={{ background: "rgba(16, 185, 129, 0.06)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: "12px", padding: "14px", display: "flex", flexDirection: "column", gap: "4px" }}
                    >
                      <span style={{ fontSize: "11px", color: "rgba(16, 185, 129, 0.8)", fontWeight: "700" }}>#{index + 1} {locationHeader}</span>
                      <span style={{ fontWeight: "600", color: "#ffffff", fontSize: "14px" }}>{nameVal || "Unknown"}</span>
                      {hasValidCode && <span style={{ fontSize: "11px", color: "#9ca3af" }}>Code: {codeVal}</span>}
                    </div>
                  );
                })}
              </div>
            </div>
          ) : (
            /* 📊 STANDARD MULTI-VALUE LAYOUT: Split Table & Bar Chart */
            <div style={{ display: "flex", gap: "24px", marginTop: "20px", flexWrap: "wrap" }}>
              <div style={{ flex: "1.2", minWidth: "280px" }}>
                <table className="result-table" style={{ width: "100%" }}>
                  <thead>
                    <tr>
                      <th style={{ width: "50px" }}>Rank</th>
                      <th>{locationHeader}</th>
                      <th className="th-metric">{metricHeader}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.results.map((row, index) => {
                      const nameVal = row.municipality_name || row.district_name || row.state_name || row.name;
                      const codeVal = row.municipality_code || row.district_code || row.state_code;
                      const hasValidCode = codeVal && codeVal !== "undefined" && codeVal !== "null";

                      return (
                        <tr key={codeVal || index}>
                          <td className="rank-badge">#{index + 1}</td>
                          <td>
                            <span className="primary-location-name" style={{ fontWeight: "500" }}>{nameVal || "Unknown"}</span>
                            {hasValidCode && <span className="sub-detail-text" style={{ fontSize: "11px", color: "#9ca3af", marginLeft: "4px" }}>({codeVal})</span>}
                          </td>
                          <td className="th-metric metric-value">
                            {row[metricKey] !== undefined ? row[metricKey].toLocaleString() : 0}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div style={{ flex: "1", minWidth: "240px", background: "rgba(255,255,255,0.02)", borderRadius: "16px", padding: "12px", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div style={{ fontSize: "11px", textTransform: "uppercase", color: "#9ca3af", fontWeight: "600", marginBottom: "12px", letterSpacing: "0.5px" }}>Visual Distribution</div>
                
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 15, left: -20, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="displayName" type="category" tick={{ fill: "#9ca3af", fontSize: "10px" }} width={80} axisLine={false} tickLine={false} />
                    <Tooltip 
                      contentStyle={{ background: "#1f2937", border: "1px solid rgba(255,255,255,0.15)", borderRadius: "8px", fontSize: "12px" }}
                      itemStyle={{ color: "#fff" }}
                      labelStyle={{ color: "#9ca3af" }}
                    />
                    <Bar dataKey="metricValue" radius={[0, 4, 4, 0]} barSize={12}>
                      {chartData.map((_, i) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}

      {!data.message && data.value !== undefined && !data.results && (
        <div className="result-value raw-json-fallback">
          {typeof data.value === "object" ? JSON.stringify(data.value, null, 2) : data.value}
        </div>
      )}
    </div>
  );
}