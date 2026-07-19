import { useEffect, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from "recharts";
import { Users, MessageSquare, BookOpen, GraduationCap, Megaphone, Clock } from "lucide-react";
import StatCard from "../../components/StatCard";
import {
  DashboardStats,
  ProviderUsagePoint,
  TimeseriesPoint,
  getConversationsTimeseries,
  getDashboardStats,
  getProviderUsage,
} from "../../lib/adminApi";

const COLORS = ["#2563EB", "#38BDF8", "#0F172A", "#94A3B8"];

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeseries, setTimeseries] = useState<TimeseriesPoint[]>([]);
  const [providerUsage, setProviderUsage] = useState<ProviderUsagePoint[]>([]);

  useEffect(() => {
    getDashboardStats().then(setStats);
    getConversationsTimeseries(14).then(setTimeseries);
    getProviderUsage().then(setProviderUsage);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-navy-900">Dashboard</h1>
        <p className="text-sm text-slate-500">Live overview of COSIB usage and content.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <StatCard icon={Users} label="Students" value={stats?.total_students ?? "—"} />
        <StatCard icon={MessageSquare} label="Conversations" value={stats?.total_conversations ?? "—"} />
        <StatCard icon={MessageSquare} label="Today's Conversations" value={stats?.todays_conversations ?? "—"} />
        <StatCard icon={BookOpen} label="KB Articles" value={stats?.knowledge_articles ?? "—"} />
        <StatCard icon={GraduationCap} label="Courses" value={stats?.courses ?? "—"} />
        <StatCard icon={Megaphone} label="Announcements" value={stats?.announcements ?? "—"} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-2">
          <h2 className="mb-4 text-sm font-semibold text-navy-900">Conversations (last 14 days)</h2>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={timeseries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#2563EB" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="mb-4 text-sm font-semibold text-navy-900">AI Provider Usage</h2>
          {providerUsage.length === 0 ? (
            <p className="py-10 text-center text-sm text-slate-400">No conversations yet.</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={providerUsage} dataKey="count" nameKey="provider" innerRadius={50} outerRadius={80}>
                  {providerUsage.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {stats?.average_response_time_ms != null && (
        <div className="card flex items-center gap-3">
          <Clock className="h-5 w-5 text-royal-600" />
          <p className="text-sm text-slate-600">
            Average AI response time: <span className="font-semibold text-navy-900">{Math.round(stats.average_response_time_ms)}ms</span>
          </p>
        </div>
      )}
    </div>
  );
}
