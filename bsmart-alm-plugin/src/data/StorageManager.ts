import * as vscode from 'vscode';

export class StorageManager {
    constructor(private context: vscode.ExtensionContext) {}

    // Secure storage for sensitive data (JWT tokens, API keys)
    async storeSecurely(key: string, value: string): Promise<void> {
        await this.context.secrets.store(key, value);
    }

    async getSecurely(key: string): Promise<string | undefined> {
        return await this.context.secrets.get(key);
    }

    async deleteSecurely(key: string): Promise<void> {
        await this.context.secrets.delete(key);
    }

    // Global state storage for non-sensitive data
    store(key: string, value: any): void {
        this.context.globalState.update(key, value);
    }

    get<T>(key: string, defaultValue?: T): T | undefined {
        return this.context.globalState.get(key, defaultValue);
    }

    delete(key: string): void {
        this.context.globalState.update(key, undefined);
    }

    // Workspace state storage (per workspace)
    storeWorkspace(key: string, value: any): void {
        this.context.workspaceState.update(key, value);
    }

    getWorkspace<T>(key: string, defaultValue?: T): T | undefined {
        return this.context.workspaceState.get(key, defaultValue);
    }

    deleteWorkspace(key: string): void {
        this.context.workspaceState.update(key, undefined);
    }

    // Clear all stored data
    async clearAll(): Promise<void> {
        // Clear secure storage
        const keys = ['bsmart.token', 'bsmart.refreshToken'];
        for (const key of keys) {
            await this.deleteSecurely(key);
        }

        // Clear global state
        const globalKeys = this.context.globalState.keys();
        for (const key of globalKeys) {
            if (key.startsWith('bsmart.')) {
                this.delete(key);
            }
        }

        // Clear workspace state
        const workspaceKeys = this.context.workspaceState.keys();
        for (const key of workspaceKeys) {
            if (key.startsWith('bsmart.')) {
                this.deleteWorkspace(key);
            }
        }
    }
}
