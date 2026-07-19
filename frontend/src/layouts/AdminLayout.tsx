import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  BookOpen,
  GraduationCap,
  Megaphone,
  CalendarDays,
  MessageSquareWarning,
  BarChart3,
  Bot,
  Settings as SettingsIcon,
  ScrollText,
  LogOut,
  ArrowLeft,
} from "lucide-react";
import { cn } from "../lib/utils";
import { useAuth } from "../store/authStore";

const NAV_ITEMS = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/admin/users", label: "Users", icon: Users },
  { to: "/admin/knowledge-base", label: "Knowledge Base", icon: BookOpen },
  { to: "/admin/courses", label: "Courses", icon: GraduationCap },
  { to: "/admin/lecturers", label: "Lecturers", icon: GraduationCap },
  { to: "/admin/announcements", label: "Announcements", icon: Megaphone },
  { to: "/admin/events", label: "Events", icon: CalendarDays },
  { to: "/admin/feedback", label: "Feedback", icon: MessageSquareWarning },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/admin/ai-configuration", label: "AI Configuration", icon: Bot },
  { to: "/admin/settings", label: "System Settings", icon: SettingsIcon },
  { to: "/admin/audit-logs", label: "Audit Logs", icon: ScrollText },
];

export default function AdminLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex h-screen bg-slate-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-navy-900 text-white">
        <div className="flex items-center gap-2 px-5 py-5 text-lg font-bold">
          <Bot className="h-6 w-6 text-sky" /> COSIB Admin
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto px-3">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition",
                  isActive ? "bg-royal-600 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 p-3">
          <NavLink to="/chat" className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/70 hover:bg-white/10 hover:text-white">
            <ArrowLeft className="h-4 w-4" /> Back to Chat
          </NavLink>
          <button
            onClick={() => logout()}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-white/70 hover:bg-white/10 hover:text-white"
          >
            <LogOut className="h-4 w-4" /> Log out
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <div />
          <span className="text-sm text-slate-600">
            {user?.full_name} · <span className="capitalize">{user?.role?.replace("_", " ")}</span>
          </span>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
