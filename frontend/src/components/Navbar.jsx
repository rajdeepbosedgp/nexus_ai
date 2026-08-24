import React from 'react';
import { Shield, Sparkles, AlertCircle, Bell, LayoutDashboard, User, LogOut } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, user, onLogout, onOpenAuth }) {
  return (
    <header className="sticky top-0 z-40 bg-[#080c14]/80 backdrop-blur-md border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center glow-indigo">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-indigo-300 font-['Outfit']">
              NEXUS
            </div>
            <div className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
              Society Intelligence Tracker
            </div>
          </div>
        </div>

        
        {user && (
          <nav className="hidden md:flex items-center gap-1 bg-slate-900/60 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>

            <button
              onClick={() => setActiveTab('complaints')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'complaints'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <AlertCircle className="w-4 h-4" />
              Complaints
            </button>

            <button
              onClick={() => setActiveTab('notices')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'notices'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Bell className="w-4 h-4" />
              Notice Board
            </button>

            <button
              onClick={() => setActiveTab('patterns')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'patterns'
                  ? 'bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-md glow-indigo'
                  : 'text-violet-400 hover:text-violet-200 hover:bg-violet-950/30'
              }`}
            >
              <Sparkles className="w-4 h-4 text-amber-300 animate-pulse" />
              Emergent Patterns
            </button>
          </nav>
        )}

        
        <div className="flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                  user.role === 'admin' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                }`}>
                  {user.name.charAt(0)}
                </div>
                <div className="text-left hidden sm:block">
                  <div className="text-xs font-semibold text-slate-200">{user.name}</div>
                  <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1">
                    {user.role === 'admin' && <Shield className="w-3 h-3 text-amber-400 inline" />}
                    {user.role}
                  </div>
                </div>
              </div>

              <button
                onClick={onLogout}
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-950/20 border border-transparent hover:border-rose-900/40 transition-all"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg glow-indigo"
            >
              <User className="w-4 h-4" />
              Log In / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
