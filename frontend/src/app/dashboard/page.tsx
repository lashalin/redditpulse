'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getMe } from '@/lib/api';
import Dashboard from '@/components/Dashboard';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('token');
        router.push('/login');
      })
      .finally(() => setLoading(false));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-10 h-10 border-2 border-brand-accent border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return <Dashboard user={user} onLogout={handleLogout} />;
}
