import * as vscode from 'vscode';
import { ConfigManager } from '../data/ConfigManager';
import { WorkItem } from '../types';

export class AIService {
    constructor(private config: ConfigManager) {}

    async export(workItem: WorkItem): Promise<void> {
        const context = this.buildContext(workItem);
        const defaultTool = this.config.getDefaultAITool();

        switch (defaultTool) {
            case 'copilot':
                await this.exportToCopilot(context);
                break;
            case 'continue':
                await this.exportToContinue(context);
                break;
            case 'kiro':
                await this.exportToKiro(context);
                break;
            case 'cursor':
                await this.exportToCursor(context);
                break;
            default:
                await this.exportToClipboard(context);
        }
    }

    private async exportToCopilot(context: string): Promise<void> {
        try {
            await vscode.commands.executeCommand(
                'github.copilot.interactiveSession.insertIntoNewSession',
                { message: context }
            );
            vscode.window.showInformationMessage('Context exported to GitHub Copilot');
        } catch (error) {
            console.log('Copilot not available, falling back to clipboard');
            await this.exportToClipboard(context);
        }
    }

    private async exportToContinue(context: string): Promise<void> {
        try {
            await vscode.commands.executeCommand('continue.sendMainUserInput', context);
            vscode.window.showInformationMessage('Context exported to Continue');
        } catch (error) {
            console.log('Continue not available, falling back to clipboard');
            await this.exportToClipboard(context);
        }
    }

    private async exportToKiro(context: string): Promise<void> {
        try {
            await vscode.commands.executeCommand('kiro.chat.sendMessage', context);
            vscode.window.showInformationMessage('Context exported to Kiro');
        } catch (error) {
            console.log('Kiro not available, falling back to clipboard');
            await this.exportToClipboard(context);
        }
    }

    private async exportToCursor(context: string): Promise<void> {
        try {
            await vscode.commands.executeCommand('cursor.chat.open', { message: context });
            vscode.window.showInformationMessage('Context exported to Cursor');
        } catch (error) {
            console.log('Cursor not available, falling back to clipboard');
            await this.exportToClipboard(context);
        }
    }

    private async exportToClipboard(context: string): Promise<void> {
        await vscode.env.clipboard.writeText(context);
        vscode.window.showInformationMessage('Context copied to clipboard');
    }

    private buildContext(workItem: WorkItem): string {
        const parts: string[] = [];

        parts.push(`# Work Item: ${workItem.title}`);
        parts.push('');
        parts.push(`**ID:** ${workItem.id}`);
        parts.push(`**Status:** ${workItem.status}`);
        parts.push(`**Priority:** ${workItem.priority}`);
        parts.push('');

        parts.push('## Description');
        parts.push(workItem.description);
        parts.push('');

        if (workItem.acceptance_criteria && workItem.acceptance_criteria.length > 0) {
            parts.push('## Acceptance Criteria');
            workItem.acceptance_criteria.forEach((ac, index) => {
                parts.push(`${index + 1}. ${ac}`);
            });
            parts.push('');
        }

        if (workItem.specifications) {
            parts.push('## Technical Specifications');
            parts.push(workItem.specifications);
            parts.push('');
        }

        if (workItem.related_files && workItem.related_files.length > 0) {
            parts.push('## Related Files');
            workItem.related_files.forEach(file => {
                parts.push(`- ${file}`);
            });
            parts.push('');
        }

        parts.push('---');
        parts.push('');
        parts.push('Please help me implement this work item following best practices:');
        parts.push('1. Write clean, maintainable code');
        parts.push('2. Add appropriate error handling');
        parts.push('3. Follow the existing code style');
        parts.push('4. Add comments for complex logic');
        parts.push('');
        parts.push('Focus on implementing exactly what\'s described in the acceptance criteria.');

        return parts.join('\n');
    }
}
