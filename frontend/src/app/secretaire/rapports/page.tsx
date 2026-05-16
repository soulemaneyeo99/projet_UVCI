'use client';
import { useEffect, useState } from 'react';
import { Download, FileText, Table } from 'lucide-react';
import api from '@/lib/api';

interface Teacher {
  id: number; nom: string; prenom: string; grade: string;
  departement: string; statut: string; taux_horaire: number;
  volume_horaire_total: number;
}

const SEUIL = 192;

export default function SecretaryReportsPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    api.get('/teachers/').then(r => setTeachers(r.data)).finally(() => setLoading(false));
  }, []);

  const downloadExcel = async () => {
    setDownloading('excel');
    try {
      const res = await api.get('/exports/excel', { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a'); a.href = url; a.download = 'etat_heures_UVCI.xlsx'; a.click();
      URL.revokeObjectURL(url);
    } finally { setDownloading(null); }
  };

  const downloadPdf = async (id: number) => {
    setDownloading(`pdf-${id}`);
    try {
      const res = await api.get(`/exports/pdf/${id}`, { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a'); a.href = url; a.download = `fiche_${id}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } finally { setDownloading(null); }
  };

  const totalVol = teachers.reduce((s, t) => s + t.volume_horaire_total, 0);
  const withOvertime = teachers.filter(t => t.volume_horaire_total > SEUIL);

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Rapports</h1>
          <p className="page-subtitle">Export et consultation des états d'heures</p>
        </div>
        <button className="btn btn-primary" onClick={downloadExcel} disabled={downloading === 'excel'}>
          <Table size={16} />
          {downloading === 'excel' ? 'Génération…' : 'Exporter en Excel'}
        </button>
      </div>

      {/* Summary */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        {[
          { label: 'Volume total', value: `${totalVol.toFixed(1)}h`, color: '#1F4E79', bg: '#EBF2F7' },
          { label: 'Enseignants actifs', value: teachers.length, color: '#0F766E', bg: '#CCFBF1' },
          { label: 'Avec heures complémentaires', value: withOvertime.length, color: '#D97706', bg: '#FEF3C7' },
        ].map(({ label, value, color, bg }) => (
          <div key={label} className="card">
            <div style={{ fontSize: '0.75rem', color: '#64748B', marginBottom: '0.5rem' }}>{label}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 800, color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9' }}>
          <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>État des heures par enseignant</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Enseignant</th><th>Grade</th><th>Département</th>
                <th style={{ textAlign: 'right' }}>Volume total</th>
                <th style={{ textAlign: 'right' }}>Heures comp.</th>
                <th style={{ textAlign: 'center' }}>Fiche</th>
              </tr>
            </thead>
            <tbody>
              {loading && <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>}
              {!loading && teachers.map(t => {
                const comp = Math.max(0, t.volume_horaire_total - SEUIL);
                return (
                  <tr key={t.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div className="avatar">{t.prenom.charAt(0)}{t.nom.charAt(0)}</div>
                        <span style={{ fontWeight: 600 }}>{t.prenom} {t.nom}</span>
                      </div>
                    </td>
                    <td style={{ fontSize: '0.8rem' }}>{t.grade}</td>
                    <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.departement}</td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F4E79' }}>{t.volume_horaire_total}h</td>
                    <td style={{ textAlign: 'right', color: comp > 0 ? '#D97706' : '#94A3B8', fontWeight: comp > 0 ? 700 : 400 }}>
                      {comp > 0 ? `+${comp.toFixed(1)}h` : '—'}
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        onClick={() => downloadPdf(t.id)}
                        disabled={downloading === `pdf-${t.id}`}
                        style={{ background: '#FEF2F2', color: '#DC2626', border: 'none', cursor: 'pointer', borderRadius: '6px', padding: '0.35rem 0.625rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}
                      >
                        <FileText size={13} />
                        {downloading === `pdf-${t.id}` ? '…' : 'PDF'}
                      </button>
                    </td>
                  </tr>
                );
              })}
              {!loading && !teachers.length && <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucun enseignant</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
