import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import api from '../api/client'

interface WorkItem {
  id: string
  title: string
  description: string
  type: string
  status: string
  priority: string
  project_id: string
  assigned_to?: string
  created_at: string
  updated_at: string
}

interface Project {
  id: string
  name: string
}

interface User {
  id: string
  email: string
  full_name?: string
}

interface Comment {
  id: string
  content: string
  created_by: string
  created_at: string
  user?: User
}

interface StateTransition {
  to_state: string
  label: string
}

export default function WorkItemDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [workItem, setWorkItem] = useState<WorkItem | null>(null)
  const [project, setProject] = useState<Project | null>(null)
  const [users, setUsers] = useState<User[]>([])
  const [comments, setComments] = useState<Comment[]>([])
  const [transitions, setTransitions] = useState<StateTransition[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [transitioning, setTransitioning] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [editForm, setEditForm] = useState({
    title: '',
    description: '',
    priority: '',
    assigned_to: ''
  })

  useEffect(() => {
    loadWorkItem()
    loadUsers()
  }, [id])

  const loadWorkItem = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/work-items/${id}`)
      setWorkItem(response.data)
      setEditForm({
        title: response.data.title,
        description: response.data.description,
        priority: response.data.priority,
        assigned_to: response.data.assigned_to || ''
      })
      
      // Load project
      const projectResponse = await api.get(`/projects/${response.data.project_id}`)
      setProject(projectResponse.data)
      
      // Load transitions
      const transitionsResponse = await api.get(`/work-items/${id}/transitions`)
      setTransitions(transitionsResponse.data.transitions || [])
      
      // Load comments
      loadComments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load work item')
    } finally {
      setLoading(false)
    }
  }

  const loadUsers = async () => {
    try {
      const response = await api.get('/users')
      console.log('Users loaded:', response.data)
      setUsers(response.data)
    } catch (err) {
      console.error('Failed to load users:', err)
    }
  }

  const loadComments = async () => {
    try {
      const response = await api.get(`/work-items/${id}/comments`)
      setComments(response.data)
    } catch (err) {
      console.error('Failed to load comments:', err)
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.patch(`/work-items/${id}`, editForm)
      setIsEditing(false)
      loadWorkItem()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update work item')
    }
  }

  const handleTransition = async (toState: string) => {
    console.log('🔄 Transitioning to:', toState)
    setTransitioning(true)
    setError('')
    
    try {
      console.log('📤 Sending transition request...')
      const response = await api.post(`/work-items/${id}/transition`, { new_status: toState })
      console.log('✅ Transition successful:', response.data)
      
      // Reload work item to get updated status
      await loadWorkItem()
      
      // Show success message
      alert(`Work item transitioned to ${toState.replace('_', ' ')}`)
    } catch (err: any) {
      console.error('❌ Transition failed:', err)
      const errorMsg = err.response?.data?.detail || 'Failed to transition work item'
      setError(errorMsg)
      alert(errorMsg)
    } finally {
      setTransitioning(false)
    }
  }

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim()) return
    
    try {
      await api.post(`/work-items/${id}/comments`, { content: newComment })
      setNewComment('')
      loadComments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add comment')
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this work item?')) return
    
    try {
      await api.delete(`/work-items/${id}`)
      navigate('/work-items')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete work item')
    }
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'backlog': 'bg-gray-100 text-gray-800',
      'todo': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-yellow-100 text-yellow-800',
      'in_review': 'bg-purple-100 text-purple-800',
      'done': 'bg-green-100 text-green-800',
      'blocked': 'bg-red-100 text-red-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      'low': 'bg-gray-100 text-gray-800',
      'medium': 'bg-blue-100 text-blue-800',
      'high': 'bg-orange-100 text-orange-800',
      'critical': 'bg-red-100 text-red-800'
    }
    return colors[priority] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const getAvailableStatusOptions = (currentStatus: string) => {
    // Map based on state machine rules
    const statusMap: Record<string, Array<{value: string, label: string}>> = {
      'draft': [
        { value: 'draft', label: 'Draft (current)' },
        { value: 'in_review', label: 'In Review' }
      ],
      'in_review': [
        { value: 'in_review', label: 'In Review (current)' },
        { value: 'approved', label: 'Approved' },
        { value: 'rejected', label: 'Rejected' }
      ],
      'approved': [
        { value: 'approved', label: 'Approved (current)' },
        { value: 'in_progress', label: 'In Progress' }
      ],
      'rejected': [
        { value: 'rejected', label: 'Rejected (current)' },
        { value: 'draft', label: 'Draft' }
      ],
      'in_progress': [
        { value: 'in_progress', label: 'In Progress (current)' },
        { value: 'done', label: 'Done' }
      ],
      'done': [
        { value: 'done', label: 'Done (final)' }
      ]
    }
    
    return statusMap[currentStatus] || [{ value: currentStatus, label: currentStatus }]
  }

  const parseDescription = (description: string) => {
    try {
      return JSON.parse(description)
    } catch {
      return null
    }
  }

  const renderDescription = (description: string) => {
    const parsed = parseDescription(description)
    
    if (!parsed) {
      // Plain text description
      return (
        <div className="text-gray-900 whitespace-pre-wrap">
          {description}
        </div>
      )
    }
    
    return (
      <div className="space-y-6">
        {/* User Story */}
        {parsed.user_story && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-lg">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
              <span className="text-xl">👤</span>
              User Story
            </h4>
            <div className="space-y-2 text-gray-800">
              <p>
                <span className="font-medium text-blue-700">As a</span>{' '}
                <span className="italic">{parsed.user_story.as_a}</span>
              </p>
              <p>
                <span className="font-medium text-blue-700">I want</span>{' '}
                <span className="italic">{parsed.user_story.i_want}</span>
              </p>
              <p>
                <span className="font-medium text-blue-700">So that</span>{' '}
                <span className="italic">{parsed.user_story.so_that}</span>
              </p>
            </div>
          </div>
        )}
        
        {/* Acceptance Criteria */}
        {parsed.acceptance_criteria && Array.isArray(parsed.acceptance_criteria) && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
              <span className="text-xl">✓</span>
              Acceptance Criteria
            </h4>
            <div className="space-y-4">
              {parsed.acceptance_criteria.map((criteria: any, index: number) => (
                <div 
                  key={index} 
                  className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <h5 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                    <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm">
                      {index + 1}
                    </span>
                    {criteria.scenario}
                  </h5>
                  <div className="space-y-2 ml-8">
                    <div className="flex gap-2">
                      <span className="font-medium text-purple-600 min-w-[60px]">Given:</span>
                      <span className="text-gray-700">{criteria.given}</span>
                    </div>
                    <div className="flex gap-2">
                      <span className="font-medium text-blue-600 min-w-[60px]">When:</span>
                      <span className="text-gray-700">{criteria.when}</span>
                    </div>
                    <div className="flex gap-2">
                      <span className="font-medium text-green-600 min-w-[60px]">Then:</span>
                      <span className="text-gray-700">{criteria.then}</span>
                    </div>
                    {criteria.and && criteria.and.length > 0 && (
                      <div className="space-y-1 mt-2 pt-2 border-t border-gray-200">
                        {criteria.and.map((item: string, i: number) => (
                          <div key={i} className="flex gap-2">
                            <span className="font-medium text-gray-600 min-w-[60px]">And:</span>
                            <span className="text-gray-700">{item}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Additional Details */}
        {parsed.details && (
          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-r-lg">
            <h4 className="font-semibold text-yellow-900 mb-2 flex items-center gap-2">
              <span className="text-xl">📝</span>
              Additional Details
            </h4>
            <p className="text-gray-800 whitespace-pre-wrap">{parsed.details}</p>
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  if (error && !workItem) {
    return (
      <div className="card bg-red-50 border-red-200">
        <p className="text-red-600">{error}</p>
        <button onClick={() => navigate('/work-items')} className="btn-secondary mt-4">
          Back to Work Items
        </button>
      </div>
    )
  }

  if (!workItem) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <button
            onClick={() => navigate('/work-items')}
            className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
          >
            ← Back to Work Items
          </button>
          <h1 className="text-2xl font-bold text-gray-900">{workItem.title}</h1>
          <p className="text-gray-600">
            {project?.name} • {workItem.type}
          </p>
        </div>
        <div className="flex gap-2">
          {/* Quick Action Buttons */}
          {workItem.status === 'in_review' && !isEditing && (
            <>
              <button 
                onClick={() => handleTransition('approved')} 
                disabled={transitioning}
                className="btn bg-green-600 hover:bg-green-700 text-white disabled:opacity-50"
              >
                {transitioning ? '⏳' : '✓'} Approve
              </button>
              <button 
                onClick={() => handleTransition('rejected')} 
                disabled={transitioning}
                className="btn bg-red-600 hover:bg-red-700 text-white disabled:opacity-50"
              >
                {transitioning ? '⏳' : '✗'} Reject
              </button>
            </>
          )}
          
          {workItem.status === 'draft' && !isEditing && (
            <button 
              onClick={() => handleTransition('in_review')} 
              disabled={transitioning}
              className="btn bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
            >
              {transitioning ? '⏳' : '📤'} Submit for Review
            </button>
          )}
          
          {workItem.status === 'approved' && !isEditing && (
            <button 
              onClick={() => handleTransition('in_progress')} 
              disabled={transitioning}
              className="btn bg-purple-600 hover:bg-purple-700 text-white disabled:opacity-50"
            >
              {transitioning ? '⏳' : '▶'} Start Work
            </button>
          )}
          
          {workItem.status === 'in_progress' && !isEditing && (
            <button 
              onClick={() => handleTransition('done')} 
              disabled={transitioning}
              className="btn bg-green-600 hover:bg-green-700 text-white disabled:opacity-50"
            >
              {transitioning ? '⏳' : '✓'} Complete
            </button>
          )}
          
          {!isEditing && (
            <>
              <button onClick={() => setIsEditing(true)} className="btn-secondary">
                Edit
              </button>
              <button onClick={handleDelete} className="btn-secondary text-red-600 hover:bg-red-50">
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Details Card */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Details</h2>
            
            {isEditing ? (
              <form onSubmit={handleUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    className="input"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    className="input"
                    rows={6}
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Priority
                    </label>
                    <select
                      value={editForm.priority}
                      onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                      className="input"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Assigned To
                    </label>
                    <select
                      value={editForm.assigned_to}
                      onChange={(e) => setEditForm({ ...editForm, assigned_to: e.target.value })}
                      className="input"
                    >
                      <option value="">Unassigned</option>
                      {users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.full_name || user.email}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button type="submit" className="btn-primary">
                    Save Changes
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditing(false)
                      setEditForm({
                        title: workItem.title,
                        description: workItem.description,
                        priority: workItem.priority,
                        assigned_to: workItem.assigned_to || ''
                      })
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-3">Description</h3>
                  {renderDescription(workItem.description)}
                </div>
              </div>
            )}
          </div>

          {/* Comments */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Comments ({comments.length})</h2>
            
            <form onSubmit={handleAddComment} className="mb-6">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
                className="input mb-2"
                rows={3}
              />
              <button type="submit" className="btn-primary">
                Add Comment
              </button>
            </form>
            
            <div className="space-y-4">
              {comments.map((comment) => (
                <div key={comment.id} className="border-l-2 border-gray-200 pl-4">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900">
                      {comment.user?.full_name || comment.user?.email || 'Unknown User'}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatDate(comment.created_at)}
                    </span>
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap">{comment.content}</p>
                </div>
              ))}
              
              {comments.length === 0 && (
                <p className="text-gray-500 text-center py-4">No comments yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Status & Transitions */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Status</h2>
            <div className="space-y-4">
              <div>
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(workItem.status)}`}>
                  {workItem.status.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              {transitions.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Available Transitions</h3>
                  <div className="space-y-2">
                    {transitions.map((transition) => (
                      <button
                        key={transition.to_state}
                        onClick={() => handleTransition(transition.to_state)}
                        disabled={transitioning}
                        className="w-full btn-secondary text-left disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {transitioning ? '⏳ ' : '→ '}{transition.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Metadata */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Information</h2>
            <div className="space-y-3">
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Status</h3>
                <select
                  value={workItem.status}
                  onChange={(e) => {
                    if (e.target.value !== workItem.status) {
                      console.log('Changing status to:', e.target.value)
                      handleTransition(e.target.value)
                    }
                  }}
                  disabled={transitioning || workItem.status === 'done'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {getAvailableStatusOptions(workItem.status).map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                {workItem.status === 'done' && (
                  <p className="text-xs text-gray-500 mt-1">Final state - cannot change</p>
                )}
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Priority</h3>
                <span className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getPriorityColor(workItem.priority)}`}>
                  {workItem.priority.toUpperCase()}
                </span>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500 mb-1">Assigned To</h3>
                <select
                  value={workItem.assigned_to || ''}
                  onChange={async (e) => {
                    try {
                      console.log('Assigning to:', e.target.value)
                      await api.patch(`/work-items/${id}`, {
                        assigned_to: e.target.value || null
                      })
                      await loadWorkItem()
                      alert('Assigned successfully!')
                    } catch (err: any) {
                      const errorMsg = err.response?.data?.detail || err.message || 'Failed to assign'
                      console.error('Assignment error:', err)
                      alert(errorMsg)
                      setError(errorMsg)
                    }
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Unassigned</option>
                  {users.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.full_name || user.email}
                    </option>
                  ))}
                </select>
                {users.length === 0 && (
                  <p className="text-xs text-red-500 mt-1">No users loaded</p>
                )}
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500">Created</h3>
                <p className="text-gray-900">{formatDate(workItem.created_at)}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-500">Updated</h3>
                <p className="text-gray-900">{formatDate(workItem.updated_at)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
