import React from 'react';
import { Film } from 'lucide-react';
import { CatalogueShow } from '../api/catalog';

interface SearchResultsProps {
  query: string;
  results: CatalogueShow[];
  isLoading: boolean;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  onSelectShow: (show: CatalogueShow) => void;
}

const CATEGORIES = [
  'adventure', 'folk', 'friendship', 'india', 'language', 'learning',
  'maths', 'music', 'nature', 'reading', 'science', 'singalong',
  'stories', 'travel', 'values'
];

export const SearchResults: React.FC<SearchResultsProps> = ({
  query,
  results,
  isLoading,
  selectedCategory,
  setSelectedCategory,
  onSelectShow,
}) => {
  return (
    <div className="pt-24 px-6 md:px-16 pb-20 space-y-8 min-h-screen">
      {/* Search Header */}
      <div className="space-y-4">
        <div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">
            {query ? `Search Results for "${query}"` : 'Browse by Category & Search'}
          </h2>
          <p className="text-xs text-neutral-400 mt-1">
            {isLoading ? 'Searching...' : `Found ${results.length} show(s)`}
          </p>
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap gap-2 pt-2">
          <button
            onClick={() => setSelectedCategory('')}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
              !selectedCategory
                ? 'bg-red-600 text-white'
                : 'bg-neutral-900 text-neutral-400 hover:text-white border border-neutral-800'
            }`}
          >
            All Categories
          </button>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(selectedCategory === cat ? '' : cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold capitalize transition ${
                selectedCategory === cat
                  ? 'bg-red-600 text-white'
                  : 'bg-neutral-900 text-neutral-400 hover:text-white border border-neutral-800'
              }`}
            >
              #{cat}
            </button>
          ))}
        </div>
      </div>

      {/* Results Grid */}
      {isLoading ? (
        <div className="p-16 text-center text-neutral-400 text-sm">Searching catalogue...</div>
      ) : results.length === 0 ? (
        <div className="p-16 rounded-3xl bg-neutral-900/40 border border-neutral-800 text-center space-y-3">
          <Film className="w-12 h-12 mx-auto text-neutral-600" />
          <h3 className="text-lg font-bold text-neutral-300">No shows or songs found</h3>
          <p className="text-xs text-neutral-500 max-w-sm mx-auto">
            Try searching for a different title, category tag, or reset audio language filters.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          {results.map((show) => {
            const posterUrl = show.artworks?.poster || show.artworks?.banner || show.artworks?.thumbnail || '/sample_assets/poster_good.jpg';
            return (
              <div
                key={show.id}
                onClick={() => onSelectShow(show)}
                className="group relative aspect-[2/3] rounded-2xl bg-neutral-900 border border-neutral-800/80 hover:border-neutral-600 transition-all duration-300 hover:scale-105 cursor-pointer overflow-hidden shadow-lg shadow-black/60 flex flex-col justify-end p-3.5"
              >
                <img
                  src={posterUrl}
                  alt={show.title}
                  onError={(e) => {
                    const target = e.currentTarget;
                    if (!target.src.endsWith('/sample_assets/poster_good.jpg')) {
                      target.src = '/sample_assets/poster_good.jpg';
                    }
                  }}
                  className="absolute inset-0 w-full h-full object-cover group-hover:opacity-85 transition-opacity"
                />

                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent opacity-90 group-hover:opacity-75 transition-opacity" />

                <div className="relative z-10 space-y-1">
                  <h3 className="font-bold text-sm text-white drop-shadow truncate group-hover:text-red-400 transition-colors">
                    {show.title}
                  </h3>
                  <div className="flex items-center justify-between text-[11px] text-neutral-300">
                    <span className="capitalize">{show.section}</span>
                    <span>{show.total_episodes} eps</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
