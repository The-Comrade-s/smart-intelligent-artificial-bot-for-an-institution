import { useEffect, useState } from "react";
import { CalendarDays, Plus, Trash2 } from "lucide-react";
import { EventItem, createEvent, deleteEvent, listEvents } from "../../lib/adminApi";
import { useToast } from "../../components/ui/Toast";
import EmptyState from "../../components/ui/EmptyState";

export default function AdminEventsPage() {
  const { showToast } = useToast();
  const [items, setItems] = useState<EventItem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", venue: "", start_time: "", organizer: "" });

  async function load() {
    setItems(await listEvents());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createEvent({ ...form, start_time: new Date(form.start_time).toISOString() });
      setForm({ title: "", description: "", venue: "", start_time: "", organizer: "" });
      setShowForm(false);
      showToast("Event created", "success");
      load();
    } catch {
      showToast("Couldn't create the event — try again", "error");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this event?")) return;
    try {
      await deleteEvent(id);
      setItems((prev) => prev.filter((e) => e.id !== id));
      showToast("Event deleted", "success");
    } catch {
      showToast("Couldn't delete the event", "error");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-navy-900">Events</h1>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
          <Plus className="mr-2 h-4 w-4" /> New Event
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card grid grid-cols-1 gap-3 sm:grid-cols-2">
          <input required className="input-field" placeholder="Title" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
          <input className="input-field" placeholder="Venue" value={form.venue} onChange={(e) => setForm((f) => ({ ...f, venue: e.target.value }))} />
          <input
            required
            type="datetime-local"
            className="input-field"
            value={form.start_time}
            onChange={(e) => setForm((f) => ({ ...f, start_time: e.target.value }))}
          />
          <input className="input-field" placeholder="Organizer" value={form.organizer} onChange={(e) => setForm((f) => ({ ...f, organizer: e.target.value }))} />
          <textarea
            className="input-field sm:col-span-2"
            placeholder="Description"
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <button type="submit" className="btn-primary sm:col-span-2">
            Create Event
          </button>
        </form>
      )}

      <div className="space-y-3">
        {items.map((ev) => (
          <div key={ev.id} className="card flex items-start justify-between">
            <div className="flex gap-3">
              <CalendarDays className="mt-1 h-4 w-4 text-royal-600" />
              <div>
                <p className="font-semibold text-navy-900">{ev.title}</p>
                <p className="text-xs text-slate-500">
                  {new Date(ev.start_time).toLocaleString()} {ev.venue && `· ${ev.venue}`}
                </p>
                {ev.description && <p className="mt-1 text-sm text-slate-600">{ev.description}</p>}
              </div>
            </div>
            <button onClick={() => handleDelete(ev.id)} className="text-slate-400 hover:text-red-500">
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
        {items.length === 0 && (
          <EmptyState icon={CalendarDays} title="No events yet" description="Create your first department event or seminar." />
        )}
      </div>
    </div>
  );
}
