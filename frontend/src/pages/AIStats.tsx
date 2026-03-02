import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import api from '../api/client'
import { TrendingUp, Zap, DollarSign, Clock } from 'lucide-react'

interface AIStats {
  total_operations: number
  total_tokens: number
  total_cost_estimate: number
  total_duration: number
  operations_by_type: Record<string, number>
  cost_by_model: Record<string, number>
  tokens_by_model: Record<string, number>
  recent_operations: Array<{
    operation: string
    model: string
    tokens: number
    cost: number
    duration: number
    created_at: string
    success: boolean
  }>
}

export default function AIStats() {
  const { projectId } = useParams()
  const [stats, setStats] = useState<AIStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadStats()
  }, [projectId, days])

  const loadStats = async () => {
    try {
      setLoading(true)
      const params: any = { days }
      if (projectId) {
        params.project_id = projectId
      }
      const response = await api.get('/ai-stats', { params })
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load AI stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!stats) {
    return <div>No statistics available</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">AI Usage Statistics</h1>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="input"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Operations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_operations}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Tokens</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.total_tokens.toLocaleString()}
              </p>
            </div>
            <Zap className="w-8 h-8 text-yellow-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Estimated Cost</p>
              <p className="text-2xl font-bold text-gray-900">
                ${stats.total_cost_estimate.toFixed(2)}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Duration</p>
              <p className="text-2xl font-bold text-gray-900">
                {(stats.total_duration / 60).toFixed(1)}m
              </p>
            </div>
            <Clock className="w-8 h-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Operations by Type */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Operations by Type</h2>
        <div className="space-y-3">
          {Object.entries(stats.operations_by_type).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between">
              <span className="text-gray-700 capitalize">{type}</span>
              <div className="flex items-center gap-3">
                <div className="w-48 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{
                      width: `${(count / stats.total_operations) * 100}%`
                    }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-900 w-12 text-right">
                  {count}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cost by Model */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Cost by Model</h2>
        <div className="space-y-3">
          {Object.entries(stats.cost_by_model).map(([model, cost]) => (
            <div key={model} className="flex items-center justify-between">
              <span className="text-gray-700">{model}</span>
              <span className="text-sm font-medium text-gray-900">
                ${cost.toFixed(4)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Operations */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Recent Operations</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Operation
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Model
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Tokens
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Cost
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Duration
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {stats.recent_operations.map((op, index) => (
                <tr key={index}>
                  <td className="px-4 py-3 text-sm text-gray-900 capitalize">
                    {op.operation}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {op.model}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    {op.tokens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-900">
                    ${op.cost.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {op.duration.toFixed(2)}s
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {new Date(op.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {op.success ? (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                        Success
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800">
                        Failed
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
