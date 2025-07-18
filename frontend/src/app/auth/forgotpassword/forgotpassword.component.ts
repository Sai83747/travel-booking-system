import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  templateUrl: './forgotpassword.component.html',
  styleUrls: ['./forgotpassword.component.css'],
  imports: [CommonModule, ReactiveFormsModule],
})
export class ForgotPasswordComponent {
  forgotForm: FormGroup; // ✅ fixed name
  successMessage = '';
  errorMessage = '';
  loading = false;

  constructor(private fb: FormBuilder, private authService: AuthService) {
    this.forgotForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
    });
  }

  onSubmit() {
    if (this.forgotForm.invalid) return;

    this.loading = true;
    const email = this.forgotForm.value.email;

    this.authService.forgotPassword(email).subscribe({
      next: (res) => {
        this.successMessage = res.message;
        this.errorMessage = '';
        this.loading = false;
      },
      error: (err) => {
        this.successMessage = '';
        this.errorMessage = err.error?.error || 'Something went wrong.';
        this.loading = false;
      },
    });
  }
}
