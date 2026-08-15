import React from 'react';
import { Tv, ShieldCheck, UserCheck, Sparkles } from 'lucide-react';

interface NavbarProps {
  activeTab: 'shows' | 'episodes' | 'publish';
  setActiveTab: (tab: 'shows' | 'episodes' | 'publish') => void;
  role: 'editor' | 'admin';
  setRole: (role: 'editor' | 'admin') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  role,
  setRole,
}) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/90 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
          <Tv className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight tracking-tight flex items-center gap-2">
            Peblo TV <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 font-mono font-medium">CMS</span>
          </h1>
          <p className="text-xs text-slate-400">Content Ingestion & Publishing Platform</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex items-center gap-1 bg-slate-950/70 p-1 rounded-xl border border-slate-800">
        <button
          onClick={() => setActiveTab('shows')}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'shows'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Shows & Seasons
        </button>
        <button
          onClick={() => setActiveTab('episodes')}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'episodes'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Episodes & Assets
        </button>
        <button
          onClick={() => setActiveTab('publish')}
          className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
            activeTab === 'publish'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          Publish Pipeline
        </button>
      </nav>

      {/* Role Switcher Toggle */}
      <div className="flex items-center gap-3 bg-slate-950/90 border border-slate-800 px-3.5 py-1.5 rounded-xl shadow-inner">
        {role === 'admin' ? (
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
        ) : (
          <UserCheck className="w-4 h-4 text-amber-400" />
        )}
        <div className="text-left">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block -mb-0.5">Role Mode</span>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as 'editor' | 'admin')}
            className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-1"
          >
            <option value="admin" className="bg-slate-900 text-white">Admin (CRUD + Publish)</option>
            <option value="editor" className="bg-slate-900 text-amber-200">Editor (CRUD Only)</option>
          </select>
        </div>
      </div>
    </header>
  );
};
