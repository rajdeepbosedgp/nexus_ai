import React, { useState, useEffect } from 'react';
import { AlertCircle, Plus, Search, Filter, History, Camera, CloudRain, CheckCircle, Clock, Shield, Tag } from 'lucide-react';
import { complaintsApi } from '../services/api';

export default function ComplaintsPage({ user }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);

  // Create form state
  const [category, setCategory] = useState('Plumbing');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [photoUrl, setPhotoUrl] = useState('');
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [weatherEvent, setWeatherEvent] = useState('');

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setUploadingPhoto(true);
      const res = await complaintsApi.uploadPhoto(file);
      setPhotoUrl(res.photo_url);
    } catch (err) {
      alert(`Photo upload failed: ${err.message}`);
    } finally {
      setUploadingPhoto(false);
    }
  };

  // Status transition state
  const [newStatus, setNewStatus] = useState('In Progress');
  const [statusNote, setStatusNote] = useState('');

  const fetchComplaints = async () => {
    try {
      setLoading(true);
      const params = {};
      if (categoryFilter) params.category = categoryFilter;
      if (statusFilter) params.status_filter = statusFilter;
      const data = await complaintsApi.list(params);
      setComplaints(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [categoryFilter, statusFilter]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      await complaintsApi.create({
        category,
        description,
        priority,
        photo_url: photoUrl || null,
        weather_event: weatherEvent || null
      });
      setShowCreateModal(false);
      setDescription('');
      setPhotoUrl('');
      setWeatherEvent('');
      fetchComplaints();
    } catch (err) {
      alert(`Error creating complaint: ${err.message}`);
    }
  };

  const handleStatusSubmit = async (e) => {
    e.preventDefault();
    if (!selectedComplaint) return;
    try {
      await complaintsApi.updateStatus(selectedComplaint.id, newStatus, statusNote);
      setShowStatusModal(false);
      setSelectedComplaint(null);
      setStatusNote('');
      fetchComplaints();
    } catch (err) {
      alert(`Error updating status: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']">Complaints Management</h1>
          <p className="text-xs text-slate-400">
            Immutable status lifecycle history logs and automated resident email dispatch
          </p>
        </div>

        {user?.role === 'resident' && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg glow-indigo"
          >
            <Plus className="w-4 h-4" />
            Raise New Complaint
          </button>
        )}
      </div>

      {/* Filter Toolbar */}
      <div className="glass-card p-4 rounded-xl flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
          <Filter className="w-4 h-4 text-indigo-400" />
          Filter By:
        </div>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-3 py-1.5 rounded-lg glass-input text-xs"
        >
          <option value="" className="bg-slate-900">All Categories</option>
          <option value="Plumbing" className="bg-slate-900">Plumbing</option>
          <option value="Electrical" className="bg-slate-900">Electrical</option>
          <option value="Cosmetic" className="bg-slate-900">Cosmetic</option>
          <option value="Cleaning" className="bg-slate-900">Cleaning</option>
          <option value="General" className="bg-slate-900">General</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-3 py-1.5 rounded-lg glass-input text-xs"
        >
          <option value="" className="bg-slate-900">All Lifecycle States</option>
          <option value="Open" className="bg-slate-900">Open</option>
          <option value="In Progress" className="bg-slate-900">In Progress</option>
          <option value="Resolved" className="bg-slate-900">Resolved</option>
        </select>
      </div>

      {/* Complaints List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12 text-slate-400 text-xs">Loading complaints...</div>
        ) : complaints.length === 0 ? (
          <div className="glass-card p-12 text-center text-slate-400 text-sm rounded-2xl">
            No complaints found matching current filter criteria.
          </div>
        ) : (
          complaints.map((c) => (
            <div key={c.id} className="glass-card p-5 rounded-2xl glass-card-hover space-y-3">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <span className="font-mono text-sm font-bold text-indigo-400">
                      INC-{c.id.substring(0, 8).toUpperCase()}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">
                      {c.category}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-md text-xs font-bold ${
                      c.priority === 'High' ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40' :
                      c.priority === 'Medium' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' :
                      'bg-slate-700 text-slate-300'
                    }`}>
                      {c.priority} Priority
                    </span>
                    {c.weather_event && (
                      <span className="px-2.5 py-0.5 rounded-md text-xs font-semibold bg-sky-950/60 text-sky-300 border border-sky-800/60">
                        <CloudRain className="w-3 h-3 inline mr-1" />
                        {c.weather_event}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-200 mt-2 leading-relaxed font-normal">
                    "{c.description}"
                  </p>

                  {c.photo_url && (
                    <div className="mt-2.5 flex items-center gap-2">
                      <a
                        href={c.photo_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-indigo-300 border border-slate-700/80 text-xs transition-all"
                      >
                        <Camera className="w-3.5 h-3.5 text-indigo-400" />
                        <span>View Attached Photo</span>
                      </a>
                      <img
                        src={c.photo_url}
                        alt="Complaint Attachment"
                        className="w-10 h-10 rounded-lg object-cover border border-slate-700 shadow-md cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={() => window.open(c.photo_url, '_blank')}
                      />
                    </div>
                  )}
                </div>

                <div className="text-right shrink-0">
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                    c.status === 'Open' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/30' :
                    c.status === 'In Progress' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30' :
                    'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  }`}>
                    {c.status}
                  </span>
                  <div className="text-[10px] text-slate-400 mt-1.5">
                    Risk Score: <span className="font-bold text-slate-300">{c.overdue_risk_score}x</span>
                  </div>
                </div>
              </div>

              {/* Admin Actions */}
              {user?.role === 'admin' && c.status !== 'Resolved' && (
                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-end gap-2">
                  <button
                    onClick={() => {
                      setSelectedComplaint(c);
                      setNewStatus(c.status === 'Open' ? 'In Progress' : 'Resolved');
                      setShowStatusModal(true);
                    }}
                    className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/30 text-xs font-semibold transition-all"
                  >
                    Update Lifecycle Status
                  </button>
                </div>
              )}

              {/* Immutable History Log Preview */}
              {c.history && c.history.length > 0 && (
                <div className="pt-3 border-t border-slate-800/60 text-[11px] text-slate-400 space-y-1">
                  <div className="font-semibold text-slate-300 flex items-center gap-1">
                    <History className="w-3 h-3 text-indigo-400" />
                    Immutable History Timeline ({c.history.length} events)
                  </div>
                  {c.history.map((h) => (
                    <div key={h.id} className="pl-4 border-l border-slate-800 flex items-center justify-between text-[10px]">
                      <span>
                        <strong className="text-slate-300">{h.from_status} → {h.to_status}</strong> {h.note ? `("${h.note}")` : ''}
                      </span>
                      <span>{new Date(h.timestamp).toLocaleString()}</span>
                    </div>
                  ))}
                </div>
              )}

            </div>
          ))
        )}
      </div>

      {/* CREATE COMPLAINT MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 w-full max-w-lg shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-4 font-['Outfit']">Raise New Society Complaint</h2>
            <form onSubmit={handleCreateSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Predefined Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                >
                  <option value="Plumbing" className="bg-slate-900">Plumbing</option>
                  <option value="Electrical" className="bg-slate-900">Electrical</option>
                  <option value="Cosmetic" className="bg-slate-900">Cosmetic</option>
                  <option value="Cleaning" className="bg-slate-900">Cleaning</option>
                  <option value="General" className="bg-slate-900">General</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Description</label>
                <textarea
                  required
                  rows={3}
                  placeholder="Describe the complaint in detail..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                  >
                    <option value="Low" className="bg-slate-900">Low</option>
                    <option value="Medium" className="bg-slate-900">Medium</option>
                    <option value="High" className="bg-slate-900">High</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Weather Context Tag</label>
                  <input
                    type="text"
                    placeholder="e.g. Heavy Rain"
                    value={weatherEvent}
                    onChange={(e) => setWeatherEvent(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Attach Photo (File Upload)</label>
                <div className="flex items-center gap-3">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="complaint-photo-file-input"
                  />
                  <label
                    htmlFor="complaint-photo-file-input"
                    className="cursor-pointer flex items-center gap-2 px-3 py-2 rounded-xl glass-input text-xs font-medium text-slate-300 hover:text-white hover:border-indigo-500/50 transition-all"
                  >
                    <Camera className="w-4 h-4 text-indigo-400" />
                    {uploadingPhoto ? 'Uploading File...' : photoUrl ? 'Change Uploaded Photo' : 'Choose Image File'}
                  </label>
                  {photoUrl && (
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5" /> File Uploaded
                      </span>
                      <img src={photoUrl} alt="Preview" className="w-8 h-8 rounded-lg object-cover border border-slate-700 shadow-md" />
                    </div>
                  )}
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg glow-indigo"
                >
                  Submit Complaint
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* UPDATE STATUS MODAL (ADMIN) */}
      {showStatusModal && selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="bg-[#0f172a] border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2 font-['Outfit']">Update Lifecycle Status</h2>
            <p className="text-xs text-slate-400 mb-4">
              Updating INC-{selectedComplaint.id.substring(0, 8).toUpperCase()} will log an immutable history record and send an email notification.
            </p>

            <form onSubmit={handleStatusSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">New Lifecycle State</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                >
                  <option value="Open" className="bg-slate-900">Open</option>
                  <option value="In Progress" className="bg-slate-900">In Progress</option>
                  <option value="Resolved" className="bg-slate-900">Resolved</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Status Note (Required for Immutable Log)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Technician dispatched to Block C."
                  value={statusNote}
                  onChange={(e) => setStatusNote(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl glass-input text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setShowStatusModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg glow-indigo"
                >
                  Confirm & Dispatch Email
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
