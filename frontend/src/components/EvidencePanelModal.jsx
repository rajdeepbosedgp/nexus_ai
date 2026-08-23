import React from 'react';
import { X, Sparkles, Database, Tag, Calendar, CloudRain, CheckCircle, Cpu, AlertTriangle } from 'lucide-react';

export default function EvidencePanelModal({ pattern, isOpen, onClose }) {
  if (!isOpen || !pattern) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-[#0b0f19] border border-violet-500/30 rounded-2xl p-6 shadow-2xl overflow-y-auto">
        
        {/* Header */}
        <div className="flex items-start justify-between border-b border-slate-800 pb-4 mb-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center shrink-0 glow-indigo text-white font-extrabold text-lg">
              {Math.round(pattern.strength_score)}
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-2xl font-bold text-white font-['Outfit']">{pattern.name}</h2>
                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  pattern.label_source === 'llm' 
                    ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                }`}>
                  <Cpu className="w-3 h-3 inline mr-1" />
                  {pattern.label_source === 'llm' ? 'LLM Generated Label' : 'Deterministic Fallback Label'}
                </span>
              </div>
              <p className="text-sm text-slate-300 mt-1">{pattern.description}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/80 transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* WHY WAS THIS DETECTED? - Signal Breakdown Grid */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-3 text-xs font-bold uppercase tracking-wider text-violet-400">
            <Sparkles className="w-4 h-4 text-violet-400" />
            WHY WAS THIS DETECTED? (Mathematical Signal Heuristics)
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Cluster Cohesion (S_cohesion)</div>
              <div className="text-xl font-bold text-indigo-300 font-['Outfit']">{pattern.cohesion} / 100</div>
              <div className="text-[10px] text-slate-400 mt-1">Normalized cosine similarity</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Cluster Size (S_size)</div>
              <div className="text-xl font-bold text-sky-300 font-['Outfit']">{pattern.size} / 100</div>
              <div className="text-[10px] text-slate-400 mt-1">{pattern.complaint_ids?.length || 0} source complaints</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Category Spread (S_category)</div>
              <div className="text-xl font-bold text-emerald-300 font-['Outfit']">{pattern.category_spread} / 100</div>
              <div className="text-[10px] text-slate-400 mt-1">Cross-category signal</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-xl">
              <div className="text-[11px] text-slate-400 font-medium">Temporal Concentration</div>
              <div className="text-xl font-bold text-amber-300 font-['Outfit']">{pattern.temporal_concentration} / 100</div>
              <div className="text-[10px] text-slate-400 mt-1">Bounded linear time decay</div>
            </div>
          </div>
        </div>

        {/* SOURCE EVIDENCE COMPLAINTS GRID */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-300">
              <Database className="w-4 h-4 text-indigo-400" />
              Source Evidence ({pattern.complaints?.length || 0} Linked Complaints)
            </div>
            <span className="text-[11px] text-slate-400">
              Traceable to real complaint records
            </span>
          </div>

          <div className="space-y-2.5">
            {pattern.complaints && pattern.complaints.length > 0 ? (
              pattern.complaints.map((c) => (
                <div key={c.id} className="bg-slate-900/60 border border-slate-800/80 p-3.5 rounded-xl hover:border-slate-700 transition-all">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="font-mono text-xs font-bold text-indigo-400">
                          INC-{c.id.substring(0, 8).toUpperCase()}
                        </span>
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                          <Tag className="w-2.5 h-2.5 inline mr-1" />
                          {c.category}
                        </span>
                        {c.weather_event && (
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-950/60 text-sky-300 border border-sky-800/60">
                            <CloudRain className="w-2.5 h-2.5 inline mr-1" />
                            {c.weather_event}
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.status === 'Open' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                          c.status === 'In Progress' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                          'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        }`}>
                          {c.status}
                        </span>
                      </div>
                      <p className="text-xs text-slate-200 mt-1 leading-relaxed">
                        "{c.description}"
                      </p>
                    </div>

                    <div className="text-right shrink-0">
                      <div className="text-[10px] text-slate-400 flex items-center gap-1 justify-end">
                        <Calendar className="w-3 h-3" />
                        {new Date(c.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-6 text-xs text-slate-400">
                Linked complaints metadata loading...
              </div>
            )}
          </div>
        </div>

        {/* Footer Note */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
          <div>Detected at: {new Date(pattern.detected_at).toLocaleString()}</div>
          <div className="text-violet-400 font-medium">NEXUS Emergent Discovery Engine v1.0</div>
        </div>

      </div>
    </div>
  );
}
