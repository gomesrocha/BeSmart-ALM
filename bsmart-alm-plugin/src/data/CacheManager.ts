import { CacheEntry } from '../types';

export class CacheManager {
    private cache = new Map<string, CacheEntry>();
    private defaultTTL: number = 300000; // 5 minutes

    set(key: string, value: any, ttl?: number): void {
        const expiryTime = ttl || this.defaultTTL;
        this.cache.set(key, {
            value,
            expiry: Date.now() + expiryTime
        });
    }

    get<T>(key: string): T | null {
        const entry = this.cache.get(key);
        if (!entry) {
            return null;
        }

        // Check if expired
        if (Date.now() > entry.expiry) {
            this.cache.delete(key);
            return null;
        }

        return entry.value as T;
    }

    has(key: string): boolean {
        const entry = this.cache.get(key);
        if (!entry) {
            return false;
        }

        // Check if expired
        if (Date.now() > entry.expiry) {
            this.cache.delete(key);
            return false;
        }

        return true;
    }

    delete(key: string): void {
        this.cache.delete(key);
    }

    clear(): void {
        this.cache.clear();
    }

    // Clear expired entries
    cleanup(): void {
        const now = Date.now();
        for (const [key, entry] of this.cache.entries()) {
            if (now > entry.expiry) {
                this.cache.delete(key);
            }
        }
    }

    // Get cache statistics
    getStats(): { size: number; keys: string[] } {
        this.cleanup(); // Clean up before getting stats
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys())
        };
    }

    // Set default TTL
    setDefaultTTL(ttl: number): void {
        this.defaultTTL = ttl;
    }
}
