import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { TimeseriesPoint, getUserGrowth } from "../../lib/adminApi";
import { api } from "../../lib/api";

interface TopFAQ {
  question: string;
  views: number;
}
interface TopArticle {
  title: string;
  views: number;
  category: string;
}

export default function AdminAnalyticsPage() {
  const [growth, setGrowth] = useState<TimeseriesPoint[]>([]);
  const [topFaqs, setTopFaqs] = useState<TopFAQ[]>([]);
  const [topArticles, setTopArticles] = useState<TopArticle[]>([]);

  useEffect(() => {
    getUserGrowth(30).then(setGrowth);
    api.get<TopFAQ[]>("/analytics/top-faqs").then((r) => setTopFaqs(r.data));
    api.get<TopArticle[]>("/analytics/top-articles").then((r) => setTopArticles(r.data));
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-navy-900">Analytics</h1>

      <div className="card">
        <h2 className="mb-4 text-sm font-semibold text-navy-900">New User Registrations (last 30 days)</h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={growth}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#2563EB" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-navy-900">Most Viewed FAQs</h2>
          <ul className="space-y-2">
            {topFaqs.map((f, i) => (
              <li key={i} className="flex items-center justify-between text-sm">
                <span className="truncate text-slate-700">{f.question}</span>
                <span className="ml-2 shrink-0 text-xs text-slate-400">{f.views} views</span>
              </li>
            ))}
            {topFaqs.length === 0 && <p className="text-sm text-slate-400">No data yet.</p>}
          </ul>
        </div>

        <div className="card">
          <h2 className="mb-3 text-sm font-semibold text-navy-900">Most Viewed Knowledge Articles</h2>
          <ul className="space-y-2">
            {topArticles.map((a, i) => (
              <li key={i} className="flex items-center justify-between text-sm">
                <span className="truncate text-slate-700">{a.title}</span>
                <span className="ml-2 shrink-0 text-xs text-slate-400">{a.views} views</span>
              </li>
            ))}
            {topArticles.length === 0 && <p className="text-sm text-slate-400">No data yet.</p>}
          </ul>
        </div>
      </div>
    </div>
  );
}
