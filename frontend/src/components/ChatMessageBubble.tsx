import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { Bot, ThumbsDown, ThumbsUp, User as UserIcon, Copy, Check } from "lucide-react";
import { useState } from "react";
import { cn } from "../lib/utils";
import { ChatMessage, reactToMessage } from "../lib/chatApi";
import TypingIndicator from "./TypingIndicator";

export default function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  const [liked, setLiked] = useState<boolean | null>(message.liked);
  const [copied, setCopied] = useState(false);

  async function handleReaction(value: boolean) {
    const next = liked === value ? null : value;
    setLiked(next);
    await reactToMessage(message.id, next);
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className={cn("flex gap-3 py-4", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-royal-600 text-white" : "bg-navy-900 text-sky"
        )}
      >
        {isUser ? <UserIcon className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className={cn("max-w-[75%] rounded-2xl px-4 py-3", isUser ? "bg-royal-600 text-white" : "bg-slate-100 text-navy-900")}>
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : message.content === "" ? (
          <TypingIndicator />
        ) : (
          <div className="prose prose-sm max-w-none prose-pre:bg-navy-900 prose-pre:text-white">
            <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {!isUser && message.content !== "" && (
          <div className="mt-2 flex items-center gap-3 border-t border-slate-200 pt-2 text-slate-400">
            <button onClick={handleCopy} className="hover:text-navy-900" title="Copy">
              {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
            <button onClick={() => handleReaction(true)} className={cn("hover:text-navy-900", liked === true && "text-emerald-600")}>
              <ThumbsUp className="h-3.5 w-3.5" />
            </button>
            <button onClick={() => handleReaction(false)} className={cn("hover:text-navy-900", liked === false && "text-red-500")}>
              <ThumbsDown className="h-3.5 w-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
