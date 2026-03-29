'use client';
import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { GraduationCap, Mail, Lock, Eye, EyeOff, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Email ou mot de passe incorrect.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (e: string, p: string) => { setEmail(e); setPassword(p); };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0F2C4A 0%, #1F4E79 40%, #2E75B6 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '1rem', position: 'relative', overflow: 'hidden'
    }}>
      {/* Background decoration */}
      {[...Array(3)].map((_, i) => (
        <div key={i} style={{
          position: 'absolute',
          width: `${300 + i * 150}px`, height: `${300 + i * 150}px`,
          borderRadius: '50%',
          border: '1px solid rgba(255,255,255,0.05)',
          top: `${-50 + i * 30}px`, right: `${-80 + i * 20}px`,
          pointerEvents: 'none'
        }} />
      ))}

      <div style={{ width: '100%', maxWidth: '420px', position: 'relative', zIndex: 1 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            width: '72px', height: '72px', borderRadius: '20px',
            background: 'rgba(255,255,255,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1rem', backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.2)'
          }}>
            <GraduationCap size={36} color="white" />
          </div>
          <h1 style={{ color: 'white', fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            GestionHeures UVCI
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.875rem' }}>
            Université Virtuelle de Côte d'Ivoire
          </p>
        </div>

        {/* Card */}
        <div style={{
          background: 'white', borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 24px 64px rgba(0,0,0,0.3)'
        }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.375rem' }}>
            Connexion
          </h2>
          <p style={{ color: '#64748B', fontSize: '0.8rem', marginBottom: '1.5rem' }}>
            Entrez vos identifiants pour accéder à votre espace
          </p>

          {error && (
            <div style={{
              background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '8px',
              padding: '0.75rem', marginBottom: '1rem',
              color: '#DC2626', fontSize: '0.8rem'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Adresse email</label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
                <input
                  type="email"
                  className="form-input"
                  style={{ paddingLeft: '2.25rem' }}
                  placeholder="votre@email.ci"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Mot de passe</label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  style={{ paddingLeft: '2.25rem', paddingRight: '2.5rem' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute', right: '0.75rem', top: '50%',
                    transform: 'translateY(-50%)', background: 'none',
                    border: 'none', cursor: 'pointer', color: '#94A3B8', padding: 0
                  }}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg"
              style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}
              disabled={loading}
            >
              {loading ? <Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} /> : null}
              {loading ? 'Connexion en cours…' : 'Se connecter'}
            </button>
          </form>

          {/* Quick access buttons */}
          <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #F1F5F9' }}>
            <p style={{ fontSize: '0.75rem', color: '#94A3B8', marginBottom: '0.75rem', textAlign: 'center' }}>
              Accès rapide (démonstration)
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
              {[
                { label: 'Admin', email: 'admin@uvci.ci', pwd: 'admin123', color: '#1F4E79' },
                { label: 'Secrétaire', email: 'secretaire@uvci.ci', pwd: 'secretaire123', color: '#0F766E' },
                { label: 'Enseignant', email: 'jkouame@uvci.ci', pwd: 'teacher123', color: '#7C3AED' },
              ].map(({ label, email: e, pwd, color }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => quickLogin(e, pwd)}
                  style={{
                    padding: '0.4rem', borderRadius: '6px', border: `1px solid ${color}20`,
                    background: `${color}08`, color, fontSize: '0.7rem', fontWeight: 600,
                    cursor: 'pointer', transition: 'all 0.15s'
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <p style={{ textAlign: 'center', color: 'rgba(255,255,255,0.4)', fontSize: '0.75rem', marginTop: '1.5rem' }}>
          © 2025 UVCI — Tous droits réservés
        </p>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
