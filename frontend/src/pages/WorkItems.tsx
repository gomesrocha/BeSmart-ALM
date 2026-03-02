import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import api from '../api/client'
import { WorkItem, Project } from '../types'
import { Plus, Search, CheckSquare } from 'lucide-react'
import Protected from '../components/Protected'
import { ProjectSelector } from '../components/ProjectSelector'

interface WorkItemForm {
  title: string
  description: string
  type: string
  project_id: string
}

const STORAGE_KEY = 'workitems_selected_project'

export default function WorkItems() {
  const [workItems, setWorkItems] = useState<WorkItem[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [projectFilter, setProjectFilter] = useState<string | null>(() => {
    return localStorage.getItem(STORAGE_KEY) || null
  })
  const { register, handleSubmit, reset, formState: { isSubmitting } } = useForm<WorkItemForm>()

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [workItemsRes, projectsRes] = await Promise.all([
        api.get('/work-items'),
        api.get('/projects')
      ])
      setWorkItems(workItemsRes.data)
      setProjects(projectsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: WorkItemForm) => {
    try {
      await api.post('/work-items', data)
      reset()
      setShowCreateForm(false)
      fetchData()
    } catch (error) {
      console.error('Failed to create work item:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'done': return 'bg-green-100 text-green-800'
      case 'in_progress': return 'bg-blue-100 text-blue-800'
      case 'approved': return 'bg-purple-100 text-purple-800'
      case 'in_review': return 'bg-yellow-100 text-yellow-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'user_story': return 'bg-blue-100 text-blue-800'
      case 'task': return 'bg-green-100 text-green-800'
      case 'defect': return 'bg-red-100 text-red-800'
      case 'requirement': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleProjectChange = (projectId: string | null) => {
    setProjectFilter(projectId)
    if (projectId) {
      localStorage.setItem(STORAGE_KEY, projectId)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  const filteredWorkItems = workItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.description?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = !statusFilter || item.status === statusFilter
    const matchesType = !typeFilter || item.type === typeFilter
    const matchesProject = !projectFilter || item.project_id === projectFilter
    return matchesSearch && matchesStatus && matchesType && matchesProject
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Work Items</h1>
          <p className="text-gray-600">Manage requirements, user stories, tasks and more</p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/work-items/kanban"
            className="btn bg-purple-600 hover:bg-purple-700 text-white flex items-center space-x-2"
          >
            <CheckSquare className="h-4 w-4" />
            <span>Kanban View</span>
          </Link>
          <Protected permission="work_item:create">
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Plus className="h-4 w-4" />
              <span>New Work Item</span>
            </button>
          </Protected>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search work items..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="w-full sm:w-48">
          <ProjectSelector
            value={projectFilter || undefined}
            onChange={handleProjectChange}
            allowAll={true}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input"
        >
          <option value="">All Statuses</option>
          <option value="draft">Draft</option>
          <option value="in_review">In Review</option>
          <option value="approved">Approved</option>
          <option value="in_progress">In Progress</option>
          <option value="done">Done</option>
        </select>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="input"
        >
          <option value="">All Types</option>
          <option value="requirement">Requirement</option>
          <option value="user_story">User Story</option>
          <option value="task">Task</option>
          <option value="defect">Defect</option>
        </select>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Create New Work Item</h3>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Title</label>
                <input
                  {...register('title', { required: true })}
                  className="input mt-1"
                  placeholder="Work item title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Type</label>
                <select {...register('type', { required: true })} className="input mt-1">
                  <option value="">Select type</option>
                  <option value="requirement">Requirement</option>
                  <option value="user_story">User Story</option>
                  <option value="task">Task</option>
                  <option value="defect">Defect</option>
                  <option value="nfr">NFR</option>
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Project</label>
              <select {...register('project_id', { required: true })} className="input mt-1">
                <option value="">Select project</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>{project.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                {...register('description')}
                className="input mt-1"
                rows={3}
                placeholder="Work item description"
              />
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary disabled:opacity-50"
              >
                {isSubmitting ? 'Creating...' : 'Create Work Item'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Work Items List */}
      <div className="space-y-4">
        {filteredWorkItems.map((item) => (
          <Link
            key={item.id}
            to={`/work-items/${item.id}`}
            className="card hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div className="p-2 bg-primary-50 rounded-lg">
                  <CheckSquare className="h-5 w-5 text-primary-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-gray-900">{item.title}</h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {item.description || 'No description'}
                  </p>
                  <div className="flex items-center space-x-2 mt-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(item.type)}`}>
                      {item.type.replace('_', ' ')}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">v{item.version}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {new Date(item.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filteredWorkItems.length === 0 && (
        <div className="text-center py-12">
          <CheckSquare className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No work items</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating a new work item.
          </p>
        </div>
      )}
    </div>
  )
}
