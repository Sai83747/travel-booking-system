import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { CategorySearchComponent } from '../../category-search/category-search.component';
import { AdminNavbarComponent } from "../../admin-navbar/admin-navbar.component";
@Component({
  standalone: true,
  selector: 'app-admin-dashboard',
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css'],
  imports: [CommonModule, ReactiveFormsModule, CategorySearchComponent, AdminNavbarComponent],
})

export class AdminDashboardComponent {
  // Modal states
  destinations: any[] = [];
  isAdminModalOpen = false;
  isAgentModalOpen = false;
  isDestinationModalOpen = false;
  isHotelModalOpen = false;
  isFlightModalOpen = false;
  isPackageModalOpen = false;

  // Forms
  adminForm: FormGroup;
  agentForm: FormGroup;
  destinationForm: FormGroup;
  hotelForm: FormGroup;
  flightForm: FormGroup;
  packageForm: FormGroup;

  // Messages
  adminMessage = '';
  agentMessage = '';
  destinationMessage = '';
  hotelMessage = '';
  flightMessage = '';
  packageMessage = '';

  constructor(private fb: FormBuilder, private http: HttpClient) {
    this.adminForm = this.fb.group({
      display_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone_number: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]],
      location: ['', Validators.required],
    });

    this.agentForm = this.fb.group({
      display_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone_number: ['', [Validators.required, Validators.pattern('^[0-9]{10}$')]],
      location: ['', Validators.required],
    });

    this.destinationForm = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      location: ['', Validators.required],
      image_url: [''],
      price: [0, [Validators.required, Validators.min(0)]],
      availability: [true],
    });

    this.hotelForm = this.fb.group({
      name: ['', Validators.required],
    
      price_per_night: [0, [Validators.required, Validators.min(0)]],
      available_rooms: [0, [Validators.required, Validators.min(1)]],
      discount: [0, [Validators.min(0), Validators.max(100)]],
      destination: ['', Validators.required],
      image_url: ['']
    });
    

  
   this.flightForm = this.fb.group({
  flight_number: ['', Validators.required],
  source: ['', Validators.required],
  destination: ['', Validators.required],
  available_seats: [0, [Validators.required, Validators.min(1)]],
  price_per_seat: [0, Validators.required],
  discount: [0],
  flight_icon_url: ['']  // Optional field
});


    this.packageForm = this.fb.group({
      name: ['', Validators.required],
      source: ['', Validators.required],
      price: [0, [Validators.required, Validators.min(0)]],
      destination: ['', Validators.required],
      image_url: ['', Validators.required],
      duration_days: [0, [Validators.required, Validators.min(1)]],
      discount: [0],
    });
    
  }

  // ADMIN
  openAdminModal() {
    this.isAdminModalOpen = true;
    this.adminForm.reset();
    this.adminMessage = '';
  }
  closeAdminModal() {
    this.isAdminModalOpen = false;
  }
  registerAdmin() {
    if (this.adminForm.invalid) return;
    const payload = this.adminForm.value;
    this.http.post('http://127.0.0.1:8000/auth/admini/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        this.adminMessage = `✅ Admin ${res.user.email} created. Temporary password: ${res.user.temporary_password}`;
      },
      error: (err) => {
        this.adminMessage = `❌ Error: ${err.error.error}`;
      },
    });
  }


  ngOnInit() {
    this.getAllDestinations();
  }
  
  getAllDestinations() {
    this.http.get<{ destinations: any[] }>('http://localhost:8000/auth/getdest/')
      .subscribe({
        next: (res) => {
          this.destinations = res.destinations;
        },
        error: (err) => {
          console.error('Failed to fetch destinations', err);
        }
      });
  }
  // AGENT
  openAgentModal() {
    this.isAgentModalOpen = true;
    this.agentForm.reset();
    this.agentMessage = '';
  }
  closeAgentModal() {
    this.isAgentModalOpen = false;
  }
  registerAgent() {
    if (this.agentForm.invalid) return;
    const payload = this.agentForm.value;
    this.http.post('http://127.0.0.1:8000/auth/agent/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        this.agentMessage = `✅ Agent ${res.user.email} created. Temporary password: ${res.user.temporary_password}`;
      },
      error: (err) => {
        this.agentMessage = `❌ Error: ${err.error.error}`;
      },
    });
  }

  // DESTINATION
  openDestinationModal() {
    this.isDestinationModalOpen = true;
    this.destinationForm.reset({ availability: true });
    this.destinationMessage = '';
  }
  closeDestinationModal() {
    this.isDestinationModalOpen = false;
  }
  addDestination() {
    if (this.destinationForm.invalid) return;
    const payload = this.destinationForm.value;
    this.http.post('http://127.0.0.1:8000/auth/admin/destination/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        this.destinationMessage = `✅ Destination "${res.destination.name}" added successfully.`;
      },
      error: (err) => {
        this.destinationMessage = `❌ Error: ${err.error.error}`;
      },
    });
  }

  // HOTEL
  openHotelModal() {
    this.isHotelModalOpen = true;
    this.hotelForm.reset();
    this.hotelMessage = '';
  }
  closeHotelModal() {
    this.isHotelModalOpen = false;
  }
  addHotel() {
    if (this.hotelForm.invalid) return;
    console.log(this.hotelForm.value);
    const payload = this.hotelForm.value;
    this.http.post('http://127.0.0.1:8000/auth/hotels/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        console.log('Hotel add response:', res); 
        this.hotelMessage = `✅ Hotel "${res.hotel.name}" added successfully.`;
      },
      error: (err) => {
        this.hotelMessage = `❌ Error: ${err.error.error}`;
      },
    });
    console.log('api called');
  }

  // FLIGHT
  openFlightModal() {
    this.isFlightModalOpen = true;
    this.flightForm.reset();
    this.flightMessage = '';
  }
  closeFlightModal() {
    this.isFlightModalOpen = false;
  }
  addFlight() {
    if (this.flightForm.invalid) return;
    const payload = this.flightForm.value;
    this.http.post('http://127.0.0.1:8000/auth/flights/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        console.log('Flight add response:', res);
        this.flightMessage = `✅ Flight "${res.flight.flight_number}" added successfully.`;
      },
      error: (err) => {
        this.flightMessage = `❌ Error: ${err.error.error}`;
      },
    });
  }

  // PACKAGE
  openPackageModal() {
    this.isPackageModalOpen = true;
    this.packageForm.reset();
    this.packageMessage = '';
  }
  closePackageModal() {
    this.isPackageModalOpen = false;
  }
  addPackage() {
    if (this.packageForm.invalid) return;
    const payload = this.packageForm.value;
    this.http.post('http://127.0.0.1:8000/auth/addpackages/', payload, { withCredentials: true }).subscribe({
      next: (res: any) => {
        console.log('Package add response:', res);
        this.packageMessage = `✅ Package "${res.package.name}" added successfully.`;
      },
      error: (err) => {
        this.packageMessage = `❌ Error: ${err.error.error}`;
      },
    });
  }
}
