from django import forms
from django.utils import timezone
from .models import Booking, BookingMessage, Room
from datetime import datetime, time
from .models import Jadwal, Room

class BookingForm(forms.ModelForm):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()  # Minimum date adalah hari ini
        }),
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '08:00',  # Jam operasional mulai
            'max': '17:00'   # Jam operasional selesai
        }),
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'type': 'time',
            'class': 'form-control',
            'min': '08:00',
            'max': '17:00'
        }),
    )
    purpose = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Jelaskan tujuan penggunaan ruangan'
        }),
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Pilih Ruangan"
    )
    

    class Meta:
        model = Booking
        fields = ['room', 'booking_date', 'start_time', 'end_time', 'purpose']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        booking_date = cleaned_data.get('booking_date')
        room = cleaned_data.get('room')

        if start_time and end_time and booking_date:
            # Validasi waktu booking
            if start_time >= end_time:
                raise forms.ValidationError("Waktu selesai harus lebih dari waktu mulai")

            # Validasi tanggal booking tidak boleh di masa lalu
            if booking_date < timezone.now().date():
                raise forms.ValidationError("Tanggal booking tidak boleh di masa lalu")

            # Validasi jam operasional (08:00 - 17:00)
            operation_start = time(8, 0)
            operation_end = time(17, 0)
            if start_time < operation_start or end_time > operation_end:
                raise forms.ValidationError("Booking hanya tersedia antara jam 08:00 - 17:00")

            # Cek ketersediaan ruangan
            if room:
                overlapping_bookings = Booking.objects.filter(
                    room=room,
                    booking_date=booking_date,
                    status__in=['pending', 'approved']
                ).exclude(pk=self.instance.pk if self.instance else None)

                for booking in overlapping_bookings:
                    if (start_time < booking.end_time and end_time > booking.start_time):
                        raise forms.ValidationError(
                            f"Ruangan sudah dibooking pada jam {booking.start_time.strftime('%H:%M')} - "
                            f"{booking.end_time.strftime('%H:%M')}"
                        )

        return cleaned_data

class BookingMessageForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Tulis pesan Anda disini...'
        }),
    )

    class Meta:
        model = BookingMessage
        fields = ['message']