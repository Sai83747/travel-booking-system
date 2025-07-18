import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private API = 'http://127.0.0.1:8000/auth'; // ✅ Backend base URL

  constructor(private http: HttpClient) {}

  // ✅ Signup API
  signup(data: any): Observable<any> {
    return this.http.post(`${this.API}/signup/`, data, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
      withCredentials: true // Ensure session cookies work if needed
    });
  }

  // ✅ Login API (Fixed endpoint)
  login(payload: { email: string; password: string }): Observable<any> {
    return this.http.post<any>(`${this.API}/login/`, payload, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
      withCredentials: true // ✅ Ensures cookies are sent/received
    });
  }

  // ✅ Forgot Password API
  forgotPassword(email: string): Observable<any> {
    return this.http.post(`${this.API}/forgot-password/`, { email }, {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    });
  }

  // ✅ Fetch Current User API (Session-based authentication)
  getCurrentUser(): Observable<any> {
    return this.http.get(`${this.API}/user/`, { withCredentials: true });
  }

  // ✅ Logout API (Destroy session)
  logout(): Observable<any> {
    return this.http.post(`${this.API}/logout/`, {}, {
      withCredentials: true // Ensure cookies are cleared
    });
  }
}
