import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  Search, 
  Plus, 
  Edit3, 
  Trash2, 
  Layers, 
  AlertTriangle, 
  CheckCircle2, 
  Film, 
  ChevronRight,
  FolderPlus,
  Loader2
} from 'lucide-react';
import { Show, fetchShows, deleteShow, createSeason } from '../api/client';
import { ShowModal } from './ShowModal';

interface ShowListProps {
  role: 'editor' | 'admin';
  onSelectShowForEpisodes?: (show: Show) => void;
}

export const ShowList: React.FC<ShowListProps> = ({ role, onSelectShowForEpisodes }) => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [sectionFilter, setSectionFilter] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingShow, setEditingShow] = useState<Show | null>(null);

  const { data: shows = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['shows', sectionFilter, search],
    queryFn: () => fetchShows({ section: sectionFilter || undefined, search: search || undefined }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteShow,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
      queryClient.invalidateQueries({ queryKey: ['validation-report'] });
    },
  });

  const seasonMutation = useMutation({
    mutationFn: ({ showId, num }: { showId: string; num: number }) => createSeason(showId, num),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shows'] });
    },
  });

  const handleAddSeason = (show: Show) => {
    const nextSeason = (show.seasons?.length || 0) + 1;
    seasonMutation.mutate({ showId: show.id, num: nextSeason });
  };

  const handleOpenCreate = () => {
    setEditingShow(null);
    setIsModalOpen(true);
  };

  const handleOpenEdit = (show: Show) => {
    setEditingShow(show);
    setIsModalOpen(true);
  };

  const handleDelete = (show: Show) => {
    if (window.confirm(`Are you sure you want to delete show '${show.title}' and all its episodes?`)) {
      deleteMutation.mutate(show.id);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Shows & Content Groups</h2>
          <p className="text-sm text-slate-400 mt-0.5">Manage shows, seasons, and section categorization</p>
        </div>

        <button
          onClick={handleOpenCreate}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold px-4 py-2.5 rounded-xl shadow-lg shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" /> Add New Show
        </button>
      </div>

      {/* Search & Section Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 bg-slate-900/60 p-3 rounded-2xl border border-slate-800">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search shows by title, slug, synopsis..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <select
          value={sectionFilter}
          onChange={(e) => setSectionFilter(e.target.value)}
          className="bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 cursor-pointer"
        >
          <option value="">All Sections</option>
          <option value="featured">Featured</option>
          <option value="series">Series</option>
          <option value="minisodes">Minisodes</option>
          <option value="songs">Songs</option>
        </select>
      </div>

      {/* Shows List Table / Cards */}
      {isLoading ? (
        <div className="p-12 flex flex-col items-center justify-center gap-3 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
          <span className="text-sm">Loading shows & catalogue hierarchy...</span>
        </div>
      ) : shows.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
          <Film className="w-12 h-12 mx-auto mb-3 text-slate-600" />
          <p className="font-semibold text-slate-300">No shows found</p>
          <p className="text-xs text-slate-500 mt-1">Try adjusting search query or click 'Add New Show'</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {shows.map((show) => {
            const totalEpisodes = show.seasons?.reduce((acc, s) => acc + (s.episodes?.length || 0), 0) || 0;
            const publishedEpisodes = show.seasons?.reduce(
              (acc, s) => acc + (s.episodes?.filter((e) => e.status === 'published').length || 0),
              0
            ) || 0;
            const isMissingSection = !show.section;

            return (
              <div
                key={show.id}
                className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition space-y-4"
              >
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  {/* Left: Info */}
                  <div className="space-y-1.5 flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-lg text-white">{show.title}</h3>
                      <span className="font-mono text-xs text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                        {show.slug}
                      </span>
                      {isMissingSection ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-red-950/60 text-red-400 border border-red-500/40">
                          <AlertTriangle className="w-3 h-3" /> Missing Section
                        </span>
                      ) : (
                        <span className="text-[11px] font-semibold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-500/30">
                          {show.section}
                        </span>
                      )}
                    </div>

                    {show.synopsis && (
                      <p className="text-xs text-slate-400 line-clamp-2 max-w-3xl leading-relaxed">
                        {show.synopsis}
                      </p>
                    )}

                    {/* Category Tags */}
                    {show.categories && show.categories.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {show.categories.map((cat) => (
                          <span
                            key={cat}
                            className="text-[10px] font-medium bg-slate-950 text-slate-400 px-2 py-0.5 rounded border border-slate-800"
                          >
                            #{cat}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Right: Metrics & Actions */}
                  <div className="flex items-center gap-4 self-end md:self-center">
                    <div className="text-right pr-2">
                      <span className="text-xs font-semibold text-white block">
                        {publishedEpisodes} / {totalEpisodes} Published
                      </span>
                      <span className="text-[11px] text-slate-400">
                        {show.seasons?.length || 0} Season(s)
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleAddSeason(show)}
                        title="Add Next Season"
                        className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
                      >
                        <FolderPlus className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleOpenEdit(show)}
                        title="Edit Show"
                        className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 transition"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      {role === 'admin' && (
                        <button
                          onClick={() => handleDelete(show)}
                          title="Delete Show (Admin)"
                          className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-red-400 hover:bg-red-950/40 hover:border-red-500/40 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Seasons Breakdown */}
                {show.seasons && show.seasons.length > 0 && (
                  <div className="pt-3 border-t border-slate-800/80 flex flex-wrap gap-2 items-center">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mr-1">
                      Seasons:
                    </span>
                    {show.seasons.map((season) => {
                      const isTrailer = season.season_number === 0;
                      return (
                        <div
                          key={season.id}
                          className={`text-xs px-2.5 py-1 rounded-lg border font-mono flex items-center gap-1.5 ${
                            isTrailer
                              ? 'bg-purple-950/40 border-purple-500/30 text-purple-300'
                              : 'bg-slate-950 border-slate-800 text-slate-300'
                          }`}
                        >
                          <span>{isTrailer ? 'Season 0 (Trailers)' : `Season ${season.season_number}`}</span>
                          <span className="text-[10px] bg-slate-800 px-1.5 py-0.2 rounded text-slate-400">
                            {season.episodes?.length || 0} eps
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Show Modal */}
      <ShowModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={() => queryClient.invalidateQueries({ queryKey: ['shows'] })}
        showToEdit={editingShow}
      />
    </div>
  );
};
