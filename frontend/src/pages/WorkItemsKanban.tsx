import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { ArrowLeft, Plus, AlertCircle } from 'lucide-react'
import { ProjectSelector } from '../components/ProjectSelector'

interface WorkItem {
  id: string
  title: string
  type: string
  status: string
  priority: string
  project_id: string
  assigned_to?: string
}

interface Column {
  id: string
  title: string
  status: string
  color: string
}

const STORAGE_KEY = 'kanban_selected_project'

const columns: Column[] = [
  { id: 'draft', title: 'Draft', status: 'draft', color: 'bg-gray-100' },
  { id: 'in_review', title: 'In Review', status: 'in_review', color: 'bg-blue-100' },
  { id: 'approved', title: 'Approved', status: 'approved', color: 'bg-green-100' },
  { id: 'rejected', title: 'Rejected', status: 'rejected', color: 'bg-red-100' },
  { id: 'in_progress', title: 'In Progress', status: 'in_progress', color: 'bg-yellow-100' },
  { id: 'done', title: 'Done', status: 'done', color: 'bg-purple-100' },
]

export default function WorkItemsKanban() {
  const [workItems, setWorkItems] = useState<WorkItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [draggedItem, setDraggedItem] = useState<string | null>(null)
  const [dragOverColumn, setDragOverColumn] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<string | null>(() => {
    return localStorage.getItem(STORAGE_KEY) || null
  })

  useEffect(() => {
    loadWorkItems()
  }, [])

  const loadWorkItems = async () => {
    try {
      setLoading(true)
      const response = await api.get('/work-items')
      setWorkItems(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load work items')
    } finally {
      setLoading(false)
    }
  }

  const handleDragStart = (e: React.DragEvent, itemId: string) => {
    setDraggedItem(itemId)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragEnd = () => {
    setDraggedItem(null)
    setDragOverColumn(null)
  }

  const handleDragOver = (e: React.DragEvent, columnStatus: string) => {
    e.preventDefault()
    
    if (!draggedItem) return
    
    const workItem = workItems.find(item => item.id === draggedItem)
    if (!workItem) return
    
    // Check if valid transition
    const isValid = canTransition(workItem.status, columnStatus)
    
    if (isValid) {
      e.dataTransfer.dropEffect = 'move'
      setDragOverColumn(columnStatus)
    } else {
      e.dataTransfer.dropEffect = 'none'
      setDragOverColumn(null)
    }
  }

  const handleDragLeave = () => {
    setDragOverColumn(null)
  }

  const canTransition = (currentStatus: string, newStatus: string): boolean => {
    const transitions: Record<string, string[]> = {
      'draft': ['in_review'],
      'in_review': ['approved', 'rejected'],
      'approved': ['in_progress'],
      'rejected': ['draft'],
      'in_progress': ['done'],
      'done': [] // Final state
    }
    
    return transitions[currentStatus]?.includes(newStatus) || false
  }

  const handleDrop = async (e: React.DragEvent, newStatus: string) => {
    e.preventDefault()
    
    if (!draggedItem) return

    const workItem = workItems.find(item => item.id === draggedItem)
    if (!workItem) return

    const currentStatus = workItem.status
    
    // Check if same status
    if (currentStatus === newStatus) {
      setDraggedItem(null)
      return
    }
    
    // Validate transition
    if (!canTransition(currentStatus, newStatus)) {
      alert(`❌ Cannot move from "${currentStatus.replace('_', ' ')}" to "${newStatus.replace('_', ' ')}"`)
      setDraggedItem(null)
      return
    }

    try {
      console.log('🔄 Kanban: Transitioning', draggedItem, 'from', currentStatus, 'to', newStatus)
      
      // Update work item status
      await api.post(`/work-items/${draggedItem}/transition`, {
        new_status: newStatus
      })
      
      console.log('✅ Kanban: Transition successful')
      
      // Reload work items
      await loadWorkItems()
      
      setDraggedItem(null)
    } catch (err: any) {
      console.error('❌ Kanban: Failed to update status:', err)
      const errorMsg = err.response?.data?.detail || 'Failed to update work item'
      alert(`❌ ${errorMsg}`)
      setDraggedItem(null)
    }
  }

  const handleProjectChange = (projectId: string | null) => {
    setSelectedProject(projectId)
    if (projectId) {
      localStorage.setItem(STORAGE_KEY, projectId)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  const getItemsByStatus = (status: string) => {
    const filtered = selectedProject 
      ? workItems.filter(item => item.project_id === selectedProject)
      : workItems
    return filtered.filter(item => item.status === status)
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'border-l-4 border-red-500',
      high: 'border-l-4 border-orange-500',
      medium: 'border-l-4 border-yellow-500',
      low: 'border-l-4 border-green-500',
    }
    return colors[priority] || 'border-l-4 border-gray-300'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/work-items" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Kanban Board</h1>
            <p className="text-gray-600">Drag and drop to change status</p>
          </div>
        </div>
        <Link to="/work-items/new" className="btn-primary flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>New Work Item</span>
        </Link>
      </div>

      {/* Project Selector */}
      <div className="card">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700 whitespace-nowrap">
            Filter by Project:
          </label>
          <div className="flex-1 max-w-md">
            <ProjectSelector
              value={selectedProject || undefined}
              onChange={handleProjectChange}
              allowAll={false}
              placeholder="Select a project to view Kanban"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Require project selection */}
      {!selectedProject ? (
        <div className="card bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900">Project Selection Required</h3>
              <p className="text-blue-700 mt-1">
                Please select a project above to view and manage work items in the Kanban board.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map(column => {
          const items = getItemsByStatus(column.status)
          const isValidDropZone = draggedItem ? (() => {
            const item = workItems.find(i => i.id === draggedItem)
            return item ? canTransition(item.status, column.status) : false
          })() : false
          const isDragOver = dragOverColumn === column.status
          
          return (
            <div
              key={column.id}
              className="flex-shrink-0 w-80"
              onDragOver={(e) => handleDragOver(e, column.status)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, column.status)}
            >
              {/* Column Header */}
              <div className={`${column.color} rounded-t-lg p-4 border-b-2 ${
                isDragOver && isValidDropZone 
                  ? 'border-green-500 bg-green-100' 
                  : draggedItem && !isValidDropZone
                  ? 'border-red-300 opacity-50'
                  : 'border-gray-300'
              } transition-all`}>
                <h3 className="font-semibold text-gray-900 flex items-center justify-between">
                  <span>{column.title}</span>
                  {isDragOver && isValidDropZone && (
                    <span className="text-green-600 text-sm">✓ Drop here</span>
                  )}
                  {draggedItem && !isValidDropZone && (
                    <span className="text-red-600 text-sm">✗ Invalid</span>
                  )}
                </h3>
                <p className="text-sm text-gray-600">
                  {items.length} {items.length === 1 ? 'item' : 'items'}
                </p>
              </div>

              {/* Column Content */}
              <div className={`bg-gray-50 rounded-b-lg p-4 min-h-[500px] space-y-3 transition-all ${
                isDragOver && isValidDropZone ? 'bg-green-50 ring-2 ring-green-300' : ''
              }`}>
                {items.map(item => (
                  <div
                    key={item.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, item.id)}
                    onDragEnd={handleDragEnd}
                    className={`bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-all cursor-move ${getPriorityColor(item.priority)} ${
                      draggedItem === item.id ? 'opacity-50 scale-95' : ''
                    }`}
                  >
                    <Link to={`/work-items/${item.id}`} className="block" onClick={(e) => draggedItem && e.preventDefault()}>
                      <h4 className="font-medium text-gray-900 mb-2 hover:text-blue-600">
                        {item.title}
                      </h4>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span className="px-2 py-1 bg-gray-100 rounded capitalize">{item.type}</span>
                        <span className={`px-2 py-1 rounded capitalize font-medium ${
                          item.priority === 'critical' ? 'bg-red-100 text-red-700' :
                          item.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                          item.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {item.priority}
                        </span>
                      </div>
                      {item.assigned_to && (
                        <div className="mt-2 text-xs text-gray-600 flex items-center gap-1">
                          <span>👤</span>
                          <span>Assigned</span>
                        </div>
                      )}
                    </Link>
                  </div>
                ))}
                
                {items.length === 0 && (
                  <div className="text-center text-gray-400 py-8">
                    {draggedItem && isValidDropZone ? (
                      <span className="text-green-600 font-medium">Drop here ↓</span>
                    ) : (
                      'No items'
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
        </div>
      )}
    </div>
  )
}
