import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { NgFor, NgIf } from '@angular/common';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-book-route',
  templateUrl: './book-route.component.html',

  standalone: true,
  imports: [NgFor, NgIf,NavbarComponent,FooterComponent],
})
export class BookRouteComponent implements OnInit {
  routeDetails: any = null;
  loading = true;
  errorMessage = '';
  numOfSeats = 1;

  constructor(
    private route: ActivatedRoute,
    private http: HttpClient
  ) {}

  ngOnInit(): void {
    const routeId = this.route.snapshot.paramMap.get('id');
    if (routeId) {
      this.fetchRouteDetails(routeId);
    } else {
      this.errorMessage = 'Invalid route ID.';
      this.loading = false;
    }
  }

  increaseSeats() {
    if (this.routeDetails && this.numOfSeats < this.routeDetails.min_available_seats) {
      this.numOfSeats++;
    }
  }

  decreaseSeats() {
    if (this.numOfSeats > 1) {
      this.numOfSeats--;
    }
  }

  fetchRouteDetails(routeId: string) {
    this.http
      .get<any>(`http://127.0.0.1:8000/auth/getflightroutes/?id=${routeId}`)
      .subscribe({
        next: data => {
          this.routeDetails = data;
          this.loading = false;
        },
        error: err => {
          console.error('Failed to load route details:', err);
          this.errorMessage = 'Unable to load route details.';
          this.loading = false;
        },
      });
  }

  confirmBooking() {
    const user_id = localStorage.getItem('user_id');
    if (!user_id) {
      alert('User not logged in.');
      return;
    }

    // Safety check
    if (!this.routeDetails?.legs || this.routeDetails.legs.length === 0) {
      alert('Route information is invalid.');
      return;
    }

    const flightNumbers: string[] = [];
    for (const leg of this.routeDetails.legs) {
      if (!leg.flights || leg.flights.length === 0) {
        alert('One or more route legs have no flights.');
        return;
      }
      flightNumbers.push(leg.flights[0].flight_number);
    }

    const sourceName = this.routeDetails.route[0];
    const destinationName = this.routeDetails.route.at(-1);

    this.getDestinationIds(sourceName, destinationName).then((ids) => {
      const payload = {
        user_id,
        source_id: ids.source_id,
        destination_id: ids.destination_id,
        number_of_people: this.numOfSeats,
        flight_numbers: flightNumbers
      };

      this.http.post('http://127.0.0.1:8000/auth/flightbooking/', payload).subscribe({
        next: (res: any) => {
          if (confirm(`Booking Confirmed!\nBooking ID: ${res.booking_id}\nProceed to payment?`)) {
            window.location.href = `/payment/${res.booking_id}`;
          }
        },
        error: err => {
          console.error('Booking error:', err);
          alert(err.error?.error || 'Booking failed.');
        }
      });
    }).catch((err) => {
      console.error('Failed to resolve destination IDs:', err);
    });
  }

  getDestinationIds(sourceName: string, destinationName: string): Promise<{ source_id: number; destination_id: number }> {
    return new Promise((resolve, reject) => {
      this.http.get<any>('http://127.0.0.1:8000/auth/getdest/').subscribe({
        next: (response) => {
          const destinations = response.destinations;

          if (!Array.isArray(destinations)) {
            console.error('Invalid destinations format:', response);
            alert('Unexpected destination format from backend.');
            reject('Invalid format');
            return;
          }

          const source = destinations.find(dest => dest.name.toLowerCase() === sourceName.toLowerCase());
          const destination = destinations.find(dest => dest.name.toLowerCase() === destinationName.toLowerCase());

          if (!source || !destination) {
            alert(`Could not resolve IDs for ${sourceName} → ${destinationName}`);
            reject('Invalid destinations');
            return;
          }

          resolve({
            source_id: source.id,
            destination_id: destination.id
          });
        },
        error: err => {
          console.error('Error fetching destination list:', err);
          alert('Failed to resolve destinations.');
          reject(err);
        }
      });
    });
  }
}
