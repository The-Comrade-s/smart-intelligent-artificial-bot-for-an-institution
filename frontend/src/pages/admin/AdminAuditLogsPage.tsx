import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { AuditLogEntry, listAuditLogs } from "../../lib/adminApi";

export default function AdminAuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [filter, setFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      setLogs(await listAuditLogs(filter || undefined));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [filter]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-navy-900">Audit Logs</h1>
          <p className="text-sm text-slate-500">System-wide trail of sensitive actions. Super admin only.</p>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input className="input-field pl-9" placeholder="Filter by action…" value={filter} onChange={(e) => setFilter(e.target.value)} />
        </div>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Resource</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">IP</th>
              <th className="px-4 py-3">When</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">Loading…</td>
              </tr>
            )}
            {!isLoading && logs.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">No audit entries found.</td>
              </tr>
            )}
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-slate-50 last:border-0">
                <td className="px-4 py-3 font-mono text-xs text-navy-900">{log.action}</td>
                <td className="px-4 py-3 text-xs text-slate-500">
                  {log.resource_type ? `${log.resource_type}${log.resource_id ? ` · ${log.resource_id.slice(0, 8)}…` : ""}` : "—"}
                </td>
                <td className="px-4 py-3">
                  <span className={log.status === "success" ? "text-emerald-600" : "text-red-500"}>{log.status}</span>
                </td>
                <td className="px-4 py-3 text-xs text-slate-400">{log.ip_address ?? "—"}</td>
                <td className="px-4 py-3 text-xs text-slate-400">{new Date(log.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
