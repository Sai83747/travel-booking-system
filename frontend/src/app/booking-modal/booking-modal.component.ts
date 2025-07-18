import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-booking-modal',
  templateUrl: './booking-modal.component.html',
  styleUrls: ['./booking-modal.component.css']
})
export class BookingModalComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: any,
    private dialogRef: MatDialogRef<BookingModalComponent>
  ) {}

  proceedToPayment() {
    // Here you could redirect to a payment page or emit an event
    alert(`Proceeding to payment for Booking ID: ${this.data.booking_id}`);
    this.dialogRef.close();
  }
}
