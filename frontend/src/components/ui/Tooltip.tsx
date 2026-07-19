import { useId, useState } from "react";
import { cn } from "../../lib/utils";

export default function Tooltip({ label, children, side = "top" }: { label: string; children: React.ReactNode; side?: "top" | "bottom" }) {
  const [visible, setVisible] = useState(false);
  const id = useId();

  return (
    <span
      className="relative inline-flex"
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      onFocus={() => setVisible(true)}
      onBlur={() => setVisible(false)}
    >
      {/* Cloned child gets aria-describedby via wrapper span rather than mutating props, keeping this generic */}
      <span aria-describedby={visible ? id : undefined}>{children}</span>
      {visible && (
        <span
          role="tooltip"
          id={id}
          className={cn(
            "pointer-events-none absolute left-1/2 z-50 -translate-x-1/2 whitespace-nowrap rounded-lg bg-navy-900 px-2.5 py-1.5 text-xs text-white shadow-lg animate-fade-in",
            side === "top" ? "bottom-full mb-2" : "top-full mt-2"
          )}
        >
          {label}
        </span>
      )}
    </span>
  );
}
