import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import ProjectDocuments from '../components/ProjectDocuments'

export default function ProjectDocumentsPage() {
  const { id } = useParams<{ id: string }>()

  if (!id) {
    return <div>Project ID not found</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <Link
          to={`/projects/${id}`}
          className="text-blue-600 hover:text-blue-700 mb-2 flex items-center gap-1"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Project
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Project Documents</h1>
      </div>

      <ProjectDocuments projectId={id} />
    </div>
  )
}
