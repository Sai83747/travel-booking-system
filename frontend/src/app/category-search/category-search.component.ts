import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-category-search',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './category-search.component.html',
})
export class CategorySearchComponent implements OnInit {
  categoryOptions = ['flights', 'hotels', 'packages'];
  selectedCategory = 'flights';
  query = '';
  results: any[] = [];
  loading = false;

  showPackageModal = false;
  selectedPackageDetails: any = null;
  showEditFlightModal = false;
  editFlightData: any = {};
  selectedFlightId: number | null = null;
  
  showUpdateModal = false;
  selectedFlight: any = null;
  updatedSeats: number = 0;
  updatedAvailability: boolean = true;
  fullEditMode = false;

  flightForm!: FormGroup;
  destinations: any[] = [];

  constructor(private http: HttpClient, private fb: FormBuilder) {}

  ngOnInit(): void {
    this.fetchCategoryItems();
    this.fetchDestinations();
    this.initFlightForm();
  }

  initFlightForm() {
    this.flightForm = this.fb.group({
      flight_number: ['', Validators.required],
      source_id: ['', Validators.required],
      destination_id: ['', Validators.required],
      discount: [0, Validators.required],
      price_per_seat: [0, Validators.required],
    });
  }

  onCategoryChange(event: Event) {
    this.selectedCategory = (event.target as HTMLSelectElement).value;
    this.query = '';
    this.fetchCategoryItems();
  }

  onSearch() {
    this.fetchCategoryItems(this.query);
  }
  openEditFlightModal(flight: any) {
    this.selectedFlightId = flight.id;
    this.editFlightData = {
      flight_number: flight.flight_number,
      source_id: flight.source_id || '',
      destination_id: flight.destination_id || '',
      price_per_seat: flight.price_per_seat || '',
      discount: flight.discount || ''
    };
    this.showEditFlightModal = true;
  }
  
  closeEditFlightModal() {
    this.showEditFlightModal = false;
    this.editFlightData = {};
    this.selectedFlightId = null;
  }
  
  submitFlightEdit() {
    const payload = { ...this.editFlightData };
  
    // Remove empty fields to avoid overwriting with blank values
    Object.keys(payload).forEach(key => {
      if (payload[key] === '' || payload[key] === null || payload[key] === undefined) {
        delete payload[key];
      }
    });
  
    if (!this.selectedFlightId) return;
  
    this.http.patch(`http://127.0.0.1:8000/auth/updateflight/${this.selectedFlightId}/`, payload).subscribe({
      next: (response: any) => {
        alert(`Flight Updated!\n\nResponse:\n${JSON.stringify(response, null, 2)}`);
        this.closeEditFlightModal();
        this.onSearch(); // refresh result if needed
      },
      error: (err) => {
        alert('Update failed: ' + (err.error?.error || 'Unknown error'));
      }
    });
  }
  
  fetchCategoryItems(query: string = '') {
    this.loading = true;
    let apiUrl = 'http://127.0.0.1:8000';

    if (this.selectedCategory === 'flights') {
      apiUrl += query ? `/auth/searchflights?query=${query}` : `/auth/searchflights/`;
    } else if (this.selectedCategory === 'hotels') {
      apiUrl += query ? `/auth/searchhotels?query=${query}` : `/auth/searchhotels/`;
    } else if (this.selectedCategory === 'packages') {
      apiUrl += query ? `/auth/searchpackages?query=${query}` : `/auth/searchpackages/`;
    }

    this.http.get<any[]>(apiUrl).subscribe({
      next: (data) => {
        this.results = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('API Error:', err);
        this.results = [];
        this.loading = false;
      }
    });
  }

  fetchDestinations() {
    console.log('📡 Fetching destinations...');
  
    this.http.get<any>('http://127.0.0.1:8000/auth/getdest/').subscribe({
      next: (res) => {
        console.log('✅ Full response:', res);
        this.destinations = res.destinations; // since it's wrapped inside 'destinations' key
        console.log('📋 Assigned destinations:', this.destinations);
      },
      error: (err) => {
        console.error('❌ Failed to load destinations', err);
      }
    });
  }

  openPackageDetails(packageId: number) {
    this.http.get(`http://127.0.0.1:8000/auth/packagedetails/${packageId}`).subscribe({
      next: (res: any) => {
        console.log('Package Details:', res);
        this.selectedPackageDetails = res;
        this.showPackageModal = true;
      },
      error: (err) => {
        console.error('Error fetching package details:', err);
      }
    });
  }

  closePackageModal() {
    this.showPackageModal = false;
    this.selectedPackageDetails = null;
  }

  intermediateCities(path: any): string[] {
    if (!path.path || !path.intermediate_hotels) return [];
    return path.path.slice(1, path.path.length - 1).filter(
      (city: string) => path.intermediate_hotels.hasOwnProperty(city)
    );
  }

 
  // Store destination list
  updatedSourceId: number | null = null;
  updatedDestinationId: number | null = null;
  
  openUpdateModal(flight: any) {
    this.selectedFlight = flight;
    this.updatedSeats = flight.available_seats;
    this.updatedAvailability = flight.is_available;
  
    this.updatedSourceId = flight.source_id;
    this.updatedDestinationId = flight.destination_id;
  
    this.showUpdateModal = true;
  }
  
  
  
  openFullEditModal(flight: any) {
    this.selectedFlight = { ...flight };
    this.fullEditMode = true;
    this.showUpdateModal = true;

    this.flightForm.patchValue({
      flight_number: flight.flight_number,
      source_id: flight.source.id,
      destination_id: flight.destination.id,
      discount: flight.discount,
      price_per_seat: flight.price_per_seat,
    });
  }

  submitFlightUpdate() {
    const updatedData: any = {
      is_available: this.updatedAvailability,
      available_seats: this.updatedSeats,
      source: this.updatedSourceId,
      destination: this.updatedDestinationId
    };
  
    console.log('📦 Sending updated flight data:', updatedData);
  
    this.http.patch(`http://localhost:8000/auth/updateflightava/${this.selectedFlight.id}/`, updatedData)
      .subscribe({
        next: (res: any) => {
          alert(`✅ ${res.message}
  ✈️ Flight: ${res.flight_number}
  📍 Source: ${res.updated_fields.source}
  📍 Destination: ${res.updated_fields.destination}
  📊 Availability: ${res.updated_fields.is_available}
  🪑 Seats: ${res.updated_fields.available_seats}`);
  
          // Update local state
          this.selectedFlight.source = res.updated_fields.source;
          this.selectedFlight.destination = res.updated_fields.destination;
          this.selectedFlight.is_available = res.updated_fields.is_available;
          this.selectedFlight.available_seats = res.updated_fields.available_seats;
  
          this.closeUpdateModal();
        },
        error: (err) => {
          console.error('❌ Update failed', err);
          alert('❌ Failed to update flight');
        }
      });
  }
  

  updateFlightAvailability(flight: any) {
    const updatedData = {
      is_available: !flight.is_available,
      available_seats: flight.available_seats
    };

    this.http.patch(`http://localhost:8000/auth/updateflightava/${flight.id}/`, updatedData)
      .subscribe({
        next: (res: any) => {
          alert(`✅ ${res.message}\n\n✈️ Flight: ${res.flight_number}\n🪪 ID: ${res.flight_id}\n📊 Availability: ${res.updated_fields.is_available}\n🪑 Seats: ${res.updated_fields.available_seats}`);
          flight.is_available = res.updated_fields.is_available;
          flight.available_seats = res.updated_fields.available_seats;
        },
        error: (err) => {
          console.error(err);
          alert('❌ Failed to update flight availability');
        }
      });
  }

  submitFullFlightUpdate() {
    if (this.flightForm.invalid) return;

    const updatedFlight = this.flightForm.value;

    this.http.patch(`http://localhost:8000/auth/updateflight/${this.selectedFlight.id}/`, updatedFlight)
      .subscribe({
        next: (res: any) => {
          alert(`✅ ${res.message}`);
          this.closeUpdateModal();
          this.fetchCategoryItems();
        },
        error: (err) => {
          console.error('Full update failed:', err);
          alert('❌ Failed to update full flight details');
        }
      });
  }
  editingHotel: any = null;
  showEditPackageModal = false;
  editPackage: any = {}; // holds package to edit
  
  openPackageEditModal(pkg: any) {
    this.editPackage = { ...pkg }; // clone to avoid direct mutation
    this.showEditPackageModal = true;
  }
  
  closeEditPackageModal() {
    this.showEditPackageModal = false;
  }
openEditHotelModal(hotel: any) {
  this.editingHotel = { ...hotel }; // Clone to avoid mutating the original
}

closeHotelModal() {
  this.editingHotel = null;
}
updatePackage() {
  if (!this.editPackage) return;

  const original = this.results.find((p: any) => p.id === this.editPackage.id);
  const payload: any = {};

  // Compare and include only changed fields
  if (original.source !== this.editPackage.source) {
    payload.source = this.editPackage.source;
  }
  if (original.price !== this.editPackage.price) {
    payload.price = this.editPackage.price;
  }
  if (original.discount !== this.editPackage.discount) {
    payload.discount = this.editPackage.discount;
  }
  if (original.duration_days !== this.editPackage.duration_days) {
    payload.duration_days = this.editPackage.duration_days;
  }

  if (Object.keys(payload).length === 0) {
    alert("No changes detected.");
    return;
  }

  this.http.patch<any>(`http://127.0.0.1:8000/auth/updatepackage/${this.editPackage.id}/`, payload).subscribe({
    next: (res) => {
      const updated = res.updated_fields;
      let message = `✅ Package updated successfully!\n\n`;

      if (updated.source) {
        message += `Source: ${updated.source.previous} → ${updated.source.current}\n`;
      }
      if (updated.price !== undefined) {
        message += `Price: ₹${updated.price}\n`;
      }
      if (updated.discount !== undefined) {
        message += `Discount: ${updated.discount}%\n`;
      }
      if (updated.duration_days !== undefined) {
        message += `Duration: ${updated.duration_days} days\n`;
      }

      alert(message);
      this.closeEditPackageModal();
      this.onSearch(); // Refresh the list
    },
    error: (err) => {
      console.error("Package update failed:", err);
      alert("Failed to update package.");
    }
  });
}

submitHotelUpdate() {
  if (!this.editingHotel) return;

  const payload: any = {};
  const original = this.results.find(h => h.id === this.editingHotel.id);

  if (original.available_rooms !== this.editingHotel.available_rooms) {
    payload.available_rooms = this.editingHotel.available_rooms;
  }
  if (original.is_available !== this.editingHotel.is_available) {
    payload.is_available = this.editingHotel.is_available;
  }
  if (original.price_per_night !== this.editingHotel.price_per_night) {
    payload.price_per_night = this.editingHotel.price_per_night;
  }
  if (original.discount !== this.editingHotel.discount) {
    payload.discount = this.editingHotel.discount;
  }

  if (Object.keys(payload).length === 0) {
    alert("No changes detected.");
    return;
  }

  this.http.patch<any>(`http://localhost:8000/auth/updatehotel/${this.editingHotel.id}/`, payload)
    .subscribe({
      next: (res) => {
        const updatedFields = res.updated_fields;
        let message = '✅ Hotel updated successfully!\n\n';

        for (let key in updatedFields) {
          const label = this.formatLabel(key);
          const value = key === 'is_available'
            ? (updatedFields[key] ? 'Available' : 'Unavailable')
            : updatedFields[key];

          message += `${label}: ${value}\n`;
        }

        alert(message);
        this.closeHotelModal();
        this.onSearch();
      },
      error: (err) => {
        console.error('Update failed:', err);
        alert("❌ Failed to update hotel.");
      }
    });
}

// Helper method for formatting keys
formatLabel(key: string): string {
  switch (key) {
    case 'available_rooms': return 'Available Rooms';
    case 'is_available': return 'Availability';
    case 'price_per_night': return 'Price per Night (₹)';
    case 'discount': return 'Discount (%)';
    default: return key;
  }
}

  
  closeUpdateModal() {
    this.showUpdateModal = false;
    this.selectedFlight = null;
    this.fullEditMode = false;
  }
}
