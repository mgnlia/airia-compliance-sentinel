import { reviews, severityColor } from "@/lib/mock-data";

const statusStyle: Record<string, string> = {
  pending: "bg-blue-500/20 text-blue-400",
  approved: "bg-green-500/20 text-green-400",
  dismissed: "bg-gray-500/20 text-gray-400",
  escalated: "bg-purple-500/20 text-purple-400",
};

export default function ReviewsPage() {
  const pending = reviews.filter((r) => r.status === "pending");
  const resolved = reviews.filter((r) => r.status !== "pending");
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">HITL Reviews</h1>

      <div>
        <h2 className="text-lg font-semibold mb-4 text-yellow-400">⏳ Pending ({pending.length})</h2>
        <div className="space-y-3">
          {pending.map((r) => (
            <div key={r.id} className="bg-sentinel-card border border-sentinel-border rounded-xl p-5">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor[r.severity]}`}>
                    {r.severity.toUpperCase()}
                  </span>
                  <div>
                    <h3 className="font-medium">{r.title}</h3>
                    <p className="text-xs text-gray-500 mt-1">Assigned to: {r.assignee} · {r.createdAt}</p>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <button className="px-3 py-1.5 text-xs rounded-lg bg-green-600/20 text-green-400 border border-green-600/30 hover:bg-green-600/30 transition-colors">✓ Approve</button>
                  <button className="px-3 py-1.5 text-xs rounded-lg bg-gray-600/20 text-gray-400 border border-gray-600/30 hover:bg-gray-600/30 transition-colors">✕ Dismiss</button>
                  <button className="px-3 py-1.5 text-xs rounded-lg bg-purple-600/20 text-purple-400 border border-purple-600/30 hover:bg-purple-600/30 transition-colors">⬆ Escalate</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-4 text-gray-400">✅ Resolved ({resolved.length})</h2>
        <div className="space-y-3">
          {resolved.map((r) => (
            <div key={r.id} className="bg-sentinel-card/50 border border-sentinel-border rounded-xl p-5 opacity-70">
              <div className="flex items-start gap-3">
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${statusStyle[r.status]}`}>
                  {r.status.toUpperCase()}
                </span>
                <div>
                  <h3 className="font-medium">{r.title}</h3>
                  <p className="text-xs text-gray-500 mt-1">{r.assignee} · {r.createdAt}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
