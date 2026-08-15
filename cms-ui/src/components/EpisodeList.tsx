import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Search, 
  Filter, 
  Edit3, 
  Trash2, 
  Film, 
  Image as ImageIcon, 
  CheckCircle2, 
  Clock, 
  Globe,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { Episode, fetchEpisodes, deleteEpisode, updateEpisode } from '../api/client';
import { EpisodeModal } from './EpisodeModal';

interface EpisodeListProps {
  role: 'editor' | 'admin';
}

export const EpisodeList: React.FC<EpisodeListProps> = ({ role }) => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [editingEpisode, setEditingEpisode] = useState<Episode | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: episodes = [], isLoading, refetch } = useQuery({
    queryKey: ['episodes', statusFilter, languageFilter, search],
    queryFn: () =>
      fetchEpisodes({
        status: statusFilter || undefined,
        language: languageFilter || undefined,
        search: search || undefined,
      }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEpisode,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
      queryClient.invalidateQueries({ queryKey: ['shows'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
  });

  const toggleStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: 'draft' | 'published' }) =>
      updateEpisode(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['episodes'] });
      queryClient.invalidateQueries({ queryKey: ['shows'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail;
      alert(typeof detail === 'string' ? detail : 'Cannot update status. Check artwork and duration.');
    },
  });

  const handleOpenEdit = (ep: Episode) => {
    setEditingEpisode(ep);
    setIsModalOpen(true);
  };

  const handleDelete = (ep: Episode) => {
    if (window.confirm(`Delete episode '${ep.title}' (${ep.id})?`)) {
      deleteMutation.mutate(ep.id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Episode Management & Assets</h2>
        <p className="text-sm text-slate-400 mt-0.5">Manage language variants, runtime durations, and artwork uploads</p>
      </div>

      {/* Filter Controls */}
      <div className="flex flex-wrap items-center gap-3 bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800">
        {/* Search */}
        <div className="relative flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by title, content group, episode ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
        >
          <option value="">All Statuses</option>
          <option value="published">Published</option>
          <option value="draft">Draft</option>
        </select>

        {/* Language Filter */}
        <select
          value={languageFilter}
          onChange={(e) => setLanguageFilter(e.target.value)}
          className="bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
        >
          <option value="">All Languages</option>
          <option value="en">English (en)</option>
          <option value="hi">Hindi (hi)</option>
        </select>
      </div>

      {/* Episodes Table */}
      {isLoading ? (
        <div className="p-12 flex flex-col items-center justify-center gap-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <span className="text-sm">Loading episodes list...</span>
        </div>
      ) : episodes.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
          <Film className="w-12 h-12 mx-auto mb-3 text-slate-600" />
          <p className="font-semibold text-slate-300">No episodes found matching filters</p>
        </div>
      ) : (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3.5">Episode</th>
                  <th className="px-4 py-3.5">Content Group</th>
                  <th className="px-4 py-3.5">Language</th>
                  <th className="px-4 py-3.5">Duration</th>
                  <th className="px-4 py-3.5">Artworks</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {episodes.map((ep) => {
                  const artworkCount = ep.artworks?.length || 0;
                  const mins = Math.floor((ep.duration_sec || 0) / 60);
                  const secs = (ep.duration_sec || 0) % 60;
                  const isTrailer = ep.id === 'ep_0093' || ep.id === 'ep_0094' || ep.title?.toLowerCase().includes('trailer');

                  return (
                    <tr key={ep.id} className="hover:bg-slate-800/40 transition">
                      {/* Title & ID */}
                      <td className="px-4 py-3.5">
                        <div className="font-bold text-white text-sm">{ep.title}</div>
                        <div className="font-mono text-[10px] text-slate-400">{ep.id} · Ep {ep.episode_number}</div>
                      </td>

                      {/* Content Group */}
                      <td className="px-4 py-3.5">
                        <span className="font-mono text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          {ep.content_group}
                        </span>
                      </td>

                      {/* Language */}
                      <td className="px-4 py-3.5">
                        <span className={`px-2 py-0.5 rounded-full font-bold text-[10px] uppercase ${
                          ep.language === 'hi'
                            ? 'bg-amber-950/80 text-amber-300 border border-amber-500/30'
                            : 'bg-blue-950/80 text-blue-300 border border-blue-500/30'
                        }`}>
                          {ep.language}
                        </span>
                      </td>

                      {/* Duration */}
                      <td className="px-4 py-3.5 text-slate-300 font-mono">
                        {mins}m {secs}s
                      </td>

                      {/* Artworks */}
                      <td className="px-4 py-3.5">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          artworkCount >= 3
                            ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-500/30'
                            : (artworkCount > 0
                                ? 'bg-amber-950/60 text-amber-400 border border-amber-500/30'
                                : 'bg-red-950/60 text-red-400 border border-red-500/30')
                        }`}>
                          <ImageIcon className="w-3 h-3" />
                          {artworkCount} / {isTrailer ? '1' : '3'} Uploaded
                        </span>
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3.5">
                        <button
                          onClick={() =>
                            toggleStatusMutation.mutate({
                              id: ep.id,
                              status: ep.status === 'published' ? 'draft' : 'published',
                            })
                          }
                          className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase transition ${
                            ep.status === 'published'
                              ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                              : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                          }`}
                        >
                          {ep.status}
                        </button>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleOpenEdit(ep)}
                            title="Edit Episode & Upload Artworks"
                            className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
                          >
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(ep)}
                            title="Delete Episode"
                            className="p-1.5 rounded-lg bg-slate-950 border border-slate-800 text-red-400 hover:bg-red-950/40 transition"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Episode Modal */}
      <EpisodeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => queryClient.invalidateQueries({ queryKey: ['episodes'] })}
        episodeToEdit={editingEpisode}
      />
    </div>
  );
};
