import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TaskFlow - 智能待办事项管理',
  description: '现代化的在线待办事项管理系统，简洁高效，助您高效管理日常任务',
  keywords: ['待办事项', '任务管理', '日程规划', 'todo', 'task manager'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
