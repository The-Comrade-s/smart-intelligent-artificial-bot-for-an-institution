import { useEffect, useState } from "react";
import { Bot } from "lucide-react";

const DEMO_EXCHANGES = [
  {
    q: "cosib> who teaches CSC 201?",
    a: "CSC 201 (Data Structures) is taught by the department's data structures unit. Ask me about office hours and I'll pull them from the lecturer directory.",
  },
  {
    q: "cosib> explain big o notation",
    a: "Big O describes how an algorithm's runtime grows as input size increases. O(1) is constant, O(n) is linear, O(n²) is quadratic — worse as n grows.",
  },
  {
    q: "cosib> what's on this week?",
    a: "Two things: SIWES orientation Thursday 10am, and the ND II registration deadline is Friday. Want the full announcement?",
  },
];

/**
 * Cycles through scripted Q&A pairs with a typewriter effect, styled like
 * a terminal — the one deliberately bold element on the page, everything
 * else stays quiet around it.
 */
export default function TerminalDemo() {
  const [exchangeIndex, setExchangeIndex] = useState(0);
  const [typedQuestion, setTypedQuestion] = useState("");
  const [typedAnswer, setTypedAnswer] = useState("");
  const [phase, setPhase] = useState<"question" | "answer" | "pause">("question");

  useEffect(() => {
    const current = DEMO_EXCHANGES[exchangeIndex];
    let cancelled = false;

    async function run() {
      setTypedQuestion("");
      setTypedAnswer("");
      setPhase("question");
      for (let i = 0; i <= current.q.length; i++) {
        if (cancelled) return;
        setTypedQuestion(current.q.slice(0, i));
        await sleep(28);
      }
      await sleep(400);
      setPhase("answer");
      for (let i = 0; i <= current.a.length; i++) {
        if (cancelled) return;
        setTypedAnswer(current.a.slice(0, i));
        await sleep(14);
      }
      setPhase("pause");
      await sleep(2600);
      if (!cancelled) setExchangeIndex((prev) => (prev + 1) % DEMO_EXCHANGES.length);
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [exchangeIndex]);

  return (
    <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-navy-900/60 shadow-2xl backdrop-blur">
      <div className="flex items-center gap-1.5 border-b border-white/10 px-4 py-3">
        <span className="h-2.5 w-2.5 rounded-full bg-red-500/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-amber-500/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/70" />
        <span className="ml-2 font-mono text-xs text-white/40">cosib-ai — department session</span>
      </div>
      <div className="min-h-[168px] px-4 py-4 font-mono text-xs leading-relaxed sm:text-sm">
        <p className="text-sky">
          {typedQuestion}
          {phase === "question" && <span className="animate-blink">▍</span>}
        </p>
        {(phase === "answer" || phase === "pause") && (
          <p className="mt-2 flex gap-2 text-white/80">
            <Bot className="mt-0.5 h-4 w-4 shrink-0 text-white/40" />
            <span>
              {typedAnswer}
              {phase === "answer" && <span className="animate-blink">▍</span>}
            </span>
          </p>
        )}
      </div>
    </div>
  );
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
