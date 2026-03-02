# Design Document - IDE Plugin for Bsmart-ALM

## Overview

Plugin extensível para IDEs modernos (VS Code, Kiro, Cursor) que integra o Bsmart-ALM diretamente no ambiente de desenvolvimento. O plugin permite autenticação, visualização de work items, exportação de contexto para ferramentas de IA, e sincronização automática com Git.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      IDE PLUGIN                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  UI Layer    │    │ Business     │    │  Data Layer  │ │
│  │              │    │ Logic        │    │              │ │
│  │ - TreeView   │◄──►│ - Auth       │◄──►│ - API Client │ │
│  │ - StatusBar  │    │ - WorkItems  │    │ - Cache      │ │
│  │ - Commands   │    │ - Projects   │    │ - Storage    │ │
│  │ - Webview    │    │ - AI Export  │    │              │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                  External Integrations                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐          │
│  │ Bsmart-ALM │  │    Git     │  │  AI Tools  │          │
│  │    API     │  │   Hooks    │  │            │          │
│  │            │  │            │  │ - Copilot  │          │
│  │ - Auth     │  │ - Commit   │  │ - Continue │          │
│  │ - Projects │  │ - Push     │  │ - Kiro     │          │
│  │ - WorkItems│  │ - Branch   │  │ - Cursor   │          │
│  └────────────┘  └────────────┘  └────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. UI Layer

#### TreeView Component
Exibe work items em estrutura hierárquica no sidebar da IDE.

```typescript
interface WorkItemTreeProvider {
  getChildren(element?: WorkItem): WorkItem[]
  getTreeItem(element: WorkItem): TreeItem
  refresh(): void
  onDidChangeTreeData: Event<WorkItem | undefined>
}

class WorkItemTreeItem extends TreeItem {
  constructor(
    public readonly workItem: WorkItem,
    public readonly collapsibleState: TreeItemCollapsibleState
  ) {
    super(workItem.title, collapsibleState)
    this.tooltip = workItem.description
    this.contextValue = 'workitem'
    this.iconPath = this.getIconForStatus(workItem.status)
    this.command = {
      command: 'bsmart.openWorkItem',
      title: 'Open Work Item',
      arguments: [workItem]
    }
  }
  
  private getIconForStatus(status: string): ThemeIcon {
    const iconMap = {
      'backlog': new ThemeIcon('circle-outline'),
      'ready': new ThemeIcon('circle'),
      'in_progress': new ThemeIcon('sync'),
      'in_review': new ThemeIcon('eye'),
      'done': new ThemeIcon('check'),
      'blocked': new ThemeIcon('error')
    }
    return iconMap[status] || new ThemeIcon('circle')
  }
}
```

#### Status Bar Component
Mostra informações do projeto e work item atual na barra de status.

```typescript
class StatusBarManager {
  private projectItem: StatusBarItem
  private workItemItem: StatusBarItem
  
  constructor() {
    this.projectItem = window.createStatusBarItem(StatusBarAlignment.Left, 100)
    this.workItemItem = window.createStatusBarItem(StatusBarAlignment.Left, 99)
  }
  
  updateProject(project: Project): void {
    this.projectItem.text = `$(project) ${project.name}`
    this.projectItem.tooltip = project.description
    this.projectItem.command = 'bsmart.selectProject'
    this.projectItem.show()
  }
  
  updateWorkItem(workItem: WorkItem): void {
    this.workItemItem.text = `$(checklist) ${workItem.title}`
    this.workItemItem.tooltip = `Status: ${workItem.status}`
    this.workItemItem.command = 'bsmart.openWorkItem'
    this.workItemItem.show()
  }
  
  showProgress(message: string): void {
    this.workItemItem.text = `$(sync~spin) ${message}`
  }
}
```

#### Command Palette
Registra comandos disponíveis para o usuário.

```typescript
const commands = {
  'bsmart.login': () => authService.login(),
  'bsmart.logout': () => authService.logout(),
  'bsmart.selectProject': () => projectService.selectProject(),
  'bsmart.refreshWorkItems': () => workItemService.refresh(),
  'bsmart.openWorkItem': (workItem: WorkItem) => workItemService.open(workItem),
  'bsmart.exportToAI': (workItem: WorkItem) => aiService.export(workItem),
  'bsmart.updateStatus': (workItem: WorkItem, status: string) => 
    workItemService.updateStatus(workItem, status),
  'bsmart.addComment': (workItem: WorkItem) => workItemService.addComment(workItem)
}
```

### 2. Business Logic Layer

#### Authentication Service
Gerencia autenticação e tokens JWT.

```typescript
class AuthService {
  private token: string | null = null
  private user: User | null = null
  private storage: StorageManager
  
  constructor(storage: StorageManager) {
    this.storage = storage
  }
  
  async login(): Promise<void> {
    // Show login form
    const credentials = await this.showLoginForm()
    
    // Authenticate
    const response = await fetch(`${this.getServerUrl()}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    })
    
    if (response.ok) {
      const data = await response.json()
      this.token = data.access_token
      await this.storage.storeSecurely('bsmart.token', data.access_token)
      await this.loadUserInfo()
      window.showInformationMessage('Successfully logged in to Bsmart-ALM')
    } else {
      throw new Error('Login failed')
    }
  }
  
  async logout(): Promise<void> {
    this.token = null
    this.user = null
    await this.storage.deleteSecurely('bsmart.token')
    window.showInformationMessage('Logged out from Bsmart-ALM')
  }
  
  async tryAutoLogin(): Promise<boolean> {
    const token = await this.storage.getSecurely('bsmart.token')
    if (token) {
      this.token = token
      try {
        await this.loadUserInfo()
        return true
      } catch (error) {
        await this.logout()
        return false
      }
    }
    return false
  }
  
  isAuthenticated(): boolean {
    return this.token !== null
  }
  
  getAuthHeaders(): Record<string, string> {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    }
  }
  
  private async loadUserInfo(): Promise<void> {
    const response = await fetch(`${this.getServerUrl()}/api/v1/auth/me`, {
      headers: this.getAuthHeaders()
    })
    
    if (response.ok) {
      this.user = await response.json()
    } else {
      throw new Error('Failed to load user info')
    }
  }
}
```

#### Work Item Service
Gerencia work items e sincronização com API.

```typescript
class WorkItemService {
  private workItems: WorkItem[] = []
  private currentWorkItem: WorkItem | null = null
  private cache: CacheManager
  
  constructor(
    private authService: AuthService,
    private apiClient: ApiClient,
    private cache: CacheManager
  ) {}
  
  async getWorkItems(projectId: string): Promise<WorkItem[]> {
    // Check cache first
    const cached = this.cache.get<WorkItem[]>(`workitems:${projectId}`)
    if (cached) return cached
    
    // Fetch from API
    const response = await this.apiClient.get(
      `/api/v1/projects/${projectId}/work-items`,
      this.authService.getAuthHeaders()
    )
    
    this.workItems = response.data
    this.cache.set(`workitems:${projectId}`, this.workItems, 300000) // 5 min
    
    return this.workItems
  }
  
  async updateStatus(workItemId: string, status: WorkItemStatus): Promise<void> {
    await this.apiClient.patch(
      `/api/v1/work-items/${workItemId}`,
      { status },
      this.authService.getAuthHeaders()
    )
    
    // Update local cache
    const workItem = this.workItems.find(wi => wi.id === workItemId)
    if (workItem) {
      workItem.status = status
    }
    
    window.showInformationMessage(`Work item status updated to ${status}`)
  }
  
  async addComment(workItemId: string, comment: string): Promise<void> {
    await this.apiClient.post(
      `/api/v1/work-items/${workItemId}/comments`,
      { content: comment },
      this.authService.getAuthHeaders()
    )
    
    window.showInformationMessage('Comment added successfully')
  }
  
  async open(workItem: WorkItem): Promise<void> {
    this.currentWorkItem = workItem
    
    // Show work item details in webview
    const panel = window.createWebviewPanel(
      'workItemDetail',
      workItem.title,
      ViewColumn.One,
      { enableScripts: true }
    )
    
    panel.webview.html = this.getWorkItemHtml(workItem)
  }
  
  private getWorkItemHtml(workItem: WorkItem): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          body { padding: 20px; font-family: var(--vscode-font-family); }
          h1 { color: var(--vscode-editor-foreground); }
          .status { 
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
          }
          .section { margin: 20px 0; }
          button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            margin-right: 8px;
          }
        </style>
      </head>
      <body>
        <h1>${workItem.title}</h1>
        <div class="status">${workItem.status}</div>
        
        <div class="section">
          <h2>Description</h2>
          <p>${workItem.description}</p>
        </div>
        
        <div class="section">
          <h2>Acceptance Criteria</h2>
          <ul>
            ${workItem.acceptance_criteria?.map(ac => `<li>${ac}</li>`).join('') || '<li>None specified</li>'}
          </ul>
        </div>
        
        <div class="section">
          <button onclick="exportToAI()">Export to AI Tool</button>
          <button onclick="updateStatus('in_progress')">Start Work</button>
          <button onclick="updateStatus('done')">Mark as Done</button>
        </div>
        
        <script>
          const vscode = acquireVsCodeApi();
          
          function exportToAI() {
            vscode.postMessage({ command: 'exportToAI', workItemId: '${workItem.id}' });
          }
          
          function updateStatus(status) {
            vscode.postMessage({ command: 'updateStatus', workItemId: '${workItem.id}', status });
          }
        </script>
      </body>
      </html>
    `
  }
}
```

#### AI Service
Exporta contexto para ferramentas de IA.

```typescript
class AIService {
  private config: ConfigManager
  
  constructor(config: ConfigManager) {
    this.config = config
  }
  
  async export(workItem: WorkItem): Promise<void> {
    const context = this.buildContext(workItem)
    const defaultTool = this.config.get('bsmart.defaultAITool', 'copilot')
    
    switch (defaultTool) {
      case 'copilot':
        await this.exportToCopilot(context)
        break
      case 'continue':
        await this.exportToContinue(context)
        break
      case 'kiro':
        await this.exportToKiro(context)
        break
      case 'cursor':
        await this.exportToCursor(context)
        break
      default:
        await this.exportToClipboard(context)
    }
  }
  
  private async exportToCopilot(context: string): Promise<void> {
    try {
      await commands.executeCommand('github.copilot.interactiveSession.insertIntoNewSession', {
        message: context
      })
      window.showInformationMessage('Context exported to GitHub Copilot')
    } catch (error) {
      await this.exportToClipboard(context)
    }
  }
  
  private async exportToContinue(context: string): Promise<void> {
    try {
      await commands.executeCommand('continue.sendMainUserInput', context)
      window.showInformationMessage('Context exported to Continue')
    } catch (error) {
      await this.exportToClipboard(context)
    }
  }
  
  private async exportToKiro(context: string): Promise<void> {
    try {
      await commands.executeCommand('kiro.chat.sendMessage', context)
      window.showInformationMessage('Context exported to Kiro')
    } catch (error) {
      await this.exportToClipboard(context)
    }
  }
  
  private async exportToCursor(context: string): Promise<void> {
    try {
      await commands.executeCommand('cursor.chat.open', { message: context })
      window.showInformationMessage('Context exported to Cursor')
    } catch (error) {
      await this.exportToClipboard(context)
    }
  }
  
  private async exportToClipboard(context: string): Promise<void> {
    await env.clipboard.writeText(context)
    window.showInformationMessage('Context copied to clipboard')
  }
  
  private buildContext(workItem: WorkItem): string {
    return `# Work Item: ${workItem.title}

## Description
${workItem.description}

## Acceptance Criteria
${workItem.acceptance_criteria?.map(ac => `- ${ac}`).join('\n') || 'None specified'}

## Technical Specifications
${workItem.specifications || 'None specified'}

## Related Files
${workItem.related_files?.map(file => `- ${file}`).join('\n') || 'None specified'}

## Priority
${workItem.priority}

## Status
${workItem.status}

Please help me implement this work item following best practices.
`
  }
}
```

#### Git Service
Integra com Git para detectar commits e pushes.

```typescript
class GitService {
  private gitExtension: GitExtension
  private workItemService: WorkItemService
  
  constructor(workItemService: WorkItemService) {
    this.workItemService = workItemService
    this.gitExtension = extensions.getExtension('vscode.git')?.exports
  }
  
  async initialize(): Promise<void> {
    if (!this.gitExtension) {
      window.showWarningMessage('Git extension not found')
      return
    }
    
    // Listen to git events
    this.gitExtension.onDidChangeState(() => {
      this.handleGitChange()
    })
  }
  
  private async handleGitChange(): Promise<void> {
    const repo = this.gitExtension.repositories[0]
    if (!repo) return
    
    // Get recent commits
    const commits = await repo.log({ maxEntries: 1 })
    if (commits.length === 0) return
    
    const latestCommit = commits[0]
    const workItemId = this.extractWorkItemId(latestCommit.message)
    
    if (workItemId) {
      // Add commit info to work item
      await this.workItemService.addComment(
        workItemId,
        `Commit: ${latestCommit.hash.substring(0, 7)} - ${latestCommit.message}`
      )
    }
  }
  
  private extractWorkItemId(commitMessage: string): string | null {
    const match = commitMessage.match(/\[WI-(\w+)\]/)
    return match ? match[1] : null
  }
  
  async createBranch(workItemId: string, title: string): Promise<void> {
    const repo = this.gitExtension.repositories[0]
    if (!repo) return
    
    const branchName = `wi-${workItemId}-${this.slugify(title)}`
    await repo.createBranch(branchName, true)
    
    window.showInformationMessage(`Created branch: ${branchName}`)
  }
  
  private slugify(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .substring(0, 50)
  }
}
```

### 3. Data Layer

#### API Client
Cliente HTTP para comunicação com Bsmart-ALM API.

```typescript
class ApiClient {
  constructor(private baseUrl: string) {}
  
  async get(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text())
    }
    
    return { data: await response.json(), status: response.status }
  }
  
  async post(endpoint: string, body: any, headers?: Record<string, string>): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text())
    }
    
    return { data: await response.json(), status: response.status }
  }
  
  async patch(endpoint: string, body: any, headers?: Record<string, string>): Promise<ApiResponse> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new ApiError(response.status, await response.text())
    }
    
    return { data: await response.json(), status: response.status }
  }
}

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}
```

#### Cache Manager
Gerencia cache local para reduzir chamadas à API.

```typescript
class CacheManager {
  private cache = new Map<string, CacheEntry>()
  
  set(key: string, value: any, ttl: number = 300000): void {
    this.cache.set(key, {
      value,
      expiry: Date.now() + ttl
    })
  }
  
  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null
    
    if (Date.now() > entry.expiry) {
      this.cache.delete(key)
      return null
    }
    
    return entry.value
  }
  
  clear(): void {
    this.cache.clear()
  }
  
  delete(key: string): void {
    this.cache.delete(key)
  }
}

interface CacheEntry {
  value: any
  expiry: number
}
```

#### Storage Manager
Gerencia armazenamento seguro de credenciais e configurações.

```typescript
class StorageManager {
  constructor(private context: ExtensionContext) {}
  
  async storeSecurely(key: string, value: string): Promise<void> {
    await this.context.secrets.store(key, value)
  }
  
  async getSecurely(key: string): Promise<string | undefined> {
    return await this.context.secrets.get(key)
  }
  
  async deleteSecurely(key: string): Promise<void> {
    await this.context.secrets.delete(key)
  }
  
  store(key: string, value: any): void {
    this.context.globalState.update(key, value)
  }
  
  get<T>(key: string, defaultValue?: T): T | undefined {
    return this.context.globalState.get(key, defaultValue)
  }
  
  delete(key: string): void {
    this.context.globalState.update(key, undefined)
  }
}
```

## Data Models

```typescript
interface User {
  id: string
  email: string
  full_name: string
  tenant_id: string
  is_superuser: boolean
}

interface Project {
  id: string
  name: string
  description: string
  tenant_id: string
  status: 'active' | 'inactive' | 'archived'
}

interface WorkItem {
  id: string
  title: string
  description: string
  status: WorkItemStatus
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignee_id?: string
  project_id: string
  acceptance_criteria?: string[]
  specifications?: string
  related_files?: string[]
  created_at: string
  updated_at: string
}

type WorkItemStatus = 'backlog' | 'ready' | 'in_progress' | 'in_review' | 'done' | 'blocked'

interface ApiResponse {
  data: any
  status: number
}
```

## Extension Lifecycle

### Activation
```typescript
export function activate(context: ExtensionContext) {
  // Initialize services
  const storage = new StorageManager(context)
  const config = new ConfigManager()
  const cache = new CacheManager()
  const authService = new AuthService(storage)
  const apiClient = new ApiClient(config.get('bsmart.serverUrl'))
  const workItemService = new WorkItemService(authService, apiClient, cache)
  const aiService = new AIService(config)
  const gitService = new GitService(workItemService)
  
  // Initialize UI
  const treeProvider = new WorkItemTreeProvider(workItemService)
  const statusBar = new StatusBarManager()
  
  // Register tree view
  window.registerTreeDataProvider('bsmartWorkItems', treeProvider)
  
  // Register commands
  Object.entries(commands).forEach(([command, handler]) => {
    context.subscriptions.push(
      commands.registerCommand(command, handler)
    )
  })
  
  // Initialize Git integration
  gitService.initialize()
  
  // Try auto-login
  authService.tryAutoLogin().then(success => {
    if (success) {
      treeProvider.refresh()
    }
  })
}

export function deactivate() {
  // Cleanup resources
}
```

## Configuration

### package.json
```json
{
  "name": "bsmart-alm-plugin",
  "displayName": "Bsmart-ALM Integration",
  "description": "Integrate your IDE with Bsmart-ALM for seamless work item management",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "categories": ["Other"],
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "views": {
      "explorer": [
        {
          "id": "bsmartWorkItems",
          "name": "Bsmart Work Items",
          "when": "bsmart.authenticated"
        }
      ]
    },
    "commands": [
      {
        "command": "bsmart.login",
        "title": "Login to Bsmart-ALM",
        "category": "Bsmart"
      },
      {
        "command": "bsmart.logout",
        "title": "Logout from Bsmart-ALM",
        "category": "Bsmart"
      },
      {
        "command": "bsmart.selectProject",
        "title": "Select Project",
        "category": "Bsmart"
      },
      {
        "command": "bsmart.refreshWorkItems",
        "title": "Refresh Work Items",
        "category": "Bsmart",
        "icon": "$(refresh)"
      },
      {
        "command": "bsmart.exportToAI",
        "title": "Export to AI Tool",
        "category": "Bsmart",
        "icon": "$(robot)"
      }
    ],
    "menus": {
      "view/title": [
        {
          "command": "bsmart.refreshWorkItems",
          "when": "view == bsmartWorkItems",
          "group": "navigation"
        }
      ],
      "view/item/context": [
        {
          "command": "bsmart.exportToAI",
          "when": "view == bsmartWorkItems && viewItem == workitem",
          "group": "inline"
        }
      ]
    },
    "configuration": {
      "title": "Bsmart-ALM",
      "properties": {
        "bsmart.serverUrl": {
          "type": "string",
          "default": "http://localhost:8086",
          "description": "Bsmart-ALM server URL"
        },
        "bsmart.defaultAITool": {
          "type": "string",
          "enum": ["copilot", "continue", "kiro", "cursor", "clipboard"],
          "default": "copilot",
          "description": "Default AI tool for context export"
        },
        "bsmart.autoRefresh": {
          "type": "boolean",
          "default": true,
          "description": "Automatically refresh work items"
        },
        "bsmart.refreshInterval": {
          "type": "number",
          "default": 300,
          "description": "Refresh interval in seconds"
        }
      }
    }
  }
}
```

## Error Handling

```typescript
class ErrorHandler {
  static handle(error: Error, context?: string): void {
    console.error(`[Bsmart Plugin] ${context || 'Error'}:`, error)
    
    if (error instanceof ApiError) {
      if (error.status === 401) {
        window.showErrorMessage('Authentication failed. Please login again.')
        commands.executeCommand('bsmart.login')
      } else if (error.status >= 500) {
        window.showErrorMessage('Server error. Please try again later.')
      } else {
        window.showErrorMessage(`API Error: ${error.message}`)
      }
    } else {
      window.showErrorMessage(`Unexpected error: ${error.message}`)
    }
  }
}
```

## Testing Strategy

### Unit Tests
- Test individual services (AuthService, WorkItemService, AIService)
- Mock API calls and storage
- Test error handling scenarios

### Integration Tests
- Test communication with real Bsmart-ALM API
- Test Git integration
- Test AI tool integrations

### E2E Tests
- Test complete user workflows
- Test authentication flow
- Test work item export to AI tools

## Performance Considerations

1. **Lazy Loading**: Load work items only when tree view is expanded
2. **Caching**: Cache API responses for 5 minutes
3. **Debouncing**: Debounce API calls to prevent spam
4. **Background Sync**: Sync status changes in background

## Security Considerations

1. **Token Storage**: Use VS Code's secure storage for JWT tokens
2. **HTTPS Only**: Enforce HTTPS for API calls in production
3. **Token Expiry**: Handle token expiration gracefully
4. **Input Validation**: Validate all user inputs

## Deployment

### Build Process
```bash
npm install
npm run compile
npm run test
npm run package
```

### Publishing
```bash
vsce package
vsce publish
```

### Installation
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```
