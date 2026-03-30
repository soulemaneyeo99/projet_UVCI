'use client';
import { useEffect, useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Mail, Phone, GraduationCap, Building2 } from 'lucide-react';
import api from '@/lib/api';

interface TeacherStats {
  teacher: { id: number; nom: string; prenom: string; grade: string; departement: string; email: string; statut: string; telephone?: string; taux_horaire: number; };
  volume_total: number;
  heures_complementaires: number;
  activites_semestre: number;
  charge_pct: number;
  seuil_statutaire: number;
}

export default function TeacherProfilePage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.teacher_id) return;
    api.get(`/dashboard/teacher-stats/${user.teacher_id}`)
      .then(r => setStats(r.data))
      .finally(() => setLoading(false));
  }, [user]);

  const t = stats?.teacher;

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Mon Profil</h1>
        <p className="page-subtitle">Informations personnelles et professionnelles</p>
      </div>

      <div style={{ maxWidth: '640px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Profile card */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div style={{
              width: '80px', height: '80px', borderRadius: '50%',
              background: 'linear-gradient(135deg, #1F4E79, #2E75B6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '1.75rem', fontWeight: 700, color: 'white', flexShrink: 0
            }}>
              {t?.prenom?.charAt(0) || '?'}{t?.nom?.charAt(0) || '?'}
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>
                {loading ? '…' : `${t?.prenom} ${t?.nom}`}
              </h2>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <span className="badge badge-blue">{t?.grade || '—'}</span>
                <span className={`badge ${t?.statut === 'Permanent' ? 'badge-green' : 'badge-orange'}`}>
                  {t?.statut || '—'}
                </span>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gap: '1rem' }}>
            {[
              { icon: Mail, label: 'Email', value: t?.email },
              { icon: Phone, label: 'Téléphone', value: t?.telephone || 'Non renseigné' },
              { icon: Building2, label: 'Département', value: t?.departement },
              { icon: GraduationCap, label: 'Grade', value: t?.grade },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.75rem', background: '#F8FAFC', borderRadius: '8px' }}>
                <div style={{ width: '2rem', height: '2rem', borderRadius: '8px', background: '#EBF2F7', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={16} color="#1F4E79" />
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500, color: '#1E293B' }}>{loading ? '…' : value}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="card">
          <h3 style={{ fontWeight: 700, marginBottom: '1rem', fontSize: '0.9rem' }}>Informations contractuelles</h3>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            {[
              { label: 'Seuil statutaire annuel', value: `${stats?.seuil_statutaire || 192}h` },
              { label: 'Taux horaire complémentaire', value: `${t?.taux_horaire?.toLocaleString('fr-FR') || '—'} FCFA/h` },
              { label: 'Volume horaire total', value: `${stats?.volume_total || 0}h` },
              { label: 'Heures complémentaires', value: `${stats?.heures_complementaires || 0}h` },
            ].map(({ label, value }) => (
              <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.625rem 0', borderBottom: '1px solid #F1F5F9' }}>
                <span style={{ fontSize: '0.875rem', color: '#64748B' }}>{label}</span>
                <span style={{ fontWeight: 700, color: '#1E293B' }}>{loading ? '…' : value}</span>
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: '#EBF2F7', borderRadius: '8px', padding: '0.875rem 1rem', fontSize: '0.8rem', color: '#1F4E79' }}>
          Pour modifier vos informations, veuillez contacter le secrétariat ou l'administration.
        </div>
      </div>
    </>
  );
}
