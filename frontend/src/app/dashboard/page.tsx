'use client';
import { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Users, Clock, UserCheck, AlertTriangle, TrendingUp, Eye } from 'lucide-react';
import api from '@/lib/api';
import Link from 'next/link';

interface Stats {
  total_teachers: number;
  heures_ce_mois: number;
  enseignants_actifs: number;
  en_attente: number;
  top_teachers: Array<{ id: number; prenom: string; nom: string; departement: string; grade: string; volume_total: number; nb_activites: number }>;
  dept_chart: Array<{ departement: string; volume: number }>;
  monthly_data: Array<{ mois: string; volume: number }>;
  recent_activities: Array<{ id: number; teacher_nom: string; course_intitule: string; type: string; volume_horaire: number; validation_status: string; created_at: string }>;
}

function BarChart({ data, color = '#2E75B6' }: { data: Array<{ label: string; value: number }>; color?: string }) {
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: '140px', paddingTop: '1rem' }}>
      {data.map(({ label, value }) => (
        <div key={label} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px', flex: 1 }}>
          <span style={{ fontSize: '0.65rem', color: '#64748B', fontWeight: 600 }}>{value > 0 ? value : ''}</span>
          <div style={{
            width: '100%', borderRadius: '4px 4px 0 0',
            background: color, height: `${Math.max((value / max) * 100, 4)}px`,
            transition: 'height 0.5s ease', minWidth: '20px'
          }} />
          <span style={{ fontSize: '0.65rem', color: '#94A3B8' }}>{label}</span>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/dashboard/stats').then(r => setStats(r.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <MainLayout>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '50vh' }}>
        <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: '3px solid #E2E8F0', borderTopColor: '#1F4E79', animation: 'spin 0.8s linear infinite' }} />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    </MainLayout>
  );

  const kpis = [
    { label: 'Total Enseignants', value: stats?.total_teachers ?? 0, icon: Users, color: '#1F4E79', bg: '#EBF2F7', desc: 'Enseignants enregistrés' },
    { label: 'Heures ce mois', value: `${stats?.heures_ce_mois ?? 0}h`, icon: Clock, color: '#0F766E', bg: '#CCFBF1', desc: 'Volume horaire mensuel' },
    { label: 'Enseignants actifs', value: stats?.enseignants_actifs ?? 0, icon: UserCheck, color: '#7C3AED', bg: '#F3E8FF', desc: 'Ont soumis des activités' },
    { label: 'En attente', value: stats?.en_attente ?? 0, icon: AlertTriangle, color: '#D97706', bg: '#FEF3C7', desc: 'Activités à valider' },
  ];

  const deptData = (stats?.dept_chart || []).map(d => ({ label: d.departement.slice(0, 6), value: d.volume }));
  const monthlyData = (stats?.monthly_data || []).map(d => ({ label: d.mois, value: d.volume }));

  return (
    <MainLayout>
      <div className="page-header">
        <h1 className="page-title">Tableau de bord</h1>
        <p className="page-subtitle">Vue d'ensemble de l'activité pédagogique — {new Date().toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</p>
      </div>

      {/* KPI Cards */}
      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        {kpis.map(({ label, value, icon: Icon, color, bg, desc }) => (
          <div key={label} className="card">
            <div className="stat-card">
              <div className="stat-icon" style={{ background: bg }}>
                <Icon size={22} color={color} />
              </div>
              <div>
                <div className="stat-value">{value}</div>
                <div className="stat-label">{label}</div>
                <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>{desc}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Volume mensuel</h3>
              <p style={{ fontSize: '0.75rem', color: '#64748B' }}>6 derniers mois (heures)</p>
            </div>
            <TrendingUp size={18} color="#2E75B6" />
          </div>
          <BarChart data={monthlyData} color="#2E75B6" />
        </div>

        <div className="card">
          <div style={{ marginBottom: '0.5rem' }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Volume par département</h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Heures pédagogiques cumulées</p>
          </div>
          <BarChart data={deptData} color="#1F4E79" />
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid-2">
        {/* Top teachers */}
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Top enseignants</h3>
              <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Par volume horaire total</p>
            </div>
            <Link href="/teachers" className="btn btn-ghost btn-sm">Voir tous</Link>
          </div>
          <div className="table-container">
            <table>
              <thead><tr>
                <th>Enseignant</th>
                <th>Département</th>
                <th style={{ textAlign: 'right' }}>Volume</th>
              </tr></thead>
              <tbody>
                {(stats?.top_teachers || []).map((t, i) => (
                  <tr key={t.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div className="avatar">{t.prenom.charAt(0)}{t.nom.charAt(0)}</div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.8rem' }}>{t.prenom} {t.nom}</div>
                          <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{t.grade}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.departement}</td>
                    <td style={{ textAlign: 'right' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.875rem', color: '#1F4E79' }}>{t.volume_total}h</span>
                    </td>
                  </tr>
                ))}
                {(!stats?.top_teachers?.length) && (
                  <tr><td colSpan={3} style={{ textAlign: 'center', color: '#94A3B8', padding: '2rem' }}>Aucune donnée</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent activities */}
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700 }}>Activités récentes</h3>
              <p style={{ fontSize: '0.75rem', color: '#64748B' }}>Dernières soumissions</p>
            </div>
            <Link href="/activities" className="btn btn-ghost btn-sm">Voir toutes</Link>
          </div>
          <div className="table-container">
            <table>
              <thead><tr>
                <th>Enseignant</th>
                <th>Type</th>
                <th>Volume</th>
                <th>Statut</th>
              </tr></thead>
              <tbody>
                {(stats?.recent_activities || []).slice(0, 6).map(act => (
                  <tr key={act.id}>
                    <td style={{ fontSize: '0.8rem', fontWeight: 600 }}>{act.teacher_nom}</td>
                    <td>
                      <span className={`badge ${act.type === 'creation' ? 'badge-blue' : 'badge-purple'}`} style={{ fontSize: '0.65rem' }}>
                        {act.type === 'creation' ? 'Création' : 'Mise à jour'}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600, fontSize: '0.8rem', color: '#1F4E79' }}>{act.volume_horaire}h</td>
                    <td>
                      <span className={`badge ${act.validation_status === 'valide' ? 'badge-green' : 'badge-orange'}`} style={{ fontSize: '0.65rem' }}>
                        {act.validation_status === 'valide' ? 'Validé' : 'En attente'}
                      </span>
                    </td>
                  </tr>
                ))}
                {!stats?.recent_activities?.length && (
                  <tr><td colSpan={4} style={{ textAlign: 'center', color: '#94A3B8', padding: '2rem' }}>Aucune activité</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
