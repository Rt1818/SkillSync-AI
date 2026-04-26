import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './navbar.html',
  styleUrls: ['./navbar.scss']
})
export class Navbar {
  @Output() toggleSidebar = new EventEmitter<void>();

  constructor(
    private api: ApiService,
    private router: Router
  ) {}

  onToggle() {
    this.toggleSidebar.emit();
  }

  createNewAssessment() {
    this.api.createSession().subscribe({
      next: (res) => {
        this.router.navigate(['/workspace', res.session_id]);
      },
      error: (err) => {
        console.error('Failed to create session', err);
        alert('Failed to start new assessment. Please try again.');
      }
    });
  }
}
