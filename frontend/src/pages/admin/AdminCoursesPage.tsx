import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Course, Department, createCourse, deleteCourse, listCourses, listDepartments } from "../../lib/academicsApi";

export default function AdminCoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ code: "", title: "", level: "ND I", semester: "First", units: 2, department_id: "" });

  async function load() {
    const [c, d] = await Promise.all([listCourses(), listDepartments()]);
    setCourses(c);
    setDepartments(d);
    if (d.length > 0) setForm((f) => ({ ...f, department_id: f.department_id || d[0].id }));
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await createCourse(form);
    setForm((f) => ({ ...f, code: "", title: "" }));
    setShowForm(false);
    load();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this course?")) return;
    await deleteCourse(id);
    setCourses((prev) => prev.filter((c) => c.id !== id));
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-navy-900">Courses</h1>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary" disabled={departments.length === 0}>
          <Plus className="mr-2 h-4 w-4" /> New Course
        </button>
      </div>

      {departments.length === 0 && (
        <p className="text-sm text-amber-600">No department found yet — run the backend seed script first.</p>
      )}

      {showForm && (
        <form onSubmit={handleCreate} className="card grid grid-cols-2 gap-3 sm:grid-cols-3">
          <input required className="input-field" placeholder="Code (e.g. CSC 201)" value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))} />
          <input required className="input-field sm:col-span-2" placeholder="Title" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
          <input required className="input-field" placeholder="Level (e.g. ND I)" value={form.level} onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))} />
          <select className="input-field" value={form.semester} onChange={(e) => setForm((f) => ({ ...f, semester: e.target.value }))}>
            <option>First</option>
            <option>Second</option>
          </select>
          <input
            type="number"
            min={1}
            max={6}
            className="input-field"
            placeholder="Units"
            value={form.units}
            onChange={(e) => setForm((f) => ({ ...f, units: parseInt(e.target.value, 10) || 1 }))}
          />
          <button type="submit" className="btn-primary sm:col-span-3">
            Save Course
          </button>
        </form>
      )}

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Level</th>
              <th className="px-4 py-3">Semester</th>
              <th className="px-4 py-3">Units</th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            {courses.map((c) => (
              <tr key={c.id} className="border-b border-slate-50 last:border-0">
                <td className="px-4 py-3 font-medium text-navy-900">{c.code}</td>
                <td className="px-4 py-3">{c.title}</td>
                <td className="px-4 py-3">{c.level}</td>
                <td className="px-4 py-3">{c.semester}</td>
                <td className="px-4 py-3">{c.units}</td>
                <td className="px-4 py-3 text-right">
                  <button onClick={() => handleDelete(c.id)} className="text-slate-400 hover:text-red-500">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
            {courses.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-slate-400">
                  No courses yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
