import { useEffect, useState } from "react";
import { CheckCircle2, Circle } from "lucide-react";
import { AIProviderSetting, activateAIProvider, listAIProviders, updateAIProvider } from "../../lib/adminApi";
import { useToast } from "../../components/ui/Toast";

export default function AdminAIConfigPage() {
  const { showToast } = useToast();
  const [providers, setProviders] = useState<AIProviderSetting[]>([]);
  const [savingKey, setSavingKey] = useState<string | null>(null);

  async function load() {
    setProviders(await listAIProviders());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleActivate(provider: string) {
    try {
      await activateAIProvider(provider);
      showToast(`${provider} is now the active AI provider`, "success");
      load();
    } catch {
      showToast("Couldn't activate that provider", "error");
    }
  }

  async function handleUpdate(provider: string, field: keyof AIProviderSetting, value: unknown) {
    setSavingKey(provider);
    try {
      const updated = await updateAIProvider(provider, { [field]: value });
      setProviders((prev) => prev.map((p) => (p.provider === provider ? updated : p)));
    } catch {
      showToast("Couldn't save that change", "error");
    } finally {
      setSavingKey(null);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-navy-900">AI Configuration</h1>
        <p className="text-sm text-slate-500">
          Switch the active provider or tune its behavior — no code changes needed. The mock provider
          works with no API key and is a safe default for demos.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {providers.map((p) => (
          <div key={p.provider} className="card space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold capitalize text-navy-900">{p.provider}</span>
              <button onClick={() => handleActivate(p.provider)} className="flex items-center gap-1 text-xs font-medium text-royal-600">
                {p.is_active ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Circle className="h-4 w-4 text-slate-300" />}
                {p.is_active ? "Active" : "Activate"}
              </button>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Temperature ({p.temperature})</label>
              <input
                type="range"
                min={0}
                max={2}
                step={0.1}
                defaultValue={p.temperature}
                onMouseUp={(e) => handleUpdate(p.provider, "temperature", parseFloat((e.target as HTMLInputElement).value))}
                className="w-full"
              />
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">Max tokens</label>
              <input
                type="number"
                className="input-field"
                defaultValue={p.max_tokens}
                onBlur={(e) => handleUpdate(p.provider, "max_tokens", parseInt(e.target.value, 10))}
              />
            </div>

            <label className="flex items-center gap-2 text-xs text-slate-600">
              <input
                type="checkbox"
                defaultChecked={p.streaming_enabled}
                onChange={(e) => handleUpdate(p.provider, "streaming_enabled", e.target.checked)}
              />
              Streaming enabled
            </label>

            <label className="flex items-center gap-2 text-xs text-slate-600">
              <input
                type="checkbox"
                defaultChecked={p.is_enabled}
                onChange={(e) => handleUpdate(p.provider, "is_enabled", e.target.checked)}
              />
              Provider enabled
            </label>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-600">System prompt override (optional)</label>
              <textarea
                className="input-field min-h-[80px] text-xs"
                defaultValue={p.system_prompt ?? ""}
                placeholder="Leave blank to use COSIB's default personality prompt"
                onBlur={(e) => handleUpdate(p.provider, "system_prompt", e.target.value || null)}
              />
            </div>

            {savingKey === p.provider && <p className="text-xs text-slate-400">Saving…</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
