import React, { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, Plus, AlertCircle } from 'lucide-react';
import { Show, createShow, updateShow } from '../api/client';

interface ShowModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  showToEdit?: Show | null;
}

const AVAILABLE_SECTIONS = ['featured', 'series', 'minisodes', 'songs'];
const AVAILABLE_CATEGORIES = [
  'adventure', 'folk', 'friendship', 'india', 'language', 'learning',
  'maths', 'music', 'nature', 'reading', 'science', 'singalong',
  'stories', 'travel', 'values'
];

export const ShowModal: React.FC<ShowModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  showToEdit,
}) => {
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [section, setSection] = useState<string>('series');
  const [synopsis, setSynopsis] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (showToEdit) {
      setTitle(showToEdit.title || '');
      setSlug(showToEdit.slug || '');
      setSection(showToEdit.section || '');
      setSynopsis(showToEdit.synopsis || '');
      setSelectedCategories(showToEdit.categories || []);
    } else {
      setTitle('');
      setSlug('');
      setSection('series');
      setSynopsis('');
      setSelectedCategories([]);
    }
    setErrorMessage(null);
  }, [showToEdit, isOpen]);

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setTitle(val);
    if (!showToEdit) {
      setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, ''));
    }
  };

  const toggleCategory = (cat: string) => {
    if (selectedCategories.includes(cat)) {
      setSelectedCategories(selectedCategories.filter((c) => c !== cat));
    } else {
      setSelectedCategories([...selectedCategories, cat]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const payload = {
        title,
        slug,
        section: section || null,
        synopsis,
        categories: selectedCategories,
      };

      if (showToEdit) {
        await updateShow(showToEdit.id, payload);
      } else {
        await createShow(payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setErrorMessage(typeof detail === 'string' ? detail : 'Failed to save show.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-lg font-bold text-white">
              {showToEdit ? 'Edit Show Details' : 'Create New Show'}
            </h3>
            <p className="text-xs text-slate-400">Configure show metadata, sections, and category tags</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-red-950/40 border border-red-500/40 text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Show Title *</label>
            <input
              type="text"
              required
              value={title}
              onChange={handleTitleChange}
              placeholder="e.g. Moti's Many Lives"
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Slug */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Slug *</label>
            <input
              type="text"
              required
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="e.g. motis-many-lives"
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm font-mono text-slate-300 focus:outline-none focus:border-indigo-500"
            />
          </div>

          {/* Section */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Section</label>
            <select
              value={section}
              onChange={(e) => setSection(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="">-- No Section Assigned (Triggers Validation Blocker) --</option>
              {AVAILABLE_SECTIONS.map((sec) => (
                <option key={sec} value={sec}>
                  {sec.charAt(0).toUpperCase() + sec.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Categories */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1.5">
              Categories ({selectedCategories.length} selected)
            </label>
            <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-950 rounded-xl border border-slate-800">
              {AVAILABLE_CATEGORIES.map((cat) => {
                const isSelected = selectedCategories.includes(cat);
                return (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => toggleCategory(cat)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                      isSelected
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Synopsis */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Synopsis</label>
            <textarea
              rows={3}
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              placeholder="Detailed storyline description for viewers and search indexing..."
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-xl text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
            >
              {isSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {showToEdit ? 'Save Changes' : 'Create Show'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
