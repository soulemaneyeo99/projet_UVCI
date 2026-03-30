'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  LayoutDashboard, Users, BookOpen, ClipboardList,
  BarChart2, Settings, LogOut, GraduationCap, FileText, User, X
} from 'lucide-react';

const adminNav = [
  { label: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { label: 'Enseignants', href: '/teachers', icon: Users },
  { label: 'Cours', href: '/courses', icon: BookOpen },
  { label: 'Activités', href: '/activities', icon: ClipboardList },
  { label: 'Rapports', href: '/reports', icon: BarChart2 },
];
const secretaryNav = [
  { label: 'Tableau de bord', href: '/secretary/dashboard', icon: LayoutDashboard },
  { label: 'Enseignants', href: '/secretary/teachers', icon: Users },
  { label: 'Saisie activité', href: '/secretary/activities', icon: ClipboardList },
  { label: 'Rapports', href: '/secretary/reports', icon: FileText },
];
const teacherNav = [
  { label: 'Mon tableau de bord', href: '/teacher/dashboard', icon: LayoutDashboard },
  { label: 'Mes activités', href: '/teacher/activities', icon: ClipboardList },
  { label: 'Mon profil', href: '/teacher/profile', icon: User },
  { label: 'Récapitulatif', href: '/teacher/recapitulatif', icon: FileText },
];
const roleLabels: Record<string, string> = {
  admin: 'Administrateur', secretary: 'Secrétaire', teacher: 'Enseignant',
};

interface SidebarProps { open: boolean; onClose: () => void; }

export default function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const role = user?.role || 'teacher';
  const navItems = role === 'admin' ? adminNav : role === 'secretary' ? secretaryNav : teacherNav;

  return (
    <>
      {/* Backdrop for mobile */}
      {open && (
        <div
          onClick={onClose}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
            zIndex: 40,
          }}
          className="desktop-hide"
        />
      )}

      <aside
        style={{
          width: '240px', minHeight: '100vh', background: 'var(--primary)',
          display: 'flex', flexDirection: 'column', flexShrink: 0,
          transition: 'transform 0.25s ease',
        }}
        className={`sidebar ${open ? 'sidebar-open' : ''}`}
      >
        {/* Header */}
        <div className="sidebar-logo" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <div style={{ width: '2.25rem', height: '2.25rem', borderRadius: '8px', background: 'rgba(255,255,255,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <GraduationCap size={20} color="white" />
            </div>
            <div>
              <div style={{ color: 'white', fontWeight: 700, fontSize: '0.9rem', lineHeight: 1.2 }}>GestionHeures</div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem' }}>UVCI</div>
            </div>
          </div>
          {/* Close button — mobile only */}
          <button
            onClick={onClose}
            className="sidebar-close-btn"
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(255,255,255,0.7)', padding: '0.25rem', borderRadius: '6px' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Role badge */}
        <div style={{ padding: '0.75rem 1.25rem 0' }}>
          <span style={{ background: 'rgba(255,255,255,0.12)', color: 'rgba(255,255,255,0.85)', fontSize: '0.7rem', fontWeight: 600, padding: '0.2rem 0.6rem', borderRadius: '999px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            {roleLabels[role] || role}
          </span>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          <div className="nav-section-label">Navigation</div>
          {navItems.map(({ label, href, icon: Icon }) => (
            <Link key={href} href={href} className={`nav-item ${pathname === href || pathname.startsWith(href + '/') ? 'active' : ''}`}>
              <Icon size={18} />
              <span>{label}</span>
            </Link>
          ))}
          {role === 'admin' && (
            <>
              <div className="nav-section-label" style={{ marginTop: '1rem' }}>Système</div>
              <Link href="/settings" className={`nav-item ${pathname === '/settings' ? 'active' : ''}`}>
                <Settings size={18} /><span>Paramètres</span>
              </Link>
            </>
          )}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem', marginBottom: '0.5rem' }}>
            <div style={{ width: '2rem', height: '2rem', borderRadius: '50%', background: 'rgba(255,255,255,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, color: 'white', flexShrink: 0 }}>
              {user?.email?.charAt(0).toUpperCase() || '?'}
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ color: 'white', fontSize: '0.8rem', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user?.email?.split('@')[0] || 'Utilisateur'}
              </div>
              <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.7rem' }}>{roleLabels[role]}</div>
            </div>
          </div>
          <button onClick={logout} className="nav-item" style={{ color: 'rgba(255,150,150,0.9)', width: '100%' }}>
            <LogOut size={16} /><span>Déconnexion</span>
          </button>
        </div>
      </aside>
    </>
  );
}
