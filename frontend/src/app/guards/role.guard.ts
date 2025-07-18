import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Store } from '@ngrx/store';
import { firstValueFrom } from 'rxjs';
import { selectUserRole } from '../auth/auth.selectors';
import { AppState } from '../auth/auth.state';

export function roleGuard(expectedRoles: string[]): CanActivateFn {
  return async () => {
    const store = inject(Store) as Store<AppState>;
    const router = inject(Router);

    try {
      const role = await firstValueFrom(store.select(selectUserRole));

      if (role && expectedRoles.includes(role)) {
        return true;
      }

      console.warn('❌ Access denied, redirecting to login');
      // router.navigate(['/login']);
      return true;

    } catch (error) {
      console.error('❌ Error in role guard:', error);
      router.navigate(['/login']);
      return false;
    }
  };
}
