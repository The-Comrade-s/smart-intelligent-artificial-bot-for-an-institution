import { cn } from "../../lib/utils";

type BadgeVariant = "neutral" | "success" | "warning" | "danger" | "info";

const VARIANT_STYLES: Record<BadgeVariant, string> = {
  neutral: "bg-slate-100 text-slate-600",
  success: "bg-emerald-50 text-emerald-700",
  warning: "bg-amber-50 text-amber-700",
  danger: "bg-red-50 text-red-600",
  info: "bg-royal-50 text-royal-700",
};

export default function Badge({ children, variant = "neutral" }: { children: React.ReactNode; variant?: BadgeVariant }) {
  return <span className={cn("badge", VARIANT_STYLES[variant])}>{children}</span>;
}
