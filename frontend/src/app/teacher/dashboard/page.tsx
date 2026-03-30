'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Clock, TrendingUp, BookOpen } from 'lucide-react';
import api from '@/lib/api';
import Link from 'next/link';

interface TeacherStats {
  teacher: { id: number; nom: string; prenom: string; grade: string; departement: string; email: string; statut: string; };
  volume_total: number;
  heures_complementaires: number;
  activites_semestre: number;
  charge_pct: number;
  seuil_statutaire: number;
  monthly_data: Array<{ mois: string; volume: number }>;
}

interface Activity {
  id: number; course_intitule?: string; type_activite: string;
  niveau_complexite: number; nb_sequences: number;
  volume_horaire_calcule: number; validation_status: string; created_at?: string;
}

function MiniBar({ data }: { data: Array<{ mois: string; volume: number }> }) {
  const max = Math.max(...data.map(d => d.volume), 1);
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '6px', height: '80px' }}>
      {data.map(({ mois, volume }) => (
        <div key={mois} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '3px', flex: 1 }}>
          <div style={{
            width: '100%', borderRadius: '3px 3px 0 0',
            background: '#2E75B6', height: `${Math.max((volume / max) * 64, 3)}px`,
          }} />
          <span style={{ fontSize: '0.6rem', color: '#94A3B8' }}>{mois}</span>
        </div>
      ))}
    </div>
  );
}

export default function TeacherDashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.teacher_id) return;
    Promise.all([
      api.get(`/dashboard/teacher-stats/${user.teacher_id}`),
      api.get(`/activities/teacher/${user.teacher_id}`),
    ]).then(([sRes, aRes]) => {
      setStats(sRes.data);
      setActivities(aRes.data);
    }).finally(() => setLoading(false));
  }, [user]);

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
      <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: '3px solid #E2E8F0', borderTopColor: '#1F4E79', animation: 'spin 0.8s linear infinite' }} />
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );

  const t = stats?.teacher;
  const now = new Date();
  const yearLabel = `${now.getFullYear() - (now.getMonth() < 8 ? 1 : 0)}-${now.getFullYear() + (now.getMonth() >= 8 ? 1 : 0)}`;

  return (
    <>
      {/* Welcome banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1F4E79, #2E75B6)',
        borderRadius: '12px', padding: '1.5rem 2rem', marginBottom: '1.5rem',
        color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center'
      }}>
        <div>
          <h1 style={{ fontSize: '1.375rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            Bonjour, {t?.prenom || 'Enseignant'} 👋
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
            Année académique {yearLabel} — {t?.departement}
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.6)', marginBottom: '4px' }}>{t?.grade}</div>
          <div style={{
            background: 'rgba(255,255,255,0.15)', borderRadius: '8px',
            padding: '0.25rem 0.75rem', fontSize: '0.8rem', fontWeight: 600
          }}>
            {t?.statut}
          </div>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#EBF2F7' }}>
              <Clock size={22} color="#1F4E79" />
            </div>
            <div>
              <div className="stat-value" style={{ color: '#1F4E79' }}>{stats?.volume_total ?? 0}h</div>
              <div className="stat-label">Heures totales</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginTop: '2px' }}>Cumulé toutes années</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: stats?.heures_complementaires ? '#FEF3C7' : '#F1F5F9' }}>
              <TrendingUp size={22} color={stats?.heures_complementaires ? '#D97706' : '#94A3B8'} />
            </div>
            <div>
              <div className="stat-value" style={{ color: stats?.heures_complementaires ? '#D97706' : '#94A3B8' }}>
                +{stats?.heures_complementaires ?? 0}h
              </div>
              <div className="stat-label">Heures complémentaires</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginTop: '2px' }}>
                Seuil : {stats?.seuil_statutaire}h/an
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#F0FDF4' }}>
              <BookOpen size={22} color="#16A34A" />
            </div>
            <div>
              <div className="stat-value" style={{ color: '#16A34A' }}>{stats?.activites_semestre ?? 0}</div>
              <div className="stat-label">Activités ce semestre</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8', marginTop: '2px' }}>Soumises et en cours</div>
            </div>
          </div>
        </div>
      </div>

      {/* Charge bar + chart */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <h3 style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '1rem' }}>Charge statutaire</h3>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
              {stats?.volume_total}h / {stats?.seuil_statutaire}h
            </span>
            <span style={{ fontSize: '0.875rem', fontWeight: 700, color: (stats?.charge_pct || 0) >= 100 ? '#D97706' : '#1F4E79' }}>
              {stats?.charge_pct ?? 0}% atteinte
            </span>
          </div>
          <div className="progress-bar" style={{ height: '12px' }}>
            <div className="progress-fill" style={{
              width: `${stats?.charge_pct ?? 0}%`,
              background: (stats?.charge_pct || 0) >= 100
                ? 'linear-gradient(90deg, #D97706, #F59E0B)'
                : 'linear-gradient(90deg, #1F4E79, #2E75B6)'
            }} />
          </div>
          {(stats?.charge_pct || 0) >= 100 && (
            <p style={{ fontSize: '0.75rem', color: '#D97706', marginTop: '0.5rem' }}>
              ⚠ Vous avez dépassé votre charge réglementaire. Les heures en surplus sont complémentaires.
            </p>
          )}
        </div>

        <div className="card">
          <h3 style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.5rem' }}>Volume mensuel</h3>
          <p style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem' }}>6 derniers mois</p>
          <MiniBar data={stats?.monthly_data || []} />
        </div>
      </div>

      {/* Recent activities */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>Mes activités récentes</h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>{activities.length} activité{activities.length > 1 ? 's' : ''} au total</p>
          </div>
          <Link href="/teacher/activities" className="btn btn-ghost btn-sm">Voir toutes</Link>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Cours</th><th>Type</th><th>Niveau</th>
                <th style={{ textAlign: 'right' }}>Séquences</th>
                <th style={{ textAlign: 'right' }}>Volume</th>
                <th>Statut</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {activities.slice(0, 8).map(act => (
                <tr key={act.id}>
                  <td style={{ fontWeight: 600, fontSize: '0.8rem', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {act.course_intitule || '—'}
                  </td>
                  <td>
                    <span className={`badge ${act.type_activite === 'creation' ? 'badge-blue' : 'badge-purple'}`} style={{ fontSize: '0.65rem' }}>
                      {act.type_activite === 'creation' ? 'Création' : 'MàJ'}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${act.niveau_complexite === 1 ? 'badge-blue' : act.niveau_complexite === 2 ? 'badge-purple' : 'badge-orange'}`} style={{ fontSize: '0.65rem' }}>
                      N{act.niveau_complexite}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', fontSize: '0.8rem' }}>{act.nb_sequences}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F4E79', fontSize: '0.8rem' }}>{act.volume_horaire_calcule}h</td>
                  <td>
                    <span className={`badge ${act.validation_status === 'valide' ? 'badge-green' : 'badge-orange'}`} style={{ fontSize: '0.65rem' }}>
                      {act.validation_status === 'valide' ? 'Validé' : 'En attente'}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.75rem', color: '#94A3B8' }}>
                    {act.created_at ? new Date(act.created_at).toLocaleDateString('fr-FR') : '—'}
                  </td>
                </tr>
              ))}
              {!activities.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#94A3B8' }}>Aucune activité enregistrée</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
