import { findings, severityColor } from "@/lib/mock-data";

export default function FindingsPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">All Findings</h1>
        <span className="text-sm text-gray-400">{findings.length} findings</span>
      </div>
      <div className="space-y-3">
        {findings.map((f) => (
          <div key={f.id} className="bg-sentinel-card border border-sentinel-border rounded-xl p-5 hover:border-gray-600 transition-colors">
            <div className="flex items-start gap-3">
              <span className={`px-2 py-0.5 rounded text-xs font-medium border shrink-0 ${severityColor[f.severity]}`}>
                {f.severity.toUpperCase()}
              </span>
              <div className="flex-1">
                <h3 className="font-medium">{f.title}</h3>
                <p className="text-sm text-gray-400 mt-1">{f.description}</p>
                <div className="flex gap-4 mt-3 text-xs text-gray-500">
                  <span>📋 {f.framework}</span>
                  <span>📂 {f.source}</span>
                  <span>🎯 {Math.round(f.confidence * 100)}% confidence</span>
                  <span>🕐 {f.timestamp}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
