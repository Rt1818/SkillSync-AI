import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { SessionService } from '../../core/services/session.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.html',
  styleUrls: ['./landing.scss']
})
export class Landing {
  constructor(
    private router: Router,
    public sessionService: SessionService
  ) {}

  async startNewAssessment() {
    const sessionId = await this.sessionService.createNewSession();
    if (sessionId) {
      this.router.navigate(['/workspace', sessionId]);
    }
  }
}
