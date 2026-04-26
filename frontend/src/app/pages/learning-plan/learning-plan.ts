import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from '../../core/services/api.service';
import { SessionService } from '../../core/services/session.service';

@Component({
  selector: 'app-learning-plan',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './learning-plan.html',
  styleUrls: ['./learning-plan.scss']
})
export class LearningPlan implements OnInit {
  isLoading = true;
  error: string | null = null;
  plan: any = null;

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
        this.fetchPlan(id);
      }
    });
  }

  fetchPlan(sessionId: string) {
    // 1. Check local state first
    const session = this.sessionService.currentSession();
    if (session && session.session_id === sessionId && session.learning_plan) {
      this.plan = session.learning_plan;
      this.isLoading = false;
      return;
    }

    // 2. Fetch from backend if not in local state
    this.api.getSession(sessionId).subscribe({
      next: (res: any) => {
        if (res.learning_plan) {
          this.plan = res.learning_plan;
          this.sessionService.currentSession.set(res); // update local state
          this.isLoading = false;
        } else {
          this.error = 'Learning plan not generated yet in the database. Please generate it from the workspace.';
          this.isLoading = false;
        }
      },
      error: (err: any) => {
        console.error("fetchPlan error:", err);
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
