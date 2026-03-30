'use client';
import { useAuth } from '@/context/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Sidebar from './Sidebar';
import Navbar from './Navbar';

const PUBLIC_ROUTES = ['/'];

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (!isLoading && !user && !isPublic) router.push('/');
  }, [user, isLoading, isPublic, router]);

  // Close sidebar on route change (mobile nav)
  useEffect(() => { setSidebarOpen(false); }, [pathname]);

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F7FA' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '50%', border: '3px solid #E2E8F0', borderTopColor: '#1F4E79', animation: 'spin 0.8s linear infinite', margin: '0 auto 1rem' }} />
          <p style={{ color: '#64748B', fontSize: '0.875rem' }}>Chargement…</p>
          <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        </div>
      </div>
    );
  }

  if (isPublic) return <>{children}</>;
  if (!user) return null;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#F5F7FA' }}>
      {/* Mobile overlay backdrop */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
            zIndex: 40, display: 'none'
          }}
          className="mobile-backdrop"
        />
      )}

      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <Navbar onMenuClick={() => setSidebarOpen(o => !o)} />
        <main style={{ flex: 1, padding: '1rem', overflow: 'auto' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
