import * as vscode from 'vscode';
import { WorkItemService } from '../services/WorkItemService';
import { ProjectService } from '../services/ProjectService';
import { SpecificationService } from '../services/SpecificationService';
import { ArchitectureService } from '../services/ArchitectureService';
import { WorkItem, WorkItemStatus } from '../types';

export class WorkItemTreeProvider implements vscode.TreeDataProvider<WorkItemTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<WorkItemTreeItem | undefined | null | void> = 
        new vscode.EventEmitter<WorkItemTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<WorkItemTreeItem | undefined | null | void> = 
        this._onDidChangeTreeData.event;

    constructor(
        private workItemService: WorkItemService,
        private projectService: ProjectService,
        private specificationService: SpecificationService,
        private architectureService: ArchitectureService
    ) {}

    async refresh(): Promise<void> {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: WorkItemTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: WorkItemTreeItem): Promise<WorkItemTreeItem[]> {
        const selectedProject = this.projectService.getSelectedProject();

        if (!selectedProject) {
            return [new WorkItemTreeItem(
                'No project selected',
                'Click to select a project',
                vscode.TreeItemCollapsibleState.None,
                null,
                'info',
                null
            )];
        }

        if (!element) {
            // Root level - show project structure
            return [
                new WorkItemTreeItem(
                    '📋 Specification',
                    'View project specification',
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'specification',
                    selectedProject.id
                ),
                new WorkItemTreeItem(
                    '🏗️ Architecture',
                    'View project architecture',
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'architecture',
                    selectedProject.id
                ),
                new WorkItemTreeItem(
                    '📝 Work Items',
                    'All project work items',
                    vscode.TreeItemCollapsibleState.Expanded,
                    null,
                    'workitems-group',
                    selectedProject.id
                )
            ];
        }

        // If element is work items group, show work items
        if (element.contextValue === 'workitems-group') {
            try {
                const workItems = await this.workItemService.getMyWorkItems(selectedProject.id);
                
                if (workItems.length === 0) {
                    return [new WorkItemTreeItem(
                        'No work items found',
                        'This project has no work items yet',
                        vscode.TreeItemCollapsibleState.None,
                        null,
                        'info',
                        null
                    )];
                }

                return workItems.map(wi => new WorkItemTreeItem(
                    wi.title,
                    `${wi.status} • ${wi.priority}`,
                    vscode.TreeItemCollapsibleState.None,
                    wi,
                    'workitem',
                    null
                ));

            } catch (error) {
                return [new WorkItemTreeItem(
                    'Error loading work items',
                    String(error),
                    vscode.TreeItemCollapsibleState.None,
                    null,
                    'error',
                    null
                )];
            }
        }

        return [];
    }
}

export class WorkItemTreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly workItem: WorkItem | null,
        public readonly contextValue: string,
        public readonly projectId: string | null
    ) {
        super(label, collapsibleState);
        
        this.description = description;
        this.contextValue = contextValue;

        if (workItem) {
            this.tooltip = this.buildTooltip(workItem);
            this.iconPath = this.getIconForStatus(workItem.status);
            
            // Make it clickable
            this.command = {
                command: 'bsmart.openWorkItem',
                title: 'Open Work Item',
                arguments: [workItem]
            };
        } else if (contextValue === 'specification') {
            this.iconPath = new vscode.ThemeIcon('book');
            this.command = {
                command: 'bsmart.viewSpecification',
                title: 'View Specification',
                arguments: [projectId]
            };
        } else if (contextValue === 'architecture') {
            this.iconPath = new vscode.ThemeIcon('symbol-structure');
            this.command = {
                command: 'bsmart.viewArchitecture',
                title: 'View Architecture',
                arguments: [projectId]
            };
        } else if (contextValue === 'workitems-group') {
            this.iconPath = new vscode.ThemeIcon('checklist');
        } else if (contextValue === 'info') {
            this.iconPath = new vscode.ThemeIcon('info');
            
            if (label === 'No project selected') {
                this.command = {
                    command: 'bsmart.selectProject',
                    title: 'Select Project'
                };
            }
        } else if (contextValue === 'error') {
            this.iconPath = new vscode.ThemeIcon('error');
        }
    }

    private buildTooltip(workItem: WorkItem): string {
        const parts: string[] = [];
        
        parts.push(`**${workItem.title}**`);
        parts.push('');
        parts.push(`Status: ${workItem.status}`);
        parts.push(`Priority: ${workItem.priority}`);
        parts.push('');
        parts.push(workItem.description.substring(0, 200));
        
        if (workItem.description.length > 200) {
            parts.push('...');
        }

        return parts.join('\n');
    }

    private getIconForStatus(status: WorkItemStatus): vscode.ThemeIcon {
        const iconMap: Record<WorkItemStatus, string> = {
            'backlog': 'circle-outline',
            'ready': 'circle',
            'in_progress': 'sync~spin',
            'in_review': 'eye',
            'done': 'check',
            'blocked': 'error'
        };

        const colorMap: Record<WorkItemStatus, vscode.ThemeColor> = {
            'backlog': new vscode.ThemeColor('charts.gray'),
            'ready': new vscode.ThemeColor('charts.blue'),
            'in_progress': new vscode.ThemeColor('charts.yellow'),
            'in_review': new vscode.ThemeColor('charts.orange'),
            'done': new vscode.ThemeColor('charts.green'),
            'blocked': new vscode.ThemeColor('charts.red')
        };

        return new vscode.ThemeIcon(iconMap[status], colorMap[status]);
    }
}
