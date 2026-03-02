import fetch from 'node-fetch';
import { ApiResponse, ApiError } from '../types';

export class ApiClient {
    private baseUrl: string;
    private maxRetries: number = 3;
    private retryDelay: number = 1000;

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    }

    async get<T = any>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>('GET', endpoint, undefined, headers);
    }

    async post<T = any>(endpoint: string, body: any, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>('POST', endpoint, body, headers);
    }

    async patch<T = any>(endpoint: string, body: any, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>('PATCH', endpoint, body, headers);
    }

    async delete<T = any>(endpoint: string, headers?: Record<string, string>): Promise<ApiResponse<T>> {
        return this.request<T>('DELETE', endpoint, undefined, headers);
    }

    private async request<T>(
        method: string,
        endpoint: string,
        body?: any,
        headers?: Record<string, string>,
        retryCount: number = 0
    ): Promise<ApiResponse<T>> {
        const url = `${this.baseUrl}${endpoint}`;
        
        const requestHeaders: Record<string, string> = {
            'Content-Type': 'application/json',
            ...headers
        };

        try {
            const response = await fetch(url, {
                method,
                headers: requestHeaders,
                body: body ? JSON.stringify(body) : undefined
            });

            if (!response.ok) {
                // Check if we should retry
                if (this.shouldRetry(response.status) && retryCount < this.maxRetries) {
                    await this.delay(this.retryDelay * (retryCount + 1));
                    return this.request<T>(method, endpoint, body, headers, retryCount + 1);
                }

                const errorText = await response.text();
                throw new ApiError(response.status, errorText || response.statusText);
            }

            const data = await response.json();
            return {
                data: data as T,
                status: response.status
            };

        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }

            // Network error - retry if possible
            if (retryCount < this.maxRetries) {
                await this.delay(this.retryDelay * (retryCount + 1));
                return this.request<T>(method, endpoint, body, headers, retryCount + 1);
            }

            throw new ApiError(0, `Network error: ${error}`);
        }
    }

    private shouldRetry(status: number): boolean {
        // Retry on server errors and rate limiting
        return status >= 500 || status === 429;
    }

    private delay(ms: number): Promise<void> {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    setBaseUrl(baseUrl: string): void {
        this.baseUrl = baseUrl.replace(/\/$/, '');
    }

    getBaseUrl(): string {
        return this.baseUrl;
    }
}
