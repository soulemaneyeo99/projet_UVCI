'use client';
import { useEffect, useState } from 'react';
import { Loader2, Calculator, CheckCircle, RefreshCw, Plus } from 'lucide-react';
import api from '@/lib/api';

interface Teacher { id: number; nom: string; prenom: string; grade: string; departement: string; }
interface Course { id: number; intitule: string; filiere: string; niveau: string; }
interface AcademicYear { id: number; libelle: string; }
interface ActivityOut {
  id: number; teacher_nom?: string; teacher_prenom?: string; course_intitule?: string;
  type_activite: string; niveau_complexite: number; nb_sequences: number;
  volume_horaire_calcule: number; validation_status: string; created_at?: string;
}

const RATES: Record<number, Record<string, number>> = {
  1: { creation: 0.4, mise_a_jour: 0.2 },
  2: { creation: 0.75, mise_a_jour: 0.375 },
  3: { creation: 1.5, mise_a_jour: 0.75 },
};

function calcVolume(type: string, niveau: number, seq: number) {
  return (RATES[niveau]?.[type] || 0) * seq;
}

export default function SecretaryActivitiesPage() {
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [years, setYears] = useState<AcademicYear[]>([]);
  const [activities, setActivities] = useState<ActivityOut[]>([]);

  const [teacherId, setTeacherId] = useState('');
  const [courseId, setCourseId] = useState('');
  const [type, setType] = useState('creation');
  const [niveau, setNiveau] = useState(1);
  const [sequences, setSequences] = useState(1);
  const [yearId, setYearId] = useState('');
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const volume = calcVolume(type, niveau, sequences);

  useEffect(() => {
    Promise.all([
      api.get('/teachers/').then(r => setTeachers(r.data)),
      api.get('/courses/').then(r => setCourses(r.data)),
      api.get('/academic-years/').then(r => setYears(r.data)),
      api.get('/activities/').then(r => setActivities(r.data)),
    ]);
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teacherId || !courseId) { setError('Veuillez sélectionner un enseignant et un cours.'); return; }
    setSaving(true); setError(''); setSuccess(false);
    try {
      const res = await api.post('/activities/', {
        teacher_id: Number(teacherId), course_id: Number(courseId),
        type_activite: type, niveau_complexite: niveau, nb_sequences: sequences,
        academic_year_id: yearId ? Number(yearId) : null,
      });
      setActivities(prev => [res.data, ...prev]);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      setTeacherId(''); setCourseId(''); setSequences(1); setNiveau(1); setType('creation');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Erreur lors de la soumission.');
    } finally { setSaving(false); }
  };

  return (
    <>
      <div className="page-header">
        <h1 className="page-title">Nouvelle Activité Pédagogique</h1>
        <p className="page-subtitle">Saisissez et calculez le volume horaire d'une activité</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Form */}
        <div className="card">
          {error && (
            <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '6px', padding: '0.625rem', marginBottom: '1rem', color: '#DC2626', fontSize: '0.8rem' }}>
              {error}
            </div>
          )}
          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Teacher with avatar */}
            <div className="form-group">
              <label className="form-label">Enseignant *</label>
              <div style={{ position: 'relative' }}>
                {teacherId && (
                  <div style={{ position: 'absolute', left: '0.625rem', top: '50%', transform: 'translateY(-50%)', zIndex: 1 }}>
                    <div className="avatar" style={{ width: '1.5rem', height: '1.5rem', fontSize: '0.6rem' }}>
                      {teachers.find(t => t.id === Number(teacherId))?.prenom.charAt(0)}
                      {teachers.find(t => t.id === Number(teacherId))?.nom.charAt(0)}
                    </div>
                  </div>
                )}
                <select
                  className="form-select"
                  style={{ paddingLeft: teacherId ? '2.5rem' : '0.75rem' }}
                  value={teacherId}
                  onChange={e => setTeacherId(e.target.value)}
                  required
                >
                  <option value="">— Sélectionner un enseignant —</option>
                  {teachers.map(t => (
                    <option key={t.id} value={t.id}>
                      {t.prenom} {t.nom} · {t.grade} · {t.departement}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Cours *</label>
              <select className="form-select" value={courseId} onChange={e => setCourseId(e.target.value)} required>
                <option value="">— Sélectionner un cours —</option>
                {courses.map(c => (
                  <option key={c.id} value={c.id}>{c.intitule} — {c.filiere} {c.niveau}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Année académique</label>
              <select className="form-select" value={yearId} onChange={e => setYearId(e.target.value)}>
                <option value="">— Optionnel —</option>
                {years.map(y => <option key={y.id} value={y.id}>{y.libelle}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Type d'activité *</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                {[
                  { v: 'creation', label: 'Création de ressource', desc: 'Contenu entièrement nouveau', icon: Plus },
                  { v: 'mise_a_jour', label: 'Mise à jour', desc: 'Ressource existante modifiée', icon: RefreshCw },
                ].map(({ v, label, desc, icon: Icon }) => (
                  <button key={v} type="button" onClick={() => setType(v)} style={{
                    padding: '0.75rem', borderRadius: '8px', cursor: 'pointer',
                    border: `2px solid ${type === v ? '#2E75B6' : '#E2E8F0'}`,
                    background: type === v ? '#EBF2F7' : 'white', textAlign: 'left',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.375rem', marginBottom: '0.25rem' }}>
                      <Icon size={14} color={type === v ? '#2E75B6' : '#94A3B8'} />
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: type === v ? '#1F4E79' : '#64748B' }}>{label}</span>
                    </div>
                    <p style={{ fontSize: '0.68rem', color: '#94A3B8' }}>{desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Niveau de complexité *</label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                {[
                  { v: 1, label: 'Niveau 1', desc: 'Contenus simples', color: '#1D4ED8' },
                  { v: 2, label: 'Niveau 2', desc: 'Activités interactives', color: '#7C3AED' },
                  { v: 3, label: 'Niveau 3', desc: 'Serious game', color: '#D97706' },
                ].map(({ v, label, desc, color }) => (
                  <button key={v} type="button" onClick={() => setNiveau(v)} style={{
                    padding: '0.625rem 0.5rem', borderRadius: '8px', cursor: 'pointer',
                    border: `2px solid ${niveau === v ? color : '#E2E8F0'}`,
                    background: niveau === v ? `${color}10` : 'white', textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: niveau === v ? color : '#64748B' }}>{label}</div>
                    <div style={{ fontSize: '0.65rem', color: '#94A3B8', marginTop: '2px' }}>{desc}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Nombre de séquences *</label>
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button type="button" onClick={() => setSequences(s => Math.max(1, s - 1))} className="btn btn-ghost btn-sm" style={{ width: '2rem', height: '2.25rem', padding: 0, justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>−</button>
                <input type="number" className="form-input" style={{ textAlign: 'center' }} min={1} max={100} value={sequences} onChange={e => setSequences(Math.max(1, Number(e.target.value)))} />
                <button type="button" onClick={() => setSequences(s => s + 1)} className="btn btn-ghost btn-sm" style={{ width: '2rem', height: '2.25rem', padding: 0, justifyContent: 'center', fontSize: '1.2rem', flexShrink: 0 }}>+</button>
              </div>
            </div>

            {/* Computed volume */}
            <div style={{
              padding: '1rem', borderRadius: '10px',
              background: success ? '#F0FDF4' : '#EBF2F7',
              border: `2px solid ${success ? '#86EFAC' : '#BFDBFE'}`,
              textAlign: 'center', transition: 'all 0.3s'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                {success ? <CheckCircle size={16} color="#16A34A" /> : <Calculator size={16} color="#2E75B6" />}
                <span style={{ fontSize: '0.75rem', color: success ? '#16A34A' : '#2E75B6', fontWeight: 600 }}>
                  {success ? 'Activité enregistrée !' : 'Volume horaire calculé'}
                </span>
              </div>
              <div style={{ fontSize: '2.25rem', fontWeight: 800, color: success ? '#16A34A' : '#1F4E79', lineHeight: 1 }}>
                {volume.toFixed(2)} h
              </div>
              <div style={{ fontSize: '0.7rem', color: '#64748B', marginTop: '0.25rem' }}>
                {sequences} séq. × {RATES[niveau]?.[type]}h/séq. (N{niveau} — {type === 'creation' ? 'Création' : 'MàJ'})
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button type="button" className="btn btn-ghost" style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => { setTeacherId(''); setCourseId(''); setSequences(1); setNiveau(1); setType('creation'); setError(''); }}>
                Annuler
              </button>
              <button type="submit" className="btn btn-primary" style={{ flex: 2, justifyContent: 'center' }} disabled={saving}>
                {saving && <Loader2 size={15} style={{ animation: 'spin 0.8s linear infinite' }} />}
                {saving ? 'Enregistrement…' : 'Enregistrer'}
              </button>
            </div>
          </form>
          <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
        </div>

        {/* Recent activities */}
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #F1F5F9' }}>
            <h3 style={{ fontWeight: 700, fontSize: '0.95rem' }}>Activités enregistrées</h3>
            <p style={{ fontSize: '0.75rem', color: '#64748B' }}>{activities.length} activité{activities.length !== 1 ? 's' : ''}</p>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Enseignant</th><th>Cours</th><th>Type</th>
                  <th>Niv.</th><th style={{ textAlign: 'right' }}>Séq.</th>
                  <th style={{ textAlign: 'right' }}>Volume</th><th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {activities.slice(0, 20).map(act => (
                  <tr key={act.id}>
                    <td style={{ fontWeight: 600, fontSize: '0.8rem' }}>{act.teacher_prenom} {act.teacher_nom}</td>
                    <td style={{ fontSize: '0.75rem', color: '#64748B', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
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
                  </tr>
                ))}
                {!activities.length && (
                  <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: '#94A3B8' }}>Aucune activité</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
