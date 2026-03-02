import { useState, useEffect } from 'react'
import api from '../api/client'
import { Upload, Globe, FileText, Trash2, FolderOpen } from 'lucide-react'

interface ProjectDocument {
  id: string
  name: string
  type: string
  category: string
  url?: string
  file_size?: number
  description?: string
  uploaded_by: string
  uploaded_at: string
  is_indexed: boolean
  chunk_count: number
  is_generated?: boolean
  generated_from?: string
  is_editable?: boolean
  version?: number
  content?: string
}

interface ProjectDocumentsProps {
  projectId: string
  selectionMode?: boolean
  onSelectionChange?: (selectedIds: string[]) => void
}

export default function ProjectDocuments({ projectId, selectionMode = false, onSelectionChange }: ProjectDocumentsProps) {
  const [documents, setDocuments] = useState<ProjectDocument[]>([])
  const [selectedDocuments, setSelectedDocuments] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [showUrl, setShowUrl] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  // Upload form
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadCategory, setUploadCategory] = useState('other')
  const [uploadDescription, setUploadDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  
  // URL form
  const [urlValue, setUrlValue] = useState('')
  const [urlName, setUrlName] = useState('')
  const [urlCategory, setUrlCategory] = useState('other')
  const [urlDescription, setUrlDescription] = useState('')
  const [addingUrl, setAddingUrl] = useState(false)

  useEffect(() => {
    loadDocuments()
  }, [projectId, selectedCategory])

  const loadDocuments = async () => {
    try {
      setLoading(true)
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : {}
      const response = await api.get(`/projects/${projectId}/documents`, { params })
      console.log('📄 Documents loaded:', response.data)
      console.log('📊 Total documents:', response.data.length)
      console.log('📋 Categories:', response.data.map((d: any) => d.category))
      setDocuments(response.data)
    } catch (err: any) {
      console.error('❌ Failed to load documents:', err)
      setError(err.response?.data?.detail || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!uploadFile) return

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', uploadFile)
      formData.append('category', uploadCategory)
      if (uploadDescription) {
        formData.append('description', uploadDescription)
      }

      await api.post(`/projects/${projectId}/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setShowUpload(false)
      setUploadFile(null)
      setUploadDescription('')
      loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleAddUrl = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!urlValue || !urlName) return

    try {
      setAddingUrl(true)
      const formData = new FormData()
      formData.append('url', urlValue)
      formData.append('name', urlName)
      formData.append('category', urlCategory)
      if (urlDescription) {
        formData.append('description', urlDescription)
      }

      await api.post(`/projects/${projectId}/documents/url`, formData)

      setShowUrl(false)
      setUrlValue('')
      setUrlName('')
      setUrlDescription('')
      loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add URL')
    } finally {
      setAddingUrl(false)
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await api.delete(`/projects/${projectId}/documents/${documentId}`)
      loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const toggleDocumentSelection = (documentId: string) => {
    const newSelection = new Set(selectedDocuments)
    if (newSelection.has(documentId)) {
      newSelection.delete(documentId)
    } else {
      newSelection.add(documentId)
    }
    setSelectedDocuments(newSelection)
    if (onSelectionChange) {
      onSelectionChange(Array.from(newSelection))
    }
  }

  const selectAll = () => {
    const allIds = documents.filter(doc => doc.is_indexed).map(doc => doc.id)
    setSelectedDocuments(new Set(allIds))
    if (onSelectionChange) {
      onSelectionChange(allIds)
    }
  }

  const clearSelection = () => {
    setSelectedDocuments(new Set())
    if (onSelectionChange) {
      onSelectionChange([])
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A'
    const kb = bytes / 1024
    if (kb < 1024) return `${kb.toFixed(1)} KB`
    return `${(kb / 1024).toFixed(1)} MB`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'url':
        return <Globe className="w-5 h-5 text-blue-500" />
      default:
        return <FileText className="w-5 h-5 text-gray-500" />
    }
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      requirements: 'bg-blue-100 text-blue-800',
      specification: 'bg-purple-100 text-purple-800',
      design: 'bg-pink-100 text-pink-800',
      technical: 'bg-green-100 text-green-800',
      business: 'bg-yellow-100 text-yellow-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || colors.other
  }

  if (loading) {
    return <div className="text-center py-8 text-gray-500">Loading documents...</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Project Documents</h2>
          <p className="text-sm text-gray-600">
            {selectionMode 
              ? `Select documents to use for requirements generation (${selectedDocuments.size} selected)`
              : 'Manage documents and URLs for AI-powered requirements generation'
            }
          </p>
        </div>
        <div className="flex gap-2">
          {selectionMode ? (
            <>
              <button
                onClick={selectAll}
                className="btn-secondary"
                disabled={documents.filter(d => d.is_indexed).length === 0}
              >
                Select All
              </button>
              <button
                onClick={clearSelection}
                className="btn-secondary"
                disabled={selectedDocuments.size === 0}
              >
                Clear
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setShowUpload(true)}
                className="btn-secondary flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                Upload File
              </button>
              <button
                onClick={() => setShowUrl(true)}
                className="btn-secondary flex items-center gap-2"
              >
                <Globe className="w-4 h-4" />
                Add URL
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

      {/* Category Filter */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['all', 'requirements', 'specification', 'design', 'technical', 'business', 'other'].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap ${
              selectedCategory === cat
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Upload Document</h3>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  File (PDF, DOCX, TXT)
                </label>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="input"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="input"
                >
                  <option value="requirements">Requirements</option>
                  <option value="specification">Specification</option>
                  <option value="design">Design</option>
                  <option value="technical">Technical</option>
                  <option value="business">Business</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  className="input"
                  rows={3}
                />
              </div>
              
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="btn-primary flex-1"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUpload(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* URL Modal */}
      {showUrl && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Add URL</h3>
            <form onSubmit={handleAddUrl} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  URL
                </label>
                <input
                  type="url"
                  value={urlValue}
                  onChange={(e) => setUrlValue(e.target.value)}
                  className="input"
                  placeholder="https://example.com"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  className="input"
                  placeholder="Document name"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={urlCategory}
                  onChange={(e) => setUrlCategory(e.target.value)}
                  className="input"
                >
                  <option value="requirements">Requirements</option>
                  <option value="specification">Specification</option>
                  <option value="design">Design</option>
                  <option value="technical">Technical</option>
                  <option value="business">Business</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (optional)
                </label>
                <textarea
                  value={urlDescription}
                  onChange={(e) => setUrlDescription(e.target.value)}
                  className="input"
                  rows={3}
                />
              </div>
              
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={addingUrl || !urlValue || !urlName}
                  className="btn-primary flex-1"
                >
                  {addingUrl ? 'Adding...' : 'Add URL'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUrl(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Documents List */}
      {documents.length === 0 ? (
        <div className="card text-center py-12">
          <FolderOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">No documents yet</p>
          <p className="text-sm text-gray-400">
            Upload documents or add URLs to use them for AI-powered requirements generation
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {documents.map((doc) => (
            <div key={doc.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                {selectionMode && doc.is_indexed && (
                  <div className="flex-shrink-0 mt-1">
                    <input
                      type="checkbox"
                      checked={selectedDocuments.has(doc.id)}
                      onChange={() => toggleDocumentSelection(doc.id)}
                      className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                  </div>
                )}
                
                <div className="flex-shrink-0 mt-1">
                  {getTypeIcon(doc.type)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">{doc.name}</h3>
                      {doc.description && (
                        <p className="text-sm text-gray-600 mt-1">{doc.description}</p>
                      )}
                      {doc.url && (
                        <a
                          href={doc.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:underline mt-1 block truncate"
                        >
                          {doc.url}
                        </a>
                      )}
                      {!doc.is_indexed && selectionMode && (
                        <p className="text-sm text-orange-600 mt-1">
                          ⚠️ Not indexed - cannot be selected
                        </p>
                      )}
                    </div>
                    
                    {!selectionMode && (
                      <div className="flex gap-2">
                        {doc.is_generated && doc.is_editable && (
                          <button
                            onClick={() => window.location.href = `/projects/${projectId}/documents/${doc.id}`}
                            className="text-blue-600 hover:text-blue-700 p-2"
                            title="View/Edit document"
                          >
                            <FolderOpen className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(doc.id)}
                          className="text-red-600 hover:text-red-700 p-2"
                          title="Delete document"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-3 mt-3 text-sm text-gray-500">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(doc.category)}`}>
                      {doc.category}
                    </span>
                    
                    {doc.is_generated && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-800">
                        🤖 Generated
                      </span>
                    )}
                    
                    {!doc.is_generated && doc.is_indexed && (
                      <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        📚 RAG Source
                      </span>
                    )}
                    {doc.file_size && (
                      <span>{formatFileSize(doc.file_size)}</span>
                    )}
                    {doc.is_indexed && (
                      <span className="text-green-600">
                        ✓ Indexed ({doc.chunk_count} chunks)
                      </span>
                    )}
                    <span>{formatDate(doc.uploaded_at)}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
