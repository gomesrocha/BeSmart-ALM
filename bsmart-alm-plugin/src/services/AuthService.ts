import * as vscode from 'vscode';
import { StorageManager } from '../data/StorageManager';
import { ApiClient } from '../data/ApiClient';
import { User, ApiError } from '../types';

export class AuthService {
    private token: string | null = null;
    private user: User | null = null;

    constructor(
        private storage: StorageManager,
        private apiClient: ApiClient
    ) {}

    async login(): Promise<void> {
        // Create webview panel for login
        const panel = vscode.window.createWebviewPanel(
            'bsmartLogin',
            'Login - Bsmart-ALM',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        // Set HTML content
        panel.webview.html = this.getLoginHtml();

        // Handle messages from webview
        return new Promise((resolve, reject) => {
            panel.webview.onDidReceiveMessage(
                async (message) => {
                    switch (message.command) {
                        case 'login':
                            try {
                                const { serverUrl, email, password } = message;

                                // Update API client base URL
                                this.apiClient.setBaseUrl(serverUrl);

                                // Authenticate
                                const response = await this.apiClient.post<{ access_token: string; token_type: string }>(
                                    '/api/v1/auth/login',
                                    { email, password }
                                );

                                this.token = response.data.access_token;
                                
                                // Store token securely
                                await this.storage.storeSecurely('bsmart.token', this.token);
                                await this.storage.store('bsmart.serverUrl', serverUrl);

                                // Load user info
                                await this.loadUserInfo();

                                vscode.window.showInformationMessage('Successfully logged in to Bsmart-ALM');
                                vscode.commands.executeCommand('setContext', 'bsmart.authenticated', true);

                                panel.dispose();
                                resolve();

                            } catch (error) {
                                let errorMessage = 'Login failed';
                                
                                if (error instanceof ApiError) {
                                    if (error.status === 401) {
                                        errorMessage = 'Invalid credentials. Please check your email and password.';
                                    } else if (error.status >= 500) {
                                        errorMessage = 'Server error. Please try again later.';
                                    }
                                }

                                // Send error back to webview
                                panel.webview.postMessage({
                                    command: 'loginError',
                                    error: errorMessage
                                });
                            }
                            break;

                        case 'cancel':
                            panel.dispose();
                            reject(new Error('Login cancelled'));
                            break;
                    }
                },
                undefined,
                []
            );
        });
    }

    private getLoginHtml(): string {
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
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background-color: var(--vscode-editor-background);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .login-container {
            width: 100%;
            max-width: 400px;
            background-color: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            font-size: 28px;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 8px;
        }
        
        .logo p {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-size: 13px;
            font-weight: 500;
            color: var(--vscode-foreground);
        }
        
        input {
            width: 100%;
            padding: 10px 12px;
            font-size: 14px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            outline: none;
        }
        
        input:focus {
            border-color: var(--vscode-focusBorder);
        }
        
        .error-message {
            display: none;
            padding: 12px;
            margin-bottom: 20px;
            background-color: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
            border-radius: 4px;
            color: var(--vscode-errorForeground);
            font-size: 13px;
        }
        
        .error-message.show {
            display: block;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        
        button {
            flex: 1;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: 500;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        
        button:hover {
            opacity: 0.9;
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-primary {
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
        }
        
        .btn-secondary {
            background-color: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
            color: var(--vscode-descriptionForeground);
        }
        
        .loading.show {
            display: block;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>🚀 Bsmart-ALM</h1>
            <p>Faça login para continuar</p>
        </div>
        
        <div id="errorMessage" class="error-message"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="serverUrl">Server URL</label>
                <input 
                    type="text" 
                    id="serverUrl" 
                    placeholder="http://localhost:8086"
                    value="http://localhost:8086"
                    required
                />
            </div>
            
            <div class="form-group">
                <label for="email">Email</label>
                <input 
                    type="email" 
                    id="email" 
                    placeholder="seu@email.com"
                    required
                    autocomplete="email"
                />
            </div>
            
            <div class="form-group">
                <label for="password">Senha</label>
                <input 
                    type="password" 
                    id="password" 
                    placeholder="••••••••"
                    required
                    autocomplete="current-password"
                />
            </div>
            
            <div class="button-group">
                <button type="button" class="btn-secondary" id="cancelBtn">
                    Cancelar
                </button>
                <button type="submit" class="btn-primary" id="loginBtn">
                    Entrar
                </button>
            </div>
            
            <div id="loading" class="loading">
                Autenticando...
            </div>
        </form>
    </div>
    
    <script>
        const vscode = acquireVsCodeApi();
        const form = document.getElementById('loginForm');
        const loginBtn = document.getElementById('loginBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const loading = document.getElementById('loading');
        const errorMessage = document.getElementById('errorMessage');
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const serverUrl = document.getElementById('serverUrl').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            // Hide error
            errorMessage.classList.remove('show');
            
            // Show loading
            loading.classList.add('show');
            loginBtn.disabled = true;
            cancelBtn.disabled = true;
            
            // Send login request
            vscode.postMessage({
                command: 'login',
                serverUrl,
                email,
                password
            });
        });
        
        cancelBtn.addEventListener('click', () => {
            vscode.postMessage({ command: 'cancel' });
        });
        
        // Listen for messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            if (message.command === 'loginError') {
                // Hide loading
                loading.classList.remove('show');
                loginBtn.disabled = false;
                cancelBtn.disabled = false;
                
                // Show error
                errorMessage.textContent = message.error;
                errorMessage.classList.add('show');
            }
        });
        
        // Focus email field
        document.getElementById('email').focus();
    </script>
</body>
</html>
        `;
    }

    async logout(): Promise<void> {
        this.token = null;
        this.user = null;
        
        // Clear stored credentials
        await this.storage.deleteSecurely('bsmart.token');
        await this.storage.delete('bsmart.user');
        
        vscode.window.showInformationMessage('Logged out from Bsmart-ALM');
        vscode.commands.executeCommand('setContext', 'bsmart.authenticated', false);
    }

    async tryAutoLogin(): Promise<boolean> {
        const token = await this.storage.getSecurely('bsmart.token');
        const serverUrl = this.storage.get<string>('bsmart.serverUrl');

        if (token && serverUrl) {
            this.token = token;
            this.apiClient.setBaseUrl(serverUrl);

            try {
                await this.loadUserInfo();
                vscode.commands.executeCommand('setContext', 'bsmart.authenticated', true);
                return true;
            } catch (error) {
                // Token expired or invalid, clear it
                await this.logout();
                return false;
            }
        }

        return false;
    }

    isAuthenticated(): boolean {
        return this.token !== null && this.user !== null;
    }

    getAuthHeaders(): Record<string, string> {
        if (!this.token) {
            throw new Error('Not authenticated');
        }

        return {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json'
        };
    }

    getUser(): User | null {
        return this.user;
    }

    getToken(): string | null {
        return this.token;
    }

    private async loadUserInfo(): Promise<void> {
        try {
            const response = await this.apiClient.get<User>(
                '/api/v1/auth/me',
                this.getAuthHeaders()
            );

            this.user = response.data;
            
            // Store user info
            this.storage.store('bsmart.user', this.user);

        } catch (error) {
            if (error instanceof ApiError && error.status === 401) {
                throw new Error('Authentication failed. Please login again.');
            }
            throw error;
        }
    }
}
