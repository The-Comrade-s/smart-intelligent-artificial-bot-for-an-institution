import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Bot } from "lucide-react";
import { useAuth } from "../store/authStore";
import AuthSplitLayout from "../layouts/AuthSplitLayout";
import PasswordStrength from "../components/PasswordStrength";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: "",
    username: "",
    email: "",
    matric_number: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function update<K extends keyof typeof form>(key: K, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await register({ ...form, matric_number: form.matric_number || undefined });
      navigate("/chat");
    } catch (err: any) {
      setError(err?.response?.data?.error?.message ?? "Unable to register. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthSplitLayout>
      <Link to="/" className="mb-8 flex items-center justify-center gap-2 font-display text-lg font-bold text-navy-900 lg:hidden">
        <Bot className="h-6 w-6 text-royal-600" /> COSIB
      </Link>
      <div className="card">
        <h1 className="mb-1 font-display text-xl font-bold">Create your account</h1>
        <p className="mb-6 text-sm text-slate-500">Join COSIB as a student.</p>

        {error && (
          <div role="alert" className="mb-4 animate-fade-in rounded-xl bg-red-50 px-4 py-2.5 text-sm text-red-600">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="full_name" className="mb-1 block text-sm font-medium text-slate-700">
              Full name
            </label>
            <input id="full_name" required className="input-field" value={form.full_name} onChange={(e) => update("full_name", e.target.value)} autoComplete="name" />
          </div>
          <div>
            <label htmlFor="username" className="mb-1 block text-sm font-medium text-slate-700">
              Username
            </label>
            <input id="username" required className="input-field" value={form.username} onChange={(e) => update("username", e.target.value)} autoComplete="username" />
          </div>
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input id="email" type="email" required className="input-field" value={form.email} onChange={(e) => update("email", e.target.value)} autoComplete="email" />
          </div>
          <div>
            <label htmlFor="matric_number" className="mb-1 block text-sm font-medium text-slate-700">
              Matric number (optional)
            </label>
            <input id="matric_number" className="input-field" value={form.matric_number} onChange={(e) => update("matric_number", e.target.value)} />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              className="input-field"
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              autoComplete="new-password"
            />
            <PasswordStrength password={form.password} />
            <p className="mt-1 text-xs text-slate-400">At least 8 characters, one number, one uppercase letter.</p>
          </div>
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full">
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <div className="my-5 flex items-center gap-3">
          <div className="h-px flex-1 bg-slate-100" />
          <span className="text-xs text-slate-400">or</span>
          <div className="h-px flex-1 bg-slate-100" />
        </div>

        <button type="button" disabled title="Coming soon" className="btn-secondary w-full cursor-not-allowed opacity-50">
          Continue with Google (coming soon)
        </button>

        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-semibold text-royal-600">
            Log in
          </Link>
        </p>
      </div>
    </AuthSplitLayout>
  );
}
