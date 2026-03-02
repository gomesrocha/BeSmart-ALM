import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { FolderKanban, ListTodo, CheckCircle, Clock } from 'lucide-react'
import type { Project, WorkItem } from '../types'

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [workItems, setWorkItems] = useState<WorkItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.get('/projects').then(r => setProjects(r.data)),
      api.get('/work-items').then(r => setWorkItems(r.data)),
    ]).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  const stats = [
    { name: 'Total Projects', value: projects.length, icon: FolderKanban, color: 'blue' },
    { name: 'Total Work Items', value: workItems.length, icon: ListTodo, color: 'purple' },
    { name: 'Completed', value: workItems.filter(w => w.status === 'done').length, icon: CheckCircle, color: 'green' },
    { name: 'In Progress', value: workItems.filter(w => w.status === 'in_progress').length, icon: Clock, color: 'yellow' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your projects and work items</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.name}</p>
                  <p className="text-3xl font-bold mt-1">{stat.value}</p>
                </div>
                <Icon className={`w-12 h-12 text-${stat.color}-500`} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Projects</h2>
            <Link to="/projects" className="text-sm text-primary-600 hover:text-primary-700">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {projects.slice(0, 5).map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}`}
                className="block p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <h3 className="font-medium">{project.name}</h3>
                <p className="text-sm text-gray-600 line-clamp-1">{project.description}</p>
              </Link>
            ))}
            {projects.length === 0 && (
              <p className="text-gray-500 text-center py-4">No projects yet</p>
            )}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Work Items</h2>
            <Link to="/work-items" className="text-sm text-primary-600 hover:text-primary-700">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {workItems.slice(0, 5).map((item) => (
              <Link
                key={item.id}
                to={`/work-items/${item.id}`}
                className="block p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{item.title}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    item.status === 'done' ? 'bg-green-100 text-green-700' :
                    item.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {item.status}
                  </span>
                </div>
              </Link>
            ))}
            {workItems.length === 0 && (
              <p className="text-gray-500 text-center py-4">No work items yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
