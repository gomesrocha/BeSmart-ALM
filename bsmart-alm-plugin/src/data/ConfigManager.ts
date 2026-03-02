import * as vscode from 'vscode';

export class ConfigManager {
    private readonly configSection = 'bsmart';

    get<T>(key: string, defaultValue?: T): T {
        const config = vscode.workspace.getConfiguration();
        return config.get<T>(key, defaultValue as T);
    }

    async set(key: string, value: any, target: vscode.ConfigurationTarget = vscode.ConfigurationTarget.Global): Promise<void> {
        const config = vscode.workspace.getConfiguration();
        await config.update(key, value, target);
    }

    getServerUrl(): string {
        return this.get<string>('bsmart.serverUrl', 'http://localhost:8086');
    }

    getDefaultAITool(): string {
        return this.get<string>('bsmart.defaultAITool', 'copilot');
    }

    getAutoRefresh(): boolean {
        return this.get<boolean>('bsmart.autoRefresh', true);
    }

    getRefreshInterval(): number {
        return this.get<number>('bsmart.refreshInterval', 300);
    }

    onDidChangeConfiguration(callback: (e: vscode.ConfigurationChangeEvent) => void): vscode.Disposable {
        return vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration(this.configSection)) {
                callback(e);
            }
        });
    }
}
