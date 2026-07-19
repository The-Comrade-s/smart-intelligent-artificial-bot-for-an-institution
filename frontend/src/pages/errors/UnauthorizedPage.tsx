import { Link } from "react-router-dom";
import { LockKeyhole } from "lucide-react";

export default function UnauthorizedPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy-900 px-4 text-center text-white">
      <LockKeyhole className="mb-4 h-10 w-10 text-sky" />
      <p className="text-sm font-semibold uppercase tracking-widest text-sky">401</p>
      <h1 className="mt-2 text-3xl font-bold font-display">Sign in required</h1>
      <p className="mt-2 max-w-sm text-white/60">Your session has ended or you're not signed in. Log in to continue.</p>
      <Link to="/login" className="btn-primary mt-6">
        Log in
      </Link>
    </div>
  );
}
