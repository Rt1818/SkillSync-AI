import { Injectable, signal } from '@angular/core';
import { Session } from '../models/types';
import { ApiService } from './api.service';

@Injectable({
  providedIn: 'root'
})
export class SessionService {
  // Reactive signals for state management
  currentSession = signal<Session | null>(null);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);

  constructor(private api: ApiService) {
    this.restoreSessionFromStorage();
  }

  // ── Session Initialization ───────────────────────────────────────────────

  async createNewSession(): Promise<string | null> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await this.api.createSession().toPromise();
      if (res && res.session_id) {
        this.saveSessionId(res.session_id);
        await this.loadSession(res.session_id);
        return res.session_id;
      }
      return null;
    } catch (e: any) {
      this.error.set(e.message || 'Failed to create session');
      return null;
    } finally {
      this.isLoading.set(false);
    }
  }

  async loadSession(sessionId: string): Promise<void> {
    this.isLoading.set(true);
    try {
      const session = await this.api.getSession(sessionId).toPromise();
      if (session) {
        this.currentSession.set(session);
        this.saveSessionId(session.session_id);
      }
    } catch (e: any) {
      this.error.set(e.message || 'Failed to load session');
    } finally {
      this.isLoading.set(false);
    }
  }

  // ── Local Storage Persistence ───────────────────────────────────────────

  private saveSessionId(id: string): void {
    localStorage.setItem('skillsync_current_session', id);
  }

  private restoreSessionFromStorage(): void {
    const savedId = localStorage.getItem('skillsync_current_session');
    if (savedId) {
      this.loadSession(savedId);
    }
  }

  clearSession(): void {
    localStorage.removeItem('skillsync_current_session');
    this.currentSession.set(null);
  }
}
