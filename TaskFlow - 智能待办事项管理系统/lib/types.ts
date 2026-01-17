export type Priority = "high" | "medium" | "low"

export type RecurringType = "none" | "daily" | "weekly" | "monthly"

export interface Task {
  id: string
  title: string
  description?: string
  completed: boolean
  priority: Priority
  dueDate?: string
  projectId: string
  recurring: RecurringType
  createdAt: string
  completedAt?: string
}

export interface Project {
  id: string
  name: string
  color: string
  icon?: string
}

export const DEFAULT_PROJECTS: Project[] = [
  { id: "inbox", name: "收件箱", color: "#6366f1" },
  { id: "work", name: "工作", color: "#f59e0b" },
  { id: "personal", name: "个人", color: "#10b981" },
]

export const PRIORITY_LABELS: Record<Priority, string> = {
  high: "高优先级",
  medium: "中优先级",
  low: "低优先级",
}

export const RECURRING_LABELS: Record<RecurringType, string> = {
  none: "不重复",
  daily: "每天",
  weekly: "每周",
  monthly: "每月",
}
