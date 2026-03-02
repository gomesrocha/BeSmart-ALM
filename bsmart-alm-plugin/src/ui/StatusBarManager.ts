import * as vscode from 'vscode';
import { Project, WorkItem } from '../types';

export class StatusBarManager {
    private projectItem: vscode.StatusBarItem;
    private workItemItem: vscode.StatusBarItem;

    constructor() {
        // Create status bar items
        this.projectItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            100
        );
        
        this.workItemItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            99
        );

        // Set default state
        this.projectItem.text = '$(project) No Project';
        this.projectItem.tooltip = 'Click to select a project';
        this.projectItem.command = 'bsmart.selectProject';
        this.projectItem.show();
    }

    updateProject(project: Project): void {
        this.projectItem.text = `$(project) ${project.name}`;
        this.projectItem.tooltip = `Project: ${project.name}\n${project.description}`;
        this.projectItem.command = 'bsmart.selectProject';
        this.projectItem.show();
    }

    updateWorkItem(workItem: WorkItem): void {
        this.workItemItem.text = `$(checklist) ${this.truncate(workItem.title, 30)}`;
        this.workItemItem.tooltip = `Work Item: ${workItem.title}\nStatus: ${workItem.status}\nPriority: ${workItem.priority}`;
        this.workItemItem.command = {
            command: 'bsmart.openWorkItem',
            title: 'Open Work Item',
            arguments: [workItem]
        };
        this.workItemItem.show();
    }

    showProgress(message: string): void {
        this.workItemItem.text = `$(sync~spin) ${message}`;
        this.workItemItem.tooltip = message;
        this.workItemItem.show();
    }

    hideProgress(): void {
        this.workItemItem.hide();
    }

    clearWorkItem(): void {
        this.workItemItem.hide();
    }

    clearProject(): void {
        this.projectItem.text = '$(project) No Project';
        this.projectItem.tooltip = 'Click to select a project';
        this.projectItem.show();
    }

    dispose(): void {
        this.projectItem.dispose();
        this.workItemItem.dispose();
    }

    private truncate(text: string, maxLength: number): string {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength - 3) + '...';
    }
}
