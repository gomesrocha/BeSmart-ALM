import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/client'
import { ArrowLeft, Edit2, Save, X, FileText } from 'lucide-react'

interface Document {
  id: string
  project_id: string
  name: string
  type: string
  category: string
  description?: string
  uploaded_at: string
  is_generated: boolean
  generated_from?: string
  is_editable: boolean
  version: number
  content?: string
}

export default function DocumentViewer() {
  const { projectId, documentId } = useParams()
  const [document, setDocument] = useState<Document | null>(null)
  const [content, setContent] = useState('')
  const [editMode, setEditMode] = useState(false)
  const [editedContent, setEditedContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadDocument()
  }, [projectId, documentId])

  const loadDocument = async () => {
    try {
      setLoading(true)
      console.log('📄 Loading document:', { projectId, documentId })
      
      // Get document metadata
      const docResponse = await api.get(`/projects/${projectId}/documents`)
      console.log('📋 All documents:', docResponse.data)
      
      const doc = docResponse.data.find((d: Document) => d.id === documentId)
      console.log('🔍 Found document:', doc)
      
      if (!doc) {
        console.error('❌ Document not found in list')
        setError('Document not found')
        return
      }
      
      setDocument(doc)
      
      // Get document content if it's a generated document
      if (doc.is_generated) {
        console.log('📥 Loading content for generated document...')
        const contentResponse = await api.get(`/projects/${projectId}/documents/${documentId}/content`)
        console.log('✅ Content loaded:', contentResponse.data)
        setContent(contentResponse.data.content || '')
        setEditedContent(contentResponse.data.content || '')
      } else {
        console.log('⚠️ Document is not generated, no content to load')
      }
    } catch (err: any) {
      console.error('❌ Failed to load document:', err)
      setError(err.response?.data?.detail || 'Failed to load document')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      const formData = new FormData()
      formData.append('content', editedContent)
      
      await api.patch(`/projects/${projectId}/documents/${documentId}/content`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setContent(editedContent)
      setEditMode(false)
      loadDocument() // Reload to get updated version
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save document')
    } finally {
      setSaving(false)
    }
  }

  const handleCancel = () => {
    setEditedContent(content)
    setEditMode(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">{error || 'Document not found'}</p>
        <Link to={`/projects/${projectId}/documents`} className="text-primary-600 hover:underline mt-4 inline-block">
          Back to Documents
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to={`/projects/${projectId}/documents`} className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <FileText className="h-6 w-6 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">{document.name}</h1>
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                document.is_generated 
                  ? 'bg-purple-100 text-purple-800'
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {document.is_generated ? 'Generated' : 'Uploaded'}
              </span>
              <span className="text-sm text-gray-600">
                Category: {document.category}
              </span>
              <span className="text-sm text-gray-600">
                Version: {document.version}
              </span>
            </div>
          </div>
        </div>
        
        {document.is_editable && !editMode && (
          <button
            onClick={() => setEditMode(true)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Edit2 className="h-4 w-4" />
            <span>Edit</span>
          </button>
        )}
        
        {editMode && (
          <div className="flex gap-2">
            <button
              onClick={handleCancel}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <X className="h-4 w-4" />
              <span>Cancel</span>
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{saving ? 'Saving...' : 'Save'}</span>
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="card">
        {editMode ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Edit Content
            </label>
            <textarea
              value={editedContent}
              onChange={(e) => setEditedContent(e.target.value)}
              className="input font-mono text-sm"
              rows={30}
              placeholder="Enter document content..."
            />
            <p className="text-xs text-gray-500 mt-2">
              Markdown formatting is supported
            </p>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800">
                {content || 'No content available'}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Metadata */}
      {document.description && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Description</h3>
          <p className="text-gray-600">{document.description}</p>
        </div>
      )}
    </div>
  )
}
