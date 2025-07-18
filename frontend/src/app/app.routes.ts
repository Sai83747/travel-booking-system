// app.routes.ts
import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { SignupComponent } from './auth/signup/signup.component';
import { ForgotPasswordComponent } from './auth/forgotpassword/forgotpassword.component';
import { AdminDashboardComponent } from './auth/admin-dashboard/admin-dashboard.component';
import { AgentDashboardComponent } from './auth/agent-dashboard/agent-dashboard.component';
import { UserDashboardComponent } from './auth/user-dashboard/user-dashboard.component';
import { CategorySearchComponent } from './category-search/category-search.component';
import { BookRouteComponent } from './book-route/book-route.component';
import { PaymentComponent } from './payment-gateway/payment-gateway.component';
import { Router } from '@angular/router'; // Make sure this is imported
import { FlightSearchComponent } from './flight-search/flight-search.component';
import { PackageSearchComponent } from './package-search/package-search.component';

import { BookingHistoryComponent } from './booking-history/booking-history.component';
import { HotelSearchComponent } from './hotels-search/hotels-search.component';
import { ContactUsComponent } from './contact-us/contact-us.component';
import { roleGuard } from './guards/role.guard';

export const routes: Routes = [
  { path: 'signup', component: SignupComponent },
  { path: 'login', component: LoginComponent },
  { path: 'forgot-password', component: ForgotPasswordComponent },

  { path: 'admin/search', component: CategorySearchComponent, canActivate: [roleGuard(['admin'])] },
  { path: 'admin-dashboard', component: AdminDashboardComponent, canActivate: [roleGuard(['admin'])] },
  { path: 'agent-dashboard', component: AgentDashboardComponent, canActivate: [roleGuard(['agent'])] },
  { path: 'user-dashboard', component: UserDashboardComponent, canActivate: [roleGuard(['user'])] },

  { path: 'flights', component: FlightSearchComponent },
  { path: 'packages', component: PackageSearchComponent },
  { path: 'hotels', component: HotelSearchComponent },
  { path: 'bookings', component: BookingHistoryComponent },
  { path: 'contact', component: ContactUsComponent },

  { path: 'book-route', component: BookRouteComponent, canActivate: [roleGuard(['user'])] },
  {
    path: 'book-route/:id',
    loadComponent: () => import('./book-route/book-route.component').then(m => m.BookRouteComponent)
  },
  {
    path: 'payment/:bookingId',
    loadComponent: () => import('./payment-gateway/payment-gateway.component').then(m => m.PaymentComponent),
    canActivate: [roleGuard(['user'])]
  },

  // ✅ Set UserDashboardComponent as home
  { path: '', component: UserDashboardComponent },

  // Catch-all
  { path: '**', redirectTo: '' }
];

