'use client';
import { useEffect, useState } from 'react';
import { Search, Eye, X, Mail, Building2, Award, BadgeCheck } from 'lucide-react';
import api from '@/lib/api';

interface Teacher {
  id: number; nom: string; prenom: string; grade: string;
  statut: string; departement: string; email: string;
  volume_horaire_total: number;
}

const GRADES = ['Assistant', 'Maître-Assistant', 'Maître de Conférences', 'Professeur'];
const STATUTS = ['Permanent', 'Vacataire'];
const DEPTS = ['Informatique', 'Mathématiques', 'Sciences Économiques', 'Droit', 'Langues'];
const SEUIL = 192;

function TeacherDetailModal({ teacher, onClose }: { teacher: Teacher; onClose: () => void }) {
  const pct = Math.min(100, Math.round((teacher.volume_horaire_total / SEUIL) * 100));
  const rows: { icon: React.ReactNode; label: string; value: string }[] = [
    { icon: <Mail size={15} />, label: 'Email', value: teacher.email },
    { icon: <Award size={15} />, label: 'Grade', value: teacher.grade },
    { icon: <Building2 size={15} />, label: 'Département', value: teacher.departement },
    { icon: <BadgeCheck size={15} />, label: 'Statut', value: teacher.statut },
  ];
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="avatar">{teacher.prenom.charAt(0)}{teacher.nom.charAt(0)}</div>
            <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>{teacher.prenom} {teacher.nom}</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748B' }}><X size={20} /></button>
        </div>
        <div className="modal-body">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {rows.map(r => (
              <div key={r.label} style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', fontSize: '0.85rem' }}>
                <span style={{ color: '#94A3B8', display: 'flex' }}>{r.icon}</span>
                <span style={{ color: '#64748B', minWidth: '110px' }}>{r.label}</span>
                <span style={{ fontWeight: 600 }}>{r.value}</span>
              </div>
            ))}
            <div style={{ marginTop: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '4px' }}>
                <span style={{ color: '#64748B' }}>Volume ce semestre — {teacher.volume_horaire_total}h / {SEUIL}h</span>
                <span style={{ fontWeight: 600, color: pct >= 100 ? '#D97706' : '#1F4E79' }}>{pct}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${pct}%`, background: pct >= 100 ? '#D97706' : pct >= 75 ? '#2E75B6' : '#86EFAC' }} />
              </div>
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-primary" onClick={onClose}>Fermer</button>
        </div>
      </div>
    </div>
  );
}

export default function SecretaryTeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [grade, setGrade] = useState('');
  const [statut, setStatut] = useState('');
  const [dept, setDept] = useState('');
  const [selected, setSelected] = useState<Teacher | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- rechargement volontaire au changement de filtre
    setLoading(true);
    const params: Record<string, string> = {};
    if (search) params.search = search;
    if (grade) params.grade = grade;
    if (statut) params.statut = statut;
    if (dept) params.departement = dept;
    api.get('/teachers/', { params }).then(r => setTeachers(r.data)).finally(() => setLoading(false));
  }, [search, grade, statut, dept]);

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Liste des enseignants</h1>
        <p className="page-subtitle">{teachers.length} enseignant{teachers.length > 1 ? 's' : ''} — consultation uniquement</p>
      </div>

      {/* Filters */}
      <div className="card card-sm" style={{ marginBottom: '1rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '180px' }}>
          <Search size={15} style={{ position: 'absolute', left: '0.625rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
          <input className="form-input" style={{ paddingLeft: '2rem' }} placeholder="Rechercher…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <select className="form-select" style={{ width: 'auto', minWidth: '160px' }} value={dept} onChange={e => setDept(e.target.value)}>
          <option value="">Tous les départements</option>
          {DEPTS.map(d => <option key={d}>{d}</option>)}
        </select>
        <select className="form-select" style={{ width: 'auto', minWidth: '150px' }} value={grade} onChange={e => setGrade(e.target.value)}>
          <option value="">Tous les grades</option>
          {GRADES.map(g => <option key={g}>{g}</option>)}
        </select>
        <select className="form-select" style={{ width: 'auto', minWidth: '140px' }} value={statut} onChange={e => setStatut(e.target.value)}>
          <option value="">Tous les statuts</option>
          {STATUTS.map(s => <option key={s}>{s}</option>)}
        </select>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Enseignant</th>
                <th>Grade</th>
                <th>Département</th>
                <th>Statut</th>
                <th style={{ minWidth: '160px' }}>Volume ce semestre</th>
                <th style={{ textAlign: 'center' }}>Détail</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>
              )}
              {!loading && teachers.map(t => {
                const pct = Math.min(100, Math.round((t.volume_horaire_total / SEUIL) * 100));
                return (
                  <tr key={t.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                        <div className="avatar">{t.prenom.charAt(0)}{t.nom.charAt(0)}</div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.prenom} {t.nom}</div>
                          <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{t.email}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize: '0.8rem' }}>{t.grade}</td>
                    <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.departement}</td>
                    <td>
                      <span className={`badge ${t.statut === 'Permanent' ? 'badge-blue' : 'badge-orange'}`} style={{ fontSize: '0.7rem' }}>
                        {t.statut}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem' }}>
                          <span style={{ color: '#64748B' }}>{t.volume_horaire_total}h / {SEUIL}h</span>
                          <span style={{ fontWeight: 600, color: pct >= 100 ? '#D97706' : '#1F4E79' }}>{pct}%</span>
                        </div>
                        <div className="progress-bar">
                          <div className="progress-fill" style={{
                            width: `${pct}%`,
                            background: pct >= 100 ? '#D97706' : pct >= 75 ? '#2E75B6' : '#86EFAC'
                          }} />
                        </div>
                      </div>
                    </td>
                    <td style={{ textAlign: 'center' }}>
                      <button
                        type="button"
                        onClick={() => setSelected(t)}
                        className="btn btn-ghost btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}
                      >
                        <Eye size={14} /> Voir détail
                      </button>
                    </td>
                  </tr>
                );
              })}
              {!loading && !teachers.length && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucun enseignant trouvé</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selected && <TeacherDetailModal teacher={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
