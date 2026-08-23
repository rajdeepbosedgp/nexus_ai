import React, { useState, useEffect } from 'react';
import { Sparkles, Cpu, Layers, CheckCircle2, ArrowRight, Activity, Shield, AlertTriangle, Info } from 'lucide-react';
import { patternsApi } from '../services/api';
import EvidencePanelModal from '../components/EvidencePanelModal';

export default function PatternsPage({ user }) {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState(null);
  const [detectionMessage, setDetectionMessage] = useState(null);
  
  const [selectedPattern, setSelectedPattern] = useState(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);

  const fetchPatterns = async () => {
    try {
      setLoading(true);
      const data = await patternsApi.list();
      setPatterns(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatterns();
  }, []);

  const handleTriggerDetect = async () => {
    setDetecting(true);
    setDetectionMessage('Running Sentence Embeddings (all-MiniLM-L6-v2) & HDBSCAN clustering...');
    setError(null);

    try {
      const res = await patternsApi.detect();
      setDetectionMessage(res.message);
      setPatterns(res.patterns);
    } catch (err) {
      setError(`Pattern Discovery Error: ${err.message}`);
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="relative rounded-2xl bg-gradient-to-r from-violet-950/60 via-indigo-900/40 to-slate-900 border border-violet-500/30 p-6 overflow-hidden shadow-2xl">
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 border border-violet-500/40 text-violet-300 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5 text-amber-300 animate-pulse" />
              NEXUS Signature Intelligence Layer
            </div>
            <h1 className="text-3xl font-extrabold text-white font-['Outfit']">
              Emergent Pattern Discovery
            </h1>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
              Unsupervised vector clustering surfaces emergent operational issues that span across predefined complaint taxonomies. Every pattern is mathematically scored and traceable to source data.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <button
              onClick={handleTriggerDetect}
              disabled={detecting}
              className="flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-bold text-sm transition-all shadow-lg glow-indigo disabled:opacity-50"
            >
              <Cpu className={`w-5 h-5 ${detecting ? 'animate-spin' : ''}`} />
              {detecting ? 'Analyzing Embeddings...' : 'Detect Patterns Now'}
            </button>
          </div>
        </div>
      </div>

      {detectionMessage && (
        <div className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/30 text-violet-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          {detectionMessage}
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {/* DISCOVERED PATTERNS LIST */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-400" />
            Active Emergent Patterns ({patterns.length})
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Fetching active patterns...</div>
        ) : patterns.length === 0 ? (
          <div className="glass-card p-12 text-center rounded-2xl space-y-3">
            <div className="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center mx-auto text-slate-500">
              <Info className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-200 font-['Outfit']">No Emergent Patterns Detected</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              NEXUS does not manufacture false positives. Click <strong>"Detect Patterns Now"</strong> to scan open complaints across categories.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {patterns.map((pat) => (
              <div
                key={pat.id}
                className="glass-card p-6 rounded-2xl border-violet-500/20 hover:border-violet-500/50 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-3 mb-3">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                          pat.label_source === 'llm'
                            ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/40'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                        }`}>
                          {pat.label_source === 'llm' ? 'LLM Label' : 'Deterministic Fallback'}
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">
                          {pat.complaint_ids?.length || 0} Complaints
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-white font-['Outfit']">{pat.name}</h3>
                    </div>

                    {/* Score Badge */}
                    <div className="text-center px-3 py-1.5 rounded-xl bg-violet-950/60 border border-violet-500/40 shrink-0">
                      <div className="text-[9px] uppercase font-semibold text-violet-300">Pattern Strength</div>
                      <div className="text-xl font-extrabold text-white font-['Outfit']">{Math.round(pat.strength_score)}/100</div>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 mb-4 leading-relaxed line-clamp-2">
                    {pat.description}
                  </p>

                  {/* Micro Heuristics Bar */}
                  <div className="grid grid-cols-4 gap-2 p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 text-center mb-4">
                    <div>
                      <div className="text-[9px] text-slate-400">Cohesion</div>
                      <div className="text-xs font-bold text-indigo-300">{pat.cohesion}</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-slate-400">Size</div>
                      <div className="text-xs font-bold text-sky-300">{pat.size}</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-slate-400">Spread</div>
                      <div className="text-xs font-bold text-emerald-300">{pat.category_spread}</div>
                    </div>
                    <div>
                      <div className="text-[9px] text-slate-400">Temporal</div>
                      <div className="text-xs font-bold text-amber-300">{pat.temporal_concentration}</div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setSelectedPattern(pat);
                    setShowEvidenceModal(true);
                  }}
                  className="w-full py-2.5 rounded-xl bg-violet-600/20 hover:bg-violet-600/30 text-violet-300 border border-violet-500/40 text-xs font-bold transition-all flex items-center justify-center gap-2"
                >
                  <Activity className="w-4 h-4 text-violet-400" />
                  Why Was This Detected? (Inspect Evidence)
                </button>

              </div>
            ))}
          </div>
        )}
      </div>

      {/* PIPELINE ARCHITECTURE CARD */}
      <div className="glass-card p-6 rounded-2xl border-slate-800">
        <h3 className="text-base font-bold text-white font-['Outfit'] mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-indigo-400" />
          Technical Discovery Pipeline (No Black Boxes)
        </h3>
        <p className="text-xs text-slate-300 mb-4 leading-relaxed">
          NEXUS separates vector intelligence from natural language generation. The LLM is strictly downstream of the detection.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-center text-xs">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="font-bold text-indigo-300">1. Text Embeddings</div>
            <div className="text-[10px] text-slate-400 mt-1">all-MiniLM-L6-v2</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="font-bold text-sky-300">2. HDBSCAN Cluster</div>
            <div className="text-[10px] text-slate-400 mt-1">Density clustering</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="font-bold text-emerald-300">3. Cross-Cat Filter</div>
            <div className="text-[10px] text-slate-400 mt-1">Spans ≥ 2 categories</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="font-bold text-amber-300">4. Equal Scoring</div>
            <div className="text-[10px] text-slate-400 mt-1">Composite 0-100 formula</div>
          </div>
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800">
            <div className="font-bold text-violet-300">5. LLM Labeler</div>
            <div className="text-[10px] text-slate-400 mt-1">GPT/Claude or Fallback</div>
          </div>
        </div>
      </div>

      {/* EVIDENCE PANEL MODAL */}
      <EvidencePanelModal
        pattern={selectedPattern}
        isOpen={showEvidenceModal}
        onClose={() => {
          setShowEvidenceModal(false);
          setSelectedPattern(null);
        }}
      />

    </div>
  );
}
