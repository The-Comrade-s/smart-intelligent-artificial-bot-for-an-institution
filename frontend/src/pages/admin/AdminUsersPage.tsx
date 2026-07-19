import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { UserRow, deleteUser, listUsers, updateUserRole, updateUserStatus } from "../../lib/adminApi";
import { useAuth } from "../../store/authStore";
import { useToast } from "../../components/ui/Toast";

const ROLES = ["student", "lecturer", "administrator", "super_administrator"];
const STATUSES = ["active", "suspended", "deactivated", "pending_verification"];

export default function AdminUsersPage() {
  const { user: currentUser } = useAuth();
  const { showToast } = useToast();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  async function load() {
    setIsLoading(true);
    try {
      const data = await listUsers(search ? { search } : undefined);
      setUsers(data);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    const t = setTimeout(load, 300);
    return () => clearTimeout(t);
  }, [search]);

  async function handleRoleChange(id: string, role: string) {
    try {
      const updated = await updateUserRole(id, role);
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)));
      showToast("Role updated", "success");
    } catch {
      showToast("Couldn't update the role", "error");
    }
  }

  async function handleStatusChange(id: string, status: string) {
    try {
      const updated = await updateUserStatus(id, status);
      setUsers((prev) => prev.map((u) => (u.id === id ? updated : u)));
      showToast("Status updated", "success");
    } catch {
      showToast("Couldn't update the status", "error");
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this user permanently? This can't be undone.")) return;
    try {
      await deleteUser(id);
      setUsers((prev) => prev.filter((u) => u.id !== id));
      showToast("User deleted", "success");
    } catch {
      showToast("Couldn't delete the user", "error");
    }
  }

  const isSuperAdmin = currentUser?.role === "super_administrator";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-navy-900">Users</h1>
          <p className="text-sm text-slate-500">{users.length} user(s)</p>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input className="input-field pl-9" placeholder="Search users…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      <div className="card overflow-x-auto p-0">
        <table className="w-full text-sm">
          <thead className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              {isSuperAdmin && <th className="px-4 py-3">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">Loading…</td>
              </tr>
            )}
            {!isLoading && users.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-slate-400">No users found.</td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.id} className="border-b border-slate-50 last:border-0">
                <td className="px-4 py-3 font-medium text-navy-900">{u.full_name}</td>
                <td className="px-4 py-3 text-slate-500">{u.email}</td>
                <td className="px-4 py-3">
                  <select
                    className="rounded-lg border border-slate-200 px-2 py-1 text-xs capitalize disabled:bg-slate-50"
                    value={u.role}
                    disabled={!isSuperAdmin}
                    onChange={(e) => handleRoleChange(u.id, e.target.value)}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <select
                    className="rounded-lg border border-slate-200 px-2 py-1 text-xs capitalize"
                    value={u.status}
                    onChange={(e) => handleStatusChange(u.id, e.target.value)}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {s.replace("_", " ")}
                      </option>
                    ))}
                  </select>
                </td>
                {isSuperAdmin && (
                  <td className="px-4 py-3">
                    <button onClick={() => handleDelete(u.id)} className="text-xs font-medium text-red-500 hover:underline">
                      Delete
                    </button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
