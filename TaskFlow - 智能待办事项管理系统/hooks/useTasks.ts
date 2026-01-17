"use client"

import { useState, useEffect, useCallback } from "react"
import { Task, Project, DEFAULT_PROJECTS } from "@/lib/types"

const STORAGE_KEY_TASKS = "taskflow-tasks"
const STORAGE_KEY_PROJECTS = "taskflow-projects"

export function useTasks() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [projects, setProjects] = useState<Project[]>(DEFAULT_PROJECTS)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load from localStorage
  useEffect(() => {
    const storedTasks = localStorage.getItem(STORAGE_KEY_TASKS)
    const storedProjects = localStorage.getItem(STORAGE_KEY_PROJECTS)
    
    if (storedTasks) {
      setTasks(JSON.parse(storedTasks))
    }
    if (storedProjects) {
      setProjects(JSON.parse(storedProjects))
    }
    setIsLoaded(true)
  }, [])

  // Save to localStorage
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_TASKS, JSON.stringify(tasks))
    }
  }, [tasks, isLoaded])

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY_PROJECTS, JSON.stringify(projects))
    }
  }, [projects, isLoaded])

  const addTask = useCallback((task: Omit<Task, "id" | "createdAt" | "completed">) => {
    const newTask: Task = {
      ...task,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      completed: false,
    }
    setTasks((prev) => [newTask, ...prev])
    return newTask
  }, [])

  const updateTask = useCallback((id: string, updates: Partial<Task>) => {
    setTasks((prev) =>
      prev.map((task) => (task.id === id ? { ...task, ...updates } : task))
    )
  }, [])

  const deleteTask = useCallback((id: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== id))
  }, [])

  const toggleTask = useCallback((id: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== id) return task
        
        const completed = !task.completed
        let updatedTask = {
          ...task,
          completed,
          completedAt: completed ? new Date().toISOString() : undefined,
        }

        // Handle recurring tasks
        if (completed && task.recurring !== "none" && task.dueDate) {
          const dueDate = new Date(task.dueDate)
          let nextDate: Date

          switch (task.recurring) {
            case "daily":
              nextDate = new Date(dueDate.setDate(dueDate.getDate() + 1))
              break
            case "weekly":
              nextDate = new Date(dueDate.setDate(dueDate.getDate() + 7))
              break
            case "monthly":
              nextDate = new Date(dueDate.setMonth(dueDate.getMonth() + 1))
              break
            default:
              nextDate = dueDate
          }

          // Create a new recurring task
          setTimeout(() => {
            addTask({
              title: task.title,
              description: task.description,
              priority: task.priority,
              dueDate: nextDate.toISOString().split("T")[0],
              projectId: task.projectId,
              recurring: task.recurring,
            })
          }, 500)
        }

        return updatedTask
      })
    )
  }, [addTask])

  const addProject = useCallback((project: Omit<Project, "id">) => {
    const newProject: Project = {
      ...project,
      id: crypto.randomUUID(),
    }
    setProjects((prev) => [...prev, newProject])
    return newProject
  }, [])

  const deleteProject = useCallback((id: string) => {
    setProjects((prev) => prev.filter((p) => p.id !== id))
    // Move tasks to inbox
    setTasks((prev) =>
      prev.map((task) =>
        task.projectId === id ? { ...task, projectId: "inbox" } : task
      )
    )
  }, [])

  return {
    tasks,
    projects,
    isLoaded,
    addTask,
    updateTask,
    deleteTask,
    toggleTask,
    addProject,
    deleteProject,
  }
}
