'use client';
import { useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, X, Loader2, BookOpen } from 'lucide-react';
import api from '@/lib/api';

interface Course {
  id: number; intitule: string; filiere: string;
  niveau: string; semestre: string; nb_heures?: number; nb_credits?: number;
}

const NIVEAUX = ['L1','L2','L3','M1','M2'];
const SEMESTRES = ['S1','S2'];

function CourseModal({ course, onClose, onSaved }: {
  course: Course | null; onClose: () => void; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    intitule: course?.intitule || '', filiere: course?.filiere || '',
    niveau: course?.niveau || 'L1', semestre: course?.semestre || 'S1',
    nb_heures: course?.nb_heures || 30, nb_credits: course?.nb_credits || 3,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const set = (k: string, v: any) => setForm(f => ({ ...f, [k]: v }));

  const save = async () => {
    setSaving(true); setError('');
    try {
      if (course) await api.put(`/courses/${course.id}`, form);
      else await api.post('/courses/', form);
      onSaved(); onClose();
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Erreur lors de la sauvegarde');
    } finally { setSaving(false); }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <div className="modal-header">
          <h3 style={{ fontWeight: 700 }}>{course ? 'Modifier le cours' : 'Ajouter un cours'}</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748B' }}>
            <X size={20} />
          </button>
        </div>
        <div className="modal-body">
          {error && (
            <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '6px', padding: '0.625rem', marginBottom: '1rem', color: '#DC2626', fontSize: '0.8rem' }}>
              {error}
            </div>
          )}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group" style={{ gridColumn: '1/-1' }}>
              <label className="form-label">Intitulé du cours *</label>
              <input className="form-input" value={form.intitule} onChange={e => set('intitule', e.target.value)} placeholder="Ex: Programmation Python" />
            </div>
            <div className="form-group" style={{ gridColumn: '1/-1' }}>
              <label className="form-label">Filière *</label>
              <input className="form-input" value={form.filiere} onChange={e => set('filiere', e.target.value)} placeholder="Ex: Informatique" />
            </div>
            <div className="form-group">
              <label className="form-label">Niveau *</label>
              <select className="form-select" value={form.niveau} onChange={e => set('niveau', e.target.value)}>
                {NIVEAUX.map(n => <option key={n}>{n}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Semestre *</label>
              <select className="form-select" value={form.semestre} onChange={e => set('semestre', e.target.value)}>
                {SEMESTRES.map(s => <option key={s}>{s}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Volume horaire</label>
              <input type="number" className="form-input" value={form.nb_heures} onChange={e => set('nb_heures', Number(e.target.value))} />
            </div>
            <div className="form-group">
              <label className="form-label">Crédits</label>
              <input type="number" className="form-input" value={form.nb_credits} onChange={e => set('nb_credits', Number(e.target.value))} />
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

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<Course | null | 'new'>(null);

  const load = () => {
    setLoading(true);
    api.get('/courses/').then(r => setCourses(r.data)).finally(() => setLoading(false));
  };
  useEffect(() => { load(); }, []);

  const del = async (id: number) => {
    if (!confirm('Supprimer ce cours ?')) return;
    await api.delete(`/courses/${id}`);
    load();
  };

  return (
    <>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className="page-title">Cours</h1>
          <p className="page-subtitle">{courses.length} cours enregistré{courses.length > 1 ? 's' : ''}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setModal('new')}>
          <Plus size={16} /> Ajouter un cours
        </button>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Intitulé</th>
                <th>Filière</th>
                <th>Niveau</th>
                <th>Semestre</th>
                <th style={{ textAlign: 'center' }}>Heures</th>
                <th style={{ textAlign: 'center' }}>Crédits</th>
                <th style={{ textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Chargement…</td></tr>
              )}
              {!loading && courses.map(c => (
                <tr key={c.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                      <div style={{
                        width: '2rem', height: '2rem', borderRadius: '8px',
                        background: '#EBF2F7', display: 'flex', alignItems: 'center', justifyContent: 'center'
                      }}>
                        <BookOpen size={14} color="#1F4E79" />
                      </div>
                      <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{c.intitule}</span>
                    </div>
                  </td>
                  <td style={{ fontSize: '0.8rem', color: '#64748B' }}>{c.filiere}</td>
                  <td><span className="badge badge-blue" style={{ fontSize: '0.7rem' }}>{c.niveau}</span></td>
                  <td><span className="badge badge-gray" style={{ fontSize: '0.7rem' }}>{c.semestre}</span></td>
                  <td style={{ textAlign: 'center', fontSize: '0.8rem' }}>{c.nb_heures || '—'}</td>
                  <td style={{ textAlign: 'center', fontSize: '0.8rem' }}>{c.nb_credits || '—'}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.375rem', justifyContent: 'center' }}>
                      <button onClick={() => setModal(c)} className="btn btn-ghost btn-sm"><Edit2 size={14} /></button>
                      <button onClick={() => del(c.id)} style={{ background: '#FEF2F2', color: '#DC2626', border: 'none', cursor: 'pointer', borderRadius: '6px', padding: '0.35rem 0.5rem' }}>
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && !courses.length && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: '#94A3B8' }}>Aucun cours enregistré</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {modal && (
        <CourseModal
          course={modal === 'new' ? null : modal}
          onClose={() => setModal(null)}
          onSaved={load}
        />
      )}
    </>
  );
}
