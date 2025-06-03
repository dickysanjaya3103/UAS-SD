from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Room, Booking, BookingMessage, Admin
from .forms import BookingForm, BookingMessageForm
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_authenticated and hasattr(user, 'admin')

@user_passes_test(is_admin, login_url='login')
def admin_rooms(request):
    rooms = Room.objects.all().order_by('number')

    # Filter berdasarkan parameter
    status = request.GET.get('status')
    floor = request.GET.get('floor')

    if status:
        rooms = rooms.filter(status=status)
    if floor:
        rooms = rooms.filter(floor=floor)

    context = {
        'rooms': rooms,
        'status_choices': Room.STATUS_CHOICES,
        'floor_choices': Room.FLOOR_CHOICES,
    }
    return render(request, 'admin/rooms.html', context)

@user_passes_test(is_admin, login_url='login')
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-created_at')

    # Filter berdasarkan status
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)

    context = {
        'bookings': bookings,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'admin/bookings.html', context)

@user_passes_test(is_admin, login_url='login')
def admin_users(request):
    users = User.objects.filter(is_superuser=False).order_by('-date_joined')
    context = {
        'users': users
    }
    return render(request, 'admin/users.html', context)

@user_passes_test(is_admin, login_url='login')
def admin_approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.save()
    messages.success(request, f'Booking {booking.id} telah disetujui')
    return redirect('admin_bookings')

@user_passes_test(is_admin, login_url='login')
def admin_reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'rejected'
    booking.save()
    messages.success(request, f'Booking {booking.id} telah ditolak')
    return redirect('admin_bookings')

@user_passes_test(is_admin, login_url='login')
def admin_dashboard(request):
    # Statistik untuk dashboard admin
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='available').count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()

    # Booking terbaru
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]

    context = {
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/admin_dashboard.html', context)



@login_required
def room_list(request):
    """View untuk menampilkan daftar semua ruangan dengan filter"""
    # Filter berdasarkan parameter
    status = request.GET.get('status')
    floor = request.GET.get('floor')
    capacity = request.GET.get('capacity')

    # Get rooms ordered by floor and room number
    rooms = Room.objects.all().order_by('floor', 'number')

    # Update status semua ruangan
    for room in rooms:
        room.update_status()

    if status:
        rooms = rooms.filter(status=status)
    if floor:
        rooms = rooms.filter(floor=floor)
    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)

    context = {
        'rooms': rooms.order_by('floor', 'number'),  # Ensure final ordering
        'floor_choices': Room.FLOOR_CHOICES,
        'status_choices': Room.STATUS_CHOICES,
    }
    return render(request, 'room_list.html', context)

@login_required
def room_detail(request, room_id):
    """View untuk menampilkan detail ruangan dan jadwal bookingnya"""
    room = get_object_or_404(Room, id=room_id)

    # Ambil booking yang akan datang untuk ruangan ini
    upcoming_bookings = Booking.objects.filter(
        room=room,
        booking_date__gte=timezone.now().date(),
        status='approved'
    ).order_by('booking_date', 'start_time')

    context = {
        'room': room,
        'upcoming_bookings': upcoming_bookings,
    }
    return render(request, 'room_detail.html', context)

@login_required
def my_bookings(request):
    """View untuk menampilkan daftar booking pengguna"""
    # Filter berdasarkan status
    status = request.GET.get('status')

    bookings = Booking.objects.filter(user=request.user)
    if status:
        bookings = bookings.filter(status=status)

    # Pisahkan booking aktif dan riwayat
    active_bookings = bookings.filter(
        Q(booking_date__gt=timezone.now().date()) |
        (Q(booking_date=timezone.now().date()) & Q(end_time__gt=timezone.now().time())),
        status__in=['pending', 'approved']
    ).order_by('booking_date', 'start_time')

    past_bookings = bookings.filter(
        Q(booking_date__lt=timezone.now().date()) |
        (Q(booking_date=timezone.now().date()) & Q(end_time__lte=timezone.now().time())) |
        Q(status__in=['cancelled', 'rejected', 'completed'])
    ).order_by('-booking_date', '-start_time')

    context = {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
        'status_choices': Booking.STATUS_CHOICES,
    }
    return render(request, 'my_bookings.html', context)

@login_required
def update_booking(request, booking_id):
    """View untuk mengupdate booking yang sudah ada"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Hanya booking dengan status pending yang bisa diupdate
    if booking.status != 'pending':
        messages.error(request, 'Hanya booking dengan status pending yang dapat diubah')
        return redirect('booking_detail', booking_id=booking.id)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking berhasil diupdate')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(instance=booking)

    return render(request, 'booking_form.html', {
        'form': form,
        'booking': booking,
        'is_update': True
    })

@login_required
def search_rooms(request):
    """View untuk mencari ruangan berdasarkan kriteria tertentu"""
    query = request.GET.get('q')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    capacity = request.GET.get('capacity')

    rooms = Room.objects.filter(status='available')

    if query:
        rooms = rooms.filter(
            Q(number__icontains=query) |
            Q(description__icontains=query)
        )

    if capacity:
        rooms = rooms.filter(capacity__gte=capacity)

    # Jika ada parameter waktu, filter ruangan yang tersedia
    if date and start_time and end_time:
        unavailable_rooms = Booking.objects.filter(
            booking_date=date,
            status='approved',
            start_time__lt=end_time,
            end_time__gt=start_time
        ).values_list('room_id', flat=True)

        rooms = rooms.exclude(id__in=unavailable_rooms)

    context = {
        'rooms': rooms,
        'query': query,
        'date': date,
        'start_time': start_time,
        'end_time': end_time,
        'capacity': capacity
    }
    return render(request, 'search_rooms.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Cek login sebagai admin
            if user_type == 'admin':
                if hasattr(user, 'admin'):
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Anda tidak memiliki akses sebagai admin!')
                    return redirect('login')
            # Login sebagai user biasa
            else:
                if hasattr(user, 'admin'):
                    messages.error(request, 'Admin harus login menggunakan opsi admin!')
                    return redirect('login')
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Username atau password salah!')
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    rooms = Room.objects.all()
    user_bookings = Booking.objects.filter(user=request.user).order_by('-created_at')[:5]

    stats = {
        'total_rooms': Room.objects.count(),
        'available_rooms': Room.objects.filter(status='available').count(),
        'active_bookings': Booking.objects.filter(
            user=request.user,
            booking_date=timezone.now().date(),
            status='approved'
        ).count(),
        'pending_bookings': Booking.objects.filter(
            user=request.user,
            status='pending'
        ).count(),
    }

    context = {
        'rooms': rooms,
        'user_bookings': user_bookings,
        'stats': stats,
    }
    return render(request, 'dashboard.html', context)  # Ubah dari admin_dashboard.html

@login_required
def book_room(request, room_id):
    """View untuk memproses booking ruangan"""
    try:
        room = get_object_or_404(Room, pk=room_id)
        
        if request.method == 'POST':
            # Validasi status ruangan
            if room.status != 'available':
                messages.error(request, 'Maaf, ruangan ini tidak tersedia untuk dibooking.')
                return redirect('room_list')

            # Ambil data dari form
            tanggal = request.POST.get('tanggal')
            waktu_mulai = request.POST.get('waktu_mulai') 
            waktu_selesai = request.POST.get('waktu_selesai')

            # Validasi input
            if not all([tanggal, waktu_mulai, waktu_selesai]):
                messages.error(request, 'Semua field harus diisi.')
                return redirect('room_list')

            try:
                # Cek apakah sudah ada booking di waktu yang sama
                existing_booking = Booking.objects.filter(
                    room=room,
                    booking_date=tanggal,
                    status__in=['pending', 'approved'],
                ).filter(
                    Q(start_time__lt=waktu_selesai) & 
                    Q(end_time__gt=waktu_mulai)
                ).exists()

                if existing_booking:
                    messages.error(request, 'Ruangan sudah dibooking untuk waktu tersebut.')
                    return redirect('room_list')

                # Buat booking baru
                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    booking_date=tanggal,
                    start_time=waktu_mulai,
                    end_time=waktu_selesai,
                    purpose="Booking ruangan",
                    status='pending'
                )
                
                # Update status ruangan
                room.update_status()
                
                messages.success(request, f'Booking untuk ruangan {room.number} berhasil dibuat!')
                return redirect('my_bookings')

            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return redirect('room_list')

        return redirect('room_list')

    except Room.DoesNotExist:
        messages.error(request, 'Ruangan tidak ditemukan.')
        return redirect('room_list')

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    messages = BookingMessage.objects.filter(booking=booking)

    if request.method == 'POST':
        form = BookingMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.booking = booking
            message.user = request.user
            message.save()
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingMessageForm()

    return render(request, 'booking_detail.html', {
        'booking': booking,
        'messages': messages,
        'form': form,
    })

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'pending' or booking.status == 'approved':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking berhasil dibatalkan')
    else:
        messages.error(request, 'Booking tidak dapat dibatalkan')

    return redirect('dashboard')

@login_required
def jadwal_list(request):
    """
    Menampilkan jadwal booking semua ruangan (hanya yang sudah disetujui).
    """
    jadwal = Booking.objects.filter(
        status='approved',
        booking_date__gte=timezone.now().date()
    ).order_by('booking_date', 'start_time')
    context = {
        'jadwal': jadwal,
    }
    return render(request, 'jadwal_list.html', context)

@login_required
def jadwal_detail(request, jadwal_id):
    """
    Menampilkan detail jadwal booking tertentu.
    """
    booking = get_object_or_404(Booking, id=jadwal_id, status='approved')
    context = {
        'booking': booking,
    }
    return render(request, 'jadwal_detail.html', context)