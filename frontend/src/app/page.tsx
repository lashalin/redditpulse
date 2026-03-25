'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) setIsLoggedIn(true);
  }, []);

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-[#0d1117]/80 backdrop-blur-xl border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="text-xl font-bold">
            <span className="text-brand-accent">Reddit</span>
            <span className="text-white">Pulse</span>
          </div>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">核心功能</a>
            <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">使用流程</a>
            <a href="#pricing" className="text-sm text-gray-400 hover:text-white transition-colors">定价方案</a>
            {isLoggedIn ? (
              <Link href="/dashboard" className="accent-gradient px-5 py-2 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity">
                进入工作台
              </Link>
            ) : (
              <Link href="/login" className="accent-gradient px-5 py-2 rounded-lg text-sm font-semibold text-white hover:opacity-90 transition-opacity">
                免费开始
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-400 hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {mobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-white/5 bg-[#0d1117]/95 backdrop-blur-xl px-6 py-4 space-y-3">
            <a href="#features" onClick={() => setMobileMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-2">核心功能</a>
            <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-2">使用流程</a>
            <a href="#pricing" onClick={() => setMobileMenuOpen(false)} className="block text-sm text-gray-400 hover:text-white py-2">定价方案</a>
            <Link
              href={isLoggedIn ? '/dashboard' : '/login'}
              className="block text-center accent-gradient px-5 py-2 rounded-lg text-sm font-semibold text-white"
            >
              {isLoggedIn ? '进入工作台' : '免费开始'}
            </Link>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 relative overflow-hidden">
        {/* Background glow effects */}
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-brand-accent/10 rounded-full blur-[128px] pointer-events-none" />
        <div className="absolute top-40 left-1/4 w-[300px] h-[300px] bg-brand-light/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="max-w-4xl mx-auto text-center relative">
          <div className="inline-block px-4 py-1.5 rounded-full bg-brand-accent/10 border border-brand-accent/20 text-brand-accent text-sm font-medium mb-6 animate-pulse-accent">
            AI 驱动 · Reddit 品牌舆情分析
          </div>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold leading-tight mb-6">
            一键洞察你的品牌在
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-accent to-brand-light">Reddit</span> 上的真实口碑
          </h1>
          <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            输入品牌关键词，自动抓取Reddit帖子，AI生成舆情分析报告、热帖摘要、
            子版块画像和营销策略建议。告别手动翻帖，让数据为你说话。
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href={isLoggedIn ? '/dashboard' : '/login'}
              className="w-full sm:w-auto accent-gradient px-8 py-4 rounded-xl text-lg font-bold text-white hover:opacity-90 transition-opacity shadow-lg shadow-brand-accent/25"
            >
              {isLoggedIn ? '进入工作台' : '免费注册，立即体验'}
            </Link>
            <a href="#how-it-works" className="w-full sm:w-auto text-center px-8 py-4 rounded-xl text-lg font-medium text-gray-300 border border-white/10 hover:border-white/30 transition-colors">
              了解更多
            </a>
          </div>
          <p className="mt-4 text-sm text-gray-500">免费版每月 3 次分析 · 无需信用卡</p>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="py-8 border-y border-white/5">
        <div className="max-w-4xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6 px-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">100+</div>
            <div className="text-sm text-gray-500 mt-1">每次分析帖子数</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">5</div>
            <div className="text-sm text-gray-500 mt-1">AI分析维度</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">3</div>
            <div className="text-sm text-gray-500 mt-1">报告导出格式</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">&lt;2min</div>
            <div className="text-sm text-gray-500 mt-1">生成报告</div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">核心功能</h2>
            <p className="text-gray-400 max-w-xl mx-auto">从数据抓取到策略建议，一站式覆盖品牌出海的Reddit营销需求</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: '📊',
                title: '品牌舆情分析',
                desc: '基于VADER算法对每条帖子进行正面/负面/中性情感分析，可视化舆情分布，快速了解品牌口碑全貌',
                highlight: true,
              },
              {
                icon: '🤖',
                title: 'AI智能过滤',
                desc: '自动抓取Reddit帖子，AI精准过滤无关内容，只保留与你的品牌真正相关的高质量讨论',
                highlight: false,
              },
              {
                icon: '🔥',
                title: '热帖总结',
                desc: 'AI深度分析热门帖子的爆火原因、用户关注焦点、讨论趋势和品牌启示',
                highlight: false,
              },
              {
                icon: '💡',
                title: '营销建议',
                desc: '基于全面数据分析，生成Reddit营销策略、内容方向、最佳发帖时间和30天行动计划',
                highlight: true,
              },
              {
                icon: '📄',
                title: '报告导出',
                desc: '一键导出专业分析报告，支持PDF、PPT、Word三种格式，直接用于团队汇报和客户提案',
                highlight: false,
              },
              {
                icon: '🏷️',
                title: '话题聚类 & 子版块画像',
                desc: '自动聚类讨论话题，分析各子版块的用户构成和讨论风格，精准定位营销阵地',
                highlight: false,
              },
            ].map((f, i) => (
              <div key={i} className={`glass-card p-6 hover:border-brand-accent/30 transition-all duration-300 group ${f.highlight ? 'border-brand-accent/20' : ''}`}>
                <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">{f.icon}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-6 bg-white/[0.02]">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">三步完成品牌舆情分析</h2>
            <p className="text-gray-400">简单易用，无需技术背景</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: '输入品牌关键词',
                desc: '输入你的品牌名称或竞品关键词，选择时间范围（1个月~1年）',
              },
              {
                step: '02',
                title: 'AI自动分析',
                desc: '系统自动抓取Reddit帖子，进行情感分析、话题聚类和子版块画像',
              },
              {
                step: '03',
                title: '获取报告 & 策略',
                desc: '查看可视化分析报告，获取AI营销建议，一键导出PDF/PPT/Word',
              },
            ].map((s, i) => (
              <div key={i} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl accent-gradient text-white text-2xl font-bold mb-6 shadow-lg shadow-brand-accent/20">
                  {s.step}
                </div>
                <h3 className="text-lg font-semibold text-white mb-3">{s.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">简洁定价，按需选择</h2>
            <p className="text-gray-400">免费版即可体验完整功能，Pro版解锁无限分析</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
            {/* Free Plan */}
            <div className="glass-card p-8">
              <div className="text-sm text-gray-400 font-medium uppercase tracking-wider mb-2">免费版</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-white">&#165;0</span>
                <span className="text-gray-500">/月</span>
              </div>
              <p className="text-gray-500 text-sm mb-8">适合个人体验和小规模调研</p>
              <ul className="space-y-3 mb-8">
                {[
                  '每月 3 次品牌分析',
                  '每次抓取 100+ 帖子',
                  '完整AI分析报告',
                  '舆情情感分析',
                  '热帖摘要 & 话题聚类',
                  '导出 PDF / PPT / Word',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm text-gray-300">
                    <span className="text-green-400 text-lg flex-shrink-0">&#10003;</span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link
                href={isLoggedIn ? '/dashboard' : '/login'}
                className="block w-full text-center py-3 rounded-lg border border-white/10 text-white font-semibold hover:border-white/30 transition-colors"
              >
                免费注册
              </Link>
            </div>

            {/* Pro Plan */}
            <div className="glass-card p-8 border-brand-accent/50 relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-brand-accent text-white text-xs font-bold px-3 py-1 rounded-bl-lg">
                推荐
              </div>
              <div className="text-sm text-brand-accent font-medium uppercase tracking-wider mb-2">专业版 Pro</div>
              <div className="flex items-baseline gap-1 mb-1">
                <span className="text-4xl font-bold text-white">&#165;99</span>
                <span className="text-gray-500">/月</span>
              </div>
              <p className="text-gray-500 text-sm mb-8">适合品牌方和营销团队日常监控</p>
              <ul className="space-y-3 mb-8">
                {[
                  '无限次品牌分析',
                  '每次抓取 500+ 帖子',
                  '完整AI分析报告',
                  '高级舆情趋势追踪',
                  '竞品对比分析',
                  '优先导出 & 客服支持',
                  '团队协作（即将上线）',
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-sm text-gray-300">
                    <span className="text-brand-accent text-lg flex-shrink-0">&#10003;</span>
                    {item}
                  </li>
                ))}
              </ul>
              <Link
                href={isLoggedIn ? '/dashboard' : '/login?plan=pro'}
                className="block w-full text-center py-3 rounded-lg accent-gradient text-white font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-brand-accent/20"
              >
                立即升级
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6 bg-white/[0.02] relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-brand-accent/5 to-transparent pointer-events-none" />
        <div className="max-w-3xl mx-auto text-center relative">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            开始洞察你的品牌在Reddit上的口碑
          </h2>
          <p className="text-gray-400 mb-8 max-w-lg mx-auto">
            无论你是品牌方、营销团队还是独立开发者，RedditPulse都能帮你快速了解用户真实反馈
          </p>
          <Link
            href={isLoggedIn ? '/dashboard' : '/login'}
            className="inline-block accent-gradient px-10 py-4 rounded-xl text-lg font-bold text-white hover:opacity-90 transition-opacity shadow-lg shadow-brand-accent/25"
          >
            免费开始使用
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-sm text-gray-500">
            &copy; 2025 <span className="text-brand-accent">Reddit</span>Pulse. All rights reserved.
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <a href="#features" className="hover:text-white transition-colors">功能介绍</a>
            <a href="#pricing" className="hover:text-white transition-colors">定价方案</a>
            <Link href="/login" className="hover:text-white transition-colors">登录 / 注册</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
