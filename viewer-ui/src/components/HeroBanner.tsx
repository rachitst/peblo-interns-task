import React from 'react';
import { Play, Info, Sparkles, Film } from 'lucide-react';
import { CatalogueShow } from '../api/catalog';

interface HeroBannerProps {
  show?: CatalogueShow | null;
  onSelectShow: (show: CatalogueShow) => void;
}

export const HeroBanner: React.FC<HeroBannerProps> = ({ show, onSelectShow }) => {
  if (!show) return null;

  const bannerUrl = show.artworks?.banner || show.artworks?.poster || '/sample_assets/banner_good.jpg';
  const hasTrailer = show.trailers && show.trailers.length > 0;

  return (
    <section className="relative h-[75vh] min-h-[500px] max-h-[720px] w-full flex items-end pb-20 px-6 md:px-16 overflow-hidden">
      {/* Background Image & Ambient Gradients */}
      <div className="absolute inset-0 -z-10 bg-neutral-950">
        <img
          src={bannerUrl}
          alt={show.title}
          onError={(e) => {
            const target = e.currentTarget;
            if (!target.src.endsWith('/sample_assets/banner_good.jpg')) {
              target.src = '/sample_assets/banner_good.jpg';
            }
          }}
          className="w-full h-full object-cover object-center opacity-60 scale-105 filter blur-[0.5px]"
        />
        {/* Cinematic Vignette Gradients */}
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-r from-black via-black/60 to-transparent" />
      </div>

      {/* Content Envelope */}
      <div className="max-w-2xl space-y-4 relative z-20">
        {/* Section Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-600/20 border border-red-500/30 text-red-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" /> Featured on Peblo TV
        </div>

        {/* Title */}
        <h1 className="text-4xl md:text-6xl font-black tracking-tight text-white drop-shadow-lg leading-tight">
          {show.title}
        </h1>

        {/* Synopsis */}
        {show.synopsis && (
          <p className="text-sm md:text-base text-neutral-300 line-clamp-3 leading-relaxed drop-shadow max-w-xl">
            {show.synopsis}
          </p>
        )}

        {/* Category & Audio Tags */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs bg-neutral-900/80 border border-neutral-800 text-neutral-300 px-2.5 py-0.5 rounded-full font-medium">
            {show.total_episodes} Episodes
          </span>
          <span className="text-xs bg-red-950/60 border border-red-500/30 text-red-300 px-2.5 py-0.5 rounded-full font-bold">
            Dual Audio (EN · HI)
          </span>
          {show.categories?.map((cat) => (
            <span
              key={cat}
              className="text-xs bg-neutral-900/60 border border-neutral-800 text-neutral-400 px-2 py-0.5 rounded-full"
            >
              #{cat}
            </span>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3.5 pt-3">
          <button
            onClick={() => onSelectShow(show)}
            className="flex items-center gap-2 bg-white text-black hover:bg-neutral-200 font-bold px-6 py-2.5 rounded-xl text-sm transition shadow-xl hover:scale-105 active:scale-95"
          >
            <Play className="w-4 h-4 fill-black" /> Watch Episodes
          </button>
          
          {hasTrailer && (
            <button
              onClick={() => onSelectShow(show)}
              className="flex items-center gap-2 bg-red-600 hover:bg-red-500 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition shadow-lg shadow-red-600/20 hover:scale-105"
            >
              <Film className="w-4 h-4" /> Watch Trailer
            </button>
          )}

          <button
            onClick={() => onSelectShow(show)}
            className="flex items-center gap-2 bg-neutral-900/80 hover:bg-neutral-800 text-white font-semibold px-5 py-2.5 rounded-xl text-sm transition backdrop-blur border border-neutral-700 hover:scale-105"
          >
            <Info className="w-4 h-4" /> More Details
          </button>
        </div>
      </div>
    </section>
  );
};
