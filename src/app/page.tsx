import { riskScore, frameworkScores, agents, findings, severityColor } from "@/lib/mock-data";

function RiskGauge({ score }: { score: number }) {
  const color = score >= 60 ? "text-red-400" : score >= 30 ? "text-yellow-400" : "text-green-400";
  const ringColor = score >= 60 ? "stroke-red-500" : score >= 30 ? "stroke-yellow-500" : "stroke-green-500";
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className="flex flex-col items-center">
      <svg width="160" height="160" className="-rotate-90">
        <circle cx="80" cy="80" r="54" fill="none" stroke="#1f2937" strokeWidth="12" />
        <circle cx="80" cy="80" r="54" fill="none" className={ringColor} strokeWidth="12"
          strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" />
      </svg>
      <div className="absolute mt-12">
        <span className={`text-4xl font-bold ${color}`}>{score}</span>
        <span className="text-gray-500 text-sm block text-center">/100</span>
      </div>
      <p className="mt-2 text-sm text-gray-400">Overall Risk Score</p>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Dashboard</h1>

      {/* Top row: Risk + Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-sentinel-card border border-sentinel-border rounded-xl p-6 flex justify-center relative">
          <RiskGauge score={riskScore} />
        </div>
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          {agents.map((a) => (
            <div key={a.name} className="bg-sentinel-card border border-sentinel-border rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-sm">{a.name}</span>
                <span className={`w-2.5 h-2.5 rounded-full ${a.active ? "bg-green-500 animate-pulse" : "bg-gray-600"}`} />
              </div>
              <p className="text-xs text-gray-500">Last heartbeat: {a.lastHeartbeat}</p>
              <p className="text-lg font-bold mt-1">{a.findingsCount} <span className="text-xs text-gray-500 font-normal">findings</span></p>
            </div>
          ))}
        </div>
      </div>

      {/* Framework scores */}
      <div className="bg-sentinel-card border border-sentinel-border rounded-xl p-6">
        <h2 className="text-lg font-semibold mb-4">Framework Risk Scores</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(frameworkScores).map(([fw, score]) => {
            const color = score >= 60 ? "text-red-400" : score >= 30 ? "text-yellow-400" : "text-green-400";
            const barColor = score >= 60 ? "bg-red-500" : score >= 30 ? "bg-yellow-500" : "bg-green-500";
            return (
              <div key={fw}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">{fw}</span>
                  <span className={color}>{score}</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div className={`${barColor} h-2 rounded-full transition-all`} style={{ width: `${score}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent findings */}
      <div className="bg-sentinel-card border border-sentinel-border rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Recent Findings</h2>
          <a href="/findings" className="text-sm text-blue-400 hover:text-blue-300">View all →</a>
        </div>
        <div className="space-y-3">
          {findings.slice(0, 5).map((f) => (
            <div key={f.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-900/50 hover:bg-gray-800/50 transition-colors">
              <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor[f.severity]}`}>
                {f.severity.toUpperCase()}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{f.title}</p>
                <p className="text-xs text-gray-500 mt-0.5">{f.framework} · {f.source} · {f.timestamp}</p>
              </div>
              <span className="text-xs text-gray-500">{Math.round(f.confidence * 100)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
