export interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'archived' | 'on_hold'
  settings: Record<string, any>
  created_at: string
  updated_at: string
}

export interface WorkItem {
  id: string
  project_id: string
  type: 'requirement' | 'user_story' | 'task' | 'defect' | 'nfr'
  title: string
  description: string
  status: 'draft' | 'in_review' | 'approved' | 'rejected' | 'in_progress' | 'done'
  version: number
  created_by: string
  assigned_to?: string
  created_at: string
  updated_at: string
}

export interface User {
  id: string
  email: string
  full_name: string
  tenant_id: string
  is_active: boolean
  created_at: string
}
