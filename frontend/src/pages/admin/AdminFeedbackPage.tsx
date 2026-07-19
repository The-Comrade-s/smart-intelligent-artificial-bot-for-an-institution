import { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { FeedbackItem, FeedbackSummary, getFeedbackSummary, listFeedback, respondToFeedback } from "../../lib/adminApi";
import StatCard from "../../components/StatCard";
import { MessageSquare, ThumbsUp, ThumbsDown, Bug } from "lucide-react";

export default function AdminFeedbackPage() {
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [summary, setSummary] = useState<FeedbackSummary | null>(null);
  const [responses, setResponses] = useState<Record<string, string>>({});

  async function load() {
    setItems(await listFeedback());
    setSummary(await getFeedbackSummary());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRespond(id: string) {
    const text = responses[id];
    if (!text?.trim()) return;
    const updated = await respondToFeedback(id, text);
    setItems((prev) => prev.map((f) => (f.id === id ? updated : f)));
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-navy-900">Feedback</h1>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard icon={MessageSquare} label="Total Feedback" value={summary?.total_feedback ?? "—"} />
        <StatCard icon={ThumbsUp} label="Positive" value={summary?.positive_count ?? "—"} />
        <StatCard icon={ThumbsDown} label="Negative" value={summary?.negative_count ?? "—"} />
        <StatCard icon={Bug} label="Bug Reports" value={summary?.bug_reports ?? "—"} />
      </div>

      <div className="space-y-3">
        {items.map((f) => (
          <div key={f.id} className="card space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {f.rating && (
                  <span className="flex items-center gap-0.5 text-amber-500">
                    {Array.from({ length: f.rating }).map((_, i) => (
                      <Star key={i} className="h-3.5 w-3.5 fill-amber-500" />
                    ))}
                  </span>
                )}
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase text-slate-500">{f.category}</span>
              </div>
              <span className="text-xs text-slate-400">{new Date(f.created_at).toLocaleDateString()}</span>
            </div>
            {f.comment && <p className="text-sm text-slate-700">{f.comment}</p>}

            {f.admin_response ? (
              <p className="rounded-xl bg-royal-50 px-3 py-2 text-xs text-royal-700">
                <span className="font-semibold">Admin response: </span>
                {f.admin_response}
              </p>
            ) : (
              <div className="flex gap-2">
                <input
                  className="input-field text-xs"
                  placeholder="Write a response…"
                  value={responses[f.id] ?? ""}
                  onChange={(e) => setResponses((prev) => ({ ...prev, [f.id]: e.target.value }))}
                />
                <button onClick={() => handleRespond(f.id)} className="btn-secondary shrink-0 text-xs">
                  Respond
                </button>
              </div>
            )}
          </div>
        ))}
        {items.length === 0 && <p className="text-center text-sm text-slate-400">No feedback yet.</p>}
      </div>
    </div>
  );
}
