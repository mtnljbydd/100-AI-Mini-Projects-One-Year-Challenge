"use client"

import * as React from "react"
import { Plus, Calendar } from "lucide-react"
import { Task, Priority, RecurringType, Project, PRIORITY_LABELS, RECURRING_LABELS } from "@/lib/types"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select"

interface TaskFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSubmit: (task: Omit<Task, "id" | "createdAt" | "completed">) => void
  projects: Project[]
  editingTask?: Task | null
  defaultProjectId?: string
}

export function TaskForm({
  open,
  onOpenChange,
  onSubmit,
  projects,
  editingTask,
  defaultProjectId = "inbox",
}: TaskFormProps) {
  const [title, setTitle] = React.useState("")
  const [description, setDescription] = React.useState("")
  const [priority, setPriority] = React.useState<Priority>("medium")
  const [dueDate, setDueDate] = React.useState("")
  const [projectId, setProjectId] = React.useState(defaultProjectId)
  const [recurring, setRecurring] = React.useState<RecurringType>("none")

  const inputRef = React.useRef<HTMLInputElement>(null)

  React.useEffect(() => {
    if (editingTask) {
      setTitle(editingTask.title)
      setDescription(editingTask.description || "")
      setPriority(editingTask.priority)
      setDueDate(editingTask.dueDate || "")
      setProjectId(editingTask.projectId)
      setRecurring(editingTask.recurring)
    } else {
      setTitle("")
      setDescription("")
      setPriority("medium")
      setDueDate("")
      setProjectId(defaultProjectId)
      setRecurring("none")
    }
  }, [editingTask, defaultProjectId, open])

  React.useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [open])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      dueDate: dueDate || undefined,
      projectId,
      recurring,
    })

    onOpenChange(false)
  }

  const selectedProject = projects.find((p) => p.id === projectId)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent onClose={() => onOpenChange(false)} className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{editingTask ? "编辑任务" : "添加新任务"}</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div>
            <Input
              ref={inputRef}
              placeholder="任务名称"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="text-base"
            />
          </div>

          <div>
            <textarea
              placeholder="描述（可选）"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="flex min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">优先级</label>
              <Select value={priority} onValueChange={(v) => setPriority(v as Priority)}>
                <SelectTrigger>
                  <span className="flex items-center gap-2">
                    <span
                      className={cn(
                        "w-2 h-2 rounded-full",
                        priority === "high" && "bg-destructive",
                        priority === "medium" && "bg-warning",
                        priority === "low" && "bg-success"
                      )}
                    />
                    {PRIORITY_LABELS[priority]}
                  </span>
                </SelectTrigger>
                <SelectContent>
                  {(["high", "medium", "low"] as Priority[]).map((p) => (
                    <SelectItem key={p} value={p}>
                      <span className="flex items-center gap-2">
                        <span
                          className={cn(
                            "w-2 h-2 rounded-full",
                            p === "high" && "bg-destructive",
                            p === "medium" && "bg-warning",
                            p === "low" && "bg-success"
                          )}
                        />
                        {PRIORITY_LABELS[p]}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">截止日期</label>
              <div className="relative">
                <Input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="pr-10"
                />
                <Calendar className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">项目</label>
              <Select value={projectId} onValueChange={setProjectId}>
                <SelectTrigger>
                  <span className="flex items-center gap-2">
                    <span
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: selectedProject?.color }}
                    />
                    {selectedProject?.name || "收件箱"}
                  </span>
                </SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.id} value={project.id}>
                      <span className="flex items-center gap-2">
                        <span
                          className="w-2 h-2 rounded-full"
                          style={{ backgroundColor: project.color }}
                        />
                        {project.name}
                      </span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-xs text-muted-foreground mb-1.5 block">重复</label>
              <Select value={recurring} onValueChange={(v) => setRecurring(v as RecurringType)}>
                <SelectTrigger>
                  {RECURRING_LABELS[recurring]}
                </SelectTrigger>
                <SelectContent>
                  {(["none", "daily", "weekly", "monthly"] as RecurringType[]).map((r) => (
                    <SelectItem key={r} value={r}>
                      {RECURRING_LABELS[r]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              取消
            </Button>
            <Button type="submit" disabled={!title.trim()}>
              <Plus className="h-4 w-4 mr-1" />
              {editingTask ? "保存" : "添加"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
