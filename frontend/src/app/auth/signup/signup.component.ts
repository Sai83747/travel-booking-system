import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import { AuthService } from '../auth.service';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css'],
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})
export class SignupComponent implements OnInit {
  signupForm!: FormGroup;
  loading = false;
  error = '';

  // Subjects for debugging or logging purposes
  emailSubject = new Subject<string>();
  passwordSubject = new Subject<string>();
  phoneSubject = new Subject<string>();

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.signupForm = this.fb.group({
      email: [
        '',
        [
          Validators.required,
          Validators.email,
          this.emailDomainValidator
        ]
      ],
      password: ['', [Validators.required, Validators.minLength(6)]],
      firstName: [''],
      middleName: ['', Validators.required],
      lastName: [''],
      phoneNumber: ['', Validators.required],
      location: ['', Validators.required],
    });

    // Optional reactive logging
    this.emailSubject.subscribe(email => console.log('Email changed:', email));
    this.passwordSubject.subscribe(password => console.log('Password changed:', password));
    this.phoneSubject.subscribe(phone => console.log('Phone changed:', phone));
  }

  // ✅ Custom validator to allow only specific email domains
  emailDomainValidator(control: AbstractControl): ValidationErrors | null {
    const email = control.value;
    if (email) {
      const domain = email.substring(email.lastIndexOf('@') + 1).toLowerCase();
      const allowedDomains = ['gmail.com', 'hotmail.com', 'email.com'];
      if (!allowedDomains.includes(domain)) {
        return { invalidDomain: true };
      }
    }
    return null;
  }

  onSubmit(): void {
    if (this.signupForm.invalid) return;

    this.loading = true;
    this.error = '';

    const formData = this.signupForm.value;
    const payload = {
      email: formData.email,
      password: formData.password,
      display_name: `${formData.firstName} ${formData.middleName} ${formData.lastName}`.trim(),
      phone_number: formData.phoneNumber,
      location: formData.location
    };

    this.authService.signup(payload).subscribe({
      next: (res) => {
        console.log('✅ Signup successful:', res);
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('❌ Signup error:', err);
        this.error = err.error?.error || 'Signup failed. Please try again.';
        this.loading = false;
      }
    });
  }
}
