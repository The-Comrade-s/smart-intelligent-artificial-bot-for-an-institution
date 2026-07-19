import { WifiOff } from "lucide-react";
import { useEffect, useState } from "react";

export default function OfflinePage() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    function goOnline() {
      setIsOnline(true);
      window.location.reload();
    }
    window.addEventListener("online", goOnline);
    return () => window.removeEventListener("online", goOnline);
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-navy-900 px-4 text-center text-white">
      <WifiOff className="mb-4 h-10 w-10 text-sky" />
      <p className="text-sm font-semibold uppercase tracking-widest text-sky">Offline</p>
      <h1 className="mt-2 text-3xl font-bold font-display">No connection</h1>
      <p className="mt-2 max-w-sm text-white/60">
        {isOnline ? "Reconnecting…" : "Check your internet connection. COSIB will reconnect automatically."}
      </p>
    </div>
  );
}
