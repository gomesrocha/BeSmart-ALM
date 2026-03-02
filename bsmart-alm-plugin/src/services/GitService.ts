import * as vscode from 'vscode';
import { WorkItemService } from './WorkItemService';

interface GitExtension {
    getAPI(version: number): GitAPI;
}

interface GitAPI {
    repositories: Repository[];
    onDidOpenRepository: vscode.Event<Repository>;
    onDidCloseRepository: vscode.Event<Repository>;
}

interface Repository {
    state: RepositoryState;
    inputBox: InputBox;
}

interface RepositoryState {
    HEAD: Branch | undefined;
    onDidChange: vscode.Event<void>;
}

interface Branch {
    name: string | undefined;
    commit: string | undefined;
}

interface InputBox {
    value: string;
}

export class GitService {
    private gitExtension: GitExtension | undefined;
    private gitAPI: GitAPI | undefined;

    constructor(private workItemService: WorkItemService) {}

    async initialize(): Promise<void> {
        try {
            const extension = vscode.extensions.getExtension<GitExtension>('vscode.git');
            
            if (!extension) {
                console.log('Git extension not found');
                return;
            }

            if (!extension.isActive) {
                await extension.activate();
            }

            this.gitExtension = extension.exports;
            this.gitAPI = this.gitExtension.getAPI(1);

            // Listen to repository changes
            if (this.gitAPI.repositories.length > 0) {
                this.setupRepositoryListeners(this.gitAPI.repositories[0]);
            }

            this.gitAPI.onDidOpenRepository(repo => {
                this.setupRepositoryListeners(repo);
            });

        } catch (error) {
            console.error('Failed to initialize Git integration:', error);
        }
    }

    private setupRepositoryListeners(repo: Repository): void {
        // Listen to state changes (commits, etc.)
        repo.state.onDidChange(() => {
            this.handleRepositoryChange(repo);
        });
    }

    private async handleRepositoryChange(repo: Repository): Promise<void> {
        try {
            const head = repo.state.HEAD;
            if (!head || !head.commit) {
                return;
            }

            // Get commit message from input box
            const commitMessage = repo.inputBox.value;
            
            if (commitMessage) {
                const workItemId = this.extractWorkItemId(commitMessage);
                
                if (workItemId) {
                    // Add commit info to work item
                    await this.workItemService.addComment(
                        workItemId,
                        `Commit: ${head.commit.substring(0, 7)} - ${commitMessage}`
                    );
                }
            }
        } catch (error) {
            console.error('Error handling repository change:', error);
        }
    }

    private extractWorkItemId(commitMessage: string): string | null {
        // Extract work item ID from commit message
        // Supports formats: [WI-123], #WI-123, WI-123
        const patterns = [
            /\[WI-(\w+)\]/i,
            /#WI-(\w+)/i,
            /WI-(\w+)/i
        ];

        for (const pattern of patterns) {
            const match = commitMessage.match(pattern);
            if (match) {
                return match[1];
            }
        }

        return null;
    }

    async createBranch(workItemId: string, title: string): Promise<void> {
        if (!this.gitAPI || this.gitAPI.repositories.length === 0) {
            vscode.window.showWarningMessage('No Git repository found');
            return;
        }

        const repo = this.gitAPI.repositories[0];
        const branchName = `wi-${workItemId}-${this.slugify(title)}`;

        try {
            // Create and checkout new branch
            await vscode.commands.executeCommand('git.branch', branchName);
            await vscode.commands.executeCommand('git.checkout', branchName);

            vscode.window.showInformationMessage(`Created branch: ${branchName}`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create branch: ${error}`);
        }
    }

    private slugify(text: string): string {
        return text
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '-')
            .replace(/^-+|-+$/g, '')
            .substring(0, 50);
    }
}
