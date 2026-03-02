import * as vscode from 'vscode';
import { AuthService } from './AuthService';
import { ApiClient } from '../data/ApiClient';
import { CacheManager } from '../data/CacheManager';
import { Architecture } from '../types';

export class ArchitectureService {
    constructor(
        private authService: AuthService,
        private apiClient: ApiClient,
        private cache: CacheManager
    ) {}

    async getArchitecture(projectId: string): Promise<Architecture | null> {
        // Check cache first
        const cacheKey = `architecture:${projectId}`;
        const cached = this.cache.get<Architecture>(cacheKey);
        if (cached) {
            console.log(`[ArchitectureService] Returning architecture from cache`);
            return cached;
        }

        // Fetch from API
        try {
            console.log(`[ArchitectureService] Fetching architecture for project ${projectId}`);
            const response = await this.apiClient.get<any>(
                `/api/v1/architectures?project_id=${projectId}`,
                this.authService.getAuthHeaders()
            );

            // O backend pode retornar um array ou um objeto único
            const archData = Array.isArray(response.data) ? response.data[0] : response.data;
            
            if (!archData) {
                console.log(`[ArchitectureService] No architecture found for project`);
                return null;
            }

            const architecture: Architecture = {
                id: archData.id,
                project_id: archData.project_id,
                content: archData.content || archData.architecture || '',
                diagram_url: archData.diagram_url,
                created_at: archData.created_at,
                updated_at: archData.updated_at
            };
            
            console.log(`[ArchitectureService] Fetched architecture`);
            
            // Cache for 10 minutes
            this.cache.set(cacheKey, architecture, 600000);

            return architecture;

        } catch (error) {
            console.error(`[ArchitectureService] Failed to fetch architecture:`, error);
            // Return null if not found (404) instead of throwing
            return null;
        }
    }

    async view(projectId: string, projectName: string): Promise<void> {
        const architecture = await this.getArchitecture(projectId);

        if (!architecture) {
            vscode.window.showInformationMessage('Este projeto ainda não possui arquitetura definida');
            return;
        }

        // Create webview panel
        const panel = vscode.window.createWebviewPanel(
            'architectureView',
            `🏗️ Architecture - ${projectName}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = this.getArchitectureHtml(architecture, projectName);
    }

    private getArchitectureHtml(arch: Architecture, projectName: string): string {
        // Convert markdown-like content to HTML
        const contentHtml = this.markdownToHtml(arch.content);

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
            padding: 30px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            line-height: 1.8;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--vscode-panel-border);
        }
        
        h1 {
            color: var(--vscode-editor-foreground);
            margin-bottom: 10px;
            font-size: 32px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .project-name {
            font-size: 16px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 15px;
        }
        
        .meta {
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
        }
        
        .content {
            margin-top: 30px;
        }
        
        .content h2 {
            margin-top: 30px;
            margin-bottom: 15px;
            color: var(--vscode-textLink-foreground);
            font-size: 24px;
        }
        
        .content h3 {
            margin-top: 25px;
            margin-bottom: 12px;
            color: var(--vscode-textLink-foreground);
            font-size: 18px;
        }
        
        .content p {
            margin: 15px 0;
            line-height: 1.8;
        }
        
        .content ul, .content ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        .content li {
            margin: 8px 0;
            line-height: 1.6;
        }
        
        .content code {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family);
            font-size: 0.9em;
        }
        
        .content pre {
            background-color: var(--vscode-textCodeBlock-background);
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            margin: 15px 0;
        }
        
        .content pre code {
            background: none;
            padding: 0;
        }
        
        .diagram {
            margin: 30px 0;
            padding: 20px;
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            text-align: center;
        }
        
        .diagram img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1><span>🏗️</span> Arquitetura</h1>
        <div class="project-name">Projeto: ${this.escapeHtml(projectName)}</div>
        <div class="meta">
            <span>Atualizado: ${new Date(arch.updated_at).toLocaleDateString('pt-BR')}</span>
        </div>
    </div>
    
    ${arch.diagram_url ? `
    <div class="diagram">
        <img src="${this.escapeHtml(arch.diagram_url)}" alt="Architecture Diagram" />
    </div>
    ` : ''}
    
    <div class="content">
        ${contentHtml}
    </div>
</body>
</html>
        `;
    }

    private markdownToHtml(content: string): string {
        // Simple markdown to HTML conversion
        let html = this.escapeHtml(content);
        
        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h2>$1</h2>');
        
        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Code blocks
        html = html.replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>');
        
        // Inline code
        html = html.replace(/`(.+?)`/g, '<code>$1</code>');
        
        // Lists
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
        
        // Paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        html = '<p>' + html + '</p>';
        
        return html;
    }

    private escapeHtml(text: string): string {
        return text.replace(/[&<>"']/g, (m: string) => {
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
