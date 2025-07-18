import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { NgFor, NgIf } from '@angular/common';
import { FlightSearchComponent } from '../../flight-search/flight-search.component';
import { HotelSearchComponent } from '../../hotels-search/hotels-search.component';
import { PackageSearchComponent } from '../../package-search/package-search.component';
import { BookingHistoryComponent } from "../../booking-history/booking-history.component";
import { FooterComponent } from "../../footer/footer.component";
import { NavbarComponent } from "../../navbar/navbar.component";
import { CarouselComponent } from '../../carousel/carousel.component';
import { SidedashboardComponent } from '../../sidedashboard/sidedashboard.component';
import { RouterModule } from '@angular/router';
import { routes } from '../../app.routes';
@Component({
  standalone: true,
  selector: 'app-user-dashboard',
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.css'],
  imports: [CommonModule, HttpClientModule, NgFor, NgIf,RouterModule, FlightSearchComponent,SidedashboardComponent, HotelSearchComponent, PackageSearchComponent, BookingHistoryComponent, FooterComponent, NavbarComponent,CarouselComponent],
})
export class UserDashboardComponent implements OnInit {
  packages: any[] = [];
  username: string = 'traveler';

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchPackages();
    this.loadUserName();
  }

  fetchPackages() {
    this.http.get<any[]>('http://127.0.0.1:8000/auth/searchpackages/').subscribe({
      next: data => this.packages = data.filter(pkg => pkg.availability > 0),
      error: (err: HttpErrorResponse) => console.error('Failed to load packages', err.message)
    });
  }
  showSidebar = false;

  toggleSidebar() {
    this.showSidebar = !this.showSidebar;
  }
  loadUserName() {
    const userId = localStorage.getItem('user_id');
    if (userId) {
      this.http.get<any>(`http://127.0.0.1:8000/auth/user/${userId}/`).subscribe({
        next: user => this.username = user.display_name,
        error: err => console.error('Failed to load user data', err)
      });
    }
  }
}