import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import api from '../api/client'
import { Project } from '../types'
import { Sparkles, ArrowLeft, Check, X, Loader, Upload, FileText, Globe, Edit2, Trash2, BookOpen, Network } from 'lucide-react'
import ProjectProgress from '../components/ProjectProgress'

interface UserStory {
  as_a: string
  i_want: string
  so_that: string
}

interface GherkinScenario {
  scenario: string
  given: string
  when: string
  then: string
  and?: string[]
}

interface RequirementItem {
  title: string
  user_story: string | UserStory
  acceptance_criteria: string[] | GherkinScenario[]
  business_context?: string
  type: string
  priority: string
}

interface GenerateForm {
  description: string
}

interface UploadForm {
  file: FileList
  additional_context: string
}

interface UrlForm {
  url: string
  additional_context: string
}

interface EditProjectForm {
  name: string
  description: string
  status: string
  target_cloud: string
  mps_br_level: string
}

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [fetchingUrl, setFetchingUrl] = useState(false)
  const [approving, setApproving] = useState(false)
  const [requirements, setRequirements] = useState<RequirementItem[]>([])
  const [showSuccess, setShowSuccess] = useState(false)
  const [inputMode, setInputMode] = useState<'text' | 'upload' | 'url'>('text')
  const [selectedRequirements, setSelectedRequirements] = useState<Set<number>>(new Set())
  const [workItemsCount, setWorkItemsCount] = useState(0)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [projectWorkItems, setProjectWorkItems] = useState<any[]>([])
  const [showRefineSection, setShowRefineSection] = useState(false)
  const [refineFeedback, setRefineFeedback] = useState('')
  const [refining, setRefining] = useState(false)
  const [iteration, setIteration] = useState(1)
  
  // Track if spec/arch exist
  const [hasSpecification, setHasSpecification] = useState(false)
  const [hasArchitecture, setHasArchitecture] = useState(false)
  
  // Specification modal states
  const [showSpecModal, setShowSpecModal] = useState(false)
  const [generatingSpec, setGeneratingSpec] = useState(false)
  const [specContent, setSpecContent] = useState('')
  const [specDocumentId, setSpecDocumentId] = useState<string | null>(null)
  const [error, setError] = useState('')
  
  // Architecture modal states
  const [showArchModal, setShowArchModal] = useState(false)
  const [generatingArch, setGeneratingArch] = useState(false)
  const [archContent, setArchContent] = useState('')
  const [archDiagrams, setArchDiagrams] = useState<string[]>([])
  const [archDocumentId, setArchDocumentId] = useState<string | null>(null)
  
  const { register, handleSubmit, formState: { isSubmitting } } = useForm<GenerateForm>()
  const { register: registerUpload, handleSubmit: handleSubmitUpload, formState: { isSubmitting: isSubmittingUpload } } = useForm<UploadForm>()
  const { register: registerUrl, handleSubmit: handleSubmitUrl, formState: { isSubmitting: isSubmittingUrl } } = useForm<UrlForm>()
  const { register: registerEdit, handleSubmit: handleSubmitEdit, formState: { isSubmitting: isSubmittingEdit }, reset: resetEdit } = useForm<EditProjectForm>()

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      const { data } = await api.get(`/projects/${id}`)
      setProject(data)
      
      // Fetch work items count for progress tracking
      const { data: workItems } = await api.get(`/work-items?project_id=${id}`)
      setWorkItemsCount(workItems.length || 0)
      setProjectWorkItems(workItems || [])
      
      // Check if specification and architecture exist
      const { data: documents } = await api.get(`/projects/${id}/documents`)
      const hasSpec = documents.some((d: any) => 
        (d.category === 'SPECIFICATION' || d.category === 'specification') && d.is_generated
      )
      const hasArch = documents.some((d: any) => 
        (d.category === 'ARCHITECTURE' || d.category === 'architecture') && d.is_generated
      )
      setHasSpecification(hasSpec)
      setHasArchitecture(hasArch)
      
      console.log('📊 Progress check:', { 
        workItems: workItems.length, 
        hasSpec, 
        hasArch,
        documents: documents.map((d: any) => ({ category: d.category, is_generated: d.is_generated }))
      })
    } catch (error) {
      console.error('Failed to fetch project:', error)
    } finally {
      setLoading(false)
    }
  }

  const onGenerate = async (data: GenerateForm) => {
    setGenerating(true)
    try {
      const { data: response } = await api.post('/requirements/generate', {
        project_id: id,
        description: data.description
      })
      setRequirements(response.requirements)
    } catch (error: any) {
      console.error('Failed to generate requirements:', error)
      alert(error.response?.data?.detail || 'Failed to generate requirements')
    } finally {
      setGenerating(false)
    }
  }

  const onUpload = async (data: UploadForm) => {
    if (!data.file || data.file.length === 0) {
      alert('Please select a file')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('project_id', id!)
      formData.append('file', data.file[0])
      if (data.additional_context) {
        formData.append('additional_context', data.additional_context)
      }

      const { data: response } = await api.post('/requirements/generate-from-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setRequirements(response.requirements)
    } catch (error: any) {
      console.error('Failed to generate requirements from document:', error)
      alert(error.response?.data?.detail || 'Failed to generate requirements from document')
    } finally {
      setUploading(false)
    }
  }

  const onUrlSubmit = async (data: UrlForm) => {
    if (!data.url) {
      alert('Please enter a URL')
      return
    }

    setFetchingUrl(true)
    try {
      const formData = new FormData()
      formData.append('project_id', id!)
      formData.append('url', data.url)
      if (data.additional_context) {
        formData.append('additional_context', data.additional_context)
      }

      const { data: response } = await api.post('/requirements/generate-from-url', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      setRequirements(response.requirements)
    } catch (error: any) {
      console.error('Failed to generate requirements from URL:', error)
      alert(error.response?.data?.detail || 'Failed to generate requirements from URL')
    } finally {
      setFetchingUrl(false)
    }
  }

  const onApprove = async () => {
    setApproving(true)
    try {
      await api.post('/requirements/approve', {
        project_id: id,
        requirements: requirements
      })
      setShowSuccess(true)
      setRequirements([])
      setSelectedRequirements(new Set())
      setTimeout(() => setShowSuccess(false), 3000)
      // Refresh project data to update progress
      fetchProject()
    } catch (error: any) {
      console.error('Failed to approve requirements:', error)
      alert(error.response?.data?.detail || 'Failed to approve requirements')
    } finally {
      setApproving(false)
    }
  }

  const onApproveSelected = async () => {
    if (selectedRequirements.size === 0) {
      alert('Please select at least one requirement to approve')
      return
    }
    
    setApproving(true)
    try {
      const toApprove = requirements.filter((_, i) => selectedRequirements.has(i))
      await api.post('/requirements/approve', {
        project_id: id,
        requirements: toApprove
      })
      setShowSuccess(true)
      // Remove approved requirements from the list
      setRequirements(requirements.filter((_, i) => !selectedRequirements.has(i)))
      setSelectedRequirements(new Set())
      setTimeout(() => setShowSuccess(false), 3000)
      // Refresh project data to update progress
      fetchProject()
    } catch (error: any) {
      console.error('Failed to approve requirements:', error)
      alert(error.response?.data?.detail || 'Failed to approve requirements')
    } finally {
      setApproving(false)
    }
  }

  const toggleRequirement = (index: number) => {
    const newSelected = new Set(selectedRequirements)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedRequirements(newSelected)
  }

  const toggleAll = () => {
    if (selectedRequirements.size === requirements.length) {
      setSelectedRequirements(new Set())
    } else {
      setSelectedRequirements(new Set(requirements.map((_, i) => i)))
    }
  }

  const removeRequirement = (index: number) => {
    setRequirements(requirements.filter((_, i) => i !== index))
    // Remove from selected if it was selected
    const newSelected = new Set(selectedRequirements)
    newSelected.delete(index)
    // Adjust indices for remaining items
    const adjustedSelected = new Set<number>()
    newSelected.forEach(i => {
      if (i > index) {
        adjustedSelected.add(i - 1)
      } else {
        adjustedSelected.add(i)
      }
    })
    setSelectedRequirements(adjustedSelected)
  }

  const onEditProject = async (data: EditProjectForm) => {
    console.log('📝 Editing project with data:', data)
    try {
      const payload = {
        name: data.name,
        description: data.description,
        status: data.status,
        settings: {
          target_cloud: data.target_cloud,
          mps_br_level: data.mps_br_level
        }
      }
      console.log('📤 Sending payload:', payload)
      
      const response = await api.patch(`/projects/${id}`, payload)
      console.log('✅ Project updated:', response.data)
      
      setShowEditModal(false)
      await fetchProject()
      alert('Project updated successfully!')
    } catch (error: any) {
      console.error('❌ Failed to update project:', error)
      console.error('Error response:', error.response?.data)
      alert(error.response?.data?.detail || 'Failed to update project')
    }
  }

  const onDeleteProject = async () => {
    setDeleting(true)
    try {
      await api.delete(`/projects/${id}`)
      window.location.href = '/projects'
    } catch (error: any) {
      console.error('Failed to delete project:', error)
      alert(error.response?.data?.detail || 'Failed to delete project')
      setDeleting(false)
    }
  }

  const openEditModal = () => {
    if (project) {
      resetEdit({
        name: project.name,
        description: project.description || '',
        status: project.status,
        target_cloud: project.settings?.target_cloud || 'AWS',
        mps_br_level: project.settings?.mps_br_level || 'G'
      })
      setShowEditModal(true)
    }
  }

  const onRefineRequirements = async (operation: 'refine' | 'add_more' | 'improve') => {
    if (!refineFeedback.trim()) {
      alert('Please provide feedback for refinement')
      return
    }
    
    setRefining(true)
    try {
      const { data: response } = await api.post('/requirements/refine', {
        project_id: id,
        existing_requirements: requirements,
        feedback: refineFeedback,
        operation: operation
      })
      
      if (operation === 'add_more') {
        // Add new requirements to existing ones
        setRequirements([...requirements, ...response.requirements])
      } else {
        // Replace with refined requirements
        setRequirements(response.requirements)
      }
      
      setIteration(response.iteration)
      setRefineFeedback('')
      setShowRefineSection(false)
    } catch (error: any) {
      console.error('Failed to refine requirements:', error)
      alert(error.response?.data?.detail || 'Failed to refine requirements')
    } finally {
      setRefining(false)
    }
  }

  const handleGenerateSpec = async () => {
    setGeneratingSpec(true)
    setError('')
    try {
      const response = await api.post('/specification/generate', {
        project_id: id
      })
      setSpecContent(response.data.specification)
      setSpecDocumentId(response.data.document_id)
      // Reload documents to show the new generated document
      fetchProject()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate specification')
      console.error('Failed to generate specification:', err)
    } finally {
      setGeneratingSpec(false)
    }
  }

  const handleGenerateArch = async () => {
    setGeneratingArch(true)
    setError('')
    try {
      const response = await api.post('/specification/architecture/generate', {
        project_id: id
      })
      setArchContent(response.data.architecture)
      setArchDiagrams(response.data.diagrams || [])
      setArchDocumentId(response.data.document_id)
      // Reload documents to show the new generated document
      fetchProject()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate architecture')
      console.error('Failed to generate architecture:', err)
    } finally {
      setGeneratingArch(false)
    }
  }

  const handleStepClick = async (stepId: string) => {
    console.log('🖱️ Step clicked:', stepId)
    switch (stepId) {
      case 'overview':
        window.scrollTo({ top: 0, behavior: 'smooth' })
        break
      case 'requirements':
        const requirementsSection = document.getElementById('requirements-section')
        if (requirementsSection) {
          requirementsSection.scrollIntoView({ behavior: 'smooth' })
        }
        break
      case 'specification':
        if (hasSpecification) {
          try {
            const response = await api.get(`/projects/${id}/documents`)
            const specDoc = response.data.find((d: any) => 
              d.category === 'specification' && d.is_generated
            )
            if (specDoc) {
              navigate(`/projects/${id}/documents/${specDoc.id}`)
            }
          } catch (error) {
            console.error('Failed to find specification document:', error)
          }
        } else {
          setShowSpecModal(true)
        }
        break
      case 'architecture':
        if (hasArchitecture) {
          try {
            const response = await api.get(`/projects/${id}/documents`)
            const archDoc = response.data.find((d: any) => 
              d.category === 'architecture' && d.is_generated
            )
            if (archDoc) {
              navigate(`/projects/${id}/documents/${archDoc.id}`)
            }
          } catch (error) {
            console.error('Failed to find architecture document:', error)
          }
        } else {
          setShowArchModal(true)
        }
        break
      case 'implementation':
        navigate(`/work-items?project_id=${id}`)
        break
      default:
        console.log('Unknown step:', stepId)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Project not found</p>
      </div>
    )
  }

  // Calculate project progress steps
  const progressSteps = [
    {
      id: 'overview',
      label: 'Visão Geral',
      completed: true, // Project exists
      current: false
    },
    {
      id: 'requirements',
      label: 'Requisitos',
      completed: workItemsCount > 0,
      current: workItemsCount === 0
    },
    {
      id: 'specification',
      label: 'Especificação',
      completed: hasSpecification,
      current: workItemsCount > 0 && !hasSpecification
    },
    {
      id: 'architecture',
      label: 'Arquitetura',
      completed: hasArchitecture,
      current: hasSpecification && !hasArchitecture
    },
    {
      id: 'implementation',
      label: 'Implementação',
      completed: false, // TODO: Check implementation status
      current: hasArchitecture
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/projects" className="text-gray-600 hover:text-gray-900">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
            <p className="text-gray-600">{project.description}</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 text-sm font-medium rounded-full ${
            project.status === 'active' 
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {project.status}
          </span>
          <Link
            to={`/projects/${id}/documents`}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <FileText className="h-4 w-4" />
            <span>Documents</span>
          </Link>
          <button
            onClick={() => setShowSpecModal(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <BookOpen className="h-4 w-4" />
            <span>Specification</span>
          </button>
          <button
            onClick={() => setShowArchModal(true)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Network className="h-4 w-4" />
            <span>Architecture</span>
          </button>
          <button
            onClick={openEditModal}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <Edit2 className="h-4 w-4" />
            <span>Edit</span>
          </button>
          <button
            onClick={() => setShowDeleteModal(true)}
            className="btn bg-red-600 hover:bg-red-700 text-white flex items-center space-x-2"
          >
            <Trash2 className="h-4 w-4" />
            <span>Delete</span>
          </button>
        </div>
      </div>

      {/* Project Progress */}
      <ProjectProgress steps={progressSteps} onStepClick={handleStepClick} />

      {/* Success Message */}
      {showSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-2">
          <Check className="h-5 w-5 text-green-500" />
          <span className="text-green-700">Requirements approved and work items created!</span>
        </div>
      )}

      {/* Generate Requirements */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Sparkles className="h-6 w-6 text-primary-600" />
            <h2 className="text-lg font-medium text-gray-900">Generate Requirements with AI</h2>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setInputMode('text')}
              className={`px-3 py-1 text-sm rounded-lg flex items-center space-x-1 ${
                inputMode === 'text'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Text</span>
            </button>
            <button
              onClick={() => setInputMode('upload')}
              className={`px-3 py-1 text-sm rounded-lg flex items-center space-x-1 ${
                inputMode === 'upload'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Upload className="h-4 w-4" />
              <span>Upload</span>
            </button>
            <button
              onClick={() => setInputMode('url')}
              className={`px-3 py-1 text-sm rounded-lg flex items-center space-x-1 ${
                inputMode === 'url'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              <Globe className="h-4 w-4" />
              <span>URL</span>
            </button>
          </div>
        </div>
        
        {inputMode === 'text' && (
          <form onSubmit={handleSubmit(onGenerate)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Describe your project requirements
              </label>
              <textarea
                {...register('description', { required: true })}
                className="input"
                rows={6}
                placeholder="Example: I need a web application for managing customer orders..."
                disabled={generating}
              />
            </div>
            
            <button
              type="submit"
              disabled={generating || isSubmitting}
              className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Generating with AI...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Generate Requirements</span>
                </>
              )}
            </button>
          </form>
        )}

        {inputMode === 'upload' && (
          <form onSubmit={handleSubmitUpload(onUpload)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Document (PDF, DOCX, TXT)
              </label>
              <input
                {...registerUpload('file', { required: true })}
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                className="input"
                disabled={uploading}
              />
              <p className="text-xs text-gray-500 mt-1">
                The AI will extract and analyze the content using RAG.
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                {...registerUpload('additional_context')}
                className="input"
                rows={3}
                placeholder="Add any additional context..."
                disabled={uploading}
              />
            </div>
            
            <button
              type="submit"
              disabled={uploading || isSubmittingUpload}
              className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              {uploading ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Processing Document with RAG...</span>
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4" />
                  <span>Upload & Generate</span>
                </>
              )}
            </button>
          </form>
        )}

        {inputMode === 'url' && (
          <form onSubmit={handleSubmitUrl(onUrlSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Web Page URL
              </label>
              <input
                {...registerUrl('url', { required: true })}
                type="url"
                className="input"
                placeholder="https://example.com/requirements"
                disabled={fetchingUrl}
              />
              <p className="text-xs text-gray-500 mt-1">
                The AI will scrape and analyze the web page content using RAG.
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Additional Context (Optional)
              </label>
              <textarea
                {...registerUrl('additional_context')}
                className="input"
                rows={3}
                placeholder="Add any additional context..."
                disabled={fetchingUrl}
              />
            </div>
            
            <button
              type="submit"
              disabled={fetchingUrl || isSubmittingUrl}
              className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
            >
              {fetchingUrl ? (
                <>
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>Fetching & Processing URL...</span>
                </>
              ) : (
                <>
                  <Globe className="h-4 w-4" />
                  <span>Fetch & Generate</span>
                </>
              )}
            </button>
          </form>
        )}
      </div>

      {/* Generated Requirements */}
      {requirements.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-medium text-gray-900">
                Generated Requirements ({requirements.length})
              </h2>
              {selectedRequirements.size > 0 && (
                <span className="text-sm text-gray-600">
                  {selectedRequirements.size} selected
                </span>
              )}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={toggleAll}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <Check className="h-4 w-4" />
                <span>{selectedRequirements.size === requirements.length ? 'Deselect All' : 'Select All'}</span>
              </button>
              <button
                onClick={() => {
                  setRequirements([])
                  setSelectedRequirements(new Set())
                }}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <X className="h-4 w-4" />
                <span>Clear All</span>
              </button>
              {selectedRequirements.size > 0 && (
                <button
                  onClick={onApproveSelected}
                  disabled={approving}
                  className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
                >
                  {approving ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Approving...</span>
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4" />
                      <span>Approve Selected ({selectedRequirements.size})</span>
                    </>
                  )}
                </button>
              )}
              <button
                onClick={onApprove}
                disabled={approving}
                className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
              >
                {approving ? (
                  <>
                    <Loader className="h-4 w-4 animate-spin" />
                    <span>Approving...</span>
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4" />
                    <span>Approve All</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="space-y-4">
            {requirements.map((req, index) => {
              const isGherkin = typeof req.user_story === 'object'
              const hasGherkinScenarios = req.acceptance_criteria.length > 0 && 
                typeof req.acceptance_criteria[0] === 'object'
              
              return (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex items-start space-x-3">
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedRequirements.has(index)}
                      onChange={() => toggleRequirement(index)}
                      className="mt-1 h-5 w-5 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                    />
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-3">
                        <h3 className="font-medium text-gray-900">{req.title}</h3>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          req.priority === 'high' 
                            ? 'bg-red-100 text-red-800'
                            : req.priority === 'medium'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {req.priority}
                        </span>
                      </div>
                      
                      {/* User Story */}
                      <div className="mb-4 p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
                        <p className="text-xs font-semibold text-blue-900 mb-2">USER STORY</p>
                        {isGherkin ? (
                          <div className="text-sm text-blue-800 space-y-1">
                            <p><span className="font-medium">As a</span> {(req.user_story as UserStory).as_a}</p>
                            <p><span className="font-medium">I want</span> {(req.user_story as UserStory).i_want}</p>
                            <p><span className="font-medium">So that</span> {(req.user_story as UserStory).so_that}</p>
                          </div>
                        ) : (
                          <p className="text-sm text-blue-800 italic">{req.user_story as string}</p>
                        )}
                      </div>
                      
                      {/* Business Context */}
                      {req.business_context && (
                        <div className="mb-4 p-3 bg-purple-50 border-l-4 border-purple-500 rounded">
                          <p className="text-xs font-semibold text-purple-900 mb-2">BUSINESS CONTEXT</p>
                          <p className="text-sm text-purple-800">{req.business_context}</p>
                        </div>
                      )}
                      
                      {/* Acceptance Criteria */}
                      <div className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
                        <p className="text-xs font-semibold text-green-900 mb-3">ACCEPTANCE CRITERIA</p>
                        {hasGherkinScenarios ? (
                          <div className="space-y-4">
                            {(req.acceptance_criteria as GherkinScenario[]).map((scenario, i) => (
                              <div key={i} className="bg-white p-3 rounded border border-green-200">
                                <p className="text-sm font-semibold text-green-900 mb-2">
                                  Scenario: {scenario.scenario}
                                </p>
                                <div className="text-sm text-gray-700 space-y-1 font-mono">
                                  <p><span className="text-blue-600 font-semibold">Given</span> {scenario.given}</p>
                                  <p><span className="text-purple-600 font-semibold">When</span> {scenario.when}</p>
                                  <p><span className="text-green-600 font-semibold">Then</span> {scenario.then}</p>
                                  {scenario.and && scenario.and.length > 0 && scenario.and.map((andItem, j) => (
                                    <p key={j}><span className="text-orange-600 font-semibold">And</span> {andItem}</p>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <ul className="list-disc list-inside space-y-1">
                            {(req.acceptance_criteria as string[]).map((criteria, i) => (
                              <li key={i} className="text-sm text-green-800">{criteria}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={() => removeRequirement(index)}
                      className="ml-4 text-gray-400 hover:text-red-600"
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Refine Requirements Section */}
      {requirements.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Refine Requirements</h2>
            <span className="text-sm text-gray-500">Iteration {iteration}</span>
          </div>
          
          {!showRefineSection ? (
            <div className="flex space-x-3">
              <button
                onClick={() => setShowRefineSection(true)}
                className="btn btn-secondary flex items-center space-x-2"
              >
                <Sparkles className="h-4 w-4" />
                <span>Refine with Feedback</span>
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provide feedback or additional requirements
                </label>
                <textarea
                  value={refineFeedback}
                  onChange={(e) => setRefineFeedback(e.target.value)}
                  className="input"
                  rows={4}
                  placeholder="Example: Add security requirements, Include performance criteria, Focus on mobile experience..."
                  disabled={refining}
                />
              </div>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => onRefineRequirements('add_more')}
                  disabled={refining || !refineFeedback.trim()}
                  className="btn btn-primary flex items-center space-x-2 disabled:opacity-50"
                >
                  {refining ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Add More Requirements</span>
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => onRefineRequirements('improve')}
                  disabled={refining || !refineFeedback.trim()}
                  className="btn btn-secondary flex items-center space-x-2 disabled:opacity-50"
                >
                  {refining ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>Improving...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      <span>Improve Existing</span>
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => {
                    setShowRefineSection(false)
                    setRefineFeedback('')
                  }}
                  className="btn btn-secondary"
                  disabled={refining}
                >
                  Cancel
                </button>
              </div>
              
              <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded">
                <p className="font-medium mb-1">Tips:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li><strong>Add More:</strong> Generates additional requirements based on your feedback</li>
                  <li><strong>Improve Existing:</strong> Refines current requirements to be more detailed</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Project Info */}
      <div className="card">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Project Information</h2>
        <dl className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <dt className="text-sm font-medium text-gray-500">Created</dt>
            <dd className="text-sm text-gray-900">{new Date(project.created_at).toLocaleDateString()}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
            <dd className="text-sm text-gray-900">{new Date(project.updated_at).toLocaleDateString()}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">Target Cloud</dt>
            <dd className="text-sm text-gray-900">{project.settings?.target_cloud || 'Not set'}</dd>
          </div>
          <div>
            <dt className="text-sm font-medium text-gray-500">MPS.BR Level</dt>
            <dd className="text-sm text-gray-900">{project.settings?.mps_br_level || 'Not set'}</dd>
          </div>
        </dl>
      </div>

      {/* Requirements Overview */}
      {projectWorkItems.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Requirements Overview</h2>
          
          {/* Statistics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">Total</p>
              <p className="text-2xl font-bold text-blue-900">{projectWorkItems.length}</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4">
              <p className="text-sm text-yellow-600 font-medium">Draft</p>
              <p className="text-2xl font-bold text-yellow-900">
                {projectWorkItems.filter(w => w.status === 'draft').length}
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Approved</p>
              <p className="text-2xl font-bold text-green-900">
                {projectWorkItems.filter(w => w.status === 'approved' || w.status === 'in_progress' || w.status === 'done').length}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Done</p>
              <p className="text-2xl font-bold text-purple-900">
                {projectWorkItems.filter(w => w.status === 'done').length}
              </p>
            </div>
          </div>
          
          {/* Requirements List */}
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-gray-700">Recent Requirements</h3>
            {projectWorkItems.slice(0, 5).map((item) => (
              <Link
                key={item.id}
                to={`/work-items/${item.id}`}
                className="block border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{item.title}</h4>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.description}</p>
                  </div>
                  <span className={`ml-4 px-2 py-1 text-xs font-medium rounded-full whitespace-nowrap ${
                    item.status === 'done'
                      ? 'bg-green-100 text-green-800'
                      : item.status === 'in_progress'
                      ? 'bg-blue-100 text-blue-800'
                      : item.status === 'approved'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {item.status}
                  </span>
                </div>
                <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                  <span>Type: {item.type}</span>
                  <span>Priority: {item.priority}</span>
                  <span>Created: {new Date(item.created_at).toLocaleDateString()}</span>
                </div>
              </Link>
            ))}
            
            {projectWorkItems.length > 5 && (
              <Link
                to={`/work-items?project_id=${id}`}
                className="block text-center text-sm text-primary-600 hover:text-primary-700 font-medium py-2"
              >
                View all {projectWorkItems.length} requirements →
              </Link>
            )}
          </div>
        </div>
      )}

      {/* Edit Project Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Edit Project</h2>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmitEdit(onEditProject)} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Name</label>
                <input
                  {...registerEdit('name', { required: true })}
                  className="input mt-1"
                  placeholder="Project name"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Description</label>
                <textarea
                  {...registerEdit('description')}
                  className="input mt-1"
                  rows={3}
                  placeholder="Project description"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <select {...registerEdit('status')} className="input mt-1">
                    <option value="active">Active</option>
                    <option value="archived">Archived</option>
                    <option value="on_hold">On Hold</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Target Cloud</label>
                  <select {...registerEdit('target_cloud')} className="input mt-1">
                    <option value="AWS">AWS</option>
                    <option value="Azure">Azure</option>
                    <option value="GCP">Google Cloud Platform</option>
                    <option value="OCI">Oracle Cloud Infrastructure</option>
                    <option value="Multi-Cloud">Multi-Cloud</option>
                    <option value="On-Premise">On-Premise</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">MPS.BR Level</label>
                <select {...registerEdit('mps_br_level')} className="input mt-1">
                  <option value="G">G - Parcialmente Gerenciado</option>
                  <option value="F">F - Gerenciado</option>
                  <option value="E">E - Parcialmente Definido</option>
                  <option value="D">D - Largamente Definido</option>
                  <option value="C">C - Definido</option>
                  <option value="B">B - Gerenciado Quantitativamente</option>
                  <option value="A">A - Em Otimização</option>
                </select>
              </div>
              
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingEdit}
                  className="btn btn-primary disabled:opacity-50"
                >
                  {isSubmittingEdit ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Delete Project</h2>
              <button
                onClick={() => setShowDeleteModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>{project.name}</strong>? 
              This action cannot be undone and will delete all associated work items and requirements.
            </p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="btn btn-secondary"
                disabled={deleting}
              >
                Cancel
              </button>
              <button
                onClick={onDeleteProject}
                disabled={deleting}
                className="btn bg-red-600 hover:bg-red-700 text-white disabled:opacity-50"
              >
                {deleting ? 'Deleting...' : 'Delete Project'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Specification Modal */}
      {showSpecModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Generate Specification
              </h2>
              <button 
                onClick={() => {
                  setShowSpecModal(false)
                  setSpecContent('')
                  setError('')
                }} 
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}
            
            {!specContent ? (
              <div className="space-y-4">
                <p className="text-gray-600">
                  Generate a detailed technical specification document based on approved requirements.
                  This will include functional requirements, non-functional requirements, business rules, and more.
                </p>
                <button
                  onClick={handleGenerateSpec}
                  disabled={generatingSpec}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {generatingSpec ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      Generating Specification...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Generate Specification
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="prose prose-sm max-w-none">
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800">
                      {specContent}
                    </pre>
                  </div>
                </div>
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
                  ✅ Especificação salva como documento do projeto! Acesse em "Documents" para editar.
                </div>
                
                <div className="flex gap-2">
                  {specDocumentId && (
                    <button 
                      onClick={() => navigate(`/projects/${id}/documents/${specDocumentId}`)} 
                      className="btn bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      📄 View Document
                    </button>
                  )}
                  <button 
                    onClick={() => {
                      setShowSpecModal(false)
                      setSpecContent('')
                    }} 
                    className="btn-primary"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => {
                      setSpecContent('')
                      setSpecDocumentId(null)
                      setError('')
                      handleGenerateSpec()
                    }}
                    className="btn-secondary"
                  >
                    Regenerate
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(specContent)
                      alert('Specification copied to clipboard!')
                    }}
                    className="btn-secondary"
                  >
                    Copy to Clipboard
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Architecture Modal */}
      {showArchModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Network className="h-5 w-5" />
                Generate Architecture
              </h2>
              <button 
                onClick={() => {
                  setShowArchModal(false)
                  setArchContent('')
                  setArchDiagrams([])
                  setError('')
                }} 
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {error}
              </div>
            )}
            
            {!archContent ? (
              <div className="space-y-4">
                <p className="text-gray-600">
                  Generate comprehensive architecture documentation with Mermaid diagrams based on project requirements.
                  This will include system architecture, component diagrams, data flow, and technical decisions.
                </p>
                <button
                  onClick={handleGenerateArch}
                  disabled={generatingArch}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {generatingArch ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      Generating Architecture...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Generate Architecture
                    </>
                  )}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="prose prose-sm max-w-none">
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800">
                      {archContent}
                    </pre>
                  </div>
                </div>
                
                {archDiagrams.length > 0 && (
                  <div className="mt-4">
                    <h3 className="text-lg font-semibold mb-2">Mermaid Diagrams ({archDiagrams.length})</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Copy these diagrams to visualize them in a Mermaid viewer or documentation tool.
                    </p>
                    {archDiagrams.map((diagram, index) => (
                      <div key={index} className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-blue-900">Diagram {index + 1}</span>
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(diagram)
                              alert(`Diagram ${index + 1} copied to clipboard!`)
                            }}
                            className="text-xs btn-secondary py-1 px-2"
                          >
                            Copy
                          </button>
                        </div>
                        <pre className="text-xs font-mono text-blue-800 whitespace-pre-wrap">
                          {diagram}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-800">
                  ✅ Arquitetura salva como documento do projeto! Acesse em "Documents" para editar.
                </div>
                
                <div className="flex gap-2">
                  {archDocumentId && (
                    <button 
                      onClick={() => navigate(`/projects/${id}/documents/${archDocumentId}`)} 
                      className="btn bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      📄 View Document
                    </button>
                  )}
                  <button 
                    onClick={() => {
                      setShowArchModal(false)
                      setArchContent('')
                      setArchDiagrams([])
                    }} 
                    className="btn-primary"
                  >
                    Close
                  </button>
                  <button
                    onClick={() => {
                      setArchContent('')
                      setArchDiagrams([])
                      setArchDocumentId(null)
                      setError('')
                      handleGenerateArch()
                    }}
                    className="btn-secondary"
                  >
                    Regenerate
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(archContent)
                      alert('Architecture copied to clipboard!')
                    }}
                    className="btn-secondary"
                  >
                    Copy Full Content
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
