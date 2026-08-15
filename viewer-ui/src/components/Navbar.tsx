import React from 'react';
import { Search, Globe, X, Film } from 'lucide-react';

interface NavbarProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  selectedLanguage: string;
  setSelectedLanguage: (lang: string) => void;
  selectedCategory: string;
  setSelectedCategory: (cat: string) => void;
  activeSection: string;
  setActiveSection: (sec: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  searchQuery,
  setSearchQuery,
  selectedLanguage,
  setSelectedLanguage,
  selectedCategory,
  setSelectedCategory,
  activeSection,
  setActiveSection,
}) => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-gradient-to-b from-black/95 via-black/80 to-transparent px-6 md:px-12 flex items-center justify-between z-50 backdrop-blur-md border-b border-neutral-900/60">
      {/* Logo & Navigation */}
      <div className="flex items-center gap-8">
        <div 
          onClick={() => {
            setActiveSection('all');
            setSearchQuery('');
            setSelectedCategory('');
          }}
          className="flex items-center gap-1.5 cursor-pointer group"
        >
          <span className="text-red-600 font-extrabold text-2xl tracking-tighter uppercase font-mono group-hover:scale-105 transition-transform">
            PEBLO
          </span>
          <span className="text-white font-light text-xl tracking-wider">TV</span>
        </div>

        <nav className="hidden md:flex items-center gap-6 text-sm">
          {['all', 'featured', 'series', 'minisodes', 'songs'].map((sec) => (
            <button
              key={sec}
              onClick={() => {
                setActiveSection(sec);
                setSearchQuery('');
              }}
              className={`transition capitalize font-medium ${
                activeSection === sec && !searchQuery
                  ? 'text-white font-bold border-b-2 border-red-600 pb-0.5'
                  : 'text-neutral-400 hover:text-neutral-200'
              }`}
            >
              {sec === 'all' ? 'Home' : sec}
            </button>
          ))}
        </nav>
      </div>

      {/* Search & Language Filters */}
      <div className="flex items-center gap-3">
        {/* Search Bar */}
        <div className="relative">
          <Search className="w-4 h-4 text-neutral-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search shows, songs, categories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-neutral-900/90 border border-neutral-800 rounded-full pl-9 pr-8 py-1.5 text-xs text-white placeholder-neutral-500 focus:outline-none focus:border-red-500 w-44 sm:w-64 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-2.5 text-neutral-400 hover:text-white"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Audio Language Filter */}
        <div className="flex items-center gap-1 bg-neutral-900/90 border border-neutral-800 rounded-full px-3 py-1 text-xs">
          <Globe className="w-3.5 h-3.5 text-red-500" />
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="bg-transparent text-xs text-neutral-300 focus:outline-none cursor-pointer pr-1"
          >
            <option value="" className="bg-neutral-900 text-white">All Audio</option>
            <option value="en" className="bg-neutral-900 text-white">English (EN)</option>
            <option value="hi" className="bg-neutral-900 text-white">Hindi (HI)</option>
          </select>
        </div>
      </div>
    </header>
  );
};
