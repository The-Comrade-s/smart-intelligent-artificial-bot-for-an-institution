import { useEffect, useState } from "react";
import { Save } from "lucide-react";
import { AppSetting, listSettings, upsertSetting } from "../../lib/adminApi";
import { useToast } from "../../components/ui/Toast";

export default function AdminSettingsPage() {
  const { showToast } = useToast();
  const [settings, setSettings] = useState<AppSetting[]>([]);
  const [savingKey, setSavingKey] = useState<string | null>(null);

  async function load() {
    setSettings(await listSettings());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSave(key: string, value: string) {
    setSavingKey(key);
    try {
      const existing = settings.find((s) => s.key === key);
      const updated = await upsertSetting({ key, value, value_json: existing?.value_json ?? null, description: existing?.description ?? null });
      setSettings((prev) => prev.map((s) => (s.key === key ? updated : s)));
      showToast("Setting saved", "success");
    } catch {
      showToast("Couldn't save that setting", "error");
    } finally {
      setSavingKey(null);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-bold text-navy-900">System Settings</h1>
        <p className="text-sm text-slate-500">Application branding and configuration, editable without a code deploy.</p>
      </div>

      <div className="card space-y-4">
        {settings.map((s) => (
          <SettingRow key={s.key} setting={s} onSave={handleSave} saving={savingKey === s.key} />
        ))}
        {settings.length === 0 && <p className="text-sm text-slate-400">No settings found — run the backend seed script.</p>}
      </div>
    </div>
  );
}

function SettingRow({ setting, onSave, saving }: { setting: AppSetting; onSave: (key: string, value: string) => void; saving: boolean }) {
  const [value, setValue] = useState(setting.value ?? "");

  return (
    <div className="flex items-end gap-3 border-b border-slate-100 pb-4 last:border-0 last:pb-0">
      <div className="flex-1">
        <label className="mb-1 block text-xs font-semibold uppercase text-slate-500">{setting.key.replace(/_/g, " ")}</label>
        {setting.description && <p className="mb-1 text-xs text-slate-400">{setting.description}</p>}
        <input className="input-field" value={value} onChange={(e) => setValue(e.target.value)} />
      </div>
      <button onClick={() => onSave(setting.key, value)} className="btn-secondary shrink-0" disabled={saving}>
        <Save className="mr-2 h-3.5 w-3.5" /> {saving ? "Saving…" : "Save"}
      </button>
    </div>
  );
}
