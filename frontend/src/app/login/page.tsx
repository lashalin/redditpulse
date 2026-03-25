'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { login, register } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, username, password);
        await login(email, password);
      }
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back to home */}
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8 text-sm">
          &larr; 返回首页
        </Link>

        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold">
            <span className="text-brand-accent">Reddit</span>Pulse
          </h1>
          <p className="text-gray-400 mt-2">AI驱动的Reddit品牌舆情分析平台</p>
        </div>

        {/* Form */}
        <div className="glass-card p-8">
          <div className="flex mb-6">
            <button
              type="button"
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2 text-center rounded-l-lg transition-colors ${
                isLogin ? 'bg-brand-accent text-white' : 'bg-white/5 text-gray-400'
              }`}
            >
              登录
            </button>
            <button
              type="button"
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2 text-center rounded-r-lg transition-colors ${
                !isLogin ? 'bg-brand-accent text-white' : 'bg-white/5 text-gray-400'
              }`}
            >
              注册
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">邮箱</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-brand-accent transition-colors"
                placeholder="请输入邮箱"
                autoComplete="email"
                required
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm text-gray-400 mb-1">用户名</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-brand-accent transition-colors"
                  placeholder="请输入用户名"
                  autoComplete="username"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-1">密码</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-brand-accent transition-colors"
                placeholder="请输入密码"
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                required
              />
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full accent-gradient text-white py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {loading ? '处理中...' : isLogin ? '登录' : '创建账号'}
            </button>
          </form>

          <p className="text-center text-xs text-gray-500 mt-4">
            免费注册即可每月使用 3 次品牌分析
          </p>
        </div>
      </div>
    </div>
  );
}
