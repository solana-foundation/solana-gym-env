import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import TrajectoryList from "./components/TrajectoryList";
import TrajectoryDetail from "./components/TrajectoryDetail";
import "./App.css";

// Type definitions
export interface RunMetrics {
  run_id: string;
  model: string;
  cumulative_rewards: number[];
  messages: MessageData[];
  programs_discovered: Record<string, number>;
  instructions_by_program?: Record<string, number[]>;
  start_time?: string;
  benchmark?: string; // Added benchmark field
}

export interface MessageData {
  index: number;
  timestamp: string;
  duration: number;
  reward: number;
  total_reward: number;
  instructions_discovered?: Record<string, number[]>;
}

export interface ConversationMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

const App: React.FC = () => {
  const [allRuns, setAllRuns] = useState<RunMetrics[]>([]);
  const [currentBenchmark, setCurrentBenchmark] = useState<string>("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load runs from both benchmarks
    loadAllBenchmarks();
  }, []);

  const loadAllBenchmarks = async () => {
    try {
      const benchmarks = ["basic", "defi"];
      const allRunsData: RunMetrics[] = [];

      for (const benchmark of benchmarks) {
        try {
          const response = await fetch(`/data/${benchmark}/manifest.json`);
          const manifest = await response.json();
          // Add benchmark field to each run
          const runsWithBenchmark = manifest.runs.map((run: RunMetrics) => ({
            ...run,
            benchmark
          }));
          allRunsData.push(...runsWithBenchmark);
        } catch (error) {
          console.error(`Failed to load ${benchmark} benchmark:`, error);
        }
      }

      setAllRuns(allRunsData);
    } catch (error) {
      console.error("Failed to load benchmarks:", error);
      setAllRuns([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter runs based on selected benchmark
  const filteredRuns = currentBenchmark === "all" 
    ? allRuns 
    : allRuns.filter(run => run.benchmark === currentBenchmark);

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <Link to="/" className="logo">
            <h1>🚀 Solana Trajectory Viewer</h1>
          </Link>
          <nav>
            <div className="benchmark-selector">
              <select 
                value={currentBenchmark} 
                onChange={(e) => setCurrentBenchmark(e.target.value)}
                className="benchmark-select"
              >
                <option value="all">All Benchmarks</option>
                <option value="basic">Basic Benchmark</option>
                <option value="defi">DeFi Benchmark</option>
              </select>
            </div>
            <Link to="/">All Runs</Link>
            <a href="/docs" target="_blank">
              Documentation
            </a>
          </nav>
        </header>

        <main className="app-main">
          <Routes>
            <Route
              path="/"
              element={<TrajectoryList runs={filteredRuns} loading={loading} benchmark={currentBenchmark} />}
            />
            <Route path="/run/:runId" element={<TrajectoryDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
