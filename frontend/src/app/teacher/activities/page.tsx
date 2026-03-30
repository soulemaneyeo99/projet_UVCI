'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';

interface Activity {
  id: number; course_intitule?: string; type_activite: string;
  niveau_complexite: number; nb_sequences: number;
  volume_horaire_calcule: number; validation_status: string;
  created_at?: string; annee_academique?: string;
}

type Semestre = 'S1' | 'S2' | 'all';

export default function TeacherActivitiesPage() {
  const { user } = useAuth();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [semestre, setSemestre] = useState<Semestre>('all');

  useEffect(() => {
    if (!user?.teacher_id) return;
    api.get(`/activities/teacher/${user.teacher_id}`)
      .then(r => setActivities(r.data))
      .finally(() => setLoading(false));
  }, [user]);

  const filtered = activities.filter(act => {
    if (semestre === 'all') return true;
    if (!act.created_at) return false;
    const month = new Date(act.created_at).getMonth() + 1;
    if (semestre === 'S1') return month >= 9 || month === 1;
    if (semestre === 'S2') return month >= 2 && month <= 7;
    return true;
  });

  const totalVol = filtered.reduce((s, a) => s + a.volume_horaire_calcule, 0);
  const validatedVol = filtered.filter(a => a.validation_status === 'valide').reduce((s, a) => s + a.volume_horaire_calcule, 0);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Mes activités</h1>
        <p className="page-subtitle">Historique complet de vos activités pédagogiques</p>
      </div>

      {/* Summary card */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem' }}>Volume total (filtre)</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1F4E79' }}>{totalVol.toFixed(1)}h</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem' }}>Heures validées</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#16A34A' }}>{validatedVol.toFixed(1)}h</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem' }}>Nombre d'activités</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#7C3AED' }}>{filtered.length}</div>
        </div>
      </div>

      {/* Semester tabs */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid #F1F5F9', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {(['all', 'S1', 'S2'] as Semestre[]).map(s => (
            <button
              key={s}
              onClick={() => setSemestre(s)}
              style={{
                padding: '0.4rem 1rem', borderRadius: '6px', border: 'none', cursor: 'pointer',
                background: semestre === s ? '#1F4E79' : '#F1F5F9',
                color: semestre === s ? 'white' : '#64748B',
                fontWeight: 600, fontSize: '0.8rem', transition: 'all 0.15s'
              }}
            >
              {s === 'all' ? 'Toute l\'année' : `Semestre ${s.slice(1)}`}
            </button>
          ))}
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Cours</th>
                <th>Type d'activité</th>
                <th>Niveau</th>
                <th style={{ textAlign: 'right' }}>Séquences</th>
                <th style={{ textAlign: 'right' }}>Volume horaire</th>
                <th>Statut</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>
              )}
              {!loading && filtered.map(act => (
                <tr key={act.id}>
                  <td style={{ fontWeight: 600, fontSize: '0.875rem', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {act.course_intitule || '—'}
                  </td>
                  <td>
                    <span className={`badge ${act.type_activite === 'creation' ? 'badge-blue' : 'badge-purple'}`}>
                      {act.type_activite === 'creation' ? 'Création' : 'Mise à jour'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${
                      act.niveau_complexite === 1 ? 'badge-blue' :
                      act.niveau_complexite === 2 ? 'badge-purple' : 'badge-orange'
                    }`}>
                      Niveau {act.niveau_complexite}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>{act.nb_sequences}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F4E79' }}>
                    {act.volume_horaire_calcule}h
                  </td>
                  <td>
                    <span className={`badge ${act.validation_status === 'valide' ? 'badge-green' : 'badge-orange'}`}>
                      {act.validation_status === 'valide' ? 'Validé' : 'En attente'}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748B' }}>
                    {act.created_at ? new Date(act.created_at).toLocaleDateString('fr-FR') : '—'}
                  </td>
                </tr>
              ))}
              {!loading && !filtered.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>
                  Aucune activité pour ce semestre
                </td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
