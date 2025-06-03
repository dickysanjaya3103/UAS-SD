from django.db import migrations, models
import django.db.models.deletion

def create_initial_rooms(apps, schema_editor):
    Room = apps.get_model('rkta', 'Room')
    rooms_data = [
        {
            'number': 'LAB.KOM',
            'floor': 4,
            'capacity': 40,
            'status': 'available',
            'description': 'Laboratorium Komputer'
        },
        {
            'number': 'MG1.04.07', 
            'floor': 4,
            'capacity': 40,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 4'
        },
        {
            'number': 'MG1.04.04',
            'floor': 4, 
            'capacity': 40,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 4'
        },
        {
            'number': 'MG1.04.02',
            'floor': 4,
            'capacity': 40,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 4'
        },
        {
            'number': 'MG1.03.08',
            'floor': 3,
            'capacity': 60,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 3'
        },
        {
            'number': 'MG1.03.07',
            'floor': 3,
            'capacity': 60,
            'status': 'available', 
            'description': 'Ruang Kelas Lantai 3'
        },
        {
            'number': 'MG1.03.04',
            'floor': 3,
            'capacity': 60,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 3'
        },
        {
            'number': 'MG1.03.03',
            'floor': 3,
            'capacity': 80,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 3'
        },
        {
            'number': 'MG1.02.07',
            'floor': 2,
            'capacity': 60,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 2'
        },
        {
            'number': 'MG1.02.06',
            'floor': 2,
            'capacity': 60,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 2'
        },
        {
            'number': 'MG1.02.02',
            'floor': 2,
            'capacity': 80,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 2'
        },
        {
            'number': 'MG1.01.07',
            'floor': 1,
            'capacity': 80,
            'status': 'available',
            'description': 'Ruang Kelas Lantai 1'
        }
    ]
    
    Room.objects.all().delete()
    
    for room_data in rooms_data:
        Room.objects.create(**room_data)

class Migration(migrations.Migration):
    dependencies = [
        ('rkta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Jadwal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal', models.DateField()),
                ('waktu_mulai', models.TimeField()),
                ('waktu_selesai', models.TimeField()),
                ('kegiatan', models.CharField(max_length=100)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rkta.room')),
            ],
        ),
        migrations.RunPython(create_initial_rooms),
    ]