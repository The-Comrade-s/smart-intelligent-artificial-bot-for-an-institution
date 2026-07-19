import { useEffect, useState } from "react";
import { Plus, Search, Pin, Trash2, MessageSquare } from "lucide-react";
import { cn } from "../lib/utils";
import {
  ConversationSummary,
  deleteConversation,
  listConversations,
  togglePinConversation,
} from "../lib/chatApi";

interface Props {
  activeConversationId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  refreshKey: number;
}

export default function ChatSidebar({ activeConversationId, onSelect, onNewChat, refreshKey }: Props) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    listConversations(search || undefined)
      .then((data) => {
        if (!cancelled) setConversations(data);
      })
      .finally(() => !cancelled && setIsLoading(false));
    return () => {
      cancelled = true;
    };
  }, [search, refreshKey]);

  async function handlePin(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    await togglePinConversation(id);
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, is_pinned: !c.is_pinned } : c)).sort((a, b) => Number(b.is_pinned) - Number(a.is_pinned))
    );
  }

  async function handleDelete(id: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (!confirm("Delete this conversation? This can't be undone.")) return;
    await deleteConversation(id);
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeConversationId === id) onNewChat();
  }

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="p-3">
        <button onClick={onNewChat} className="btn-primary w-full">
          <Plus className="mr-2 h-4 w-4" /> New Chat
        </button>
      </div>

      <div className="px-3 pb-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="input-field pl-9"
            placeholder="Search conversations…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-3">
        {isLoading && <p className="px-2 py-4 text-center text-sm text-slate-400">Loading…</p>}
        {!isLoading && conversations.length === 0 && (
          <p className="px-2 py-4 text-center text-sm text-slate-400">No conversations yet.</p>
        )}
        {conversations.map((c) => (
          <button
            key={c.id}
            onClick={() => onSelect(c.id)}
            className={cn(
              "group mb-1 flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm transition",
              activeConversationId === c.id ? "bg-royal-50 text-royal-700" : "text-slate-700 hover:bg-slate-50"
            )}
          >
            <span className="flex min-w-0 items-center gap-2">
              <MessageSquare className="h-4 w-4 shrink-0 text-slate-400" />
              <span className="truncate">{c.title}</span>
            </span>
            <span className="ml-2 hidden shrink-0 items-center gap-1 group-hover:flex">
              <Pin
                onClick={(e) => handlePin(c.id, e)}
                className={cn("h-3.5 w-3.5", c.is_pinned ? "fill-royal-600 text-royal-600" : "text-slate-400")}
              />
              <Trash2 onClick={(e) => handleDelete(c.id, e)} className="h-3.5 w-3.5 text-slate-400 hover:text-red-500" />
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}
