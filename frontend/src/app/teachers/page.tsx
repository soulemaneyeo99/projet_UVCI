'use client';
import { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { Plus, Search, Edit2, Trash2, X, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface Teacher {
  id: number; nom: string; prenom: string; grade: string;
  statut: string; departement: string; taux_horaire: number;
  email: string; telephone?: string; volume_horaire_total: number;
}

const GRADES = ['Assistant', 'Maître-Assistant', 'Maître de Conférences', 'Professeur'];
const STATUTS = ['Permanent', 'Vacataire'];
const DEPARTEMENTS = ['Informatique', 'Mathématiques', 'Sciences Économiques', 'Droit', 'Langues'];

function TeacherModal({ teacher, onClose, onSaved }: {
  teacher: Teacher | null; onClose: () => void; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    nom: teacher?.nom || '', prenom: teacher?.prenom || '',
    grade: teacher?.grade || GRADES[0], statut: teacher?.statut || STATUTS[0],
    departement: teacher?.departement || DEPARTEMENTS[0],
    taux_horaire: teacher?.taux_horaire || 2500,
    email: teacher?.email || '', telephone: teacher?.telephone || '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }));

  const save = async () => {
    setSaving(true); setError('');
    try {
      if (teacher) await api.put(`/teachers/${teacher.id}`, form);
      else await api.post('/teachers/', form);
      onSaved(); onClose();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3 style={{ fontWeight: 700, fontSize: '1rem' }}>{teacher ? 'Modifier l\'enseignant' : 'Ajouter un enseignant'}</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748B' }}><X size={20} /></button>
        </div>
        <div className="modal-body">
          {error && <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '6px', padding: '0.625rem', marginBottom: '1rem', color: '#DC2626', fontSize: '0.8rem' }}>{error}</div>}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Nom *</label>
              <input className="form-input" value={form.nom} onChange={e => set('nom', e.target.value)} placeholder="Kouamé" />
            </div>
            <div className="form-group">
              <label className="form-label">Prénom *</label>
              <input className="form-input" value={form.prenom} onChange={e => set('prenom', e.target.value)} placeholder="Jean-Pierre" />
            </div>
            <div className="form-group">
              <label className="form-label">Grade *</label>
              <select className="form-select" value={form.grade} onChange={e => set('grade', e.target.value)}>
                {GRADES.map(g => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Statut *</label>
              <select className="form-select" value={form.statut} onChange={e => set('statut', e.target.value)}>
                {STATUTS.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Département *</label>
              <select className="form-select" value={form.departement} onChange={e => set('departement', e.target.value)}>
                {DEPARTEMENTS.map(d => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Taux horaire (FCFA) *</label>
              <input type="number" className="form-input" value={form.taux_horaire} onChange={e => set('taux_horaire', Number(e.target.value))} />
            </div>
            <div className="form-group" style={{ gridColumn: '1/-1' }}>
              <label className="form-label">Email *</label>
              <input type="email" className="form-input" value={form.email} onChange={e => set('email', e.target.value)} placeholder="enseignant@uvci.ci" />
            </div>
            <div className="form-group" style={{ gridColumn: '1/-1' }}>
              <label className="form-label">Téléphone</label>
              <input className="form-input" value={form.telephone} onChange={e => set('telephone', e.target.value)} placeholder="+225 07 00 00 00 00" />
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>Annuler</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving && <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />}
            {saving ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </div>
      </div>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}

export default function TeachersPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [grade, setGrade] = useState('');
  const [statut, setStatut] = useState('');
  const [modal, setModal] = useState<Teacher | null | 'new'>(null);
  const [page, setPage] = useState(1);
  const PER_PAGE = 10;

  const load = () => {
    setLoading(true);
    const params: any = {};
    if (search) params.search = search;
    if (grade) params.grade = grade;
    if (statut) params.statut = statut;
    api.get('/teachers/', { params }).then(r => setTeachers(r.data)).finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [search, grade, statut]);

  const del = async (id: number) => {
    if (!confirm('Supprimer cet enseignant ?')) return;
    await api.delete(`/teachers/${id}`);
    load();
  };

  const paged = teachers.slice((page - 1) * PER_PAGE, page * PER_PAGE);
  const totalPages = Math.ceil(teachers.length / PER_PAGE);

  return (
    <MainLayout>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Enseignants</h1>
          <p className="page-subtitle">{teachers.length} enseignant{teachers.length > 1 ? 's' : ''} enregistré{teachers.length > 1 ? 's' : ''}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModal('new')}>
          <Plus size={16} /> Ajouter un enseignant
        </button>
      </div>

      {/* Filters */}
      <div className="card card-sm" style={{ marginBottom: '1rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: '200px' }}>
          <Search size={15} style={{ position: 'absolute', left: '0.625rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
          <input
            className="form-input"
            style={{ paddingLeft: '2rem' }}
            placeholder="Rechercher par nom, email…"
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <select className="form-select" style={{ width: 'auto', minWidth: '160px' }} value={grade} onChange={e => { setGrade(e.target.value); setPage(1); }}>
          <option value="">Tous les grades</option>
          {GRADES.map(g => <option key={g}>{g}</option>)}
        </select>
        <select className="form-select" style={{ width: 'auto', minWidth: '140px' }} value={statut} onChange={e => { setStatut(e.target.value); setPage(1); }}>
          <option value="">Tous les statuts</option>
          {STATUTS.map(s => <option key={s}>{s}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0 }}>
        <div className="table-container">
          <table>
            <thead><tr>
              <th>Nom / Prénom</th>
              <th>Grade</th>
              <th>Statut</th>
              <th>Département</th>
              <th>Email</th>
              <th style={{ textAlign: 'right' }}>Volume horaire</th>
              <th style={{ textAlign: 'center' }}>Actions</th>
            </tr></thead>
            <tbody>
              {loading && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>
              )}
              {!loading && paged.map(t => (
                <tr key={t.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                      <div className="avatar">{t.prenom.charAt(0)}{t.nom.charAt(0)}</div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{t.prenom} {t.nom}</div>
                        <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>{t.telephone || '—'}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ fontSize: '0.8rem' }}>{t.grade}</td>
                  <td>
                    <span className={`badge ${t.statut === 'Permanent' ? 'badge-blue' : 'badge-orange'}`}>{t.statut}</span>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.departement}</td>
                  <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{t.email}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: '#1F4E79' }}>{t.volume_horaire_total}h</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.375rem', justifyContent: 'center' }}>
                      <button onClick={() => setModal(t)} className="btn btn-ghost btn-sm" title="Modifier">
                        <Edit2 size={14} />
                      </button>
                      <button onClick={() => del(t.id)} className="btn btn-sm" style={{ background: '#FEF2F2', color: '#DC2626', border: 'none', cursor: 'pointer', borderRadius: '6px', padding: '0.35rem 0.5rem' }} title="Supprimer">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && !paged.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucun enseignant trouvé</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid #F1F5F9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.8rem', color: '#64748B' }}>Page {page} / {totalPages}</span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Précédent</button>
              <button className="btn btn-ghost btn-sm" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Suivant</button>
            </div>
          </div>
        )}
      </div>

      {modal && (
        <TeacherModal
          teacher={modal === 'new' ? null : modal}
          onClose={() => setModal(null)}
          onSaved={load}
        />
      )}
    </MainLayout>
  );
}
