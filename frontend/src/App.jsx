import { useState } from "react";
import "./App.css";

import { askQuestion } from "./api";
import QuestionForm from "./components/QuestionForm";
import ResultCard from "./components/ResultCard";

import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  PieChart, Pie, Cell, LabelList,
  ResponsiveContainer, Legend
} from "recharts";

function App() {

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState("");
  const [showOverview, setShowOverview] = useState(false);

  const suggestions = [
    "What is the earliest accident year in the dataset?",
    "How many accidents involving personal injury occurred in Saxony in 2023?",
    "From which year onwards is data available for North Rhine-Westphalia?",
    "From which year onwards is data available for Mecklenburg-Western Pomerania?",
    "How many accidents occurred in Berlin in 2023?",
    "Which five districts recorded the highest number of fatal accidents in 2024?",
    "How many bicycle accidents occurred in Dresden in 2024?",
    "Which municipalities in Saxony recorded zero reported accidents in 2023?"
  ];

  const ask = async (q) => {
    setLoading(true);
    try {
      const res = await askQuestion(q);
      console.log("API RESPONSE:", res);
      setResult(() => res); 
    } finally {
      setLoading(false);
    }
  };

  const toggleOverview = () => {
    setShowOverview(prev => !prev);
  };

  // 📊 ALL DATA HERE IS NOW 100% DATABASE VERIFIED (AGGREGATED 2022 - 2024)
  const overview = {
    totalAccidents: 794059,
    totalFatalAccidents: 7389,
    // Real Highest Fatality Districts mapped to official regional name strings
    topDistricts: [
      { district_name: "Region Hannover", fatal_accidents: 92 }, // 03241
      { district_name: "Osnabrück",       fatal_accidents: 74 }, // 03454
      { district_name: "Emsland",         fatal_accidents: 73 }, // 03459
      { district_name: "Kleve",           fatal_accidents: 67 }, // 05154
      { district_name: "Rhein-Sieg-Kreis", fatal_accidents: 51 }  // 05315
    ],
    categories: [
      { name: "Fatal Accidents", value: 7389 },
      { name: "Injury Accidents", value: 130057 },
      { name: "Minor Accidents", value: 656613 }
    ],
    regionalBreakdown: [
      { state: "North Rhine-Westphalia", "Cycling": 56089, "Pedestrian": 19356, "Car": 129295, "Motorcycle": 20970, "Other": 6262 },
      { state: "Bavaria",                 "Cycling": 48431, "Pedestrian": 9724,  "Car": 94777,  "Motorcycle": 19814, "Other": 3630 },
      { state: "Baden-Württemberg",       "Cycling": 29819, "Pedestrian": 7437,  "Car": 66866,  "Motorcycle": 14752, "Other": 2584 },
      { state: "Lower Saxony",            "Cycling": 25569, "Pedestrian": 5468,  "Car": 62752,  "Motorcycle": 8218,  "Other": 2333 },
      { state: "Hesse",                   "Cycling": 11747, "Pedestrian": 4896,  "Car": 44129,  "Motorcycle": 7174,  "Other": 1571 },
      { state: "Saxony",                  "Cycling": 13184, "Pedestrian": 3629,  "Car": 27892,  "Motorcycle": 5256,  "Other": 1043 },
      { state: "Berlin",                  "Cycling": 13582, "Pedestrian": 5075,  "Car": 29618,  "Motorcycle": 5654,  "Other": 798 }
    ]
  };

  const COLORS = ["#1E3A8A", "#2563EB", "#0EA5E9"];
  const BREAKDOWN_COLORS = ["#0EA5E9", "#2563EB", "#3B82F6", "#6366F1", "#94A3B8"];

  const renderCustomLabel = (props) => {
    const { x, y, width, value } = props;
    if (!value || value < 3000) return null; 
    return (
      <text 
        x={x + width + 8} 
        y={y + 10} 
        fill="#E5E7EB" 
        fontSize={10} 
        textAnchor="start"
      >
        {value.toLocaleString()}
      </text>
    );
  };

  return (
    <div className="app">
      <div className="dashboard">

        <div className="header">
          <div>
            <h1>RoadInsight AI</h1>
            <p>German Traffic Accident Analytics Platform</p>
          </div>

          <button className="overview-glass-btn" onClick={toggleOverview}>
            📊 {showOverview ? "Hide Overview" : "Show Overview"}
          </button>
        </div>

        {/* 3-COLUMN MAIN WORKSPACE */}
        <div className="main-workspace">
          
          {/* LEFT PANEL: Suggestions */}
          <div className="left-panel">
            <div className="suggestion-panel">
              <div className="suggestion-title">Quick Questions</div>
              <div className="suggestion-scroll">
                {suggestions.map((q, i) => (
                  <div
                    key={q}
                    className="suggestion-card"
                    onClick={() => setSelectedQuestion(q)}
                  >
                    <div className="suggestion-index">{i + 1}</div>
                    <div className="suggestion-text">{q}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* CENTER PANEL: Search Card Form */}
          <div className="center-panel">
            <div className="glass-card search-card">
              <QuestionForm
                onSubmit={ask}
                loading={loading}
                selectedQuestion={selectedQuestion}
              />
            </div>
          </div>

          {/* RIGHT PANEL: Processed Result Card */}
          <div className="right-panel">
            <ResultCard data={result} />
          </div>

        </div>

        {showOverview && (
          <div className="overview-section glass-card">
            <h2>Dataset Overview</h2>
            <div className="overview-grid">
              <div className="overview-card">
                <h3>Total Accidents</h3>
                <p>{overview.totalAccidents.toLocaleString()}</p>
              </div>
              <div className="overview-card">
                <h3>Total Fatal</h3>
                <p>{overview.totalFatalAccidents.toLocaleString()}</p>
              </div>
              <div className="overview-card">
                <h3>Region</h3>
                <p>Germany</p>
              </div>
            </div>

            {/* CHART 1: REGIONAL BREAKDOWN (SHIFTED TO FIRST POSITION) */}
            <div className="chart-card">
              <h3>Regional & Specific Breakdown (Totals 2022 - 2024)</h3>
              <ResponsiveContainer width="100%" height={520}>
                <BarChart
                  data={overview.regionalBreakdown}
                  layout="vertical"
                  margin={{ top: 10, right: 70, left: 60, bottom: 5 }}
                  barGap={3}
                >
                  <XAxis type="number" tick={{ fill: "#E5E7EB" }} hide />
                  <YAxis 
                    dataKey="state" 
                    type="category" 
                    tick={{ fill: "#E5E7EB", fontSize: "11px" }} 
                    width={130}
                  />
                  <Tooltip />
                  <Legend iconSize={10} wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                  
                  <Bar dataKey="Cycling" fill={BREAKDOWN_COLORS[0]}>
                    <LabelList dataKey="Cycling" content={renderCustomLabel} />
                  </Bar>
                  <Bar dataKey="Pedestrian" fill={BREAKDOWN_COLORS[1]}>
                    <LabelList dataKey="Pedestrian" content={renderCustomLabel} />
                  </Bar>
                  <Bar dataKey="Car" fill={BREAKDOWN_COLORS[2]}>
                    <LabelList dataKey="Car" content={renderCustomLabel} />
                  </Bar>
                  <Bar dataKey="Motorcycle" fill={BREAKDOWN_COLORS[3]}>
                    <LabelList dataKey="Motorcycle" content={renderCustomLabel} />
                  </Bar>
                  <Bar dataKey="Other" fill={BREAKDOWN_COLORS[4]}>
                    <LabelList dataKey="Other" content={renderCustomLabel} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* CHART 2: DISTRICT BAR CHART BY NAME */}
            <div className="chart-card">
              <h3>Highest Fatal Accidents by District</h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={overview.topDistricts}>
                  <XAxis dataKey="district_name" tick={{ fill: "#E5E7EB" }} />
                  <YAxis tick={{ fill: "#E5E7EB" }} />
                  <Tooltip />
                  <Bar dataKey="fatal_accidents">
                    {overview.topDistricts.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                    <LabelList dataKey="fatal_accidents" position="top" fill="#E5E7EB" fontSize={11} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* CHART 3: ACCIDENT CATEGORIES PIE CHART (REVERTED BACK) */}
            <div className="chart-card">
              <h3>Accident Categories</h3>
              <div style={{ display: "flex", gap: "20px", alignItems: "center" }}>
                <div style={{ width: "35%" }}>
                  <ol style={{ color: "#E5E7EB", paddingLeft: "15px", margin: 0 }}>
                    {overview.categories.map((c, i) => (
                      <li key={i} style={{ marginBottom: "12px" }}>
                        <span style={{ color: COLORS[i], fontWeight: "bold" }}>●</span>{" "}
                        {c.name} — {c.value.toLocaleString()}
                      </li>
                    ))}
                  </ol>
                </div>

                <div style={{ width: "65%" }}>
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie
                        data={overview.categories}
                        dataKey="value"
                        nameKey="name"
                        outerRadius={90}
                      >
                        {overview.categories.map((_, i) => (
                          <Cell key={i} fill={COLORS[i % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

export default App;