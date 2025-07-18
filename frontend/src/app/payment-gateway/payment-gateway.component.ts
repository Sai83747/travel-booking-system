import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';
import { environment } from '../../../environment'; // 🔁 Adjust if path differs

@Component({
  selector: 'app-payment-gateway',
  templateUrl: './payment-gateway.component.html',
  styleUrls: ['./payment-gateway.component.css'],
  standalone: true,
  imports: [NgIf, FormsModule, NgFor]
})
export class PaymentComponent implements OnInit {
  bookingId: string | null = null;
  bookingDetails: any = null;
  paymentMethod: string = 'credit_card';
  loading = true;
  errorMessage = '';
  fcmToken: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.bookingId = this.route.snapshot.paramMap.get('bookingId');
    console.log('🔍 Booking ID from URL:', this.bookingId);

    if (this.bookingId) {
      this.fetchBookingDetails(this.bookingId);
    } else {
      this.errorMessage = 'Invalid booking ID.';
      console.error('❌ Booking ID not found in route.');
      this.loading = false;
    }

    // Initialize FCM on component load
    this.initFirebaseMessaging();
  }

  fetchBookingDetails(bookingId: string) {
    const apiUrl = `http://127.0.0.1:8000/auth/getbookingdetails/${bookingId}/`;
    console.log('📡 Fetching booking details from:', apiUrl);

    this.http.get(apiUrl).subscribe({
      next: data => {
        console.log('✅ Booking details received:', data);
        this.bookingDetails = data;
        this.loading = false;
      },
      error: err => {
        console.error('❌ Failed to load booking details:', err);
        this.errorMessage = 'Failed to load booking details.';
        this.loading = false;
      }
    });
  }

  payNow() {
    if (!this.bookingId) {
      console.warn('⚠️ Cannot pay: Missing booking ID');
      return;
    }

    const confirmUrl =
      this.bookingDetails.category === 'package'
        ? 'http://127.0.0.1:8000/auth/confirmpackage/'
        : 'http://127.0.0.1:8000/auth/confirmflight/';

    console.log('💳 Initiating payment for:', this.bookingDetails.category);

    const payload = {
      booking_id: this.bookingId,
      status: 'completed',
      transaction_id: 'TXN' + Date.now()
    };

    this.http.post(confirmUrl, payload).subscribe({
      next: () => {
        console.log('✅ Payment successful!');
        alert('Payment successful! Redirecting...');

        // 🔔 Show push notification
        this.sendNotification();

        this.router.navigate(['/user-dashboard']);
      },
      error: err => {
        console.error('❌ Payment failed:', err);
        alert('Payment failed.');
      }
    });
  }

  initFirebaseMessaging() {
    const app = initializeApp(environment.firebaseConfig);
    const messaging = getMessaging(app);

    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        getToken(messaging, {
          vapidKey: environment.firebaseConfig.vapidKey
        }).then(token => {
          console.log('📲 FCM Token (frontend):', token);
          this.fcmToken = token;

          // ✅ Send FCM token to backend
          if (this.bookingId && token) {
            this.http.post('http://127.0.0.1:8000/auth/registerfcm/', {
              token: token,
              booking_id: this.bookingId
            }).subscribe({
              next: () => console.log('✅ FCM token registered with backend.'),
              error: err => console.error('❌ Failed to register FCM token:', err)
            });
          }
        }).catch(err => {
          console.error('❌ Error getting FCM token:', err);
        });
      } else {
        console.warn('❌ Notification permission denied.');
      }
    });
  }

  sendNotification() {
    // ⛳ Optional: You can trigger backend-side FCM message from here
    // OR do it inside Django confirm API after payment
    console.log('🔔 Push notification will be triggered from backend');
  }
}
