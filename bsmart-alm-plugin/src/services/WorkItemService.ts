import * as vscode from 'vscode';
import { AuthService } from './AuthService';
import { ApiClient } from '../data/ApiClient';
import { CacheManager } from '../data/CacheManager';
import { WorkItem, WorkItemStatus } from '../types';

export class WorkItemService {
    private workItems: WorkItem[] = [];
    private currentWorkItem: WorkItem | null = null;

    constructor(
        private authService: AuthService,
        private apiClient: ApiClient,
        private cache: CacheManager
    ) {}

    async getWorkItems(projectId: string): Promise<WorkItem[]> {
        // Check cache first
        const cacheKey = `workitems:${projectId}`;
        const cached = this.cache.get<WorkItem[]>(cacheKey);
        if (cached) {
            console.log(`[WorkItemService] Returning ${cached.length} work items from cache`);
            this.workItems = cached;
            return cached;
        }

        // Fetch from API
        try {
            console.log(`[WorkItemService] Fetching work items for project ${projectId}`);
            const response = await this.apiClient.get<WorkItem[]>(
                `/api/v1/work-items?project_id=${projectId}`,
                this.authService.getAuthHeaders()
            );

            this.workItems = response.data;
            console.log(`[WorkItemService] Fetched ${this.workItems.length} work items`);
            
            // Cache for 5 minutes
            this.cache.set(cacheKey, this.workItems, 300000);

            return this.workItems;

        } catch (error) {
            console.error(`[WorkItemService] Failed to fetch work items:`, error);
            throw new Error(`Failed to fetch work items: ${error}`);
        }
    }

    async getMyWorkItems(projectId: string): Promise<WorkItem[]> {
        // Retorna TODOS os work items do projeto, não apenas os atribuídos
        return await this.getWorkItems(projectId);
    }

    async updateStatus(workItemId: string, status: WorkItemStatus): Promise<void> {
        try {
            await this.apiClient.patch(
                `/api/v1/work-items/${workItemId}`,
                { status },
                this.authService.getAuthHeaders()
            );

            // Update local cache
            const workItem = this.workItems.find(wi => wi.id === workItemId);
            if (workItem) {
                workItem.status = status;
            }

            // Invalidate cache
            this.cache.delete(`workitems:${workItem?.project_id}`);

            vscode.window.showInformationMessage(`Work item status updated to ${status}`);

        } catch (error) {
            throw new Error(`Failed to update status: ${error}`);
        }
    }

    async addComment(workItemId: string, comment: string): Promise<void> {
        try {
            await this.apiClient.post(
                `/api/v1/work-items/${workItemId}/comments`,
                { content: comment },
                this.authService.getAuthHeaders()
            );

            vscode.window.showInformationMessage('Comment added successfully');

        } catch (error) {
            throw new Error(`Failed to add comment: ${error}`);
        }
    }

    async open(workItem: WorkItem): Promise<void> {
        this.currentWorkItem = workItem;

        // Verificar se o work item já tem assignee
        const user = this.authService.getUser();
        if (!user) {
            vscode.window.showErrorMessage('Usuário não autenticado');
            return;
        }

        // Se não tem assignee, perguntar se quer se atribuir
        if (!workItem.assignee_id) {
            const shouldAssign = await vscode.window.showInformationMessage(
                `Deseja se atribuir como desenvolvedor de "${workItem.title}"?`,
                'Sim, Me Atribuir',
                'Não, Apenas Visualizar'
            );

            if (shouldAssign === 'Sim, Me Atribuir') {
                try {
                    await this.assignToMe(workItem.id);
                    workItem.assignee_id = user.id;
                    vscode.window.showInformationMessage(`Você foi atribuído ao work item "${workItem.title}"`);
                } catch (error) {
                    vscode.window.showErrorMessage(`Erro ao atribuir: ${error}`);
                }
            }
        }

        // Auto-update status to in_progress if not already
        if (workItem.status === 'ready' || workItem.status === 'backlog') {
            const shouldStart = await vscode.window.showInformationMessage(
                `Deseja iniciar o trabalho em "${workItem.title}"?`,
                'Sim, Iniciar',
                'Não'
            );

            if (shouldStart === 'Sim, Iniciar') {
                await this.updateStatus(workItem.id, 'in_progress');
                workItem.status = 'in_progress';
            }
        }

        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'workItemDetail',
            workItem.title,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getWorkItemHtml(workItem);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'exportToAI':
                        vscode.commands.executeCommand('bsmart.exportToAI', workItem);
                        break;
                    case 'updateStatus':
                        await this.updateStatus(workItem.id, message.status);
                        
                        // Show success message
                        if (message.status === 'done') {
                            vscode.window.showInformationMessage(
                                `✅ Work item "${workItem.title}" marcado como concluído!`
                            );
                        }
                        
                        // Refresh tree view
                        vscode.commands.executeCommand('bsmart.refreshWorkItems');
                        panel.dispose();
                        break;
                    case 'addComment':
                        const comment = await vscode.window.showInputBox({
                            prompt: 'Enter your comment',
                            placeHolder: 'Comment text...'
                        });
                        if (comment) {
                            await this.addComment(workItem.id, comment);
                        }
                        break;
                }
            },
            undefined,
            []
        );
    }

    async assignToMe(workItemId: string): Promise<void> {
        const user = this.authService.getUser();
        if (!user) {
            throw new Error('Not authenticated');
        }

        try {
            await this.apiClient.patch(
                `/api/v1/work-items/${workItemId}`,
                { assignee_id: user.id },
                this.authService.getAuthHeaders()
            );

            // Update local cache
            const workItem = this.workItems.find(wi => wi.id === workItemId);
            if (workItem) {
                workItem.assignee_id = user.id;
            }

            // Invalidate cache
            this.cache.delete(`workitems:${workItem?.project_id}`);

        } catch (error) {
            throw new Error(`Failed to assign work item: ${error}`);
        }
    }

    getCurrentWorkItem(): WorkItem | null {
        return this.currentWorkItem;
    }

    clearCache(): void {
        this.cache.clear();
    }

    private getWorkItemHtml(workItem: WorkItem): string {
        const statusColors: Record<WorkItemStatus, string> = {
            'backlog': '#6c757d',
            'ready': '#0d6efd',
            'in_progress': '#ffc107',
            'in_review': '#fd7e14',
            'done': '#198754',
            'blocked': '#dc3545'
        };

        const priorityColors = {
            'low': '#6c757d',
            'medium': '#0d6efd',
            'high': '#fd7e14',
            'critical': '#dc3545'
        };

        const statusLabels: Record<WorkItemStatus, string> = {
            'backlog': 'Backlog',
            'ready': 'Pronto',
            'in_progress': 'Em Progresso',
            'in_review': 'Em Revisão',
            'done': 'Concluído',
            'blocked': 'Bloqueado'
        };

        const priorityLabels = {
            'low': 'Baixa',
            'medium': 'Média',
            'high': 'Alta',
            'critical': 'Crítica'
        };

        return `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            padding: 20px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            line-height: 1.6;
        }
        
        .header {
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        h1 {
            color: var(--vscode-editor-foreground);
            margin-bottom: 15px;
            font-size: 24px;
        }
        
        .badges {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }
        
        .section {
            margin: 25px 0;
            padding: 20px;
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 6px;
            border-left: 3px solid var(--vscode-textLink-foreground);
        }
        
        .section h2 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 16px;
            color: var(--vscode-textLink-foreground);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section p {
            margin: 10px 0;
            line-height: 1.8;
        }
        
        ul {
            margin: 10px 0;
            padding-left: 25px;
        }
        
        li {
            margin: 8px 0;
            line-height: 1.6;
        }
        
        .actions {
            display: flex;
            gap: 12px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .btn-primary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        
        .btn-success {
            background: #198754;
            color: white;
        }
        
        .btn-warning {
            background: #ffc107;
            color: #000;
        }
        
        .btn-secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .icon {
            font-size: 16px;
        }
        
        .empty-state {
            color: var(--vscode-descriptionForeground);
            font-style: italic;
        }
        
        .work-item-id {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="work-item-id">ID: ${this.escapeHtml(workItem.id)}</div>
        <h1>${this.escapeHtml(workItem.title)}</h1>
        
        <div class="badges">
            <span class="badge" style="background-color: ${statusColors[workItem.status]}">
                ${statusLabels[workItem.status]}
            </span>
            <span class="badge" style="background-color: ${priorityColors[workItem.priority]}">
                Prioridade: ${priorityLabels[workItem.priority]}
            </span>
        </div>
    </div>
    
    <div class="section">
        <h2><span class="icon">📝</span> Descrição</h2>
        <p>${this.escapeHtml(workItem.description)}</p>
    </div>
    
    ${workItem.acceptance_criteria && workItem.acceptance_criteria.length > 0 ? `
    <div class="section">
        <h2><span class="icon">✅</span> Critérios de Aceitação</h2>
        <ul>
            ${workItem.acceptance_criteria.map(ac => `<li>${this.escapeHtml(ac)}</li>`).join('')}
        </ul>
    </div>
    ` : ''}
    
    ${workItem.specifications ? `
    <div class="section">
        <h2><span class="icon">🔧</span> Especificações Técnicas</h2>
        <p>${this.escapeHtml(workItem.specifications)}</p>
    </div>
    ` : ''}
    
    ${workItem.related_files && workItem.related_files.length > 0 ? `
    <div class="section">
        <h2><span class="icon">📁</span> Arquivos Relacionados</h2>
        <ul>
            ${workItem.related_files.map(file => `<li>${this.escapeHtml(file)}</li>`).join('')}
        </ul>
    </div>
    ` : ''}
    
    <div class="actions">
        <button class="btn-primary" onclick="exportToAI()">
            <span class="icon">🤖</span>
            Exportar para IA
        </button>
        
        ${workItem.status !== 'in_progress' && workItem.status !== 'done' ? `
            <button class="btn-warning" onclick="updateStatus('in_progress')">
                <span class="icon">▶️</span>
                Iniciar Trabalho
            </button>
        ` : ''}
        
        ${workItem.status === 'in_progress' ? `
            <button class="btn-success" onclick="updateStatus('done')">
                <span class="icon">✅</span>
                Marcar como Concluído
            </button>
        ` : ''}
        
        ${workItem.status !== 'done' ? `
            <button class="btn-secondary" onclick="addComment()">
                <span class="icon">💬</span>
                Adicionar Comentário
            </button>
        ` : ''}
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function exportToAI() {
            vscode.postMessage({ command: 'exportToAI' });
        }
        
        function updateStatus(status) {
            const confirmMessages = {
                'in_progress': 'Deseja iniciar o trabalho neste item?',
                'done': 'Deseja marcar este item como concluído?'
            };
            
            if (confirm(confirmMessages[status])) {
                vscode.postMessage({ command: 'updateStatus', status: status });
            }
        }
        
        function addComment() {
            vscode.postMessage({ command: 'addComment' });
        }
    </script>
</body>
</html>
        `;
    }

    private escapeHtml(text: string): string {
        const div = { textContent: text } as any;
        return div.innerHTML || text.replace(/[&<>"']/g, (m: string) => {
            const escapeMap: Record<string, string> = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            };
            return escapeMap[m];
        });
    }
}
