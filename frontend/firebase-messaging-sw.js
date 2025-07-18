// firebase-messaging-sw.js
importScripts("https://www.gstatic.com/firebasejs/10.8.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.8.1/firebase-messaging-compat.js");

firebase.initializeApp({
    apiKey: "AIzaSyBimMJty8PlTs_OguaFy9SuWJTFhajGQ8Q",
    authDomain: "emsy-ea251.firebaseapp.com",
    projectId: "emsy-ea251",
    storageBucket: "emsy-ea251.appspot.com", // ⚠️ Fix typo in storageBucket
    messagingSenderId: "35877507292",
    appId: "1:35877507292:web:414e6241a54f74e4086419",
    measurementId: "G-PSJ4PJNGP4",
    vapidKey:    "BOnqIdYZ-Rme-WWFfC8RMwH8xXgUKW0uJGqTNTJFRMjpPu44Gu-UkrudYs8xeveXMLpLaUrp1IMWDCbyoCAB1R8"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/assets/icons/icon-72x72.png' // Optional
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
