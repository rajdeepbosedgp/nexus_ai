import React, { useState, useEffect } from 'react';
import { Bell, Plus, Pin, Calendar, Shield, Send } from 'lucide-react';
import { noticesApi } from '../services/api';

export default function NoticesPage({ user }) {
  const [notices, setNotices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [isImportant, setIsImportant] = useState(false);

  const fetchNotices = async () => {
    try {
      setLoading(true);
      const data = await noticesApi.list();
      setNotices(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotices();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await noticesApi.create({ title, body, is_important: isImportant });
      setShowModal(false);
      setTitle('');
      setBody('');
      setIsImportant(false);
      fetchNotices();
    } catch (err) {
      alert(`Error posting notice: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      
      
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Society Notice Board</h1>
          <p className="text-xs text-slate-400">Official announcements and important resident broadcasts</p>
        </div>

        {user?.role === 'admin' && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg glow-indigo"
          >
            <Plus className="w-4 h-4" />
            Post New Notice
          </button>
        )}
      </div>

      
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Loading notice board...</div>
        ) : notices.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-400 text-sm rounded-2xl">
            No notices posted yet.
          </div>
        ) : (
          notices.map((n) => (
            <div
              key={n.id}
              className={`glass-card p-6 rounded-2xl transition-all ${
                n.is_important
                  ? 'border-amber-500/40 bg-amber-950/10 shadow-lg glow-amber'
                  : 'hover:border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex items-center gap-2 flex-wrap">
                  {n.is_important && (
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40 flex items-center gap-1">
                      <Pin className="w-3 h-3 text-amber-400" />
                      PINNED IMPORTANT
                    </span>
                  )}
                  <h2 className="text-lg font-bold text-white font-['Outfit']">{n.title}</h2>
                </div>

                <div className="text-[10px] text-slate-400 flex items-center gap-1 shrink-0">
                  <Calendar className="w-3 h-3" />
                  {new Date(n.created_at).toLocaleDateString()}
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed whitespace-pre-line">
                {n.body}
              </p>
            </div>
          ))
        )}
      </div>

      
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2 font-['Outfit']">Post Society Notice</h2>
            <p className="text-xs text-slate-400 mb-4">
              Notices marked as "Important" will trigger an immediate email notification broadcast to all residents.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Notice Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Water Tank Maintenance Schedule"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Announcement Content</label>
                <textarea
                  required
                  rows={4}
                  placeholder="Write the full notice body..."
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_important"
                  checked={isImportant}
                  onChange={(e) => setIsImportant(e.target.checked)}
                  className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="is_important" className="text-xs font-semibold text-amber-300 flex items-center gap-1 cursor-pointer">
                  <Pin className="w-3.5 h-3.5 text-amber-400" />
                  Mark as Important Announcement (Sends Email Broadcast)
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg glow-indigo flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  Broadcast Notice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
