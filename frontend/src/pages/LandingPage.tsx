import { Link } from "react-router-dom";
import { Bot, BookOpen, Users, Megaphone, ArrowRight, MessageCircle, Search, Sparkles } from "lucide-react";
import TerminalDemo from "../components/TerminalDemo";
import Accordion from "../components/ui/Accordion";

const FEATURES = [
  { icon: Bot, title: "AI Chat", desc: "Ask COSIB anything about your courses, code, or campus life, in plain language." },
  { icon: BookOpen, title: "Knowledge Base", desc: "Verified department and academic information, kept current by the department itself." },
  { icon: Users, title: "Lecturer Directory", desc: "Find office hours, contacts, and research interests in seconds." },
  { icon: Megaphone, title: "Announcements", desc: "Registration deadlines and department notices, surfaced before you have to ask." },
];

const STEPS = [
  { icon: MessageCircle, title: "Ask", desc: "Type a question the way you'd ask a classmate — about a course, a concept, or what's due this week." },
  { icon: Search, title: "COSIB checks the record", desc: "It searches verified department knowledge first, not a generic guess." },
  { icon: Sparkles, title: "You get a straight answer", desc: "Grounded in real course and department data, with follow-up questions ready if you need to go deeper." },
];

const STATS = [
  { value: "24/7", label: "Available, including exam week" },
  { value: "3", label: "Knowledge modes: department, academic, campus" },
  { value: "0", label: "Made-up answers about department policy — COSIB says when it isn't sure" },
];

const FAQ_ITEMS = [
  { question: "Do I need a student ID to use COSIB?", answer: "You need a COSIB account, created with your school email. Registration takes under a minute." },
  { question: "Can lecturers use COSIB too?", answer: "Yes — lecturer accounts can publish announcements and manage events in addition to using chat." },
  { question: "Where does COSIB get department information?", answer: "From a knowledge base maintained by department administrators, not the open internet — so answers reflect actual department policy." },
  { question: "What if COSIB doesn't know something?", answer: "It says so directly and points you to the department office, instead of guessing." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-navy-900 text-white">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-2 font-display text-lg font-bold">
          <Bot className="h-6 w-6 text-sky" />
          COSIB
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-sm font-medium text-white/80 hover:text-white">
            Log in
          </Link>
          <Link to="/register" className="btn-primary">
            Start Chatting
          </Link>
        </div>
      </nav>

      {/* Hero — the terminal demo is the one bold element; everything else stays quiet */}
      <header className="mx-auto grid max-w-6xl grid-cols-1 items-center gap-12 px-6 py-16 lg:grid-cols-2 lg:py-24">
        <div>
          <p className="mb-4 font-mono text-xs uppercase tracking-widest text-sky">
            Computer Science Department · Gateway ICT Polytechnic, Saapade
          </p>
          <h1 className="font-display text-4xl font-bold leading-tight sm:text-5xl">
            Your Intelligent Academic Companion
          </h1>
          <p className="mt-6 max-w-lg text-lg text-white/70">
            COSIB answers your department questions, explains Computer Science concepts, and keeps
            you on top of announcements — grounded in what the department actually says, not a guess.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link to="/register" className="btn-primary">
              Start Chatting <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
            <Link to="/login" className="btn-secondary border-white/20 bg-transparent text-white hover:bg-white/10">
              Admin Login
            </Link>
          </div>
        </div>
        <div className="flex justify-center lg:justify-end">
          <TerminalDemo />
        </div>
      </header>

      {/* Features */}
      <section className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 pb-20 sm:grid-cols-2 lg:grid-cols-4">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="rounded-2xl border border-white/10 bg-white/5 p-6">
            <Icon className="mb-4 h-8 w-8 text-sky" />
            <h3 className="mb-2 font-display font-semibold">{title}</h3>
            <p className="text-sm text-white/60">{desc}</p>
          </div>
        ))}
      </section>

      {/* How it works — a genuine sequence, so numbering earns its place */}
      <section className="border-t border-white/10 bg-white/5 py-20">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="mb-12 text-center font-display text-3xl font-bold">How COSIB works</h2>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <div key={step.title} className="relative">
                <div className="mb-4 flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-full bg-royal-600 font-mono text-sm font-bold">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <step.icon className="h-5 w-5 text-sky" />
                </div>
                <h3 className="mb-2 font-display font-semibold">{step.title}</h3>
                <p className="text-sm text-white/60">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          {STATS.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="font-display text-4xl font-bold text-sky">{stat.value}</p>
              <p className="mt-2 text-sm text-white/60">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Testimonials placeholder — intentionally marked as such until real quotes are collected */}
      <section className="border-t border-white/10 bg-white/5 py-20">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="mb-4 font-display text-3xl font-bold">What students are saying</h2>
          <p className="mb-8 text-sm text-white/50">
            Testimonials will appear here once COSIB is live with the department — this space is reserved for real student feedback.
          </p>
          <div className="rounded-2xl border border-dashed border-white/20 p-10 text-white/40">
            <p className="font-mono text-sm">// awaiting student testimonials</p>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="mx-auto max-w-2xl px-6 py-20">
        <h2 className="mb-8 text-center font-display text-3xl font-bold">Frequently asked questions</h2>
        <Accordion items={FAQ_ITEMS} />
      </section>

      <footer className="border-t border-white/10 py-8 text-center text-sm text-white/50">
        © {new Date().getFullYear()} COSIB — Computer Science Department, Gateway ICT Polytechnic, Saapade
      </footer>
    </div>
  );
}
