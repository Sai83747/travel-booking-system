import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { NgFor, NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-agent-dashboard',
  templateUrl: './agent-dashboard.component.html',
  imports: [NgFor, NgIf, FormsModule, CommonModule],
})
export class AgentDashboardComponent implements OnInit {
  bookings: any[] = [];
  filteredBookings: any[] = [];

  // Filter fields
  searchText: string = '';
  selectedCategory: string = '';
  selectedStatus: string = '';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.loadBookings();
  }
  processRefund(bookingId: number): void {
    const confirmRefund = confirm(`Are you sure you want to process refund for booking #${bookingId}?`);
    if (!confirmRefund) return;
  
    this.http.post(`http://127.0.0.1:8000/auth/processrefund/${bookingId}/`, {}).subscribe(
      res => {
        alert(`✅ Refund processed for booking #${bookingId}`);
  
       
        this.filteredBookings = this.filteredBookings.filter(b => b.booking_id !== bookingId);
        this.bookings = this.bookings.filter(b => b.booking_id !== bookingId);
  
     
        // this.loadBookings();
      },
      err => {
        alert(`❌ Failed to process refund.`);
        console.error(err);
      }
    );
  }
  
  loadBookings(): void {
    this.http.get<any>('http://127.0.0.1:8000/auth/getallbookings/').subscribe(
      response => {
        console.log('✅ API Response:', response);
        this.bookings = response.bookings || [];
        this.filteredBookings = [...this.bookings];
        console.log('🗃️ Loaded Bookings:', this.filteredBookings);
      },
      error => {
        console.error('❌ Error fetching bookings:', error);
      }
    );
  }

  filterBookings(): void {
    this.filteredBookings = this.bookings.filter(booking => {
      const matchesSearch =
        !this.searchText ||
        booking.user_name.toLowerCase().includes(this.searchText.toLowerCase()) ||
        booking.source?.toLowerCase().includes(this.searchText.toLowerCase()) ||
        booking.destination?.toLowerCase().includes(this.searchText.toLowerCase());

      const matchesCategory =
        !this.selectedCategory || booking.category === this.selectedCategory;

      const matchesStatus =
        !this.selectedStatus || booking.status === this.selectedStatus;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }
}
