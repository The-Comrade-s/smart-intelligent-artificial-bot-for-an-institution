import { api, API_BASE, tokenStorage } from "./api";

export interface ConversationSummary {
  id: string;
  title: string;
  is_pinned: boolean;
  is_archived: boolean;
  ai_provider_used: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  liked: boolean | null;
  created_at: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ChatMessage[];
}

export async function listConversations(search?: string): Promise<ConversationSummary[]> {
  const { data } = await api.get("/conversations", { params: search ? { search } : {} });
  return data;
}

export async function getConversation(id: string): Promise<ConversationDetail> {
  const { data } = await api.get(`/conversations/${id}`);
  return data;
}

export async function renameConversation(id: string, title: string): Promise<ConversationSummary> {
  const { data } = await api.patch(`/conversations/${id}/rename`, { title });
  return data;
}

export async function togglePinConversation(id: string): Promise<ConversationSummary> {
  const { data } = await api.patch(`/conversations/${id}/pin`);
  return data;
}

export async function deleteConversation(id: string): Promise<void> {
  await api.delete(`/conversations/${id}`);
}

export async function reactToMessage(messageId: string, liked: boolean | null): Promise<ChatMessage> {
  const { data } = await api.patch(`/chat/messages/${messageId}/reaction`, null, { params: { liked } });
  return data;
}

/**
 * Streams a chat response via Server-Sent Events using fetch (axios doesn't
 * support streaming response bodies in the browser the way we need here).
 */
export async function streamChatMessage(
  conversationId: string | null,
  message: string,
  handlers: {
    onConversationId: (id: string) => void;
    onToken: (text: string) => void;
    onDone: (payload: { message_id: string; suggestions: string[] }) => void;
    onError: (error: string) => void;
  }
): Promise<void> {
  const token = tokenStorage.getAccess();

  const response = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ conversation_id: conversationId, message }),
  });

  if (!response.ok || !response.body) {
    handlers.onError(`Request failed (${response.status})`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";

    for (const rawEvent of events) {
      const lines = rawEvent.split("\n");
      const eventLine = lines.find((l) => l.startsWith("event:"));
      const dataLine = lines.find((l) => l.startsWith("data:"));
      if (!eventLine || !dataLine) continue;

      const eventName = eventLine.replace("event:", "").trim();
      const data = JSON.parse(dataLine.replace("data:", "").trim());

      if (eventName === "conversation") handlers.onConversationId(data.conversation_id);
      else if (eventName === "token") handlers.onToken(data.text);
      else if (eventName === "done") handlers.onDone(data);
    }
  }
}
