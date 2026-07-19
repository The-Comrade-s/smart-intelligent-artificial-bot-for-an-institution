import { motion } from "framer-motion";
import { GraduationCap, BookOpen, Users, Calendar, Megaphone, Code, FileQuestion, Lightbulb } from "lucide-react";

const ACTIONS = [
  { icon: GraduationCap, label: "Explain a Programming Concept", prompt: "Explain the concept of recursion with a simple example." },
  { icon: BookOpen, label: "Course Information", prompt: "What are the courses offered in ND II?" },
  { icon: Users, label: "Meet Our Lecturers", prompt: "Tell me about the lecturers in the Computer Science department." },
  { icon: Calendar, label: "Academic Calendar", prompt: "What's on the academic calendar this semester?" },
  { icon: Megaphone, label: "Latest Announcements", prompt: "Show me the latest department announcements." },
  { icon: Code, label: "Programming Help", prompt: "I'm getting a syntax error in my Python code, can you help me debug it?" },
  { icon: FileQuestion, label: "Generate Quiz", prompt: "Generate a 5-question quiz on Data Structures." },
  { icon: Lightbulb, label: "Study Tips", prompt: "Give me tips for studying for my Database Management exam." },
];

export default function QuickActionCards({ onSelect }: { onSelect: (prompt: string) => void }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {ACTIONS.map(({ icon: Icon, label, prompt }, i) => (
        <motion.button
          key={label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.04, duration: 0.3 }}
          onClick={() => onSelect(prompt)}
          className="card text-left transition hover:border-royal-200 hover:shadow-md"
        >
          <Icon className="mb-3 h-6 w-6 text-royal-600" />
          <p className="text-sm font-semibold text-navy-900">{label}</p>
        </motion.button>
      ))}
    </div>
  );
}
