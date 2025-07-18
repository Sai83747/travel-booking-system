import { Injectable } from '@angular/core';
import { getToken, onMessage } from 'firebase/messaging';
import { Messaging } from '@angular/fire/messaging';
import { environment } from './environment';

@Injectable({
  providedIn: 'root',
})
export class MessagingService {
  currentMessage: any;

  constructor(private messaging: Messaging) {}

  requestPermission(): Promise<string> {
    return getToken(this.messaging, { vapidKey: environment.firebaseConfig.vapidKey })
      .then(token => {
        console.log('Permission granted! Token:', token);
        return token;
      })
      .catch(err => {
        console.error('Unable to get permission for notifications', err);
        throw err;
      });
  }

  listen(): void {
    onMessage(this.messaging, (payload) => {
      console.log('Message received: ', payload);
      alert(payload?.notification?.title + '\n' + payload?.notification?.body);
    });
  }
}
