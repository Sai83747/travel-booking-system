from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
#     path('logout/', views.user_logout, name='user_logout'),
      path('signup/', views.register_user, name='register_admin'),
    path('user/', views.get_current_user, name='get_current_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('admini/', views.register_admin, name='register_admin'),
    path('admin/destination/', views.add_destination, name='add_destination'),
    path('forgotpassword/', views.forgot_password, name='forgot_password'),
    path('agent/', views.register_travel_agent, name='register_travel_agent'),
    path('flights/', views.add_flight, name='add_flight'),
    path('hotels/', views.add_hotel, name='add_hotel'),
    path('getdest/',views.get_all_destinations,name='getdestinations'),
    path('getflightroutes/',views.get_flight_routes,name='get_flight_routes'),
    path('addpackages/',views.add_package,name='add_package'),
     path('searchflights/',views.search_flights,name='add_package'),
      path('searchhotels/',views.search_hotels,name='add_package'),
       path('searchpackages/',views.search_packages,name='add_package'),
       path('packagedetails/<int:package_id>/',views.view_package_details,name='view_package_details'),
       path('updateflightava/<int:flight_id>/',views.update_flight_availability,name='update_flight'),
         path('updateflight/<int:flight_id>/',views.update_flight,name='update_flight'),
          path('updatehotel/<int:hotel_id>/',views.update_hotel,name='update_flight'),
          path('updatepackage/<int:package_id>/',views.update_package,name='update_flight'),
          path('searchdestinations/',views.search_destinations,name='search_destinations'),
          path('flightbooking/',views.create_flight_booking,name='create_flight_booking'),
         path('confirmflight/',views.confirmflight,name='create_flight_booking'),
         path('getbookingdetails/<int:booking_id>/',views.get_booking_details,name='get_booking_details'),
         path('filterhotelsadv/', views.filter_hotels_advanced, name='filter-hotels-advanced'),
         path('addorupdatereview/', views.add_or_update_review, name='add_or_update_review'),
          path('createhotelbooking/', views.create_hotel_booking, name='create_hotel_booking'),
          path('confirmhotel/', views.confirmhotel, name='confirm_hotel_booking'),
          path('searchpackageuser/', views.searchpackagesuser, name='search_package_user'),
          path('bookpackagepath/', views.book_package_path, name='book_package_path'),
          path('confirmpackage/', views.confirm_package, name='confirm_package'),
          path('getbookinghistory/<int:user_id>/', views.get_booking_history, name='confirm_package'),
          path('cancelbooking/', views.cancel_booking, name='cancel_booking'),
          path('getmyrefunds/<int:user_id>/', views.get_refunds_by_user, name='get_my_refunds'),
          path('getallbookings/', views.get_all_bookings_for_agent, name='get_all_bookings'),
          path('processrefund/<int:booking_id>/', views.process_refund, name='process_refund'),
#     path('createevent/', views.create_event, name='create_event'),
#     path('cem/', views.create_event_manager, name='create_event_manager'),
#     path("editevent/<int:event_id>/", views.edit_event, name="edit_event"),
#     path("deleteevent/<int:event_id>/", views.delete_event, name="delete_event"),
#     path('searchevent/', views.search_events, name='search_events'),

#     path('book/', views.request_booking, name='request_booking'),
#     path('eventdetails/<int:event_id>/', views.get_event_by_id, name='get_event_details_by_id'),
#     path('booking/confirm_payment/<int:booking_id>/', views.confirm_booking_payment, name='confirm_booking_payment'),
#     path('event/history/', views.view_booking_history, name='view_booking_history'),
#     path('event/cancelevent/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
#     path('usersbyrole/', views.get_users_by_role, name='get_users_by_role'),
#     path('getalleventsclient/', views.get_all_events_client, name='get_all_events_client'),
#     path('getclientbookings/<int:client_id>/', views.get_client_bookings, name='get_client_bookings'),
#     path('geteventmanagerevents/<int:manager_id>/', views.get_event_manager_events, name='get_event_manager_events'),
#     path('deleteuser/<int:user_id>/', views.delete_user_by_admin, name='delete_user_by_admin'),
#     path('assigneventtomanager/<int:event_id>/', views.assign_event_to_manager, name='assign_event_manager'),
#     path('assigntasktostaff/', views.assign_task_to_staff, name='assign_task_to_staff'),
# path('hire-staff/', views.get_my_unassigned_staff, name='get_my_unassigned_staff'),
# path('hire-staff/<int:staff_id>/', views.hire_staff, name='hire_staff'),
# path('mystaff/', views.get_my_staff, name='get_staff'),
# path('getstafftasks/<int:staff_id>/', views.get_staff_tasks, name='get_staff_tasks'),
# path('eventmanagerdetails/<int:event_id>/', views.view_event_manager_details, name='view_event_manager_details'),


]
