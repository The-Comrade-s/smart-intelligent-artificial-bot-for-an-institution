import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";

export default function ForbiddenPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy-900 px-4 text-center text-white">
      <ShieldAlert className="mb-4 h-10 w-10 text-sky" />
      <p className="text-sm font-semibold uppercase tracking-widest text-sky">403</p>
      <h1 className="mt-2 text-3xl font-bold font-display">You don't have access to this page</h1>
      <p className="mt-2 max-w-sm text-white/60">
        This area is restricted to specific roles. If you believe this is a mistake, contact an administrator.
      </p>
      <Link to="/chat" className="btn-primary mt-6">
        Back to Chat
      </Link>
    </div>
  );
}
