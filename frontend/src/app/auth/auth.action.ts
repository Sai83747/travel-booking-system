import { createAction, props } from '@ngrx/store';

export const loginSuccess = createAction(
  '[Auth] Login Success',
  props<{ email: string; role: string }>()
);

export const logout = createAction('[Auth] Logout');
