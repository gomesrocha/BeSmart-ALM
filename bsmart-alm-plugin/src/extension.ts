import * as vscode from 'vscode';
import { StorageManager } from './data/StorageManager';
import { ConfigManager } from './data/ConfigManager';
import { CacheManager } from './data/CacheManager';
import { ApiClient } from './data/ApiClient';
import { AuthService } from './services/AuthService';
import { WorkItemService } from './services/WorkItemService';
import { SpecificationService } from './services/SpecificationService';
import { ArchitectureService } from './services/ArchitectureService';
import { AIService } from './services/AIService';
import { GitService } from './services/GitService';
import { ProjectService } from './services/ProjectService';
import { WorkItemTreeProvider } from './ui/WorkItemTreeProvider';
import { StatusBarManager } from './ui/StatusBarManager';
import { BsmartWebviewProvider } from './ui/BsmartWebviewProvider';

export function activate(context: vscode.ExtensionContext) {
    console.log('Bsmart-ALM plugin is now active');

    // Initialize services
    const storage = new StorageManager(context);
    const config = new ConfigManager();
    const cache = new CacheManager();
    const apiClient = new ApiClient(config.get('bsmart.serverUrl', 'http://localhost:8086'));
    const authService = new AuthService(storage, apiClient);
    const projectService = new ProjectService(authService, apiClient, storage);
    const workItemService = new WorkItemService(authService, apiClient, cache);
    const specificationService = new SpecificationService(authService, apiClient, cache);
    const architectureService = new ArchitectureService(authService, apiClient, cache);
    const aiService = new AIService(config);
    const gitService = new GitService(workItemService);

    // Initialize UI
    const treeProvider = new WorkItemTreeProvider(
        workItemService,
        projectService,
        specificationService,
        architectureService
    );
    const statusBar = new StatusBarManager();
    const webviewProvider = new BsmartWebviewProvider(
        context.extensionUri,
        authService,
        projectService,
        workItemService,
        aiService
    );

    // Register webview provider for sidebar panel
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            BsmartWebviewProvider.viewType,
            webviewProvider
        )
    );

    // Register tree view
    const treeView = vscode.window.createTreeView('bsmartWorkItems', {
        treeDataProvider: treeProvider,
        showCollapseAll: true
    });

    context.subscriptions.push(treeView);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.login', async () => {
            try {
                await authService.login();
                await treeProvider.refresh();
                webviewProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Login failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.logout', async () => {
            try {
                await authService.logout();
                await treeProvider.refresh();
                webviewProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Logout failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.selectProject', async () => {
            try {
                await projectService.selectProject();
                await treeProvider.refresh();
                webviewProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Project selection failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.refreshWorkItems', async () => {
            try {
                await treeProvider.refresh();
                webviewProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Refresh failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.openWorkItem', async (workItem) => {
            try {
                await workItemService.open(workItem);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to open work item: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.exportToAI', async (workItem) => {
            try {
                await aiService.export(workItem);
            } catch (error) {
                vscode.window.showErrorMessage(`Export failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.updateStatus', async (workItem, status) => {
            try {
                await workItemService.updateStatus(workItem.id, status);
                await treeProvider.refresh();
            } catch (error) {
                vscode.window.showErrorMessage(`Status update failed: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.addComment', async (workItem) => {
            try {
                const comment = await vscode.window.showInputBox({
                    prompt: 'Enter your comment',
                    placeHolder: 'Comment text...'
                });
                
                if (comment) {
                    await workItemService.addComment(workItem.id, comment);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to add comment: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.viewSpecification', async (projectId) => {
            try {
                const project = projectService.getSelectedProject();
                if (!project) {
                    vscode.window.showWarningMessage('No project selected');
                    return;
                }
                await specificationService.view(projectId || project.id, project.name);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to view specification: ${error}`);
            }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('bsmart.viewArchitecture', async (projectId) => {
            try {
                const project = projectService.getSelectedProject();
                if (!project) {
                    vscode.window.showWarningMessage('No project selected');
                    return;
                }
                await architectureService.view(projectId || project.id, project.name);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to view architecture: ${error}`);
            }
        })
    );

    // Initialize Git integration
    gitService.initialize();

    // Try auto-login
    authService.tryAutoLogin().then(async (success) => {
        if (success) {
            vscode.commands.executeCommand('setContext', 'bsmart.authenticated', true);
            await treeProvider.refresh();
            webviewProvider.refresh();
            
            // Load selected project if exists
            const selectedProject = projectService.getSelectedProject();
            if (selectedProject) {
                statusBar.updateProject(selectedProject);
            }
        }
    });
}

export function deactivate() {
    console.log('Bsmart-ALM plugin is now deactivated');
}
