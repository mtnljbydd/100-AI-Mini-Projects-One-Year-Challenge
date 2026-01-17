"use client"

import * as React from "react"
import { format, isToday, isPast, parseISO } from "date-fns"
import { zhCN } from "date-fns/locale"
import { Trash2, Calendar, RefreshCw, Edit2 } from "lucide-react"
import { Task, PRIORITY_LABELS, RECURRING_LABELS } from "@/lib/types"
import { cn } from "@/lib/utils"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface TaskItemProps {
  task: Task
  onToggle: (id: string) => void
  onDelete: (id: string) => void
  onEdit: (task: Task) => void
  projectColor?: string
}

export function TaskItem({ task, onToggle, onDelete, onEdit, projectColor }: TaskItemProps) {
  const [isDeleting, setIsDeleting] = React.useState(false)

  const isOverdue = task.dueDate && !task.completed && isPast(parseISO(task.dueDate)) && !isToday(parseISO(task.dueDate))
  const isDueToday = task.dueDate && isToday(parseISO(task.dueDate))

  const handleDelete = () => {
    setIsDeleting(true)
    setTimeout(() => onDelete(task.id), 300)
  }

  return (
    <div
      className={cn(
        "group flex items-start gap-3 rounded-lg border bg-card p-4 transition-all duration-300",
        task.completed && "opacity-60",
        isOverdue && "border-l-4 border-l-destructive",
        isDueToday && !task.completed && "border-l-4 border-l-primary",
        isDeleting && "opacity-0 translate-x-4"
      )}
      style={{ borderLeftColor: !isOverdue && !isDueToday ? projectColor : undefined }}
    >
      <div className="pt-0.5">
        <Checkbox
          checked={task.completed}
          onCheckedChange={() => onToggle(task.id)}
          className={cn(task.completed && "animate-check-bounce")}
        />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3
              className={cn(
                "font-medium text-foreground transition-all duration-300",
                task.completed && "line-through text-muted-foreground"
              )}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                {task.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => onEdit(task)}
            >
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive hover:text-destructive"
              onClick={handleDelete}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="mt-2 flex flex-wrap items-center gap-2">
          <Badge variant={task.priority}>{PRIORITY_LABELS[task.priority]}</Badge>
          
          {task.dueDate && (
            <span
              className={cn(
                "inline-flex items-center gap-1 text-xs",
                isOverdue && "text-destructive font-medium",
                isDueToday && !task.completed && "text-primary font-medium",
                !isOverdue && !isDueToday && "text-muted-foreground"
              )}
            >
              <Calendar className="h-3 w-3" />
              {isDueToday
                ? "今天"
                : format(parseISO(task.dueDate), "M月d日", { locale: zhCN })}
              {isOverdue && " (已过期)"}
            </span>
          )}

          {task.recurring !== "none" && (
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <RefreshCw className="h-3 w-3" />
              {RECURRING_LABELS[task.recurring]}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
