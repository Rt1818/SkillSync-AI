import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';
import { SessionService } from '../../../core/services/session.service';
import { Session } from '../../../core/models/types';
import { Router } from '@angular/router';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.html',
  styleUrls: ['./sidebar.scss']
})
export class Sidebar implements OnInit {
  @Input() isOpen = false;
  @Output() close = new EventEmitter<void>();

  sessions: Session[] = [];
  isLoading = false;

  constructor(
    private api: ApiService,
    public sessionService: SessionService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadSessions();
  }

  loadSessions() {
    this.isLoading = true;
    this.api.getAllSessions().subscribe({
      next: (data) => {
        this.sessions = data;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  onClose() {
    this.close.emit();
  }

  selectSession(sessionId: string) {
    this.sessionService.loadSession(sessionId);
    this.router.navigate(['/workspace', sessionId]);
  }

  formatDate(dateString: string): string {
    const d = new Date(dateString);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
}
