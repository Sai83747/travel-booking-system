import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgIf, NgFor, CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { NavbarComponent } from "../navbar/navbar.component";
import { FooterComponent } from "../footer/footer.component";

@Component({
  selector: 'app-booking-history',
  templateUrl: './booking-history.component.html',
  imports: [NgIf, NgFor, FormsModule, CommonModule, NavbarComponent, FooterComponent],
  styleUrls: ['./booking-history.component.css']
})
export class BookingHistoryComponent implements OnInit {
  bookings: any[] = [];
  refunds: any[] = [];
  userId = 1; // Replace with actual logged-in user ID

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchBookingHistory();
    this.fetchRefunds();
  }

  fetchBookingHistory(): void {
    this.http.get<any>(`http://127.0.0.1:8000/auth/getbookinghistory/${this.userId}/`).subscribe(
      (response) => {
        this.bookings = response.bookings;
      },
      (error) => {
        console.error('Error fetching booking history:', error);
      }
    );
  }
  showReviewModal = false;
  selectedBooking: any = null;
  reviewData = {
    user_id: '', // fill dynamically from auth context or user session
    object_id: '',
    model_name: '',
    rating: 5,
    feedback: ''
  };
  
  cancelBooking(bookingId: number) {
    const confirmCancel = confirm(`Are you sure you want to cancel booking #${bookingId}?`);
    if (!confirmCancel) return;
  
    this.http.post('http://127.0.0.1:8000/auth/cancelbooking/', { booking_id: bookingId }).subscribe(
      (res: any) => {
        alert('✅ Booking cancelled.');
        this.fetchBookingHistory(); // Refresh booking list
        this.fetchRefunds();        // 👈 Refresh refunds list too
      },
      err => {
        alert('❌ Error cancelling booking.');
        console.error(err);
      }
    );
  }
  
  
  openReviewModal(booking: any) {
    console.log('Opening review modal for booking:', booking);
  
    this.selectedBooking = booking;
  
    let actualObjectId = null;
  
    if (booking.category === 'hotel' && booking.hotel) {
      actualObjectId = booking.hotel.id;
    } else if (booking.category === 'flight' && booking.flight) {
      actualObjectId = booking.flight.id;
    } else if (booking.category === 'package' && booking.package) {
      actualObjectId = booking.package.id;
    } else {
      console.error('❌ Could not determine object_id for review');
      return;
    }
  
    this.reviewData = {
      user_id: booking.user_id,
      object_id: actualObjectId,
      model_name: booking.category.toLowerCase(),
      rating: 5,
      feedback: ''
    };
  
    console.log('✅ Review data prepared:', this.reviewData);
  
    this.showReviewModal = true;
  }
  
  
  closeReviewModal() {
    this.showReviewModal = false;
  }
  
  submitReview() {
    this.http.post('http://127.0.0.1:8000/auth/addorupdatereview/', this.reviewData).subscribe(
      (res: any) => {
        alert(res.message || '✅ Review submitted.');
        this.closeReviewModal();
      },
      err => {
        alert('❌ Failed to submit review.');
        console.error(err);
      }
    );
  }
  
  fetchRefunds(): void {
    this.http.get<any>(`http://127.0.0.1:8000/auth/getmyrefunds/${this.userId}/`).subscribe(
      (response) => {
        this.refunds = response.refunds;
      },
      (error) => {
        console.error('Error fetching refunds:', error);
      }
    );
  }
}
