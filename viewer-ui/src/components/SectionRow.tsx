import React from 'react';
import { ChevronRight } from 'lucide-react';
import { CatalogueShow } from '../api/catalog';

interface SectionRowProps {
  title: string;
  sectionKey: string;
  shows: CatalogueShow[];
  onSelectShow: (show: CatalogueShow) => void;
}

export const SectionRow: React.FC<SectionRowProps> = ({
  title,
  shows,
  onSelectShow,
}) => {
  if (!shows || shows.length === 0) return null;

  return (
    <div className="space-y-3.5">
      {/* Row Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold tracking-tight text-neutral-100 flex items-center gap-2 group cursor-pointer">
          <span>{title}</span>
          <ChevronRight className="w-4 h-4 text-neutral-500 group-hover:text-white transition-colors" />
        </h2>
        <span className="text-xs text-neutral-500 font-medium">
          {shows.length} {shows.length === 1 ? 'Show' : 'Shows'}
        </span>
      </div>

      {/* Horizontal Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
        {shows.map((show) => {
          const posterUrl = show.artworks?.poster || show.artworks?.banner || show.artworks?.thumbnail || '/sample_assets/poster_good.jpg';
          const languages = Array.from(
            new Set(
              show.seasons?.flatMap((s) => s.episodes?.flatMap((e) => e.languages || []) || []) || []
            )
          );

          return (
            <div
              key={show.id}
              onClick={() => onSelectShow(show)}
              className="group relative aspect-[2/3] rounded-2xl bg-neutral-900 border border-neutral-800/80 hover:border-neutral-600 transition-all duration-300 hover:scale-105 cursor-pointer overflow-hidden shadow-lg shadow-black/60 flex flex-col justify-end p-3.5"
            >
              {/* Background Poster Image */}
              <img
                src={posterUrl}
                alt={show.title}
                loading="lazy"
                onError={(e) => {
                  const target = e.currentTarget;
                  if (!target.src.endsWith('/sample_assets/poster_good.jpg')) {
                    target.src = '/sample_assets/poster_good.jpg';
                  }
                }}
                className="absolute inset-0 w-full h-full object-cover group-hover:opacity-85 transition-opacity"
              />

              {/* Gradient Vignette Overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/30 to-transparent opacity-90 group-hover:opacity-75 transition-opacity" />

              {/* Bottom Card Content */}
              <div className="relative z-10 space-y-1">
                <h3 className="font-bold text-sm text-white drop-shadow truncate group-hover:text-red-400 transition-colors">
                  {show.title}
                </h3>
                
                <div className="flex items-center justify-between text-[11px] text-neutral-300">
                  <span>{show.total_episodes} eps</span>
                  {languages.length > 0 && (
                    <span className="text-[10px] font-bold uppercase px-1.5 py-0.2 rounded bg-black/60 border border-neutral-700 text-neutral-300">
                      {languages.join(' · ')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
