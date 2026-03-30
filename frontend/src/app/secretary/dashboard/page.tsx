'use client';
import { useEffect, useState } from 'react';
import { CheckCircle, Clock, Check } from 'lucide-react';
import api from '@/lib/api';
import Link from 'next/link';

interface Activity {
  id: number; teacher_nom?: string; teacher_prenom?: string;
  course_intitule?: string; type_activite: string;
  volume_horaire_calcule: number; validation_status: string;
  created_at?: string; niveau_complexite: number; nb_sequences: number;
}

export default function SecretaryDashboardPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState<number | null>(null);

  const load = () => {
    setLoading(true);
    api.get('/activities/').then(r => setActivities(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  const validate = async (id: number) => {
    setValidating(id);
    try {
      await api.put(`/activities/${id}/validate`, { validation_status: 'valide' });
      setActivities(prev => prev.map(a => a.id === id ? { ...a, validation_status: 'valide' } : a));
    } finally { setValidating(null); }
  };

  const thisMonth = activities.filter(a => {
    if (!a.created_at) return false;
    const d = new Date(a.created_at);
    const now = new Date();
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  });

  const pending = activities.filter(a => a.validation_status === 'en_attente');

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Tableau de bord — Secrétariat</h1>
        <p className="page-subtitle">Gestion et validation des activités pédagogiques</p>
      </div>

      {/* KPI */}
      <div className="grid-2" style={{ marginBottom: '1.5rem', maxWidth: '640px' }}>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#EBF2F7' }}>
              <CheckCircle size={22} color="#1F4E79" />
            </div>
            <div>
              <div className="stat-value">{thisMonth.length}</div>
              <div className="stat-label">Activités ce mois</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#FEF3C7' }}>
              <Clock size={22} color="#D97706" />
            </div>
            <div>
              <div className="stat-value">{pending.length}</div>
              <div className="stat-label">En attente de validation</div>
            </div>
          </div>
        </div>
      </div>

      {/* Activities table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>Activités récentes</h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Toutes les activités soumises</p>
          </div>
          <Link href="/secretary/activities" className="btn btn-primary btn-sm">
            + Nouvelle activité
          </Link>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Enseignant</th>
                <th>Cours</th>
                <th>Type</th>
                <th>Volume</th>
                <th>Statut</th>
                <th style={{ textAlign: 'center' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>
              )}
              {!loading && activities.slice(0, 20).map(act => (
                <tr key={act.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="avatar">
                        {(act.teacher_prenom || '?').charAt(0)}{(act.teacher_nom || '?').charAt(0)}
                      </div>
                      <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>
                        {act.teacher_prenom} {act.teacher_nom}
                      </span>
                    </div>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748B', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {act.course_intitule || '—'}
                  </td>
                  <td>
                    <span className={`badge ${act.type_activite === 'creation' ? 'badge-blue' : 'badge-purple'}`} style={{ fontSize: '0.7rem' }}>
                      {act.type_activite === 'creation' ? 'Création' : 'Mise à jour'}
                    </span>
                  </td>
                  <td style={{ fontWeight: 700, color: '#1F4E79' }}>{act.volume_horaire_calcule}h</td>
                  <td>
                    <span className={`badge ${act.validation_status === 'valide' ? 'badge-green' : 'badge-orange'}`} style={{ fontSize: '0.7rem' }}>
                      {act.validation_status === 'valide' ? 'Validé' : 'En attente'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {act.validation_status === 'en_attente' ? (
                      <button
                        onClick={() => validate(act.id)}
                        disabled={validating === act.id}
                        className="btn btn-sm"
                        style={{ background: '#DCFCE7', color: '#16A34A', border: 'none', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}
                      >
                        <Check size={13} />
                        {validating === act.id ? '…' : 'Valider'}
                      </button>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>—</span>
                    )}
                  </td>
                </tr>
              ))}
              {!loading && !activities.length && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucune activité</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
