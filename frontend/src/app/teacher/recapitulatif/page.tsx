'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { FileText, Table, Download } from 'lucide-react';
import api from '@/lib/api';

interface TeacherStats {
  teacher: { id: number; nom: string; prenom: string; grade: string; departement: string; email: string; };
  volume_total: number;
  heures_complementaires: number;
  activites_semestre: number;
  charge_pct: number;
  seuil_statutaire: number;
}

interface Activity {
  id: number; course_intitule?: string; type_activite: string;
  niveau_complexite: number; nb_sequences: number; volume_horaire_calcule: number;
  validation_status: string;
}

export default function TeacherRecapPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

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

  const downloadPdf = async () => {
    if (!user?.teacher_id) return;
    setDownloading('pdf');
    try {
      const res = await api.get(`/exports/pdf/${user.teacher_id}`, { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `recapitulatif_${stats?.teacher.nom}_${stats?.teacher.prenom}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally { setDownloading(null); }
  };

  const downloadExcel = async () => {
    setDownloading('excel');
    try {
      const res = await api.get('/exports/excel', { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a'); a.href = url; a.download = 'recapitulatif.xlsx'; a.click();
      URL.revokeObjectURL(url);
    } finally { setDownloading(null); }
  };

  const t = stats?.teacher;
  const totalVol = activities.reduce((s, a) => s + a.volume_horaire_calcule, 0);
  const heuresComp = Math.max(0, totalVol - (stats?.seuil_statutaire || 192));

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Mon Récapitulatif</h1>
        <p className="page-subtitle">Téléchargez votre bilan d'heures pédagogiques</p>
      </div>

      <div style={{ maxWidth: '800px' }}>
        {/* Preview card */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ fontWeight: 700, marginBottom: '1.25rem', color: '#64748B', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Aperçu du document
          </h3>

          {/* Simulated document preview */}
          <div style={{
            border: '2px dashed #E2E8F0', borderRadius: '10px', padding: '1.5rem',
            background: '#FAFBFD'
          }}>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '2px solid #1F4E79' }}>
              <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#1F4E79', marginBottom: '0.25rem' }}>
                UNIVERSITÉ VIRTUELLE DE CÔTE D'IVOIRE
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                Récapitulatif des Heures Pédagogiques — Année 2024-2025
              </div>
            </div>

            {/* Teacher info */}
            {loading ? (
              <div style={{ textAlign: 'center', color: '#94A3B8', padding: '1rem' }}>Chargement…</div>
            ) : (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1.25rem', fontSize: '0.8rem' }}>
                  {[
                    ['Nom et Prénom', `${t?.prenom} ${t?.nom}`],
                    ['Grade', t?.grade],
                    ['Département', t?.departement],
                    ['Email', t?.email],
                  ].map(([k, v]) => (
                    <div key={k} style={{ display: 'flex', gap: '0.5rem' }}>
                      <span style={{ color: '#64748B', minWidth: '100px' }}>{k} :</span>
                      <span style={{ fontWeight: 600 }}>{v}</span>
                    </div>
                  ))}
                </div>

                {/* Summary table */}
                <div style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, marginBottom: '0.5rem', color: '#1F4E79' }}>
                    Récapitulatif par cours
                  </div>
                  <div style={{ fontSize: '0.75rem' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr 1fr 1fr', background: '#1F4E79', color: 'white', padding: '0.375rem 0.5rem', borderRadius: '4px 4px 0 0', fontWeight: 600 }}>
                      <span>Cours</span><span style={{ textAlign: 'center' }}>Type</span><span style={{ textAlign: 'center' }}>Séq.</span><span style={{ textAlign: 'right' }}>Volume</span>
                    </div>
                    {activities.slice(0, 5).map((act, i) => (
                      <div key={act.id} style={{ display: 'grid', gridTemplateColumns: '3fr 1fr 1fr 1fr', padding: '0.3rem 0.5rem', background: i % 2 ? '#F5F7FA' : 'white', borderBottom: '1px solid #F1F5F9' }}>
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{act.course_intitule || '—'}</span>
                        <span style={{ textAlign: 'center' }}>{act.type_activite === 'creation' ? 'Créat.' : 'MàJ'}</span>
                        <span style={{ textAlign: 'center' }}>{act.nb_sequences}</span>
                        <span style={{ textAlign: 'right', fontWeight: 600 }}>{act.volume_horaire_calcule}h</span>
                      </div>
                    ))}
                    {activities.length > 5 && (
                      <div style={{ padding: '0.3rem 0.5rem', color: '#94A3B8', fontStyle: 'italic', fontSize: '0.7rem' }}>
                        + {activities.length - 5} activité{activities.length - 5 > 1 ? 's' : ''} supplémentaire{activities.length - 5 > 1 ? 's' : ''}…
                      </div>
                    )}
                    <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr 1fr 1fr', padding: '0.375rem 0.5rem', background: '#EBF2F7', fontWeight: 700, borderRadius: '0 0 4px 4px' }}>
                      <span>TOTAL</span><span /><span />
                      <span style={{ textAlign: 'right', color: '#1F4E79' }}>{totalVol.toFixed(2)}h</span>
                    </div>
                  </div>
                </div>

                {/* Highlights */}
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem' }}>
                  <div style={{ flex: 1, background: '#EBF2F7', borderRadius: '6px', padding: '0.5rem 0.75rem' }}>
                    <div style={{ color: '#64748B' }}>Charge statutaire</div>
                    <div style={{ fontWeight: 700, color: '#1F4E79' }}>{totalVol.toFixed(1)}h / {stats?.seuil_statutaire}h</div>
                  </div>
                  <div style={{ flex: 1, background: heuresComp > 0 ? '#FEF3C7' : '#F1F5F9', borderRadius: '6px', padding: '0.5rem 0.75rem' }}>
                    <div style={{ color: '#64748B' }}>Heures complémentaires</div>
                    <div style={{ fontWeight: 700, color: heuresComp > 0 ? '#D97706' : '#94A3B8' }}>
                      {heuresComp > 0 ? `+${heuresComp.toFixed(1)}h` : 'Aucune'}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Download buttons */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
          <button
            onClick={downloadPdf}
            disabled={downloading === 'pdf' || loading}
            style={{
              padding: '1.25rem', borderRadius: '12px', border: '2px solid #FEE2E2',
              background: 'white', cursor: 'pointer', display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: '0.5rem', transition: 'all 0.15s',
            }}
            onMouseOver={e => (e.currentTarget.style.background = '#FEF2F2')}
            onMouseOut={e => (e.currentTarget.style.background = 'white')}
          >
            <div style={{ width: '3rem', height: '3rem', borderRadius: '10px', background: '#FEF2F2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <FileText size={24} color="#DC2626" />
            </div>
            <span style={{ fontWeight: 700, color: '#DC2626' }}>
              {downloading === 'pdf' ? 'Génération…' : 'Télécharger en PDF'}
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Fiche individuelle complète</span>
          </button>

          <button
            onClick={downloadExcel}
            disabled={downloading === 'excel' || loading}
            style={{
              padding: '1.25rem', borderRadius: '12px', border: '2px solid #DCFCE7',
              background: 'white', cursor: 'pointer', display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: '0.5rem', transition: 'all 0.15s',
            }}
            onMouseOver={e => (e.currentTarget.style.background = '#F0FDF4')}
            onMouseOut={e => (e.currentTarget.style.background = 'white')}
          >
            <div style={{ width: '3rem', height: '3rem', borderRadius: '10px', background: '#F0FDF4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Table size={24} color="#16A34A" />
            </div>
            <span style={{ fontWeight: 700, color: '#16A34A' }}>
              {downloading === 'excel' ? 'Génération…' : 'Télécharger en Excel'}
            </span>
            <span style={{ fontSize: '0.75rem', color: '#94A3B8' }}>État global des heures</span>
          </button>
        </div>

        {/* Note */}
        <div style={{ background: '#F8FAFC', borderRadius: '8px', padding: '0.875rem 1rem', border: '1px solid #E2E8F0', fontSize: '0.8rem', color: '#64748B' }}>
          <strong style={{ color: '#1E293B' }}>Note :</strong> Les fichiers générés contiennent uniquement les données validées par le secrétariat. Les activités en attente de validation ne sont pas incluses dans le calcul des paiements.
        </div>
      </div>
    </>
  );
}
