import React, { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { X, Sparkles, Loader2, AlertCircle, CheckCircle2, Film } from 'lucide-react';
import { Episode, updateEpisode, createEpisode, Artwork } from '../api/client';
import { ArtworkDropzone } from './ArtworkDropzone';

interface EpisodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  episodeToEdit?: Episode | null;
  seasonIdForNewEpisode?: string;
}

export const EpisodeModal: React.FC<EpisodeModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  episodeToEdit,
  seasonIdForNewEpisode,
}) => {
  const queryClient = useQueryClient();

  const [title, setTitle] = useState('');
  const [contentGroup, setContentGroup] = useState('');
  const [episodeNumber, setEpisodeNumber] = useState(1);
  const [language, setLanguage] = useState('en');
  const [durationSec, setDurationSec] = useState(300);
  const [synopsis, setSynopsis] = useState('');
  const [status, setStatus] = useState<'draft' | 'published'>('draft');
  const [artworks, setArtworks] = useState<Artwork[]>([]);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (episodeToEdit) {
      setTitle(episodeToEdit.title || '');
      setContentGroup(episodeToEdit.content_group || '');
      setEpisodeNumber(episodeToEdit.episode_number || 1);
      setLanguage(episodeToEdit.language || 'en');
      setDurationSec(episodeToEdit.duration_sec || 0);
      setSynopsis(episodeToEdit.synopsis || '');
      setStatus(episodeToEdit.status || 'draft');
      setArtworks(episodeToEdit.artworks || []);
    } else {
      setTitle('');
      setContentGroup('');
      setEpisodeNumber(1);
      setLanguage('en');
      setDurationSec(300);
      setSynopsis('');
      setStatus('draft');
      setArtworks([]);
    }
    setErrorMessage(null);
  }, [episodeToEdit, isOpen]);

  const handleArtworkSuccess = (newArtwork: Artwork) => {
    setArtworks((prev) => {
      const filtered = prev.filter((a) => a.type !== newArtwork.type);
      return [...filtered, newArtwork];
    });
    queryClient.invalidateQueries({ queryKey: ['episodes'] });
    queryClient.invalidateQueries({ queryKey: ['shows'] });
    queryClient.invalidateQueries({ queryKey: ['validation-report'] });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      const payload = {
        title,
        content_group: contentGroup,
        episode_number: Number(episodeNumber),
        language,
        duration_sec: Number(durationSec),
        synopsis,
        status,
      };

      if (episodeToEdit) {
        await updateEpisode(episodeToEdit.id, payload);
      } else if (seasonIdForNewEpisode) {
        await createEpisode(seasonIdForNewEpisode, payload);
      }
      onSuccess();
      onClose();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      setErrorMessage(typeof detail === 'string' ? detail : 'Failed to save episode.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  const posterArt = artworks.find((a) => a.type === 'poster');
  const bannerArt = artworks.find((a) => a.type === 'banner');
  const thumbArt = artworks.find((a) => a.type === 'thumbnail');

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-4xl w-full p-6 shadow-2xl space-y-6 max-h-[92vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">
                {episodeToEdit ? `Edit Episode: ${episodeToEdit.id}` : 'Create New Episode'}
              </h3>
              <span className={`text-xs px-2 py-0.5 rounded-full font-semibold uppercase ${
                status === 'published' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-amber-950 text-amber-400 border border-amber-500/30'
              }`}>
                {status}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">Manage episode metadata, language variants, and artwork uploads</p>
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

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Metadata Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Title */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Episode Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. The Lost Kite"
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Content Group */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Content Group * <span className="text-slate-400 font-normal">(Shared across EN/HI variants)</span>
              </label>
              <input
                type="text"
                required
                value={contentGroup}
                onChange={(e) => setContentGroup(e.target.value)}
                placeholder="e.g. motis-many-lives-s01e01"
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm font-mono text-slate-300 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Language */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Language *</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
              >
                <option value="en">English (en)</option>
                <option value="hi">Hindi (hi)</option>
              </select>
            </div>

            {/* Episode Number */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Episode Number *</label>
              <input
                type="number"
                min={0}
                required
                value={episodeNumber}
                onChange={(e) => setEpisodeNumber(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Duration (Seconds) */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">
                Duration (Seconds) * {durationSec > 0 && <span className="text-slate-400 font-normal">({Math.floor(durationSec/60)}m {durationSec%60}s)</span>}
              </label>
              <input
                type="number"
                min={0}
                required
                value={durationSec}
                onChange={(e) => setDurationSec(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Status */}
            <div>
              <label className="text-xs font-semibold text-slate-300 block mb-1">Status</label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as 'draft' | 'published')}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
              >
                <option value="draft">Draft (Work in Progress)</option>
                <option value="published">Published (Visible in Catalogue)</option>
              </select>
            </div>
          </div>

          {/* Synopsis */}
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-1">Episode Synopsis</label>
            <textarea
              rows={2}
              value={synopsis}
              onChange={(e) => setSynopsis(e.target.value)}
              placeholder="Brief summary of this episode..."
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500 resize-none"
            />
          </div>

          {/* Dedicated Artwork Upload Slots (Only when episode exists) */}
          {episodeToEdit ? (
            <div className="space-y-3 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">Artwork Upload Slots</h4>
                  <p className="text-xs text-slate-400">Validated via Pillow against canonical specs (200 KB ceiling enforced)</p>
                </div>
                <span className="text-xs text-slate-400 font-mono">
                  {artworks.length} / 3 Uploaded
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <ArtworkDropzone
                  episodeId={episodeToEdit.id}
                  artworkType="poster"
                  existingArtwork={posterArt}
                  onUploadSuccess={handleArtworkSuccess}
                />
                <ArtworkDropzone
                  episodeId={episodeToEdit.id}
                  artworkType="banner"
                  existingArtwork={bannerArt}
                  onUploadSuccess={handleArtworkSuccess}
                />
                <ArtworkDropzone
                  episodeId={episodeToEdit.id}
                  artworkType="thumbnail"
                  existingArtwork={thumbArt}
                  onUploadSuccess={handleArtworkSuccess}
                />
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-400 text-center">
              Please save the episode first to unlock artwork upload dropzones.
            </div>
          )}

          {/* Footer Actions */}
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
              {episodeToEdit ? 'Save Changes' : 'Create Episode'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
