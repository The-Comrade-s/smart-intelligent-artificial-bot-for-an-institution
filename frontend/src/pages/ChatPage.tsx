import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { Bot, LogOut, Send, Square, ShieldCheck } from "lucide-react";
import ChatSidebar from "../components/ChatSidebar";
import ChatMessageBubble from "../components/ChatMessageBubble";
import QuickActionCards from "../components/QuickActionCards";
import { useAuth } from "../store/authStore";
import { ChatMessage, getConversation, streamChatMessage } from "../lib/chatApi";

export default function ChatPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { conversationId: routeConversationId } = useParams();

  const [conversationId, setConversationId] = useState<string | null>(routeConversationId ?? null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);
  const streamingContentRef = useRef("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (routeConversationId && routeConversationId !== conversationId) {
      loadConversation(routeConversationId);
    }
  }, [routeConversationId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function loadConversation(id: string) {
    const data = await getConversation(id);
    setConversationId(data.id);
    setMessages(data.messages);
    setSuggestions([]);
  }

  function handleNewChat() {
    setConversationId(null);
    setMessages([]);
    setSuggestions([]);
    navigate("/chat");
  }

  function handleSelectConversation(id: string) {
    navigate(`/chat/${id}`);
  }

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;

    setInput("");
    setSuggestions([]);
    const userMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: trimmed,
      liked: null,
      created_at: new Date().toISOString(),
    };
    const assistantPlaceholder: ChatMessage = {
      id: `pending-${Date.now()}`,
      role: "assistant",
      content: "",
      liked: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);
    setIsStreaming(true);
    streamingContentRef.current = "";

    await streamChatMessage(conversationId, trimmed, {
      onConversationId: (id) => {
        if (!conversationId) {
          setConversationId(id);
          navigate(`/chat/${id}`, { replace: true });
        }
      },
      onToken: (chunk) => {
        streamingContentRef.current += chunk;
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = { ...copy[copy.length - 1], content: streamingContentRef.current };
          return copy;
        });
      },
      onDone: ({ message_id, suggestions: newSuggestions }) => {
        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = { ...copy[copy.length - 1], id: message_id };
          return copy;
        });
        setSuggestions(newSuggestions);
        setIsStreaming(false);
        setSidebarRefreshKey((k) => k + 1);
      },
      onError: () => {
        setIsStreaming(false);
      },
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    sendMessage(input);
  }

  const isEmpty = messages.length === 0;

  return (
    <div className="flex h-screen bg-slate-50">
      <ChatSidebar
        activeConversationId={conversationId}
        onSelect={handleSelectConversation}
        onNewChat={handleNewChat}
        refreshKey={sidebarRefreshKey}
      />

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
          <div className="flex items-center gap-2 font-bold text-navy-900">
            <Bot className="h-5 w-5 text-royal-600" /> COSIB AI
          </div>
          <div className="flex items-center gap-4">
            {(user?.role === "administrator" || user?.role === "super_administrator") && (
              <Link to="/admin" className="flex items-center gap-1 text-sm text-slate-500 hover:text-royal-600">
                <ShieldCheck className="h-4 w-4" /> Admin
              </Link>
            )}
            <span className="text-sm text-slate-600">{user?.full_name}</span>
            <button onClick={() => logout()} className="text-slate-400 hover:text-navy-900" title="Log out">
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-6 py-6">
          {isEmpty ? (
            <div className="mx-auto max-w-3xl">
              <div className="mb-8 text-center">
                <Bot className="mx-auto mb-4 h-10 w-10 text-royal-600" />
                <h1 className="text-xl font-bold text-navy-900">
                  Hello, {user?.full_name?.split(" ")[0]}! How can I help you today?
                </h1>
                <p className="mt-1 text-sm text-slate-500">
                  Ask about courses, lecturers, announcements, or any Computer Science concept.
                </p>
              </div>
              <QuickActionCards onSelect={(prompt) => sendMessage(prompt)} />
            </div>
          ) : (
            <div className="mx-auto max-w-3xl">
              {messages.map((m) => (
                <ChatMessageBubble key={m.id} message={m} />
              ))}
              {suggestions.length > 0 && !isStreaming && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {suggestions.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendMessage(s)}
                      className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 hover:border-royal-300 hover:text-royal-700"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          )}
        </main>

        <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white px-6 py-4">
          <div className="mx-auto flex max-w-3xl items-center gap-2">
            <input
              className="input-field"
              placeholder="Ask COSIB anything…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isStreaming}
            />
            <button
              type="submit"
              disabled={isStreaming || !input.trim()}
              className="btn-primary shrink-0 !px-3"
              title={isStreaming ? "Generating…" : "Send"}
            >
              {isStreaming ? <Square className="h-4 w-4" /> : <Send className="h-4 w-4" />}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
