import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { NgIf, NgFor, NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-package-search',
  templateUrl: './package-search.component.html',
  styleUrls: ['./package-search.component.css'],
  standalone: true,
  imports: [NgIf, NgFor, FormsModule, CommonModule, NgClass,NavbarComponent,FooterComponent]
})
export class PackageSearchComponent implements OnInit {

  sourceQuery: string = '';
  destinationQuery: string = '';
  sourceResults: any[] = [];
  destinationResults: any[] = [];
  selectedSource: any = null;
  selectedDestination: any = null;

  minPrice: number = 0;
  maxPrice: number = 99999;

  packages: any[] = [];
  loading = false;
  errorMessage = '';
  user_id = 1; // Replace with actual user ID

  selectedPackage: any = null;
  packageDetails: Array<{
    path: string[],
    availability: number,
    price: number,
    flights: any[],
    source_hotels: any[],
    destination_hotels: any[],
    intermediate_hotels: { [key: string]: any[] }
    numPeople: number 
  }> = [];
   // ✅ Explicitly set to an array
  showDetailsModal: boolean = false;

  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit(): void {}

  searchSource() {
    if (this.sourceQuery.trim()) {
      this.http.get<any[]>(`http://127.0.0.1:8000/auth/searchdestinations/?q=${this.sourceQuery}`)
        .subscribe(data => this.sourceResults = data);
    }
  }

  searchDestination() {
    if (this.destinationQuery.trim()) {
      this.http.get<any[]>(`http://127.0.0.1:8000/auth/searchdestinations/?q=${this.destinationQuery}`)
        .subscribe(data => this.destinationResults = data);
    }
  }

  selectSource(source: any) {
    this.selectedSource = source;
    this.sourceQuery = source.name;
    this.sourceResults = [];
  }
  bookPath(path: any) {
    const numberOfPeople = path.numPeople || 1;
  
    const payload = {
      user_id: this.user_id,
      package_id: this.selectedPackage.id,
      number_of_people: numberOfPeople,
      status: 'pending',
      flights: path.flights.map((f: any) => f.id),
      hotels: [
        ...path.source_hotels.map((h: any) => h.id),
        ...path.destination_hotels.map((h: any) => h.id),
        ...Object.values(path.intermediate_hotels).flat().map((h: any) => h.id)
      ]
    };
  
    this.http.post('http://127.0.0.1:8000/auth/bookpackagepath/', payload).subscribe({
      next: (res: any) => {
        alert(`✅ Booking created! Booking ID: ${res.booking_id}. Redirecting to payment...`);
        this.router.navigate(['/payment', res.booking_id]);
      },
      error: (err) => {
        console.error('❌ Booking failed:', err);
        alert('❌ Failed to create booking. Please try again.');
      }
    });
  }
  
  selectDestination(dest: any) {
    this.selectedDestination = dest;
    this.destinationQuery = dest.name;
    this.destinationResults = [];
  }

  searchPackages() {
    if (!this.selectedSource?.id || !this.selectedDestination?.id) {
      this.errorMessage = 'Please select both source and destination.';
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    const params = new HttpParams()
      .set('source', this.selectedSource.id)
      .set('destination', this.selectedDestination.id)
      .set('min_price', this.minPrice.toString())
      .set('max_price', this.maxPrice.toString());

    this.http.get<any[]>('http://127.0.0.1:8000/auth/searchpackageuser/', { params }).subscribe({
      next: data => {
        this.packages = data;
        this.loading = false;
      },
      error: err => {
        console.error('❌ Failed to fetch packages:', err);
        this.errorMessage = 'Failed to load packages.';
        this.loading = false;
      }
    });
  }

  getAverageRating(pkg: any): number {
    const reviews = pkg.reviews || [];
    if (reviews.length === 0) return 0;
    const total = reviews.reduce((sum: number, r: any) => sum + r.rating, 0);
    return total / reviews.length;
  }

  ratePackage(pkg: any, rating: number) {
    const payload = {
      user_id: this.user_id,
      model_name: 'package',
      object_id: pkg.id,
      rating: rating,
      feedback: ''
    };

    this.http.post('http://127.0.0.1:8000/auth/addorupdatereview/', payload).subscribe({
      next: () => {
        pkg.reviews = this.updatePackageReviews(pkg.reviews, rating);
      },
      error: err => {
        console.error('Failed to submit package rating:', err);
      }
    });
  }

  viewPackageDetails(pkg: any) {
    const url = `http://127.0.0.1:8000/auth/packagedetails/${pkg.id}/`;
    this.http.get<any>(url).subscribe({
      next: (data) => {
        console.log('✅ Package Details Response:', data);
        this.selectedPackage = data.package;
        this.packageDetails = data.valid_paths || []; // ✅ Ensure it's always an array
        this.showDetailsModal = true;
        this.packageDetails = (data.valid_paths || []).map((path: any) => ({
          ...path,
          numPeople: 1
        }));
      },

      error: (err) => {
        console.error('❌ Failed to fetch package details:', err);
        alert('Failed to load package details.');
      }
    });
  }

  closeModal() {
    this.showDetailsModal = false;
    this.selectedPackage = null;
    this.packageDetails = [];
  }

  updatePackageReviews(reviews: any[], newRating: number) {
    const existing = reviews.find(r => r.user_id === this.user_id);
    if (existing) {
      existing.rating = newRating;
    } else {
      reviews.push({ user_id: this.user_id, rating: newRating });
    }
    return reviews;
  }
}
