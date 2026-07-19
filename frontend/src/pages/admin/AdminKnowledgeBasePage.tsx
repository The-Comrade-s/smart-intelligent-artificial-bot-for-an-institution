import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { cn } from "../../lib/utils";
import {
  FAQ,
  KnowledgeArticle,
  createArticle,
  createFAQ,
  deleteArticle,
  deleteFAQ,
  listArticles,
  listFAQs,
} from "../../lib/adminApi";

export default function AdminKnowledgeBasePage() {
  const [tab, setTab] = useState<"articles" | "faqs">("articles");
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [faqs, setFaqs] = useState<FAQ[]>([]);
  const [showForm, setShowForm] = useState(false);

  const [articleForm, setArticleForm] = useState({ title: "", category: "", content: "", status: "published" });
  const [faqForm, setFaqForm] = useState({ category: "", question: "", answer: "", status: "published" });

  async function load() {
    setArticles(await listArticles());
    setFaqs(await listFAQs());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreateArticle(e: React.FormEvent) {
    e.preventDefault();
    await createArticle(articleForm);
    setArticleForm({ title: "", category: "", content: "", status: "published" });
    setShowForm(false);
    load();
  }

  async function handleCreateFAQ(e: React.FormEvent) {
    e.preventDefault();
    await createFAQ(faqForm);
    setFaqForm({ category: "", question: "", answer: "", status: "published" });
    setShowForm(false);
    load();
  }

  async function handleDeleteArticle(id: string) {
    if (!confirm("Delete this article?")) return;
    await deleteArticle(id);
    setArticles((prev) => prev.filter((a) => a.id !== id));
  }

  async function handleDeleteFAQ(id: string) {
    if (!confirm("Delete this FAQ?")) return;
    await deleteFAQ(id);
    setFaqs((prev) => prev.filter((f) => f.id !== id));
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-navy-900">Knowledge Base</h1>
        <button onClick={() => setShowForm((s) => !s)} className="btn-primary">
          <Plus className="mr-2 h-4 w-4" /> New {tab === "articles" ? "Article" : "FAQ"}
        </button>
      </div>

      <div className="flex gap-2 border-b border-slate-200">
        {(["articles", "faqs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => {
              setTab(t);
              setShowForm(false);
            }}
            className={cn(
              "px-4 py-2 text-sm font-medium capitalize",
              tab === t ? "border-b-2 border-royal-600 text-royal-600" : "text-slate-500"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {showForm && tab === "articles" && (
        <form onSubmit={handleCreateArticle} className="card space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input required className="input-field" placeholder="Title" value={articleForm.title} onChange={(e) => setArticleForm((f) => ({ ...f, title: e.target.value }))} />
            <input required className="input-field" placeholder="Category" value={articleForm.category} onChange={(e) => setArticleForm((f) => ({ ...f, category: e.target.value }))} />
          </div>
          <textarea required className="input-field min-h-[120px]" placeholder="Content" value={articleForm.content} onChange={(e) => setArticleForm((f) => ({ ...f, content: e.target.value }))} />
          <button type="submit" className="btn-primary">
            Save Article
          </button>
        </form>
      )}

      {showForm && tab === "faqs" && (
        <form onSubmit={handleCreateFAQ} className="card space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input required className="input-field" placeholder="Category" value={faqForm.category} onChange={(e) => setFaqForm((f) => ({ ...f, category: e.target.value }))} />
          </div>
          <input required className="input-field" placeholder="Question" value={faqForm.question} onChange={(e) => setFaqForm((f) => ({ ...f, question: e.target.value }))} />
          <textarea required className="input-field min-h-[100px]" placeholder="Answer" value={faqForm.answer} onChange={(e) => setFaqForm((f) => ({ ...f, answer: e.target.value }))} />
          <button type="submit" className="btn-primary">
            Save FAQ
          </button>
        </form>
      )}

      {tab === "articles" && (
        <div className="space-y-3">
          {articles.map((a) => (
            <div key={a.id} className="card flex items-start justify-between">
              <div>
                <div className="mb-1 flex items-center gap-2">
                  <span className="font-semibold text-navy-900">{a.title}</span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase text-slate-500">{a.category}</span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase text-slate-500">{a.status}</span>
                </div>
                <p className="line-clamp-2 text-sm text-slate-600">{a.content}</p>
                <p className="mt-1 text-xs text-slate-400">{a.view_count} views</p>
              </div>
              <button onClick={() => handleDeleteArticle(a.id)} className="text-slate-400 hover:text-red-500">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          {articles.length === 0 && <p className="text-center text-sm text-slate-400">No articles yet.</p>}
        </div>
      )}

      {tab === "faqs" && (
        <div className="space-y-3">
          {faqs.map((f) => (
            <div key={f.id} className="card flex items-start justify-between">
              <div>
                <div className="mb-1 flex items-center gap-2">
                  <span className="font-semibold text-navy-900">{f.question}</span>
                  <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase text-slate-500">{f.category}</span>
                </div>
                <p className="text-sm text-slate-600">{f.answer}</p>
              </div>
              <button onClick={() => handleDeleteFAQ(f.id)} className="text-slate-400 hover:text-red-500">
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          {faqs.length === 0 && <p className="text-center text-sm text-slate-400">No FAQs yet.</p>}
        </div>
      )}
    </div>
  );
}
