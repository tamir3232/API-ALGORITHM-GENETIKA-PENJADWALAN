from django.db import models
import uuid

class User(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)  # Anda dapat mengganti ini dengan model yang sesuai dengan Django
    username = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    # Tambahkan field lain yang sesuai dengan kebutuhan Anda
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.username


class Dosen(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    nip = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'dosens'
        
    def __str__(self):
        return self.name
    
class Hari(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    nama = models.CharField(max_length=255)

    class Meta:
        db_table = 'hari'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return self.nama   
    
class Jam(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    range_jam = models.CharField(max_length=255)
    awal = models.TimeField()
    akhir = models.TimeField()

    class Meta:
        db_table = 'jam'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f"id: {self.id}, range_jam: {self.range_jam}, awal: {self.awal}, akhir: {self.akhir} "    

    
    
class Kelas(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    nama = models.CharField(max_length=255)
    semester = models.CharField(max_length=255)

    class Meta:
        db_table = 'kelas'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f" nama : {self.nama}, semeseter :{ self.semester}"


class Matakuliah(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    nama = models.CharField(max_length=255)
    kode_matkul = models.CharField(max_length=255)
    semester = models.CharField(max_length=255)
    sks = models.PositiveIntegerField()
    status = models.CharField(max_length=255)

    class Meta:
        db_table = 'matakuliah'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f" nama : {self.nama}, kode_matkul :{ self.kode_matkul}, semester:{self.semester}, sks:{self.sks}, status:{self.status}"


class Ruangan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    nama = models.CharField(max_length=255)

    class Meta:
        db_table = 'ruangan'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return self.nama   
    
class Pengampu(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    matakuliah = models.ForeignKey(Matakuliah, on_delete=models.CASCADE)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE)
    dosen = models.ForeignKey(Dosen, on_delete=models.CASCADE)
    # Tambahkan field yang sesuai dengan model Laravel

    class Meta:
        db_table = 'pengampu'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f"Pengampu ID: {self.id}, Matakuliah: {self.matakuliah}, Kelas: {self.kelas}, Dosen:{self.dosen}"
    
    
    
class Reservasi(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    hari = models.ForeignKey(Hari, on_delete=models.CASCADE, null=True)
    jam = models.ForeignKey(Jam, on_delete=models.CASCADE, null=True)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.CASCADE, null=True)
    pengampu = models.ForeignKey(Pengampu, on_delete=models.CASCADE, null=True)
    reservasiby = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=255)

    class Meta:
        db_table = 'reservasi'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f"Reservasi ID: {self.id}, Hari: {self.hari}, Jam: {self.jam}, Ruangan: {self.ruangan}, Pengampu: {self.pengampu}, Jadwal: {self.jadwal}, reservasi_by: {self.reservasiby}, Status: {self.status}"    

    


class Jadwal(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    hari = models.ForeignKey(Hari, on_delete=models.CASCADE, null=True)
    jam = models.ForeignKey(Jam, on_delete=models.CASCADE, null=True)
    ruangan = models.ForeignKey(Ruangan, on_delete=models.CASCADE, null=True)
    pengampu = models.ForeignKey(Pengampu, on_delete=models.CASCADE, null=True)
    reservasi = models.ForeignKey(Reservasi, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'jadwal'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f"Jadwal ID: {self.id}, Hari: {self.hari}, Jam: {self.jam.range_jam}, Ruangan: {self.ruangan.nama}, Pengampu: {self.pengampu}, reservasi: {self.reservasi}"

 
    
class Contraint(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    dosen = models.ForeignKey(Dosen, on_delete=models.CASCADE)
    hari = models.ForeignKey(Hari, on_delete=models.CASCADE)
    jam = models.ForeignKey(Jam, on_delete=models.CASCADE)

    class Meta:
        db_table = 'contraint'
        # Anda dapat menambahkan konfigurasi lain sesuai kebutuhan

    def __str__(self):
        return f"Contraint ID: {self.id}, Dosen: {self.dosen.name}, Hari: {self.hari.name}, Jam: {self.jam.name}"



