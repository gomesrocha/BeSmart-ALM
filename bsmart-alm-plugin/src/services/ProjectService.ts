import * as vscode from 'vscode';
import { AuthService } from './AuthService';
import { ApiClient } from '../data/ApiClient';
import { StorageManager } from '../data/StorageManager';
import { Project } from '../types';

export class ProjectService {
    private projects: Project[] = [];
    private selectedProject: Project | null = null;

    constructor(
        private authService: AuthService,
        private apiClient: ApiClient,
        private storage: StorageManager
    ) {
        // Load selected project from storage
        const stored = this.storage.get<Project>('bsmart.selectedProject');
        if (stored) {
            this.selectedProject = stored;
        }
    }

    async getProjects(): Promise<Project[]> {
        try {
            const user = this.authService.getUser();
            if (!user) {
                throw new Error('Not authenticated');
            }

            const response = await this.apiClient.get<Project[]>(
                '/api/v1/projects',
                this.authService.getAuthHeaders()
            );

            this.projects = response.data.filter(p => p.status === 'active');
            return this.projects;

        } catch (error) {
            throw new Error(`Failed to fetch projects: ${error}`);
        }
    }

    async selectProject(): Promise<void> {
        const projects = await this.getProjects();

        if (projects.length === 0) {
            vscode.window.showWarningMessage('No active projects found');
            return;
        }

        const items = projects.map(p => ({
            label: p.name,
            description: p.description,
            project: p
        }));

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a project'
        });

        if (selected) {
            this.selectedProject = selected.project;
            this.storage.store('bsmart.selectedProject', this.selectedProject);
            
            vscode.window.showInformationMessage(`Selected project: ${this.selectedProject.name}`);
            
            // Trigger refresh of work items
            vscode.commands.executeCommand('bsmart.refreshWorkItems');
        }
    }

    getSelectedProject(): Project | null {
        return this.selectedProject;
    }

    clearSelection(): void {
        this.selectedProject = null;
        this.storage.delete('bsmart.selectedProject');
    }
}
