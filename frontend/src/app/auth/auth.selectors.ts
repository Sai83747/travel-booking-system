import { createFeatureSelector, createSelector } from '@ngrx/store';
import { AuthState } from './auth.reducer';

export const selectAuthState = createFeatureSelector<AuthState>('auth');

export const selectUserRole = createSelector(selectAuthState, state => state.role);
export const selectUserEmail = createSelector(selectAuthState, state => state.email);
