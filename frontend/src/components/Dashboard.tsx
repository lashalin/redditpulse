'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  getMonitors,
  deleteMonitor,
  runAnalysis,
  checkTaskStatus,
  getSnapshot,
  generateReport,
  checkReportStatus,
  getDownloadUrl,
} from '@/lib/api';
import AnalysisView from '@/components/AnalysisView';

interface DashboardProps {
  user: any;
  onLogout: () => void;
}

export default function Dashboard({ user, onLogout }: DashboardProps) {
  const [keyword, setKeyword] = useState('');
  const [timeRange, setTimeRange] = useState('3m');
  const [monitors, setMonitors] = useState<any[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [progress, setProgress] = useState('');
  const [progressStage, setProgressStage] = useState('');
  const [selectedMonitor, setSelectedMonitor] = useState<any>(null);
  const [snapshot, setSnapshot] = useState<any>(null);
  const [error, setError] = useState('');
  const [loadingSnapshot, setLoadingSnapshot] = useState(false);

  useEffect(() => {
    loadMonitors();
  }, []);

  // Poll task status
  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      try {
        const status = await checkTaskStatus(taskId);
        if (status.status === 'SUCCESS') {
          setAnalyzing(false);
          setTaskId(null);
          setProgress('');
          setProgressStage('');
          // Reload monitors and auto-open the result
          const updatedMonitors = await loadMonitors();
          // Find the monitor matching current keyword and auto-view it
          if (status.result?.monitor_id) {
            const monitor = updatedMonitors?.find(
              (m: any) => m.id === status.result.monitor_id
            );
            if (monitor) {
              handleViewAnalysis(monitor);
            }
          }
        } else if (status.status === 'FAILURE') {
          setAnalyzing(false);
          setTaskId(null);
          setProgress('');
          setProgressStage('');
          setError(`分析失败: ${status.result || '未知错误'}`);
        } else {
          // Update progress based on status
          const stageMap: Record<string, string> = {
            CRAWLING: '正在抓取Reddit帖子...',
            ANALYZING: '正在进行AI分析...',
          };
          setProgressStage(stageMap[status.status] || status.status);
        }
      } catch {
        // Keep polling
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [taskId]);

  const loadMonitors = async () => {
    try {
      const data = await getMonitors();
      setMonitors(data);
      return data;
    } catch (err: any) {
      console.error('Failed to load monitors:', err);
      return [];
    }
  };

  const handleKeywordChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setKeyword(e.target.value);
    },
    []
  );

  const handleTimeRangeChange = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      setTimeRange(e.target.value);
    },
    []
  );

  const handleAnalyze = async () => {
    if (!keyword.trim()) return;
    setError('');
    setAnalyzing(true);
    setProgress('提交分析任务...');
    setProgressStage('');

    try {
      const result = await runAnalysis(keyword.trim(), timeRange);
      setTaskId(result.task_id);
      setProgress('分析任务已启动');
      setProgressStage('正在抓取Reddit帖子...');
    } catch (err: any) {
      setAnalyzing(false);
      setProgress('');
      setError(err.message);
    }
  };

  const handleViewAnalysis = async (monitor: any) => {
    setSelectedMonitor(monitor);
    setLoadingSnapshot(true);
    try {
      const data = await getSnapshot(monitor.id);
      setSnapshot(data);
    } catch {
      setSnapshot(null);
    } finally {
      setLoadingSnapshot(false);
    }
  };

  const handleDeleteMonitor = async (
    e: React.MouseEvent,
    monitorId: number
  ) => {
    e.stopPropagation();
    try {
      await deleteMonitor(monitorId);
      loadMonitors();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleExport = async (reportType: string) => {
    if (!selectedMonitor) return;
    setError('');
    setProgress(`正在生成 ${reportType.toUpperCase()} 报告...`);
    try {
      const result = await generateReport(selectedMonitor.id, reportType);
      const pollReport = setInterval(async () => {
        try {
          const status = await checkReportStatus(result.id);
          if (status.status === 'completed') {
            clearInterval(pollReport);
            setProgress('');
            const url = getDownloadUrl(result.id);
            window.open(url, '_blank');
          } else if (status.status === 'failed') {
            clearInterval(pollReport);
            setProgress('');
            setError('报告生成失败，请重试');
          }
        } catch {
          clearInterval(pollReport);
          setProgress('');
          setError('检查报告状态失败');
        }
      }, 2000);
      setTimeout(() => clearInterval(pollReport), 60000);
    } catch (err: any) {
      setProgress('');
      setError(err.message);
    }
  };

  const handleBack = () => {
    setSelectedMonitor(null);
    setSnapshot(null);
    setError('');
    setProgress('');
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1
            className="text-2xl font-bold cursor-pointer"
            onClick={handleBack}
          >
            <span className="text-brand-accent">Reddit</span> 品牌舆情分析
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              {user.username} | {user.plan_tier.toUpperCase()} | 用量:{' '}
              {user.monthly_analysis_used}/{user.monthly_analysis_limit}
            </span>
            <button
              onClick={onLogout}
              className="text-sm text-gray-400 hover:text-white transition-colors"
            >
              退出登录
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-6">
        {/* Search Bar - always visible */}
        <div className="glass-card p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">
            {selectedMonitor ? '新建分析' : '品牌舆情分析'}
          </h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={keyword}
              onChange={handleKeywordChange}
              placeholder="输入品牌名称或关键词，如 Anker、ChatGPT、Tesla..."
              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-brand-accent"
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
            />
            <select
              value={timeRange}
              onChange={handleTimeRangeChange}
              className="bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-brand-accent"
            >
              <option value="1m">过去1个月</option>
              <option value="3m">过去3个月</option>
              <option value="6m">过去6个月</option>
              <option value="1y">过去1年</option>
              <option value="all">全部时间</option>
            </select>
            <button
              onClick={handleAnalyze}
              disabled={analyzing || !keyword.trim()}
              className="accent-gradient px-8 py-3 rounded-lg font-semibold text-white hover:opacity-90 disabled:opacity-50 transition-opacity whitespace-nowrap"
            >
              {analyzing ? '分析中...' : '开始分析'}
            </button>
          </div>

          {/* Progress indicator */}
          {analyzing && (
            <div className="mt-4 p-4 bg-white/5 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-5 h-5 border-2 border-brand-accent border-t-transparent rounded-full animate-spin"></div>
                <span className="text-brand-accent font-medium">
                  {progress}
                </span>
              </div>
              {progressStage && (
                <p className="text-sm text-gray-400 ml-8">{progressStage}</p>
              )}
              <p className="text-xs text-gray-500 ml-8 mt-1">
                预计需要1-2分钟，请耐心等待...
              </p>
            </div>
          )}

          {!analyzing && progress && (
            <p className="mt-3 text-sm text-brand-accent">{progress}</p>
          )}
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
        </div>

        {/* Analysis View - when a monitor is selected */}
        {selectedMonitor && (
          <div>
            <button
              onClick={handleBack}
              className="mb-4 text-gray-400 hover:text-white transition-colors flex items-center gap-2"
            >
              <span>&larr;</span> 返回监控列表
            </button>

            <AnalysisView
              monitor={selectedMonitor}
              snapshot={snapshot}
              loading={loadingSnapshot}
              onExport={handleExport}
            />
          </div>
        )}

        {/* Monitor List - when no monitor selected */}
        {!selectedMonitor && !analyzing && (
          <div>
            <h2 className="text-lg font-semibold mb-4 text-gray-300">
              历史分析记录
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {monitors.map((monitor) => (
                <div
                  key={monitor.id}
                  className="stat-card cursor-pointer hover:border-brand-accent/50"
                  onClick={() => handleViewAnalysis(monitor)}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold text-white">
                      {monitor.keyword}
                    </h3>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-1 rounded-full ${
                          monitor.status === 'active'
                            ? 'bg-green-500/20 text-green-400'
                            : monitor.status === 'crawling' ||
                              monitor.status === 'analyzing'
                            ? 'bg-blue-500/20 text-blue-400 animate-pulse'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}
                      >
                        {monitor.status === 'active'
                          ? '已完成'
                          : monitor.status === 'crawling'
                          ? '抓取中'
                          : monitor.status === 'analyzing'
                          ? '分析中'
                          : monitor.status}
                      </span>
                      <button
                        onClick={(e) => handleDeleteMonitor(e, monitor.id)}
                        className="text-gray-600 hover:text-red-400 transition-colors text-sm"
                        title="删除"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                  <div className="text-sm text-gray-400 space-y-1">
                    <p>帖子数: {monitor.total_posts || 0}</p>
                    <p>
                      时间范围:{' '}
                      {
                        {
                          '1m': '过去1个月',
                          '3m': '过去3个月',
                          '6m': '过去6个月',
                          '1y': '过去1年',
                          all: '全部时间',
                        }[monitor.time_range] || monitor.time_range
                      }
                    </p>
                    <p>
                      最后分析:{' '}
                      {monitor.last_crawled_at
                        ? new Date(monitor.last_crawled_at).toLocaleString(
                            'zh-CN'
                          )
                        : '暂无'}
                    </p>
                  </div>
                  <div className="mt-3 text-xs text-brand-accent">
                    点击查看分析详情 &rarr;
                  </div>
                </div>
              ))}

              {monitors.length === 0 && (
                <div className="col-span-full text-center py-16 text-gray-500">
                  <div className="text-5xl mb-4">📊</div>
                  <p className="text-xl mb-2">暂无分析记录</p>
                  <p>在上方输入品牌关键词（如 Anker），点击"开始分析"</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
