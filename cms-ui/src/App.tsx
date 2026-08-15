import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { ShowList } from './components/ShowList';
import { EpisodeList } from './components/EpisodeList';
import { PublishPipeline } from './components/PublishPipeline';
import { setApiRole } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState<'shows' | 'episodes' | 'publish'>('shows');
  const [role, setRole] = useState<'editor' | 'admin'>('admin');

  useEffect(() => {
    setApiRole(role);
  }, [role]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-600 selection:text-white">
      {/* Navbar with Role Switcher */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        role={role}
        setRole={setRole}
      />

      {/* Main Content Area */}
      <main className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
        {activeTab === 'shows' && <ShowList role={role} />}
        {activeTab === 'episodes' && <EpisodeList role={role} />}
        {activeTab === 'publish' && <PublishPipeline role={role} />}
      </main>
    </div>
  );
}
