"use client"

import * as React from "react"
import { isToday, parseISO, isPast } from "date-fns"
import { Plus, Search, Menu, X, Filter, SortAsc } from "lucide-react"
import { Task } from "@/lib/types"
import { cn } from "@/lib/utils"
import { useTasks } from "@/hooks/useTasks"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TaskItem } from "@/components/task-item"
import { TaskForm } from "@/components/task-form"
import { Sidebar } from "@/components/sidebar"
import { ToastProvider, useToast } from "@/components/ui/toast"

function TodoApp() {
  const {
    tasks,
    projects,
    isLoaded,
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    addProject,
    deleteProject,
  } = useTasks()

  const { addToast } = useToast()

  const [activeView, setActiveView] = React.useState("today")
  const [showTaskForm, setShowTaskForm] = React.useState(false)
  const [editingTask, setEditingTask] = React.useState<Task | null>(null)
  const [searchQuery, setSearchQuery] = React.useState("")
  const [showMobileSidebar, setShowMobileSidebar] = React.useState(false)
  const [quickInput, setQuickInput] = React.useState("")
  const [sortBy, setSortBy] = React.useState<"priority" | "date" | "created">("priority")

  const quickInputRef = React.useRef<HTMLInputElement>(null)

  // Keyboard shortcuts
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K for search focus
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault()
        document.getElementById("search-input")?.focus()
      }
      // N for new task (when not in input)
      if (e.key === "n" && !["INPUT", "TEXTAREA"].includes((e.target as HTMLElement)?.tagName)) {
        e.preventDefault()
        setShowTaskForm(true)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  // Filter and sort tasks
  const filteredTasks = React.useMemo(() => {
    let result = tasks.filter((task) => {
      // Filter by view
      if (activeView === "today") {
        return task.dueDate && isToday(parseISO(task.dueDate)) && !task.completed
      }
      if (activeView === "all") {
        return true
      }
      return task.projectId === activeView
    })

    // Filter by search
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (task) =>
          task.title.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query)
      )
    }

    // Sort
    result.sort((a, b) => {
      // Completed tasks at bottom
      if (a.completed !== b.completed) return a.completed ? 1 : -1

      if (sortBy === "priority") {
        const priorityOrder = { high: 0, medium: 1, low: 2 }
        return priorityOrder[a.priority] - priorityOrder[b.priority]
      }
      if (sortBy === "date") {
        if (!a.dueDate) return 1
        if (!b.dueDate) return -1
        return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
      }
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    })

    return result
  }, [tasks, activeView, searchQuery, sortBy])

  // Calculate task counts
  const taskCounts = React.useMemo(() => {
    const counts: Record<string, number> = {}
    tasks.forEach((task) => {
      if (!task.completed) {
        counts[task.projectId] = (counts[task.projectId] || 0) + 1
      }
    })
    return counts
  }, [tasks])

  const todayCount = React.useMemo(() => {
    return tasks.filter(
      (task) => task.dueDate && isToday(parseISO(task.dueDate)) && !task.completed
    ).length
  }, [tasks])

  const overdueCount = React.useMemo(() => {
    return tasks.filter(
      (task) =>
        task.dueDate &&
        !task.completed &&
        isPast(parseISO(task.dueDate)) &&
        !isToday(parseISO(task.dueDate))
    ).length
  }, [tasks])

  // Quick add task
  const handleQuickAdd = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && quickInput.trim()) {
      addTask({
        title: quickInput.trim(),
        priority: "medium",
        projectId: activeView !== "today" && activeView !== "all" ? activeView : "inbox",
        recurring: "none",
        dueDate: activeView === "today" ? new Date().toISOString().split("T")[0] : undefined,
      })
      setQuickInput("")
      addToast("任务已添加", "success")
    }
  }

  const handleTaskSubmit = (taskData: Omit<Task, "id" | "createdAt" | "completed">) => {
    if (editingTask) {
      updateTask(editingTask.id, taskData)
      addToast("任务已更新", "success")
    } else {
      addTask(taskData)
      addToast("任务已添加", "success")
    }
    setEditingTask(null)
  }

  const handleToggle = (id: string) => {
    const task = tasks.find((t) => t.id === id)
    toggleTask(id)
    if (task && !task.completed) {
      addToast("做得好！任务已完成", "success")
    }
  }

  const handleDelete = (id: string) => {
    deleteTask(id)
    addToast("任务已删除", "info")
  }

  const handleEdit = (task: Task) => {
    setEditingTask(task)
    setShowTaskForm(true)
  }

  const getViewTitle = () => {
    if (activeView === "today") return "今天"
    if (activeView === "all") return "全部任务"
    return projects.find((p) => p.id === activeView)?.name || "任务"
  }

  const getActiveProject = () => {
    return projects.find((p) => p.id === activeView)
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <span className="text-muted-foreground">加载中...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 border-r bg-card">
        <Sidebar
          projects={projects}
          activeView={activeView}
          onViewChange={setActiveView}
          onAddProject={addProject}
          onDeleteProject={deleteProject}
          taskCounts={taskCounts}
          todayCount={todayCount}
        />
      </div>

      {/* Mobile Sidebar Overlay */}
      {showMobileSidebar && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setShowMobileSidebar(false)}
          />
          <div className="absolute left-0 top-0 bottom-0 w-64 bg-card border-r shadow-lg animate-slide-in">
            <Sidebar
              projects={projects}
              activeView={activeView}
              onViewChange={setActiveView}
              onAddProject={addProject}
              onDeleteProject={deleteProject}
              taskCounts={taskCounts}
              todayCount={todayCount}
              onClose={() => setShowMobileSidebar(false)}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card/50 backdrop-blur-sm">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={() => setShowMobileSidebar(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <div>
                <h1 className="text-xl font-bold text-foreground">{getViewTitle()}</h1>
                {overdueCount > 0 && activeView === "today" && (
                  <p className="text-sm text-destructive">
                    {overdueCount} 个过期任务需要处理
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="relative hidden sm:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="search-input"
                  placeholder="搜索任务... (Ctrl+K)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-48 lg:w-64 pl-9"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    <X className="h-4 w-4 text-muted-foreground hover:text-foreground" />
                  </button>
                )}
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSortBy(sortBy === "priority" ? "date" : sortBy === "date" ? "created" : "priority")}
                title={`排序: ${sortBy === "priority" ? "优先级" : sortBy === "date" ? "截止日期" : "创建时间"}`}
              >
                <SortAsc className="h-5 w-5" />
              </Button>

              <Button onClick={() => setShowTaskForm(true)}>
                <Plus className="h-4 w-4 mr-1" />
                <span className="hidden sm:inline">添加任务</span>
              </Button>
            </div>
          </div>

          {/* Mobile Search */}
          <div className="px-4 pb-3 sm:hidden">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索任务..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
        </header>

        {/* Task List */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-4">
          {/* Quick Add */}
          <div className="mb-4">
            <div className="relative">
              <Plus className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                ref={quickInputRef}
                placeholder="快速添加任务，按 Enter 确认..."
                value={quickInput}
                onChange={(e) => setQuickInput(e.target.value)}
                onKeyDown={handleQuickAdd}
                className="pl-9"
              />
            </div>
          </div>

          {/* Tasks */}
          <div className="space-y-2">
            {filteredTasks.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">
                  {activeView === "today" ? "🎯" : "📝"}
                </div>
                <h3 className="text-lg font-medium text-foreground mb-1">
                  {searchQuery ? "未找到匹配的任务" : "还没有任务"}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {searchQuery
                    ? "尝试其他搜索关键词"
                    : activeView === "today"
                    ? "今天没有待办事项，享受美好的一天！"
                    : "点击上方按钮添加新任务"}
                </p>
              </div>
            ) : (
              filteredTasks.map((task) => (
                <TaskItem
                  key={task.id}
                  task={task}
                  onToggle={handleToggle}
                  onDelete={handleDelete}
                  onEdit={handleEdit}
                  projectColor={getActiveProject()?.color || projects.find((p) => p.id === task.projectId)?.color}
                />
              ))
            )}
          </div>
        </div>

        {/* Stats Footer */}
        <footer className="border-t bg-card/50 px-4 py-2">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {filteredTasks.filter((t) => !t.completed).length} 个待完成任务
            </span>
            <span>
              {filteredTasks.filter((t) => t.completed).length} 个已完成
            </span>
          </div>
        </footer>
      </main>

      {/* Task Form Dialog */}
      <TaskForm
        open={showTaskForm}
        onOpenChange={(open) => {
          setShowTaskForm(open)
          if (!open) setEditingTask(null)
        }}
        onSubmit={handleTaskSubmit}
        projects={projects}
        editingTask={editingTask}
        defaultProjectId={activeView !== "today" && activeView !== "all" ? activeView : "inbox"}
      />
    </div>
  )
}

export default function Home() {
  return (
    <ToastProvider>
      <TodoApp />
    </ToastProvider>
  )
}
