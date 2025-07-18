import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { NgFor, NgIf } from '@angular/common';

@Component({
  standalone: true,
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css'],
  imports: [CommonModule, HttpClientModule, NgFor, NgIf],
})
export class CarouselComponent implements OnInit, OnDestroy {
  packages: any[] = [];
  scrollPosition = 0;
  interval: any;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.fetchPackages();
    this.interval = setInterval(() => this.autoSlide(), 3000);
  }

  fetchPackages() {
    this.http.get<any[]>('http://127.0.0.1:8000/auth/searchpackages/').subscribe({
      next: (data) => {
        this.packages = data.filter(pkg => pkg.availability > 0);
      },
      error: (err: HttpErrorResponse) => {
        console.error('Failed to load packages', err.message);
      }
    });
  }

  autoSlide() {
    const itemWidth = 288; // ~18rem
    const visibleItems = 3;
    const maxScroll = this.packages.length * itemWidth - itemWidth * visibleItems;
    this.scrollPosition += itemWidth;
    if (this.scrollPosition > maxScroll) {
      this.scrollPosition = 0;
    }
  }

  ngOnDestroy(): void {
    clearInterval(this.interval);
  }
}