import { createReducer, on } from '@ngrx/store';
import { loginSuccess,logout } from './auth.action';

export interface AuthState {
  email: string | null;
  role: string | null;
}

export const initialAuthState: AuthState = {
  email: null,
  role: null,
};

export const authReducer = createReducer(
  initialAuthState,

  // Set email and role on successful login
  on(loginSuccess, (state, { email, role }) => ({
    ...state,
    email,
    role
  })),

  // Clear state on logout
  on(logout, () => initialAuthState)
);
