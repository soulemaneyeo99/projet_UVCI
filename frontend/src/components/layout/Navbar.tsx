'use client';
import { Bell, Menu } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const roleLabels: Record<string, string> = {
  admin: 'Administrateur', secretary: 'Secrétaire Principal', teacher: 'Enseignant',
};

export default function Navbar({ onMenuClick }: { onMenuClick: () => void }) {
  const { user } = useAuth();
  const role = user?.role || '';

  return (
    <header style={{
      height: '60px', background: 'white', borderBottom: '1px solid #E2E8F0',
      display: 'flex', alignItems: 'center', padding: '0 1rem', gap: '0.75rem', flexShrink: 0
    }}>
      {/* Hamburger — mobile only */}
      <button
        onClick={onMenuClick}
        className="hamburger-btn"
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          padding: '0.4rem', borderRadius: '8px', color: '#64748B',
          display: 'flex', alignItems: 'center',
        }}
      >
        <Menu size={22} />
      </button>

      {/* Title on mobile */}
      <span className="navbar-title" style={{ fontWeight: 700, fontSize: '0.95rem', color: '#1F4E79' }}>
        GestionHeures
      </span>

      <div style={{ flex: 1 }} />

      {/* Notifications */}
      <button style={{ position: 'relative', background: 'none', border: 'none', cursor: 'pointer', padding: '0.5rem', borderRadius: '8px', display: 'flex', alignItems: 'center', color: '#64748B' }}>
        <Bell size={20} />
        <span style={{ position: 'absolute', top: '6px', right: '6px', width: '8px', height: '8px', borderRadius: '50%', background: '#DC2626', border: '2px solid white' }} />
      </button>

      {/* User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <div className="navbar-user-info" style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#1E293B' }}>
            {user?.email?.split('@')[0] || 'Utilisateur'}
          </div>
          <div style={{ fontSize: '0.7rem', color: '#64748B' }}>{roleLabels[role] || role}</div>
        </div>
        <div style={{ width: '2.25rem', height: '2.25rem', borderRadius: '50%', background: '#1F4E79', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 700, flexShrink: 0 }}>
          {user?.email?.charAt(0).toUpperCase() || '?'}
        </div>
      </div>
    </header>
  );
}
