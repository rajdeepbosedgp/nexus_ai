import React, { useState, useEffect } from 'react';
import { LayoutDashboard, AlertTriangle, CheckCircle2, Clock, Sparkles, Flame, Shield, ArrowUpRight } from 'lucide-react';
import { dashboardApi } from '../services/api';

export default function DashboardPage({ user, setActiveTab }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await dashboardApi.getMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center gap-3 text-indigo-400 font-medium">
          <Sparkles className="w-5 h-5 animate-spin" />
          Loading NEXUS Dashboard Metrics...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          Failed to load dashboard: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      
      
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/20 p-6 overflow-hidden shadow-xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-semibold mb-2">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
              {user?.role === 'admin' ? 'Admin Command Center' : 'Resident Portal'}
            </div>
            <h1 className="text-3xl font-extrabold text-white font-['Outfit']">
              Society Maintenance Command & Intelligence
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Real-time complaint lifecycle tracking, weighted overdue risk scoring, and unsupervised cross-category pattern discovery.
            </p>
          </div>

          <button
            onClick={() => setActiveTab('patterns')}
            className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold text-sm transition-all shadow-lg glow-indigo shrink-0"
          >
            <Sparkles className="w-4 h-4 text-amber-300" />
            Detect Emergent Patterns
          </button>
        </div>
      </div>

      
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Complaints</span>
            <LayoutDashboard className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white font-['Outfit']">{metrics?.total_complaints || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Logged across all units</div>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Open Pending</span>
            <Clock className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400 font-['Outfit']">{metrics?.open_count || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Awaiting technician dispatch</div>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">In Progress</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-['Outfit']">{metrics?.in_progress_count || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Active resolution phase</div>
        </div>

        <div className="glass-card p-4 rounded-xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-['Outfit']">{metrics?.resolved_count || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Completed lifecycle</div>
        </div>

        <div className="glass-card p-4 rounded-xl bg-violet-950/20 border-violet-500/30">
          <div className="flex items-center justify-between text-violet-300 mb-2">
            <span className="text-xs font-semibold">Emergent Patterns</span>
            <Sparkles className="w-4 h-4 text-amber-300" />
          </div>
          <div className="text-2xl font-bold text-violet-300 font-['Outfit']">{metrics?.detected_patterns_count || 0}</div>
          <div className="text-[10px] text-slate-400 mt-1">Vector clusters surfaced</div>
        </div>
      </div>

      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        
        <div className="lg:col-span-2 glass-card p-5 rounded-2xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5 text-rose-400 animate-pulse" />
              <h2 className="text-lg font-bold text-white font-['Outfit']">Overdue Risk Leaderboard</h2>
            </div>
            <div className="text-xs font-mono text-slate-400">
              Formula: risk_score = days_open / category_avg_resolution
            </div>
          </div>

          <div className="space-y-3">
            {metrics?.top_overdue && metrics.top_overdue.length > 0 ? (
              metrics.top_overdue.map((c) => (
                <div key={c.id} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-mono text-xs font-bold text-indigo-400">INC-{c.id.substring(0, 8).toUpperCase()}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {c.category}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        {c.priority} Priority
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 truncate">"{c.description}"</p>
                  </div>

                  <div className="text-right shrink-0">
                    <div className="text-sm font-extrabold text-rose-400 font-['Outfit']">
                      Risk Score: {c.overdue_risk_score}x
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Opened {new Date(c.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-xs text-slate-400">
                No overdue risk items currently pending. System operating within category SLA thresholds!
              </div>
            )}
          </div>
        </div>

        
        <div className="glass-card p-5 rounded-2xl">
          <h2 className="text-lg font-bold text-white font-['Outfit'] mb-4">Complaints by Category</h2>
          <div className="space-y-4">
            {metrics?.by_category && Object.keys(metrics.by_category).length > 0 ? (
              Object.entries(metrics.by_category).map(([cat, count]) => {
                const percentage = Math.round((count / (metrics.total_complaints || 1)) * 100);
                return (
                  <div key={cat}>
                    <div className="flex items-center justify-between text-xs font-medium text-slate-300 mb-1">
                      <span>{cat}</span>
                      <span className="font-mono text-slate-400">{count} ({percentage}%)</span>
                    </div>
                    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-8 text-xs text-slate-400">No complaint data recorded.</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
