import { Link } from "react-router-dom";
import { Bot } from "lucide-react";

export default function AuthSplitLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      {/* Brand panel — hidden on small screens to keep the form the focus */}
      <div className="relative hidden flex-col justify-between overflow-hidden bg-navy-900 p-10 text-white lg:flex">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(56,189,248,0.15),transparent_50%)]" />
        <Link to="/" className="relative flex items-center gap-2 font-display text-lg font-bold">
          <Bot className="h-6 w-6 text-sky" /> COSIB
        </Link>
        <div className="relative">
          <p className="font-mono text-xs uppercase tracking-widest text-sky">Computer Science Department</p>
          <h2 className="mt-3 max-w-sm font-display text-2xl font-bold leading-snug">
            Your Intelligent Academic Companion
          </h2>
          <p className="mt-3 max-w-sm text-sm text-white/60">
            Gateway ICT Polytechnic, Saapade — department knowledge, course info, and programming help in one chat.
          </p>
        </div>
        <p className="relative text-xs text-white/30">© {new Date().getFullYear()} COSIB</p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center bg-slate-50 px-4 py-12">
        <div className="w-full max-w-sm">{children}</div>
      </div>
    </div>
  );
}
