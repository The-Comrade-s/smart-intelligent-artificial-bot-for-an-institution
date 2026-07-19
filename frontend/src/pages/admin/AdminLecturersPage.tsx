import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Department, Lecturer, createLecturer, deleteLecturer, listDepartments, listLecturers } from "../../lib/academicsApi";

export default function AdminLecturersPage() {
  const [lecturers, setLecturers] = useState<Lecturer[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ full_name: "", title: "", email: "", office: "", office_hours: "", department_id: "" });

  async function load() {
    const [l, d] = await Promise.all([listLecturers(), listDepartments()]);
    setLecturers(l);
    setDepartments(d);
    if (d.length > 0) setForm((f) => ({ ...f, department_id: f.department_id || d[0].id }));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await createLecturer(form);
    setForm((f) => ({ ...f, full_name: "", email: "" }));
    setShowForm(false);
    load();
  }

  async function handleDelete(id: string) {
    if (!confirm("Remove this lecturer?")) return;
    await deleteLecturer(id);
    setLecturers((prev) => prev.filter((l) => l.id !== id));
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-navy-900">Lecturers</h1>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary" disabled={departments.length === 0}>
          <Plus className="mr-2 h-4 w-4" /> New Lecturer
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card grid grid-cols-2 gap-3 sm:grid-cols-3">
          <input required className="input-field" placeholder="Full name" value={form.full_name} onChange={(e) => setForm((f) => ({ ...f, full_name: e.target.value }))} />
          <input className="input-field" placeholder="Title (e.g. Dr.)" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
          <input className="input-field" placeholder="Email" value={form.email} onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))} />
          <input className="input-field" placeholder="Office" value={form.office} onChange={(e) => setForm((f) => ({ ...f, office: e.target.value }))} />
          <input className="input-field sm:col-span-2" placeholder="Office hours" value={form.office_hours} onChange={(e) => setForm((f) => ({ ...f, office_hours: e.target.value }))} />
          <button type="submit" className="btn-primary sm:col-span-3">
            Save Lecturer
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {lecturers.map((l) => (
          <div key={l.id} className="card">
            <div className="mb-2 flex items-start justify-between">
              <p className="font-semibold text-navy-900">
                {l.title} {l.full_name}
              </p>
              <button onClick={() => handleDelete(l.id)} className="text-slate-400 hover:text-red-500">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
            {l.email && <p className="text-xs text-slate-500">{l.email}</p>}
            {l.office && <p className="text-xs text-slate-500">Office: {l.office}</p>}
            {l.office_hours && <p className="text-xs text-slate-500">Hours: {l.office_hours}</p>}
          </div>
        ))}
        {lecturers.length === 0 && <p className="text-center text-sm text-slate-400">No lecturers yet.</p>}
      </div>
    </div>
  );
}
