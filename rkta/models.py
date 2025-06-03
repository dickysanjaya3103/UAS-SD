from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

    class Meta:
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'


class Room(models.Model):
    FLOOR_CHOICES = [
        (1, 'Lantai 1'),
        (2, 'Lantai 2'),
        (3, 'Lantai 3'),
        (4, 'Lantai 4'),
    ]

    STATUS_CHOICES = [
        ('available', 'Tersedia'),
        ('booked', 'Sedang Digunakan'),
        ('maintenance', 'Maintenance'),
    ]

    number = models.CharField(max_length=10)
    floor = models.IntegerField(choices=FLOOR_CHOICES)
    capacity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Room {self.number}"

    def is_currently_booked(self):
        """Check if room is currently being used based on active bookings"""
        from django.utils import timezone
        current_time = timezone.localtime()
        
        active_booking = Booking.objects.filter(
            room=self,
            booking_date=current_time.date(),
            start_time__lte=current_time.time(),
            end_time__gte=current_time.time(),
            status='approved'
        ).exists()
        
        return active_booking

    def update_status(self):
        """Update room status based on current bookings"""
        if self.is_currently_booked():
            self.status = 'booked'
        else:
            self.status = 'available'
        self.save()


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Menunggu Konfirmasi'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
        ('cancelled', 'Dibatalkan'),
        ('completed', 'Selesai'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room.number} - {self.booking_date} ({self.start_time} - {self.end_time})"


class BookingMessage(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.user.username} on {self.created_at}'


class AdminMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_admin_messages'
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_admin_messages'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    attachment = models.FileField(
        upload_to='chat_attachments/',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Admin Message'
        verbose_name_plural = 'Admin Messages'

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @property
    def short_message(self):
        """Returns truncated message for preview"""
        return (self.message[:50] + '...') if len(self.message) > 50 else self.message

    @property
    def time_since_sent(self):
        """Returns how long ago the message was sent"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(self.created_at, timezone.now())


# ✅ Tambahkan model Jadwal DI LUAR class lain
class Jadwal(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    tanggal = models.DateField()
    waktu_mulai = models.TimeField()
    waktu_selesai = models.TimeField()
    kegiatan = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.kegiatan} ({self.tanggal} {self.waktu_mulai}-{self.waktu_selesai})"
