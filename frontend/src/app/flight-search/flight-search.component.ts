import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  standalone: true,
  selector: 'app-flight-search',
  templateUrl: './flight-search.component.html',
  styleUrls: ['./flight-search.component.css'],
  imports: [CommonModule, FormsModule,NavbarComponent,FooterComponent]
})
export class FlightSearchComponent {
  sourceQuery = '';
  destinationQuery = '';
  travelDate = '';
  errorMessage: string = '';
  sourceResults: any[] = [];
  destinationResults: any[] = [];
  flights: any[] = [];
  flightRoutes: any = null;

  selectedSource: any = null;
  selectedDestination: any = null;

  constructor(private http: HttpClient, private router: Router) {}

  searchSource() {
    if (this.sourceQuery.trim()) {
      this.http.get<any[]>(`http://127.0.0.1:8000/auth/searchdestinations/?q=${this.sourceQuery}`)
        .subscribe(data => this.sourceResults = data);
    } else {
      this.sourceResults = [];
    }
  }

  searchDestination() {
    if (this.destinationQuery.trim()) {
      this.http.get<any[]>(`http://127.0.0.1:8000/auth/searchdestinations/?q=${this.destinationQuery}`)
        .subscribe(data => this.destinationResults = data);
    } else {
      this.destinationResults = [];
    }
  }

  selectSource(src: any) {
    this.selectedSource = src;
    this.sourceQuery = src.name;
    this.sourceResults = [];
  }

  selectDestination(dest: any) {
    this.selectedDestination = dest;
    this.destinationQuery = dest.name;
    this.destinationResults = [];
  }

  // Optional: you can use this later
  bookFlight(flight: any) {
    console.log('Booking flight:', flight);
  }

  // ✅ Use route_id to navigate to /book-route/:id
  bookRoute(path: any) {
    if (path.route_id) {
      this.router.navigate(['/book-route', path.route_id]);
    } else {
      console.error('Missing route_id in path:', path);
    }
  }

  searchFlightRoutes() {
    this.errorMessage = '';
  
    if (!this.sourceQuery || !this.destinationQuery) {
      this.errorMessage = 'Please select both source and destination.';
      return;
    }
  
    if (this.sourceQuery.trim().toLowerCase() === this.destinationQuery.trim().toLowerCase()) {
      this.errorMessage = 'Source and destination cannot be the same.';
      this.flightRoutes = null;
      return;
    }
  
    if (!this.travelDate) {
      this.errorMessage = 'Please select a travel date.';
      return;
    }
  
    const params = new URLSearchParams({
      source: this.sourceQuery,
      destination: this.destinationQuery,
      travel_date: this.travelDate // optional: send it to the backend too
    });
  
    this.http.get<any>(`http://127.0.0.1:8000/auth/getflightroutes/?${params}`).subscribe({
      next: data => {
        this.flightRoutes = data;
        console.log("✈️ Received flight routes:", data);
        if (!data.all_paths || data.all_paths.length === 0) {
          this.errorMessage = 'No routes found between selected cities.';
        }
      },
      error: err => {
        console.error('Server error:', err);
        this.flightRoutes = null;
        this.errorMessage = 'Something went wrong. Please try again later.';
      }
    });
  }
  
}
