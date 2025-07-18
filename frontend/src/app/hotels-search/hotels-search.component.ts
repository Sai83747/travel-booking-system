import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { NgIf, NgFor, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-hotel-search',
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, NgClass, CommonModule, NavbarComponent, FooterComponent],
  templateUrl: './hotels-search.component.html',
  styleUrls: ['./hotels-search.component.css']
})
export class HotelSearchComponent implements OnInit {
  destinationQuery: string = '';
  selectedDestination: any = null;
  destinationResults: any[] = [];
  guests: number = 1;
  minPrice: number = 0;
  maxPrice: number = 99999;
  hotels: any[] = [];
  loading = false;
  errorMessage = '';
  user_id = 1; // Replace with dynamic logged-in user if applicable

  showPopup: boolean = false;
  bookingDetails: any = null;

  // Pagination variables
  currentPage = 1;
  pageSize = 4;
  totalPages = 1;
  paginationRange: number[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.searchHotels();
  }

  searchDestination() {
    if (this.destinationQuery.trim()) {
      this.http.get<any[]>(`http://127.0.0.1:8000/auth/searchdestinations/?q=${this.destinationQuery}`)
        .subscribe(data => this.destinationResults = data);
    } else {
      this.destinationResults = [];
    }
  }

  selectDestination(dest: any) {
    this.selectedDestination = dest;
    this.destinationQuery = dest.name;
    this.destinationResults = [];
  }

  searchHotels(page: number = 1) {
    if (!this.destinationQuery || this.guests <= 0 || this.minPrice < 0 || this.maxPrice <= 0) {
      this.errorMessage = 'Please fill all fields correctly.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';
    this.currentPage = page;

    const params = new HttpParams()
      .set('destination', this.destinationQuery)
      .set('guests', this.guests.toString())
      .set('min_price', this.minPrice.toString())
      .set('max_price', this.maxPrice.toString())
      .set('page', page.toString())
      .set('page_size', this.pageSize.toString());

    this.http.get<any>('http://127.0.0.1:8000/auth/filterhotelsadv/', { params }).subscribe({
      next: (res) => {
        this.hotels = res.results || [];
        const totalItems = res.count || this.hotels.length;
        this.totalPages = Math.ceil(totalItems / this.pageSize);
        this.generatePagination();
        this.loading = false;
      },
      error: err => {
        console.error('❌ Failed to fetch hotels:', err);
        this.errorMessage = 'Failed to load hotels.';
        this.loading = false;
      }
    });
  }

  generatePagination() {
    this.paginationRange = Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }

  changePage(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.searchHotels(page);
    }
  }

  getAverageRating(hotel: any): number {
    const reviews = hotel.reviews || [];
    if (reviews.length === 0) return 0;
    const total = reviews.reduce((sum: number, r: any) => sum + r.rating, 0);
    return total / reviews.length;
  }

  rateHotel(hotel: any, rating: number) {
    const payload = {
      user_id: this.user_id,
      model_name: 'hotel',
      object_id: hotel.id,
      rating: rating,
      feedback: ''
    };

    this.http.post('http://127.0.0.1:8000/auth/addorupdatereview/', payload).subscribe({
      next: () => {
        hotel.reviews = this.updateHotelReviews(hotel.reviews, rating);
      },
      error: err => {
        console.error('Failed to submit rating:', err.error);
      }
    });
  }

  updateHotelReviews(reviews: any[], newRating: number) {
    const existing = reviews.find(r => r.user_id === this.user_id);
    if (existing) {
      existing.rating = newRating;
    } else {
      reviews.push({ user_id: this.user_id, rating: newRating });
    }
    return reviews;
  }

  bookHotel(hotel: any) {
    const payload = {
      user_id: this.user_id,
      hotel_id: hotel.id,
      number_of_people: this.guests,
      source_id: this.selectedDestination?.id || null
    };

    this.http.post('http://127.0.0.1:8000/auth/createhotelbooking/', payload).subscribe({
      next: (response: any) => {
        this.bookingDetails = response.booking;
        this.showPopup = true;
      },
      error: err => {
        console.error('Booking failed:', err);
        this.errorMessage = 'Failed to book hotel.';
      }
    });
  }

  closePopup() {
    this.showPopup = false;
    this.bookingDetails = null;
  }

  proceedToPayment() {
    const payload = {
      booking_id: this.bookingDetails.booking_id,
      payment_method: 'online'
    };

    this.http.post('http://127.0.0.1:8000/auth/confirmhotel/', payload).subscribe({
      next: (res: any) => {
        alert(`✅ Payment successful!\nTransaction ID: ${res.transaction_id}`);
        this.closePopup();
      },
      error: err => {
        console.error('Payment failed:', err);
        alert('❌ Payment failed. Please try again.');
      }
    });
  }
}
