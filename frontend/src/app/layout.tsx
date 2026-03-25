import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RedditPulse - AI驱动的Reddit品牌舆情分析工具',
  description: '输入品牌关键词，自动抓取Reddit帖子，AI生成舆情分析报告、热帖摘要、子版块画像和营销策略建议。支持PDF/PPT/Word导出。',
  keywords: 'Reddit舆情分析,品牌监控,AI分析,Reddit营销,品牌出海,舆情监测',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
