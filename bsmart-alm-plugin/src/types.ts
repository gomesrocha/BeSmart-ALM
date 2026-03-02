export interface User {
    id: string;
    email: string;
    full_name: string;
    tenant_id: string;
    is_superuser: boolean;
}

export interface Project {
    id: string;
    name: string;
    description: string;
    tenant_id: string;
    status: 'active' | 'inactive' | 'archived';
}

export type WorkItemStatus = 'backlog' | 'ready' | 'in_progress' | 'in_review' | 'done' | 'blocked';

export interface WorkItem {
    id: string;
    title: string;
    description: string;
    status: WorkItemStatus;
    priority: 'low' | 'medium' | 'high' | 'critical';
    assignee_id?: string;
    project_id: string;
    acceptance_criteria?: string[];
    specifications?: string;
    related_files?: string[];
    created_at: string;
    updated_at: string;
}

export interface Specification {
    id: string;
    project_id: string;
    content: string;
    version?: string;
    created_at: string;
    updated_at: string;
}

export interface Architecture {
    id: string;
    project_id: string;
    content: string;
    diagram_url?: string;
    created_at: string;
    updated_at: string;
}

export interface ApiResponse<T = any> {
    data: T;
    status: number;
}

export interface CacheEntry {
    value: any;
    expiry: number;
}

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = 'ApiError';
    }
}
