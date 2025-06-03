from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard, name='dashboard'),
    # Room URLs
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/book/', views.book_room, name='book_room'),
    path('rooms/search/', views.search_rooms, name='search_rooms'),
    # path('book-room/<int:room_id>/', views.book_room, name='c'),
    path('logout/', views.logout_view, name='logout'),

    # Booking URLs
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/update/', views.update_booking, name='update_booking'),
    path('bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/rooms/', views.admin_rooms, name='admin_rooms'),
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/booking/<int:booking_id>/approve/', views.admin_approve_booking, name='admin_approve_booking'),
    path('admin/booking/<int:booking_id>/reject/', views.admin_reject_booking, name='admin_reject_booking'),
    # Jadwal Page
    path('jadwal/', views.jadwal_list, name='jadwal_list'),
    path('jadwal/<int:jadwal_id>/', views.jadwal_detail, name='jadwal_detail'),
]