import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';
import { SessionService } from '../../core/services/session.service';
import { ChatMessage } from '../../core/models/types';

@Component({
  selector: 'app-workspace',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './workspace.html',
  styleUrls: ['./workspace.scss']
})
export class Workspace implements OnInit, OnDestroy {
  // Upload State
  jdText = '';
  resumeFile: File | null = null;
  isUploadingJd = false;
  isUploadingResume = false;
  isAnalyzing = false;

  // Chat State
  chatMessages = signal<ChatMessage[]>([]);
  chatInput = '';
  isChatStreaming = false;

  // Generation State
  isGeneratingPlan = false;
  isGeneratingPrep = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    public sessionService: SessionService,
    private api: ApiService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('sessionId');
      if (id && id !== this.sessionService.currentSession()?.session_id) {
        this.sessionService.loadSession(id).then(() => {
          this.loadChatHistory(id);
        });
      } else if (id) {
        this.loadChatHistory(id);
      }
    });
  }

  ngOnDestroy() {}

  // ── Upload Handlers ───────────────────────────────────────────────────

  async uploadJd() {
    const text = this.jdText.trim();
    if (!text) return;
    const session = this.sessionService.currentSession();
    if (!session) return;

    this.isUploadingJd = true;
    
    let isUrl = text.startsWith('http://') || text.startsWith('https://');
    let urlParam = isUrl ? text : undefined;
    let textParam = isUrl ? undefined : text;

    this.api.uploadJD(session.session_id, undefined, textParam, urlParam).subscribe({
      next: (res: any) => {
        this.isUploadingJd = false;
        this.sessionService.loadSession(session.session_id); // refresh state
      },
      error: (err: any) => {
        this.isUploadingJd = false;
        alert('JD Upload Failed: ' + (err.error?.detail || err.message));
      }
    });
  }

  onResumeSelected(event: any) {
    if (event.target.files.length > 0) {
      this.resumeFile = event.target.files[0];
    }
  }

  uploadResume() {
    if (!this.resumeFile) return;
    const session = this.sessionService.currentSession();
    if (!session) return;

    this.isUploadingResume = true;
    this.api.uploadResume(session.session_id, this.resumeFile).subscribe({
      next: (res: any) => {
        this.isUploadingResume = false;
        this.sessionService.loadSession(session.session_id);
      },
      error: (err: any) => {
        this.isUploadingResume = false;
        alert('Resume Upload Failed: ' + err.message);
      }
    });
  }

  // ── Analysis ──────────────────────────────────────────────────────────

  generateAnalysis() {
    const session = this.sessionService.currentSession();
    if (!session) return;

    this.isAnalyzing = true;
    this.api.generateAnalysis(session.session_id).subscribe({
      next: (res: any) => {
        this.isAnalyzing = false;
        this.sessionService.loadSession(session.session_id);
        
        setTimeout(() => {
          if (this.chatMessages().length === 0) {
            this.chatInput = "Hello, I have uploaded my resume. Let's begin the assessment.";
            this.sendMessage(true);
          }
        }, 500);
      },
      error: (err: any) => {
        this.isAnalyzing = false;
        alert('Analysis Failed: ' + err.message);
      }
    });
  }

  // ── Plan & Prep Generation ──────────────────────────────────────────────

  generateLearningPlan() {
    const session = this.sessionService.currentSession();
    if (!session) return;
    
    if (session.learning_plan) {
      this.router.navigate(['/learning-plan', session.session_id]);
      return;
    }

    this.isGeneratingPlan = true;
    this.api.generateLearningPlan(session.session_id).subscribe({
      next: (res: any) => {
        this.sessionService.loadSession(session.session_id).then(() => {
          this.isGeneratingPlan = false;
          this.router.navigate(['/learning-plan', session.session_id]);
        });
      },
      error: (err: any) => {
        this.isGeneratingPlan = false;
        alert('Failed to generate Learning Plan: ' + err.message);
      }
    });
  }

  generateInterviewPrep() {
    const session = this.sessionService.currentSession();
    if (!session) return;
    
    if (session.interview_prep) {
      this.router.navigate(['/interview-prep', session.session_id]);
      return;
    }

    this.isGeneratingPrep = true;
    this.api.generateInterviewPrep(session.session_id).subscribe({
      next: (res: any) => {
        this.sessionService.loadSession(session.session_id).then(() => {
          this.isGeneratingPrep = false;
          this.router.navigate(['/interview-prep', session.session_id]);
        });
      },
      error: (err: any) => {
        this.isGeneratingPrep = false;
        alert('Failed to generate Interview Prep: ' + err.message);
      }
    });
  }

  // ── Chat & SSE ────────────────────────────────────────────────────────

  loadChatHistory(sessionId: string) {
    this.api.getChatHistory(sessionId).subscribe((res: any) => {
      this.chatMessages.set(res.messages || []);
    });
  }

  async sendMessage(hiddenUser: boolean = false) {
    if (!this.chatInput.trim() || this.isChatStreaming) return;
    const session = this.sessionService.currentSession();
    if (!session) return;

    const userMessage = this.chatInput;
    this.chatInput = '';
    
    // Add user message immediately
    if (!hiddenUser) {
      this.chatMessages.update(m => [...m, { role: 'human', content: userMessage }]);
    }
    
    // Add empty AI message placeholder
    this.chatMessages.update(m => [...m, { role: 'ai', content: '' }]);
    
    this.isChatStreaming = true;

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: session.session_id, message: userMessage })
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let aiContent = '';
        let isDone = false;
        while (!isDone) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.includes('[DONE]')) {
              isDone = true;
              break;
            }
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));
                aiContent += data.content || '';
                
                // Update the last message
                this.chatMessages.update(messages => {
                  const newMessages = [...messages];
                  newMessages[newMessages.length - 1].content = aiContent;
                  return newMessages;
                });
              } catch (e) {}
            }
          }
        }
      }
    } catch (e) {
      console.error('Chat error', e);
    } finally {
      this.isChatStreaming = false;
    }
  }

  // Helpers
  formatMessage(content: string): string {
    if (!content) return '';
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/### (.*?)\n/g, '<h3>$1</h3>\n')
      .replace(/\n/g, '<br/>');
  }

  getScoreColor(score: number): string {
    if (score >= 80) return 'var(--status-strong)';
    if (score >= 50) return 'var(--status-moderate)';
    if (score >= 25) return 'var(--status-weak)';
    return 'var(--status-missing)';
  }
}
