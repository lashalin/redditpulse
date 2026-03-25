'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

interface AnalysisViewProps {
  monitor: any;
  snapshot: any;
  loading?: boolean;
  onExport: (type: string) => void;
}

type TabKey = 'overview' | 'hotposts' | 'topics' | 'subreddits' | 'advice';

export default function AnalysisView({
  monitor,
  snapshot,
  loading,
  onExport,
}: AnalysisViewProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('overview');

  if (loading) {
    return (
      <div className="glass-card p-12 text-center text-gray-400">
        <div className="inline-block w-10 h-10 border-2 border-brand-accent border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="text-xl mb-2">加载分析数据中...</p>
        <p>正在获取 &quot;{monitor.keyword}&quot; 的分析结果</p>
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div className="glass-card p-12 text-center text-gray-400">
        <div className="text-5xl mb-4">📭</div>
        <p className="text-xl mb-2">暂无分析数据</p>
        <p>请先运行分析任务</p>
      </div>
    );
  }

  const tabs: { key: TabKey; label: string; icon: string }[] = [
    { key: 'overview', label: '总览', icon: '📊' },
    { key: 'hotposts', label: '热帖摘要', icon: '🔥' },
    { key: 'topics', label: '话题聚类', icon: '🏷️' },
    { key: 'subreddits', label: '子版块分析', icon: '📋' },
    { key: 'advice', label: '营销建议', icon: '💡' },
  ];

  const dist = snapshot.sentiment_distribution || {};
  const subredditData = snapshot.subreddit_breakdown?.data || [];

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">
            「{monitor.keyword}」品牌舆情分析报告
          </h2>
          <p className="text-gray-400 mt-1">
            分析日期: {snapshot.snapshot_date} · 共抓取{' '}
            <span className="text-brand-accent font-semibold">
              {snapshot.total_posts}
            </span>{' '}
            条帖子
          </p>
        </div>
        <div className="flex gap-2">
          {['pdf', 'pptx', 'docx'].map((type) => (
            <button
              key={type}
              onClick={() => onExport(type)}
              className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-gray-300 hover:border-brand-accent hover:text-white transition-colors"
            >
              导出 {type.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-white/5 rounded-xl p-1">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? 'bg-brand-accent text-white'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="glass-card p-6">
        {/* ===== OVERVIEW TAB ===== */}
        {activeTab === 'overview' && (
          <div>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
              <StatCard label="帖子总数" value={snapshot.total_posts} />
              <StatCard
                label="平均舆情得分"
                value={snapshot.avg_sentiment?.toFixed(3) || 'N/A'}
                color={
                  snapshot.avg_sentiment > 0.05
                    ? 'text-green-400'
                    : snapshot.avg_sentiment < -0.05
                    ? 'text-red-400'
                    : 'text-yellow-400'
                }
              />
              <StatCard
                label="正面评价"
                value={`${dist.positive || 0}%`}
                color="text-green-400"
              />
              <StatCard
                label="中性评价"
                value={`${dist.neutral || 0}%`}
                color="text-gray-400"
              />
              <StatCard
                label="负面评价"
                value={`${dist.negative || 0}%`}
                color="text-red-400"
              />
            </div>

            {/* Sentiment Bar */}
            <div className="mb-8">
              <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                舆情分布可视化
              </h3>
              <div className="flex h-10 rounded-lg overflow-hidden">
                <div
                  style={{ width: `${dist.positive || 0}%` }}
                  className="bg-green-500 flex items-center justify-center text-xs font-bold text-white"
                >
                  {(dist.positive || 0) > 8
                    ? `正面 ${dist.positive}%`
                    : ''}
                </div>
                <div
                  style={{ width: `${dist.neutral || 0}%` }}
                  className="bg-gray-500 flex items-center justify-center text-xs font-bold text-white"
                >
                  {(dist.neutral || 0) > 8
                    ? `中性 ${dist.neutral}%`
                    : ''}
                </div>
                <div
                  style={{ width: `${dist.negative || 0}%` }}
                  className="bg-red-500 flex items-center justify-center text-xs font-bold text-white"
                >
                  {(dist.negative || 0) > 8
                    ? `负面 ${dist.negative}%`
                    : ''}
                </div>
              </div>
            </div>

            {/* Subreddit Breakdown Chart */}
            {subredditData.length > 0 && (
              <div className="mb-8">
                <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                  发帖频率最高的子版块 Top {Math.min(subredditData.length, 10)}
                </h3>
                <div className="space-y-3">
                  {subredditData
                    .slice(0, 10)
                    .map((sub: any, i: number) => (
                      <div key={i} className="flex items-center gap-3">
                        <span className="text-brand-accent font-mono text-sm w-44 truncate">
                          r/{sub.name}
                        </span>
                        <div className="flex-1 bg-white/5 rounded-full h-7 overflow-hidden">
                          <div
                            className="h-full accent-gradient rounded-full flex items-center pl-3 transition-all duration-500"
                            style={{
                              width: `${Math.max(
                                Math.min(
                                  (sub.post_count /
                                    (subredditData[0]?.post_count || 1)) *
                                    100,
                                  100
                                ),
                                8
                              )}%`,
                            }}
                          >
                            <span className="text-xs text-white font-semibold">
                              {sub.post_count} 条帖子
                            </span>
                          </div>
                        </div>
                        <span
                          className={`text-xs w-20 text-right ${
                            sub.avg_sentiment > 0.05
                              ? 'text-green-400'
                              : sub.avg_sentiment < -0.05
                              ? 'text-red-400'
                              : 'text-gray-400'
                          }`}
                        >
                          舆情: {sub.avg_sentiment?.toFixed(2)}
                        </span>
                        {sub.subscriber_count && (
                          <span className="text-xs text-gray-500 w-24 text-right">
                            {sub.subscriber_count >= 1000000
                              ? `${(sub.subscriber_count / 1000000).toFixed(1)}M`
                              : sub.subscriber_count >= 1000
                              ? `${(sub.subscriber_count / 1000).toFixed(0)}K`
                              : sub.subscriber_count}{' '}
                            订阅
                          </span>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Quick Insight */}
            <div className="bg-white/5 rounded-lg p-4 border-l-4 border-brand-accent">
              <h3 className="font-semibold text-white mb-2">📝 快速洞察</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                在过去分析的 <strong>{snapshot.total_posts}</strong> 条Reddit帖子中，
                品牌「{monitor.keyword}」的整体舆情
                {snapshot.avg_sentiment > 0.05
                  ? '偏正面，社区反馈积极'
                  : snapshot.avg_sentiment < -0.05
                  ? '偏负面，需要关注社区痛点'
                  : '中性，社区讨论较为客观'}
                。正面评价占 <strong>{dist.positive || 0}%</strong>，
                负面评价占 <strong>{dist.negative || 0}%</strong>。
                讨论主要集中在{' '}
                <strong>
                  {subredditData
                    .slice(0, 3)
                    .map((s: any) => `r/${s.name}`)
                    .join('、') || '多个子版块'}
                </strong>
                。点击上方标签页查看详细分析。
              </p>
            </div>
          </div>
        )}

        {/* ===== HOT POSTS TAB ===== */}
        {activeTab === 'hotposts' && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              🔥 热门帖子分析摘要
            </h3>
            <div className="markdown-content">
              <ReactMarkdown>
                {snapshot.hot_posts?.raw || '暂无热帖数据'}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* ===== TOPICS TAB ===== */}
        {activeTab === 'topics' && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              🏷️ 话题聚类分析
            </h3>
            <div className="markdown-content">
              <ReactMarkdown>
                {snapshot.top_topics?.raw || '暂无话题数据'}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {/* ===== SUBREDDITS TAB ===== */}
        {activeTab === 'subreddits' && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              📋 子版块详细分析
            </h3>
            <div className="markdown-content">
              <ReactMarkdown>
                {snapshot.subreddit_breakdown?.profiles || '暂无子版块数据'}
              </ReactMarkdown>
            </div>

            {/* Subreddit data table */}
            {subredditData.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                  子版块数据概览
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/20">
                        <th className="text-left p-3 text-brand-accent font-semibold">
                          子版块
                        </th>
                        <th className="text-right p-3 text-brand-accent font-semibold">
                          帖子数
                        </th>
                        <th className="text-right p-3 text-brand-accent font-semibold">
                          订阅数
                        </th>
                        <th className="text-right p-3 text-brand-accent font-semibold">
                          平均舆情
                        </th>
                        <th className="text-left p-3 text-brand-accent font-semibold">
                          热门标题
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {subredditData.map((sub: any, i: number) => (
                        <tr
                          key={i}
                          className="border-b border-white/5 hover:bg-white/5"
                        >
                          <td className="p-3">
                            <a
                              href={`https://reddit.com/r/${sub.name}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-brand-accent hover:underline"
                            >
                              r/{sub.name}
                            </a>
                          </td>
                          <td className="p-3 text-right text-white font-semibold">
                            {sub.post_count}
                          </td>
                          <td className="p-3 text-right text-gray-400">
                            {sub.subscriber_count
                              ? sub.subscriber_count >= 1000000
                                ? `${(sub.subscriber_count / 1000000).toFixed(1)}M`
                                : sub.subscriber_count >= 1000
                                ? `${(sub.subscriber_count / 1000).toFixed(0)}K`
                                : sub.subscriber_count
                              : '-'}
                          </td>
                          <td className="p-3 text-right">
                            <span
                              className={
                                sub.avg_sentiment > 0.05
                                  ? 'text-green-400'
                                  : sub.avg_sentiment < -0.05
                                  ? 'text-red-400'
                                  : 'text-gray-400'
                              }
                            >
                              {sub.avg_sentiment?.toFixed(3)}
                            </span>
                          </td>
                          <td className="p-3 text-gray-300 max-w-xs truncate">
                            {sub.sample_titles?.[0] || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ===== MARKETING ADVICE TAB ===== */}
        {activeTab === 'advice' && (
          <div>
            <h3 className="text-lg font-semibold text-white mb-4">
              💡 AI营销策略建议
            </h3>
            <div className="markdown-content">
              <ReactMarkdown>
                {snapshot.marketing_advice?.raw || '暂无营销建议'}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  color = 'text-white',
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="bg-white/5 rounded-lg p-4 text-center">
      <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">
        {label}
      </p>
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
    </div>
  );
}
