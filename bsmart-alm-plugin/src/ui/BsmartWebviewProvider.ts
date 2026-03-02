import * as vscode from 'vscode';
import { AuthService } from '../services/AuthService';
import { ProjectService } from '../services/ProjectService';
import { WorkItemService } from '../services/WorkItemService';
import { AIService } from '../services/AIService';
import { WorkItem } from '../types';

export class BsmartWebviewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'bsmartDashboard';
    
    private _view?: vscode.WebviewView;
    
    constructor(
        private readonly _extensionUri: vscode.Uri,
        private authService: AuthService,
        private projectService: ProjectService,
        private workItemService: WorkItemService,
        private aiService: AIService
    ) {}
    
    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken,
    ) {
        this._view = webviewView;
        
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };
        
        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
        
        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'login':
                    try {
                        await vscode.commands.executeCommand('bsmart.login');
                        this.refresh();
                    } catch (error) {
                        vscode.window.showErrorMessage(`Login failed: ${error}`);
                    }
                    break;
                    
                case 'logout':
                    try {
                        await vscode.commands.executeCommand('bsmart.logout');
                        this.refresh();
                    } catch (error) {
                        vscode.window.showErrorMessage(`Logout failed: ${error}`);
                    }
                    break;
                    
                case 'selectProject':
                    try {
                        await vscode.commands.executeCommand('bsmart.selectProject');
                        this.refresh();
                    } catch (error) {
                        vscode.window.showErrorMessage(`Project selection failed: ${error}`);
                    }
                    break;
                    
                case 'refreshWorkItems':
                    try {
                        await vscode.commands.executeCommand('bsmart.refreshWorkItems');
                        this.refresh();
                    } catch (error) {
                        vscode.window.showErrorMessage(`Refresh failed: ${error}`);
                    }
                    break;
                    
                case 'openWorkItem':
                    try {
                        const workItem = data.workItem as WorkItem;
                        await vscode.commands.executeCommand('bsmart.openWorkItem', workItem);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Failed to open work item: ${error}`);
                    }
                    break;
                    
                case 'exportToAI':
                    try {
                        const workItem = data.workItem as WorkItem;
                        await vscode.commands.executeCommand('bsmart.exportToAI', workItem);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Export failed: ${error}`);
                    }
                    break;
            }
        });
        
        // Initial load
        this.refresh();
    }
    
    public refresh() {
        if (this._view) {
            this._view.webview.html = this._getHtmlForWebview(this._view.webview);
        }
    }
    
    private _getHtmlForWebview(webview: vscode.Webview) {
        const isAuthenticated = this.authService.isAuthenticated();
        const user = this.authService.getUser();
        const selectedProject = this.projectService.getSelectedProject();
        
        return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bsmart-ALM</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-sideBar-background);
            padding: 16px;
            font-size: 13px;
        }
        
        .header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
        }
        
        .logo {
            font-size: 18px;
            font-weight: 600;
            color: var(--vscode-textLink-foreground);
        }
        
        .section {
            margin-bottom: 20px;
        }
        
        .section-title {
            font-size: 11px;
            font-weight: 600;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: 0.5px;
        }
        
        .user-info, .project-info {
            background: var(--vscode-editor-inactiveSelectionBackground);
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 8px;
        }
        
        .user-name, .project-name {
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .user-email, .project-desc {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
        }
        
        button {
            width: 100%;
            padding: 8px 12px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-bottom: 8px;
            transition: background 0.2s;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        button.secondary {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        button.secondary:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .empty-state {
            text-align: center;
            color: var(--vscode-descriptionForeground);
            font-style: italic;
            padding: 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <span class="logo">🚀 Bsmart-ALM</span>
    </div>
    
    ${!isAuthenticated ? `
        <div class="section">
            <div class="empty-state">
                <p>Faça login para começar</p>
            </div>
            <button onclick="login()">🔑 Fazer Login</button>
        </div>
    ` : `
        <div class="section">
            <div class="section-title">Usuário</div>
            <div class="user-info">
                <div class="user-name">${user?.full_name || 'Usuário'}</div>
                <div class="user-email">${user?.email || ''}</div>
            </div>
            <button class="secondary" onclick="logout()">Sair</button>
        </div>
        
        <div class="section">
            <div class="section-title">Projeto</div>
            ${selectedProject ? `
                <div class="project-info">
                    <div class="project-name">${selectedProject.name}</div>
                    <div class="project-desc">${selectedProject.description || 'Sem descrição'}</div>
                </div>
            ` : `
                <div class="empty-state">
                    <p>Nenhum projeto selecionado</p>
                </div>
            `}
            <button onclick="selectProject()">📁 Selecionar Projeto</button>
        </div>
        
        ${selectedProject ? `
            <div class="section">
                <div class="section-title">Work Items</div>
                <div class="empty-state">
                    <p>Clique em "Atualizar" para carregar work items</p>
                </div>
                <button onclick="refreshWorkItems()">🔄 Atualizar</button>
            </div>
        ` : ''}
    `}
    
    <script>
        const vscode = acquireVsCodeApi();
        
        function login() {
            vscode.postMessage({ type: 'login' });
        }
        
        function logout() {
            vscode.postMessage({ type: 'logout' });
        }
        
        function selectProject() {
            vscode.postMessage({ type: 'selectProject' });
        }
        
        function refreshWorkItems() {
            vscode.postMessage({ type: 'refreshWorkItems' });
        }
    </script>
</body>
</html>`;
    }
}
