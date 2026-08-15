import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Navbar } from './components/Navbar';
import { HeroBanner } from './components/HeroBanner';
import { SectionRow } from './components/SectionRow';
import { ShowDetailModal } from './components/ShowDetailModal';
import { SearchResults } from './components/SearchResults';
import { fetchCatalogue, searchCatalogue, CatalogueShow } from './api/catalog';
import { Film, Loader2 } from 'lucide-react';

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [activeSection, setActiveSection] = useState('all');
  const [selectedShow, setSelectedShow] = useState<CatalogueShow | null>(null);

  // Fetch full published catalogue
  const {
    data: catalogue,
    isLoading: isCatLoading,
    isError: isCatError,
  } = useQuery({
    queryKey: ['catalogue'],
    queryFn: fetchCatalogue,
    retry: 2,
  });

  // Search query
  const isSearching = !!searchQuery || !!selectedCategory || !!selectedLanguage;
  const {
    data: searchData,
    isLoading: isSearchLoading,
  } = useQuery({
    queryKey: ['search', searchQuery, selectedCategory, selectedLanguage, activeSection],
    queryFn: () =>
      searchCatalogue({
        q: searchQuery || undefined,
        category: selectedCategory || undefined,
        language: selectedLanguage || undefined,
        section: activeSection !== 'all' ? activeSection : undefined,
      }),
    enabled: isSearching,
  });

  const featuredShows = catalogue?.sections?.featured || [];
  const seriesShows = catalogue?.sections?.series || [];
  const minisodesShows = catalogue?.sections?.minisodes || [];
  const songsShows = catalogue?.sections?.songs || [];

  // Pick first featured show for hero
  const heroShow = featuredShows.length > 0 ? featuredShows[0] : (seriesShows[0] || null);

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-red-600 selection:text-white">
      {/* Top Navbar */}
      <Navbar
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        selectedLanguage={selectedLanguage}
        setSelectedLanguage={setSelectedLanguage}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        activeSection={activeSection}
        setActiveSection={setActiveSection}
      />

      {/* Main Viewport */}
      {isSearching ? (
        <SearchResults
          query={searchQuery}
          results={searchData?.results || []}
          isLoading={isSearchLoading}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          onSelectShow={setSelectedShow}
        />
      ) : isCatLoading ? (
        <div className="h-screen flex flex-col items-center justify-center gap-3 text-neutral-400">
          <Loader2 className="w-10 h-10 animate-spin text-red-600" />
          <span className="text-sm font-medium">Loading published catalogue...</span>
        </div>
      ) : isCatError ? (
        <div className="h-screen flex flex-col items-center justify-center p-8 text-center space-y-4">
          <div className="p-4 rounded-full bg-red-950/40 border border-red-500/40 text-red-400">
            <Film className="w-10 h-10" />
          </div>
          <h2 className="text-2xl font-bold text-white">Catalogue Not Published Yet</h2>
          <p className="text-xs text-neutral-400 max-w-md leading-relaxed">
            The viewer catalogue has not been published yet. Please open the <strong>Internal CMS (Port 3000)</strong>, resolve any pre-flight validation blockers, and click <strong>Publish Catalogue</strong>.
          </p>
        </div>
      ) : (
        <div className="space-y-6 pb-24">
          {/* Hero Banner for Home View */}
          {activeSection === 'all' && (
            <HeroBanner show={heroShow} onSelectShow={setSelectedShow} />
          )}

          {/* Section Rows */}
          <div className={`px-6 md:px-16 space-y-10 relative z-20 ${activeSection === 'all' ? '-mt-10' : 'pt-24'}`}>
            {(activeSection === 'all' || activeSection === 'featured') && (
              <SectionRow
                title="Featured on Peblo TV"
                sectionKey="featured"
                shows={featuredShows}
                onSelectShow={setSelectedShow}
              />
            )}

            {(activeSection === 'all' || activeSection === 'series') && (
              <SectionRow
                title="Original Series & Stories"
                sectionKey="series"
                shows={seriesShows}
                onSelectShow={setSelectedShow}
              />
            )}

            {(activeSection === 'all' || activeSection === 'minisodes') && (
              <SectionRow
                title="Minisodes & Learning Bytes"
                sectionKey="minisodes"
                shows={minisodesShows}
                onSelectShow={setSelectedShow}
              />
            )}

            {(activeSection === 'all' || activeSection === 'songs') && (
              <SectionRow
                title="Peblo Songs & Sing-Alongs"
                sectionKey="songs"
                shows={songsShows}
                onSelectShow={setSelectedShow}
              />
            )}
          </div>
        </div>
      )}

      {/* Show Detail Modal */}
      <ShowDetailModal show={selectedShow} onClose={() => setSelectedShow(null)} />
    </div>
  );
}
