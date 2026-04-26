import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Session, ChatHistoryResponse } from '../models/types';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // ── Sessions ─────────────────────────────────────────────────────────────
  
  createSession(): Observable<{ session_id: string; status: string; created_at: string }> {
    return this.http.post<any>(`${this.baseUrl}/sessions`, {});
  }

  getSession(sessionId: string): Observable<Session> {
    return this.http.get<Session>(`${this.baseUrl}/sessions/${sessionId}`);
  }

  getAllSessions(): Observable<Session[]> {
    return this.http.get<Session[]>(`${this.baseUrl}/sessions`);
  }

  // ── Uploads ──────────────────────────────────────────────────────────────

  uploadJD(sessionId: string, file?: File, text?: string, url?: string): Observable<any> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    if (file) formData.append('file', file);
    if (text) formData.append('text', text);
    if (url) formData.append('url', url);
    
    return this.http.post<any>(`${this.baseUrl}/upload/jd`, formData);
  }

  uploadResume(sessionId: string, file: File): Observable<any> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    return this.http.post<any>(`${this.baseUrl}/upload/resume`, formData);
  }

  // ── Generation Endpoints ──────────────────────────────────────────────────

  generateAnalysis(sessionId: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/analysis/generate`, { session_id: sessionId });
  }

  generateLearningPlan(sessionId: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/learning-plan/generate`, { session_id: sessionId });
  }

  generateInterviewPrep(sessionId: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/interview-prep/generate`, { session_id: sessionId });
  }

  // ── Chat ─────────────────────────────────────────────────────────────────

  getChatHistory(sessionId: string): Observable<ChatHistoryResponse> {
    return this.http.get<ChatHistoryResponse>(`${this.baseUrl}/chat/${sessionId}/history`);
  }

  // Note: Streaming chat response is handled natively via fetch/EventSource in the component
}
