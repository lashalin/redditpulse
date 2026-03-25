import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Reddit品牌舆情分析工具',
  description: 'AI驱动的Reddit品牌舆情分析平台',
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
