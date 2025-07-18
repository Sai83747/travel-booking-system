import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  imports: [CommonModule, FormsModule],
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {
  email: string = '';

  onSubscribe() {
    if (this.email) {
      alert(`Thanks for subscribing with ${this.email}!`);
      this.email = '';
    }
  }
}
