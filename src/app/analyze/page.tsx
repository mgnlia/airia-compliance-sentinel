export default function AnalyzePage() {
  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">Manual Analysis</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { title: "PR Analysis", icon: "🔀", placeholder: "Paste PR diff or enter PR URL...", desc: "Analyze a GitHub Pull Request for compliance issues" },
          { title: "Slack Message", icon: "💬", placeholder: "Paste Slack message content...", desc: "Check a Slack message for policy violations" },
          { title: "Document", icon: "📄", placeholder: "Paste document text or URL...", desc: "Scan a document for outdated compliance language" },
        ].map((t) => (
          <div key={t.title} className="bg-sentinel-card border border-sentinel-border rounded-xl p-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">{t.icon}</span>
              <h2 className="text-lg font-semibold">{t.title}</h2>
            </div>
            <p className="text-sm text-gray-400 mb-4">{t.desc}</p>
            <textarea
              className="w-full h-32 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500 resize-none"
              placeholder={t.placeholder}
            />
            <button className="mt-3 w-full py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors">
              Analyze
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
