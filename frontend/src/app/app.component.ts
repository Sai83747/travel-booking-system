import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './auth/auth.service';
import { Store } from '@ngrx/store';
import { AppState } from './auth/auth.state';
import { loginSuccess } from './auth/auth.action';
import { RouterModule } from '@angular/router';
import { NavbarComponent } from './navbar/navbar.component';
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken, onMessage } from 'firebase/messaging';
import { environment } from '../../environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterModule, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  title = 'travelFrontend';

  constructor(
    private authService: AuthService,
    private store: Store<AppState>
  ) {}

  ngOnInit(): void {
    this.restoreSession();
    this.initFirebaseMessaging();
  }

  restoreSession(): void {
    this.authService.getCurrentUser().subscribe({
      next: (res) => {
        const user = res.user;
        if (user?.email && user?.role) {
          this.store.dispatch(loginSuccess({ email: user.email, role: user.role }));
          console.log('✅ Session restored from cookie:', user);
        }
      },
      error: (err) => {
        console.warn('❌ No active session or error restoring session:', err);
      }
    });
  }

  initFirebaseMessaging(): void {
    const app = initializeApp(environment.firebaseConfig);
    const messaging = getMessaging(app);

    // Request permission and get FCM token
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        getToken(messaging, { vapidKey: environment.firebaseConfig.vapidKey }).then(currentToken => {
          if (currentToken) {
            console.log('📲 FCM Token:', currentToken);
            // You can send this token to your backend to associate with the user
          } else {
            console.warn('⚠️ No registration token available. Request permission to generate one.');
          }
        }).catch(err => {
          console.error('❌ An error occurred while retrieving token. ', err);
        });
      } else {
        console.warn('❌ Notification permission denied.');
      }
    });

    // Handle foreground messages
    onMessage(messaging, payload => {
      console.log('📩 Foreground message received:', payload);
      alert(`🔔 New Notification: ${payload.notification?.title}`);
    });
  }
}
