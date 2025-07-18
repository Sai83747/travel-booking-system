import { Component } from '@angular/core';
import { NavbarComponent } from '../navbar/navbar.component';
import { FooterComponent } from '../footer/footer.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-contact-us',
  imports: [NavbarComponent,FooterComponent,CommonModule,FormsModule],
  templateUrl: './contact-us.component.html',
  styleUrl: './contact-us.component.css'
})
export class ContactUsComponent {
  contact = {
    name: '',
    email: '',
    message: ''
  };

  submitContactForm() {
    // You can connect this to your backend
    alert('Thank you for reaching out! We will get back to you soon.');
    this.contact = { name: '', email: '', message: '' };
  }
}

