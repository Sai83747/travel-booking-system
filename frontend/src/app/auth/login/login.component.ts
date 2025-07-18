import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';
import { Store } from '@ngrx/store';
import { AppState } from '../auth.state';
import { loginSuccess } from '../auth.action';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  imports: [CommonModule, ReactiveFormsModule,RouterModule]
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  error = '';

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router,
    private store: Store<AppState> // ✅ Inject store
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) return;

    this.loading = true;
    this.error = '';

    const payload = this.loginForm.value;

    this.authService.login(payload).subscribe({
      next: (res) => {
        console.log('✅ Login successful:', res);

        const email = res.user?.email;
        const role = res.user?.role;
        console.log('🚀 Extracted role:', role);
        const userId = res.user?.user_id; // ✅ Extract Django user_id

        console.log('🚀 Extracted role:', role);
        console.log('🆔 Django User ID:', userId);
  
        // ✅ Store Django user_id in localStorage
        localStorage.setItem('user_id', userId);
        // ✅ Dispatch loginSuccess to store role and email
        this.store.dispatch(loginSuccess({ email, role }));

        if (role === 'admin') {
          console.log('🔀 Redirecting to admin-dashboard');
          this.router.navigate(['/admin-dashboard']);
        } else if (role === 'travel_agent') {
          console.log('🔀 Redirecting to agent-dashboard');
          this.router.navigate(['/agent-dashboard']);
        } else {
          console.log('🔀 Redirecting to user-dashboard');
          this.router.navigate(['/user-dashboard']);
        }
      },
      error: (err) => {
        console.error('❌ Login error:', err);
        this.error = err.error?.error || 'Invalid credentials or server error.';
        this.loading = false;
      }
    });
  }
}
