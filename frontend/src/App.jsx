import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AuthModal from './components/AuthModal';
import DashboardPage from './pages/DashboardPage';
import ComplaintsPage from './pages/ComplaintsPage';
import NoticesPage from './pages/NoticesPage';
import PatternsPage from './pages/PatternsPage';
import { authApi } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('nexus_token');
    if (token) {
      authApi.getMe()
        .then((userData) => setUser(userData))
        .catch(() => {
          localStorage.removeItem('nexus_token');
          setUser(null);
        })
        .finally(() => setInitializing(false));
    } else {
      setInitializing(false);
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('nexus_token');
    setUser(null);
  };

  if (initializing) {
    return (
      <div className="min-h-screen bg-[#080c14] flex items-center justify-center text-slate-400 font-medium text-sm">
        Initializing NEXUS Platform...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 font-sans flex flex-col">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onLogout={handleLogout}
        onOpenAuth={() => setShowAuthModal(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!user ? (
          <div className="text-center py-20 max-w-xl mx-auto space-y-6">
            <div className="inline-block p-4 rounded-3xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
              <span className="text-4xl">🏢</span>
            </div>
            <h1 className="text-4xl font-extrabold text-white font-['Outfit']">
              NEXUS Society Intelligence
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed">
              Log in with an Admin or Resident demo account to explore real-time complaint tracking, weighted overdue risk scoring, and Emergent Pattern Discovery.
            </p>
            <div className="flex justify-center gap-4">
              <button
                onClick={() => setShowAuthModal(true)}
                className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-lg glow-indigo transition-all"
              >
                Log In / Choose Persona
              </button>
            </div>
          </div>
        ) : (
          <>
            {activeTab === 'dashboard' && <DashboardPage user={user} setActiveTab={setActiveTab} />}
            {activeTab === 'complaints' && <ComplaintsPage user={user} />}
            {activeTab === 'notices' && <NoticesPage user={user} />}
            {activeTab === 'patterns' && <PatternsPage user={user} />}
          </>
        )}
      </main>

      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-400">
        NEXUS Society Maintenance Tracker & Emergent Intelligence &copy; 2026
      </footer>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLoginSuccess={(loggedUser) => setUser(loggedUser)}
      />
    </div>
  );
}
