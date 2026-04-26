import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { SessionService } from '../../core/services/session.service';

@Component({
  selector: 'app-interview-prep',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './interview-prep.html',
  styleUrls: ['./interview-prep.scss']
})
export class InterviewPrep implements OnInit {
  isLoading = true;
  error: string | null = null;
  prep: any = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private api: ApiService,
    public sessionService: SessionService
  ) {}

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const id = params.get('sessionId');
      if (id) {
        this.fetchPrep(id);
      }
    });
  }

  fetchPrep(sessionId: string) {
    // 1. Check local state first
    const session = this.sessionService.currentSession();
    if (session && session.session_id === sessionId && session.interview_prep) {
      this.prep = session.interview_prep;
      this.isLoading = false;
      return;
    }

    // 2. Fetch from backend if not in local state
    this.api.getSession(sessionId).subscribe({
      next: (res: any) => {
        if (res.interview_prep) {
          this.prep = res.interview_prep;
          this.sessionService.currentSession.set(res); // update local state
          this.isLoading = false;
        } else {
          this.error = 'Interview prep not generated yet in the database. Please generate it from the workspace.';
          this.isLoading = false;
        }
      },
      error: (err: any) => {
        console.error("fetchPrep error:", err);
        this.error = 'Failed to load session: ' + (err.message || 'Unknown error');
        this.isLoading = false;
      }
    });
  }

  goBack() {
    const session = this.sessionService.currentSession();
    if (session) {
      this.router.navigate(['/workspace', session.session_id]);
    }
  }

  openUrl(url: string) {
    window.open(url, '_blank');
  }
}
