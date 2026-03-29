'use client';
import { Bell, Search } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

const roleLabels: Record<string, string> = {
  admin: 'Administrateur',
  secretary: 'Secrétaire Principal',
  teacher: 'Enseignant',
};

export default function Navbar() {
  const { user } = useAuth();
  const role = user?.role || '';

  return (
    <header style={{
      height: '60px', background: 'white',
      borderBottom: '1px solid #E2E8F0',
      display: 'flex', alignItems: 'center',
      padding: '0 1.5rem', gap: '1rem', flexShrink: 0
    }}>
      {/* Search */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '0.5rem',
        background: '#F5F7FA', borderRadius: '8px',
        padding: '0.4rem 0.75rem', flex: 1, maxWidth: '360px'
      }}>
        <Search size={15} color="#94A3B8" />
        <input
          placeholder="Rechercher enseignant, cours…"
          style={{
            border: 'none', background: 'transparent', outline: 'none',
            fontSize: '0.875rem', color: '#1E293B', width: '100%'
          }}
        />
      </div>

      <div style={{ flex: 1 }} />

      {/* Notifications */}
      <button style={{
        position: 'relative', background: 'none', border: 'none',
        cursor: 'pointer', padding: '0.5rem', borderRadius: '8px',
        display: 'flex', alignItems: 'center', color: '#64748B'
      }}>
        <Bell size={20} />
        <span style={{
          position: 'absolute', top: '6px', right: '6px',
          width: '8px', height: '8px', borderRadius: '50%',
          background: '#DC2626', border: '2px solid white'
        }} />
      </button>

      {/* User */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
        <div style={{
          textAlign: 'right', display: 'flex', flexDirection: 'column', gap: '1px'
        }}>
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#1E293B' }}>
            {user?.email?.split('@')[0] || 'Utilisateur'}
          </span>
          <span style={{ fontSize: '0.7rem', color: '#64748B' }}>
            {roleLabels[role] || role}
          </span>
        </div>
        <div style={{
          width: '2.25rem', height: '2.25rem', borderRadius: '50%',
          background: '#1F4E79', color: 'white',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.8rem', fontWeight: 700
        }}>
          {user?.email?.charAt(0).toUpperCase() || '?'}
        </div>
      </div>
    </header>
  );
}
