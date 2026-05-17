'use client';

import {
  BarChart3,
  Download,
  FileSpreadsheet,
  FileText,
  TrendingUp,
  Calendar,
  Filter,
  Users,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
} from 'lucide-react';
import api from '@/lib/api';
import { useState, useEffect, useCallback } from 'react';

interface AcademicYear {
  id: number;
  libelle: string;
  status: boolean;
}

interface TeacherRow {
  id: number;
  nom: string;
  prenom: string;
  grade: string;
  departement: string;
  statut: string;
  taux_horaire: number;
  volume_total: number;
  heures_complementaires: number;
  montant_estime: number;
}

interface DashboardStats {
  total_teachers: number;
  volume_total: number;
  dept_chart: { departement: string; volume: number }[];
}

const DEPTS = ['', 'Informatique', 'Mathématiques', 'Sciences Économiques', 'Droit', 'Langues'];

export default function ReportsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [academicYears, setAcademicYears] = useState<AcademicYear[]>([]);
  const [teachers, setTeachers] = useState<TeacherRow[]>([]);
  const [selectedDept, setSelectedDept] = useState('');
  const [downloading, setDownloading] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);

  const showToast = (msg: string, type: 'ok' | 'err' = 'ok') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 4000);
  };

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, ayRes, teachersRes] = await Promise.all([
        api.get('/dashboard/stats'),
        api.get('/academic-years/'),
        api.get('/teachers/'),
      ]);
      setStats(statsRes.data);
      setAcademicYears(ayRes.data);

      // Compute payment rows from teachers list + their activities
      const rows: TeacherRow[] = await Promise.all(
        teachersRes.data.map(async (t: any) => {
          let volume = 0;
          let seuil = 192;
          try {
            const res = await api.get(`/dashboard/teacher-stats/${t.id}`);
            volume = res.data.volume_total ?? 0;
            seuil = res.data.seuil_statutaire ?? 192;
          } catch (_) {}
          const heuresComp = Math.max(0, volume - seuil);
          return {
            id: t.id,
            nom: t.nom,
            prenom: t.prenom,
            grade: t.grade,
            departement: t.departement,
            statut: t.statut,
            taux_horaire: t.taux_horaire ?? 0,
            volume_total: volume,
            heures_complementaires: heuresComp,
            montant_estime: heuresComp * (t.taux_horaire ?? 0),
          };
        })
      );
      setTeachers(rows);
    } catch (e) {
      showToast('Erreur de chargement des données', 'err');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  const filtered = selectedDept
    ? teachers.filter(t => t.departement === selectedDept)
    : teachers;

  const totalVolume = filtered.reduce((s, t) => s + t.volume_total, 0);
  const totalComp = filtered.reduce((s, t) => s + t.heures_complementaires, 0);
  const totalMontant = filtered.reduce((s, t) => s + t.montant_estime, 0);
  const activeYear = academicYears.find(y => y.status);

  const handleExportExcel = async () => {
    setDownloading('excel');
    try {
      const params = selectedDept ? { departement: selectedDept } : {};
      const res = await api.get('/exports/excel', { responseType: 'blob', params });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `etat_paiement_${activeYear?.libelle ?? 'UVCI'}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Export Excel téléchargé avec succès !');
    } catch {
      showToast("Erreur lors de l'export Excel", 'err');
    } finally {
      setDownloading(null);
    }
  };

  const handleExportRapportAnnuel = async () => {
    setDownloading('rapport');
    try {
      const params: Record<string, any> = {};
      if (selectedDept) params.departement = selectedDept;
      const res = await api.get('/exports/rapport-annuel', { responseType: 'blob', params });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `rapport_annuel_${activeYear?.libelle ?? 'UVCI'}.xlsx`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Rapport annuel téléchargé avec succès !');
    } catch {
      showToast("Erreur lors de la génération du rapport annuel", 'err');
    } finally {
      setDownloading(null);
    }
  };

  const handleExportPdf = async (teacherId: number, nom: string) => {
    setDownloading(`pdf-${teacherId}`);
    try {
      const res = await api.get(`/exports/pdf/${teacherId}`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `recapitulatif_${nom}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(`Fiche PDF de ${nom} téléchargée !`);
    } catch {
      showToast('Erreur lors de la génération du PDF', 'err');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <>
      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', top: '1.5rem', right: '1.5rem', zIndex: 9999,
          display: 'flex', alignItems: 'center', gap: '0.75rem',
          padding: '0.875rem 1.25rem', borderRadius: '12px',
          background: toast.type === 'ok' ? '#DCFCE7' : '#FEE2E2',
          color: toast.type === 'ok' ? '#15803D' : '#DC2626',
          boxShadow: '0 4px 24px rgba(0,0,0,0.12)',
          fontWeight: 600, fontSize: '0.875rem',
          animation: 'slideIn 0.2s ease',
        }}>
          {toast.type === 'ok' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          {toast.msg}
        </div>
      )}
      <style>{`@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}`}</style>

      {/* Header */}
      <div className="page-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title">Rapports &amp; États de Paiement</h1>
          <p className="page-subtitle">
            Exportez les états de paiement annuels et les fiches individuelles des enseignants.
            {activeYear && (
              <span style={{ marginLeft: '0.5rem', background: '#DCFCE7', color: '#15803D', padding: '0.15rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                Année active : {activeYear.libelle}
              </span>
            )}
          </p>
        </div>
        <button onClick={loadData} disabled={loading} className="btn btn-ghost btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Actualiser
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#EBF2F7' }}><TrendingUp size={22} color="#1F4E79" /></div>
            <div>
              <div className="stat-value" style={{ color: '#1F4E79' }}>{totalVolume.toFixed(1)}h</div>
              <div className="stat-label">Volume total</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Toutes activités validées</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#FEF3C7' }}><BarChart3 size={22} color="#D97706" /></div>
            <div>
              <div className="stat-value" style={{ color: '#D97706' }}>{totalComp.toFixed(1)}h</div>
              <div className="stat-label">Heures complémentaires</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Au-delà du seuil statutaire</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: '#F0FDF4' }}><Users size={22} color="#16A34A" /></div>
            <div>
              <div className="stat-value" style={{ color: '#16A34A' }}>
                {totalMontant.toLocaleString('fr-FR')} F
              </div>
              <div className="stat-label">Montant total estimé</div>
              <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Sur heures complémentaires</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '1.5rem', alignItems: 'start' }}>

        {/* Table des états de paiement */}
        <div className="card" style={{ padding: 0 }}>
          {/* Toolbar */}
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>État de paiement des enseignants</h3>
              <p style={{ fontSize: '0.75rem', color: '#64748B' }}>
                {filtered.length} enseignant{filtered.length > 1 ? 's' : ''}
                {selectedDept ? ` — ${selectedDept}` : ' — tous départements'}
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <Filter size={14} color="#64748B" />
              <select
                className="form-select"
                style={{ width: 'auto', minWidth: '180px', padding: '0.375rem 0.75rem', fontSize: '0.8rem' }}
                value={selectedDept}
                onChange={e => setSelectedDept(e.target.value)}
              >
                <option value="">Tous les départements</option>
                {(stats?.dept_chart ?? []).map(d => (
                  <option key={d.departement} value={d.departement}>{d.departement}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Enseignant</th>
                  <th>Grade</th>
                  <th>Statut</th>
                  <th style={{ textAlign: 'right' }}>Heures totales</th>
                  <th style={{ textAlign: 'right' }}>H. complémentaires</th>
                  <th style={{ textAlign: 'right' }}>Taux/h</th>
                  <th style={{ textAlign: 'right' }}>Montant estimé</th>
                  <th style={{ textAlign: 'center' }}>Fiche PDF</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div style={{ width: '18px', height: '18px', borderRadius: '50%', border: '2px solid #E2E8F0', borderTopColor: '#1F4E79', animation: 'spin 0.8s linear infinite' }} />
                      Chargement des données…
                    </div>
                    <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
                  </td></tr>
                )}
                {!loading && filtered.map((t, i) => (
                  <tr key={t.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div className="avatar">{t.prenom.charAt(0)}{t.nom.charAt(0)}</div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.prenom} {t.nom}</div>
                          <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>{t.departement}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.grade}</td>
                    <td>
                      <span className={`badge ${t.statut === 'Permanent' ? 'badge-blue' : 'badge-orange'}`} style={{ fontSize: '0.7rem' }}>
                        {t.statut}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F4E79', fontSize: '0.875rem' }}>
                      {t.volume_total.toFixed(1)}h
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {t.heures_complementaires > 0 ? (
                        <span style={{ fontWeight: 700, color: '#D97706' }}>+{t.heures_complementaires.toFixed(1)}h</span>
                      ) : (
                        <span style={{ color: '#94A3B8', fontSize: '0.8rem' }}>—</span>
                      )}
                    </td>
                    <td style={{ textAlign: 'right', fontSize: '0.8rem', color: '#64748B' }}>
                      {t.taux_horaire.toLocaleString('fr-FR')} F
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: t.montant_estime > 0 ? '#15803D' : '#94A3B8', fontSize: '0.875rem' }}>
                      {t.montant_estime > 0 ? `${t.montant_estime.toLocaleString('fr-FR')} F` : '—'}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        onClick={() => handleExportPdf(t.id, `${t.nom}_${t.prenom}`)}
                        disabled={downloading === `pdf-${t.id}`}
                        style={{
                          background: 'none', border: '1px solid #E2E8F0', borderRadius: '6px',
                          padding: '0.3rem 0.6rem', cursor: 'pointer', display: 'inline-flex',
                          alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: '#DC2626',
                          fontWeight: 600, transition: 'all 0.15s'
                        }}
                        onMouseOver={e => (e.currentTarget.style.background = '#FEF2F2')}
                        onMouseOut={e => (e.currentTarget.style.background = 'none')}
                      >
                        <FileText size={13} />
                        {downloading === `pdf-${t.id}` ? '…' : 'PDF'}
                      </button>
                    </td>
                  </tr>
                ))}
                {!loading && !filtered.length && (
                  <tr><td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucun enseignant trouvé</td></tr>
                )}
                {/* Total row */}
                {!loading && filtered.length > 0 && (
                  <tr style={{ background: '#EBF2F7', fontWeight: 700 }}>
                    <td colSpan={3} style={{ padding: '0.75rem 1rem', fontSize: '0.875rem' }}>TOTAUX</td>
                    <td style={{ textAlign: 'right', color: '#1F4E79' }}>{totalVolume.toFixed(1)}h</td>
                    <td style={{ textAlign: 'right', color: '#D97706' }}>{totalComp.toFixed(1)}h</td>
                    <td />
                    <td style={{ textAlign: 'right', color: '#15803D' }}>{totalMontant.toLocaleString('fr-FR')} F</td>
                    <td />
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Panneau d'export */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

          {/* Centre d'exportation */}
          <div className="card" style={{ textAlign: 'center', padding: '1.5rem 1rem' }}>
            <div style={{ width: '3.5rem', height: '3.5rem', borderRadius: '50%', background: '#EBF2F7', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
              <Download size={22} color="#1F4E79" />
            </div>
            <h3 style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>Centre d'Exportation</h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '1.25rem' }}>
              Générez les documents officiels pour la comptabilité et l'administration.
            </p>

            {/* Export global Excel */}
            <button
              onClick={handleExportExcel}
              disabled={downloading === 'excel' || loading}
              style={{
                width: '100%', padding: '0.875rem', borderRadius: '10px',
                border: '2px solid #DCFCE7', background: 'white', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                marginBottom: '0.75rem', transition: 'all 0.15s',
                opacity: (downloading === 'excel' || loading) ? 0.6 : 1,
              }}
              onMouseOver={e => (e.currentTarget.style.background = '#F0FDF4')}
              onMouseOut={e => (e.currentTarget.style.background = 'white')}
            >
              <div style={{ width: '2.5rem', height: '2.5rem', borderRadius: '8px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <FileSpreadsheet size={18} color="#16A34A" />
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#15803D' }}>
                  {downloading === 'excel' ? 'Génération en cours…' : 'État Global (Excel)'}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#94A3B8' }}>
                  {selectedDept || 'Tous les départements'} • {activeYear?.libelle ?? 'Année courante'}
                </div>
              </div>
            </button>

            {/* Rapport annuel complet */}
            <button
              onClick={handleExportRapportAnnuel}
              disabled={downloading === 'rapport' || loading}
              style={{
                width: '100%', padding: '0.875rem', borderRadius: '10px',
                border: '2px solid #EDE9FE', background: 'white', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '0.75rem',
                marginBottom: '0.75rem', transition: 'all 0.15s',
                opacity: (downloading === 'rapport' || loading) ? 0.6 : 1,
              }}
              onMouseOver={e => (e.currentTarget.style.background = '#F5F3FF')}
              onMouseOut={e => (e.currentTarget.style.background = 'white')}
            >
              <div style={{ width: '2.5rem', height: '2.5rem', borderRadius: '8px', background: '#F5F3FF', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <FileSpreadsheet size={18} color="#7C3AED" />
              </div>
              <div style={{ textAlign: 'left' }}>
                <div style={{ fontWeight: 700, fontSize: '0.8rem', color: '#7C3AED' }}>
                  {downloading === 'rapport' ? 'Génération en cours…' : 'Rapport Annuel (par dept.)'}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#94A3B8' }}>
                  Onglet par département • {activeYear?.libelle ?? 'Année courante'}
                </div>
              </div>
            </button>

            <div style={{ fontSize: '0.7rem', color: '#94A3B8', padding: '0.5rem', background: '#F8FAFC', borderRadius: '6px', border: '1px solid #F1F5F9' }}>
              Les exports incluent uniquement les activités <strong>validées</strong> par le secrétariat.
            </div>
          </div>

          {/* Répartition par département */}
          <div className="card">
            <h3 style={{ fontWeight: 700, fontSize: '0.875rem', marginBottom: '1rem' }}>Répartition par département</h3>
            {loading ? (
              <div style={{ color: '#94A3B8', fontSize: '0.8rem' }}>Chargement…</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                {(stats?.dept_chart ?? []).map(d => {
                  const pct = totalVolume > 0 ? (d.volume / totalVolume) * 100 : 0;
                  return (
                    <div key={d.departement}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600, color: '#1E293B' }}>{d.departement}</span>
                        <span style={{ color: '#64748B', fontWeight: 700 }}>{d.volume.toFixed(1)}h</span>
                      </div>
                      <div style={{ height: '6px', background: '#F1F5F9', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${pct}%`, background: 'linear-gradient(90deg, #1F4E79, #2E75B6)', borderRadius: '4px', transition: 'width 0.6s ease' }} />
                      </div>
                      <div style={{ fontSize: '0.68rem', color: '#94A3B8', marginTop: '2px', textAlign: 'right' }}>{pct.toFixed(0)}%</div>
                    </div>
                  );
                })}
                {!stats?.dept_chart?.length && (
                  <div style={{ color: '#94A3B8', fontSize: '0.8rem', textAlign: 'center' }}>Aucune donnée disponible</div>
                )}
              </div>
            )}
          </div>

          {/* Années académiques */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.875rem' }}>
              <Calendar size={15} color="#64748B" />
              <h3 style={{ fontWeight: 700, fontSize: '0.875rem' }}>Années académiques</h3>
            </div>
            {academicYears.length === 0 && !loading && (
              <p style={{ fontSize: '0.78rem', color: '#94A3B8' }}>Aucune année configurée.</p>
            )}
            {academicYears.map(ay => (
              <div key={ay.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '0.5rem 0.75rem', borderRadius: '8px', marginBottom: '0.4rem',
                background: ay.status ? '#EBF2F7' : '#F8FAFC',
                border: `1px solid ${ay.status ? '#BFDBFE' : '#F1F5F9'}`,
              }}>
                <span style={{ fontSize: '0.82rem', fontWeight: ay.status ? 700 : 400, color: ay.status ? '#1F4E79' : '#64748B' }}>
                  {ay.libelle}
                </span>
                {ay.status && (
                  <span style={{ fontSize: '0.65rem', background: '#DCFCE7', color: '#15803D', padding: '0.15rem 0.4rem', borderRadius: '4px', fontWeight: 700 }}>
                    ACTIVE
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
