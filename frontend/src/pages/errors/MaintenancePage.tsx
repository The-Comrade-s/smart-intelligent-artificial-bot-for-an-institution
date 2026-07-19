import { Wrench } from "lucide-react";

export default function MaintenancePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy-900 px-4 text-center text-white">
      <Wrench className="mb-4 h-10 w-10 text-sky" />
      <p className="text-sm font-semibold uppercase tracking-widest text-sky">Maintenance</p>
      <h1 className="mt-2 text-3xl font-bold font-display">COSIB is getting a tune-up</h1>
      <p className="mt-2 max-w-sm text-white/60">
        We're making some improvements behind the scenes. Please check back shortly.
      </p>
    </div>
  );
}
