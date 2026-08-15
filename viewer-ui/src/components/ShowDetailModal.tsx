import React, { useState } from 'react';
import { X, Play, Film, Globe, Clock } from 'lucide-react';
import { CatalogueShow } from '../api/catalog';

interface ShowDetailModalProps {
  show: CatalogueShow | null;
  onClose: () => void;
}

export const ShowDetailModal: React.FC<ShowDetailModalProps> = ({ show, onClose }) => {
  if (!show) return null;

  const [selectedSeasonNum, setSelectedSeasonNum] = useState<number>(
    show.seasons && show.seasons.length > 0 ? show.seasons[0].season_number : 1
  );
  const [selectedEpisodeLang, setSelectedEpisodeLang] = useState<Record<string, string>>({});
  const [, setPlayingItem] = useState<string | null>(null);

  const bannerUrl = show.artworks?.banner || show.artworks?.poster || '/sample_assets/banner_good.jpg';
  const activeSeason = show.seasons?.find((s) => s.season_number === selectedSeasonNum);
  const hasTrailers = show.trailers && show.trailers.length > 0;

  const handleLangToggle = (contentGroup: string, lang: string) => {
    setSelectedEpisodeLang((prev) => ({ ...prev, [contentGroup]: lang }));
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 md:p-8 overflow-y-auto">
      <div className="bg-neutral-950 border border-neutral-800 rounded-3xl max-w-4xl w-full overflow-hidden shadow-2xl space-y-6 my-auto max-h-[92vh] flex flex-col">
        {/* Banner Hero Header */}
        <div className="relative h-64 md:h-80 w-full shrink-0 flex items-end p-6 md:p-8">
          <img
            src={bannerUrl}
            alt={show.title}
            onError={(e) => {
              const target = e.currentTarget;
              if (!target.src.endsWith('/sample_assets/banner_good.jpg')) {
                target.src = '/sample_assets/banner_good.jpg';
              }
            }}
            className="absolute inset-0 w-full h-full object-cover opacity-60"
          />

          {/* Gradients */}
          <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/50 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-neutral-950 via-neutral-950/40 to-transparent" />

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-black/60 hover:bg-black/90 text-white border border-neutral-700 transition"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Show Header Info */}
          <div className="relative z-10 space-y-2 max-w-xl">
            <span className="text-xs uppercase font-bold px-2.5 py-0.5 rounded-full bg-red-600/30 text-red-400 border border-red-500/30">
              {show.section}
            </span>
            <h2 className="text-3xl md:text-5xl font-black text-white tracking-tight drop-shadow-md">
              {show.title}
            </h2>
            <div className="flex flex-wrap gap-2 text-xs text-neutral-300">
              <span>{show.total_episodes} Total Episodes</span>
              <span>·</span>
              <span className="text-red-400 font-semibold">Dual Audio (EN · HI)</span>
              {show.categories?.map((c) => (
                <span key={c} className="text-neutral-400">#{c}</span>
              ))}
            </div>
          </div>
        </div>

        {/* Modal Body Scroll Area */}
        <div className="p-6 md:p-8 space-y-8 overflow-y-auto flex-1">
          {/* Synopsis */}
          {show.synopsis && (
            <div className="space-y-1.5">
              <h4 className="text-xs uppercase font-bold tracking-wider text-neutral-400">Synopsis</h4>
              <p className="text-sm text-neutral-200 leading-relaxed max-w-3xl">
                {show.synopsis}
              </p>
            </div>
          )}

          {/* Dedicated Trailers Section (Season 0) */}
          {hasTrailers && (
            <div className="space-y-3 p-5 rounded-2xl bg-neutral-900/60 border border-neutral-800">
              <div className="flex items-center gap-2">
                <Film className="w-4 h-4 text-red-500" />
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                  Official Trailers & Previews (Season 0)
                </h3>
              </div>
              <p className="text-xs text-neutral-400">
                Trailers are isolated from the main episode catalogue
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                {show.trailers.map((trailer) => {
                  const trailerThumb = trailer.artworks?.thumbnail || trailer.artworks?.banner || '/sample_assets/thumb_good.jpg';
                  return (
                    <div
                      key={trailer.episode_id}
                      className="flex items-center gap-3 p-3 rounded-xl bg-black/60 border border-neutral-800 hover:border-neutral-700 transition"
                    >
                      <div className="w-24 aspect-[16/9] rounded-lg bg-neutral-900 shrink-0 overflow-hidden relative group">
                        <img
                          src={trailerThumb}
                          alt={trailer.title}
                          onError={(e) => {
                            const target = e.currentTarget;
                            if (!target.src.endsWith('/sample_assets/thumb_good.jpg')) {
                              target.src = '/sample_assets/thumb_good.jpg';
                            }
                          }}
                          className="w-full h-full object-cover"
                        />
                        <div 
                          onClick={() => setPlayingItem(trailer.episode_id)}
                          className="absolute inset-0 bg-black/40 flex items-center justify-center cursor-pointer hover:bg-black/20 transition"
                        >
                          <Play className="w-5 h-5 fill-white text-white" />
                        </div>
                      </div>

                      <div className="flex-1 min-w-0">
                        <h4 className="font-bold text-xs text-white truncate">{trailer.title}</h4>
                        <div className="text-[11px] text-neutral-400 mt-0.5 flex items-center gap-2">
                          <span>{trailer.duration_sec}s</span>
                          <span className="uppercase font-mono text-[9px] px-1 rounded bg-neutral-800 text-neutral-300">
                            {trailer.language}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Regular Episodes Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <h3 className="text-lg font-bold text-white">Episodes</h3>

              {/* Season Selector */}
              {show.seasons && show.seasons.length > 1 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-neutral-400">Season:</span>
                  <select
                    value={selectedSeasonNum}
                    onChange={(e) => setSelectedSeasonNum(Number(e.target.value))}
                    className="bg-neutral-900 border border-neutral-800 rounded-xl px-3 py-1.5 text-xs text-white focus:outline-none focus:border-red-500 cursor-pointer"
                  >
                    {show.seasons.map((s) => (
                      <option key={s.season_number} value={s.season_number}>
                        Season {s.season_number} ({s.episodes?.length || 0} eps)
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* Episodes List with Collapsed Language Variants */}
            {!activeSeason || !activeSeason.episodes || activeSeason.episodes.length === 0 ? (
              <div className="p-8 text-center text-xs text-neutral-500">
                No episodes published in Season {selectedSeasonNum}.
              </div>
            ) : (
              <div className="space-y-3">
                {activeSeason.episodes.map((ep) => {
                  const currentLang = selectedEpisodeLang[ep.content_group] || ep.languages[0] || 'en';
                  const activeVariant = ep.variants?.find((v) => v.language === currentLang) || {
                    title: ep.title,
                    duration_sec: ep.duration_sec,
                    synopsis: ep.synopsis,
                  };
                  const thumb = ep.artworks?.thumbnail || ep.artworks?.banner || ep.artworks?.poster || '/sample_assets/thumb_good.jpg';
                  const mins = Math.floor(activeVariant.duration_sec / 60);
                  const secs = activeVariant.duration_sec % 60;

                  return (
                    <div
                      key={ep.content_group}
                      className="p-4 rounded-2xl bg-neutral-900/60 border border-neutral-800/80 hover:border-neutral-700 transition flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
                    >
                      {/* Left: Thumbnail & Details */}
                      <div className="flex items-start gap-4 flex-1 min-w-0">
                        <div className="relative w-32 aspect-[16/9] rounded-xl bg-neutral-950 shrink-0 overflow-hidden group">
                          <img
                            src={thumb}
                            alt={activeVariant.title}
                            onError={(e) => {
                              const target = e.currentTarget;
                              if (!target.src.endsWith('/sample_assets/thumb_good.jpg')) {
                                target.src = '/sample_assets/thumb_good.jpg';
                              }
                            }}
                            className="w-full h-full object-cover"
                          />
                          <div 
                            onClick={() => setPlayingItem(ep.content_group)}
                            className="absolute inset-0 bg-black/30 flex items-center justify-center cursor-pointer hover:bg-black/10 transition"
                          >
                            <Play className="w-5 h-5 fill-white text-white drop-shadow" />
                          </div>
                        </div>

                        <div className="space-y-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-bold text-neutral-400 font-mono">
                              Ep {ep.episode_number}
                            </span>
                            <h4 className="font-bold text-sm text-white truncate">
                              {activeVariant.title}
                            </h4>
                          </div>

                          <div className="flex items-center gap-2 text-xs text-neutral-400">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" /> {mins}m {secs}s
                            </span>
                          </div>

                          {activeVariant.synopsis && (
                            <p className="text-xs text-neutral-400 line-clamp-2 leading-relaxed">
                              {activeVariant.synopsis}
                            </p>
                          )}
                        </div>
                      </div>

                      {/* Right: Language Variant Switcher */}
                      <div className="flex items-center gap-2 self-end md:self-center bg-neutral-950 p-1.5 rounded-xl border border-neutral-800">
                        <Globe className="w-3.5 h-3.5 text-neutral-400 ml-1" />
                        <span className="text-[11px] text-neutral-400 mr-1">Audio:</span>
                        {ep.languages.map((lang) => (
                          <button
                            key={lang}
                            onClick={() => handleLangToggle(ep.content_group, lang)}
                            className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase transition ${
                              currentLang === lang
                                ? 'bg-red-600 text-white shadow-md'
                                : 'text-neutral-400 hover:text-white'
                            }`}
                          >
                            {lang}
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
