import { cn } from "../lib/utils";

function scorePassword(password: string): number {
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  return Math.min(score, 4);
}

const LABELS = ["Too short", "Weak", "Okay", "Good", "Strong"];
const COLORS = ["bg-red-400", "bg-amber-400", "bg-amber-400", "bg-emerald-500", "bg-emerald-500"];

export default function PasswordStrength({ password }: { password: string }) {
  if (!password) return null;
  const score = scorePassword(password);

  return (
    <div className="mt-1.5">
      <div className="flex gap-1">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className={cn("h-1 flex-1 rounded-full transition-colors", i < score ? COLORS[score] : "bg-slate-100")} />
        ))}
      </div>
      <p className="mt-1 text-xs text-slate-400">{LABELS[score]}</p>
    </div>
  );
}
