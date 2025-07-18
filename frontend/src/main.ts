import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideStore } from '@ngrx/store'; // ✅ Import NgRx Store
import { authReducer } from './app/auth/auth.reducer'; // ✅ Import your reducer
import { routes } from './app/app.routes'; // make sure routes is exported from your routing file

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideStore({
      auth: authReducer // ✅ Register the auth slice
    })
  ]
});
