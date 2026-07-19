import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ChatPage from "./pages/ChatPage";
import NotFoundPage from "./pages/NotFoundPage";
import { ProtectedRoute } from "./routes/ProtectedRoute";
import AdminLayout from "./layouts/AdminLayout";
import AdminDashboardPage from "./pages/admin/AdminDashboardPage";
import AdminUsersPage from "./pages/admin/AdminUsersPage";
import AdminKnowledgeBasePage from "./pages/admin/AdminKnowledgeBasePage";
import AdminCoursesPage from "./pages/admin/AdminCoursesPage";
import AdminLecturersPage from "./pages/admin/AdminLecturersPage";
import AdminAnnouncementsPage from "./pages/admin/AdminAnnouncementsPage";
import AdminEventsPage from "./pages/admin/AdminEventsPage";
import AdminFeedbackPage from "./pages/admin/AdminFeedbackPage";
import AdminAnalyticsPage from "./pages/admin/AdminAnalyticsPage";
import AdminAIConfigPage from "./pages/admin/AdminAIConfigPage";
import AdminSettingsPage from "./pages/admin/AdminSettingsPage";
import AdminAuditLogsPage from "./pages/admin/AdminAuditLogsPage";
import UnauthorizedPage from "./pages/errors/UnauthorizedPage";
import ForbiddenPage from "./pages/errors/ForbiddenPage";
import ServerErrorPage from "./pages/errors/ServerErrorPage";
import OfflinePage from "./pages/errors/OfflinePage";
import MaintenancePage from "./pages/errors/MaintenancePage";

const ADMIN_ROLES = ["administrator", "super_administrator"];

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/chat/:conversationId" element={<ChatPage />} />
        {/* /dashboard kept as an alias so old links still resolve */}
        <Route path="/dashboard" element={<ChatPage />} />
      </Route>

      <Route element={<ProtectedRoute allowedRoles={ADMIN_ROLES} />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboardPage />} />
          <Route path="users" element={<AdminUsersPage />} />
          <Route path="knowledge-base" element={<AdminKnowledgeBasePage />} />
          <Route path="courses" element={<AdminCoursesPage />} />
          <Route path="lecturers" element={<AdminLecturersPage />} />
          <Route path="announcements" element={<AdminAnnouncementsPage />} />
          <Route path="events" element={<AdminEventsPage />} />
          <Route path="feedback" element={<AdminFeedbackPage />} />
          <Route path="analytics" element={<AdminAnalyticsPage />} />
          <Route path="ai-configuration" element={<AdminAIConfigPage />} />
          <Route path="settings" element={<AdminSettingsPage />} />
          <Route path="audit-logs" element={<AdminAuditLogsPage />} />
        </Route>
      </Route>

      <Route path="/401" element={<UnauthorizedPage />} />
      <Route path="/403" element={<ForbiddenPage />} />
      <Route path="/500" element={<ServerErrorPage />} />
      <Route path="/offline" element={<OfflinePage />} />
      <Route path="/maintenance" element={<MaintenancePage />} />

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
