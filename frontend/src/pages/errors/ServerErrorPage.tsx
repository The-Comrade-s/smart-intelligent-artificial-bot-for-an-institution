import { AlertOctagon } from "lucide-react";

export default function ServerErrorPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy-900 px-4 text-center text-white">
      <AlertOctagon className="mb-4 h-10 w-10 text-sky" />
      <p className="text-sm font-semibold uppercase tracking-widest text-sky">500</p>
      <h1 className="mt-2 text-3xl font-bold font-display">Something went wrong on our end</h1>
      <p className="mt-2 max-w-sm text-white/60">
        COSIB hit an unexpected error. It's been logged — try again in a moment.
      </p>
      <button onClick={() => window.location.reload()} className="btn-primary mt-6">
        Reload
      </button>
    </div>
  );
}
