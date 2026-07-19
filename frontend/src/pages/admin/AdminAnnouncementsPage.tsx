import { useEffect, useState } from "react";
import { Pin, Plus, Trash2 } from "lucide-react";
import { Announcement, createAnnouncement, deleteAnnouncement, listAllAnnouncements } from "../../lib/adminApi";
import { useToast } from "../../components/ui/Toast";
import EmptyState from "../../components/ui/EmptyState";
import { Megaphone } from "lucide-react";

const PRIORITIES = ["low", "normal", "high", "urgent"];

export default function AdminAnnouncementsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState<Announcement[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", priority: "normal", status: "published", is_pinned: false });

  async function load() {
    setItems(await listAllAnnouncements());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createAnnouncement(form);
      setForm({ title: "", content: "", priority: "normal", status: "published", is_pinned: false });
      setShowForm(false);
      showToast("Announcement published", "success");
      load();
    } catch {
      showToast("Couldn't publish the announcement — try again", "error");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this announcement?")) return;
    try {
      await deleteAnnouncement(id);
      setItems((prev) => prev.filter((a) => a.id !== id));
      showToast("Announcement deleted", "success");
    } catch {
      showToast("Couldn't delete the announcement", "error");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-navy-900">Announcements</h1>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
          <Plus className="mr-2 h-4 w-4" /> New Announcement
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card space-y-3">
          <input
            required
            className="input-field"
            placeholder="Title"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
          />
          <textarea
            required
            className="input-field min-h-[100px]"
            placeholder="Content"
            value={form.content}
            onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
          />
          <div className="flex items-center gap-4">
            <select
              className="input-field w-auto"
              value={form.priority}
              onChange={(e) => setForm((f) => ({ ...f, priority: e.target.value }))}
            >
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input type="checkbox" checked={form.is_pinned} onChange={(e) => setForm((f) => ({ ...f, is_pinned: e.target.checked }))} />
              Pin to top
            </label>
          </div>
          <button type="submit" className="btn-primary">
            Publish
          </button>
        </form>
      )}

      <div className="space-y-3">
        {items.map((a) => (
          <div key={a.id} className="card flex items-start justify-between">
            <div>
              <div className="mb-1 flex items-center gap-2">
                {a.is_pinned && <Pin className="h-3.5 w-3.5 text-royal-600" />}
                <span className="font-semibold text-navy-900">{a.title}</span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase text-slate-500">{a.priority}</span>
              </div>
              <p className="text-sm text-slate-600">{a.content}</p>
            </div>
            <button onClick={() => handleDelete(a.id)} className="text-slate-400 hover:text-red-500">
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <EmptyState icon={Megaphone} title="No announcements yet" description="Publish your first announcement to keep students informed." />
        )}
      </div>
    </div>
  );
}
