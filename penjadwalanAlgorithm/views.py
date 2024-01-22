from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import pandas as pd
from penjadwalanAlgorithm import modulee as md
from penjadwalanAlgorithm.models import *
from numba import jit, cuda
from timeit import default_timer as timer   
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


    # dosen = Dosen.objects.all()
    # Jadwals = Jadwal.objects.all()
    # user = User.objects.all()
    # jam = Jam.objects.all()
    # hari = Hari.objects.all()
    # kelas = Kelas.objects.all()
    # matakuliah = Matakuliah.objects.all()
    # ruangan = Ruangan.objects.all()
    # pengampu= Pengampu.objects.all()
    # reservasi = Reservasi.objects.all()
    # jadwal = Jadwal.objects.all()
    # contraint = Contraint.objects.all()
    
    # for data in Jadwals:
    #     print(data.jam.awal)
    # # dosen_data = list(dosen)
    # return HttpResponse(contraint)
class predict(APIView):
    def get(self,request):
        
        print('mulai')
        start = timer()
        df_dataset_T = Pengampu.objects.filter(matakuliah__status__in = ["WAJIB", "PEMINATAN"])
        # print(df_dataset_T)
        df_ruangan = Ruangan.objects.all()
        df_hari = Hari.objects.all()
        df_jam = Jam.objects.all().order_by('awal')

        # print(df_jam)

        ruangan_list =  list(df_ruangan)
        array_ruangan = [d.nama for d in ruangan_list]
        hari_list = list(df_hari)
        array_hari = [h.nama for h in hari_list]


        mapped_jam = list(df_jam)
        array_jam_awal = [j.awal for j in mapped_jam]
        array_jam_akhir = [j.akhir for j in mapped_jam]


        # awal_akhir_array = ["{} - {}".format(jam.awal, jam.akhir) for jam in mapped_jam]
        # print(awal_akhir_array)
        # print(awal_jam)
        jadwalexist=[]
        df_jadwal = Jadwal.objects.all().values_list('jam__awal','jam__akhir','hari__nama', 'ruangan__nama')
        if df_jadwal:    
            for item in df_jadwal:
                # Memisahkan jam dan hari
                jam, hari,ruangan = item[:-1], item[-2],item[-1]

                # Menggabungkan jam dan hari dalam satu elemen array
                jadwalexist.append([f'{jam[0]} - {jam[1]}', hari, ruangan])

        # print(mapped_jam)
        # print(mapped_jam)

        courses_T = md.generate_course_list(
            df_dataset_T, array_ruangan, array_hari, array_jam_awal, array_jam_akhir, jadwalexist)
        # print(courses_T)
        population = md.generate_schedule(courses_T)
        # print(population)
        best_schedule_T, best_fitness_per_generation_T = md.genetic_algorithm(
            courses_T, 10, 2)
        print("SELESAI",timer()-start)
        # plt.plot(best_fitness_per_generation_T)
        # plt.xlabel("Generation")
        # plt.ylabel("Best Fitness")
        # plt.title("Best Fitness per Generation For Theory")
        # plt.savefig("migration/Theory.png")


        # for value in population:
        #     print(value.kode_matakuliah)

        days_order = {'Senin': 1, 'Selasa': 2,
                        'Rabu': 3, 'Kamis': 4, 'Jumat': 5}

        best_schedule_T.sort(key=lambda x: (days_order[x.day], x.time))
        courses_data_T = []
        for course in best_schedule_T:
            qmatakuliah = Matakuliah.objects.filter(nama = course.nama_matakuliah, kode_matkul = course.kode_matakuliah).first()
            qhari = Hari.objects.filter(nama = course.day).first()
            qdosen = Dosen.objects.filter(name = course.lecturer1).first()
            qkelas = Kelas.objects.filter(nama = course.kelas, semester = course.semester).first()
            qruangan = Ruangan.objects.filter(nama = course.room).first()
            # print(qkelas.id)
            qpengampu = Pengampu.objects.filter(dosen_id = qdosen.id, kelas_id = qkelas.id , matakuliah_id = qmatakuliah.id ).first()
            
            waktu = md.pembagi_waktu(course.time)
            for i in range(len(waktu)):
                time =Jam.objects.filter(awal = waktu[i]).first()
                jadwal = Jadwal(hari_id=qhari.id,jam_id=time.id,ruangan_id=qruangan.id,pengampu_id=qpengampu.id )
                jadwal.save()
            # print('---------------------')
            # print(f'Kode matakuliah\t:{course.kode_matakuliah}')
            # print(f'Nama matakuliah\t:{course.nama_matakuliah}')
            # print(f'Jenis\t\t:{course.jenis}')
            # print(f'Jam\t\t:{course.time}')
            # print(f'Hari\t\t:{course.day}')
            # print(f'Ruangan\t\t:{course.room}')
            # print(f'Dosen1\t\t:{course.lecturer1}')
            # print(f'Kelas\t\t:{course.kelas}')
            # print(f'Semester\t:{course.semester}')
            # print('---------------------')
            # course_dict = {
            #     'Kode matakuliah': course.kode_matakuliah,
            #     'Nama matakuliah': course.nama_matakuliah,
            #     'Jenis': course.jenis,
            #     'Jam': course.time,
            #     'Hari': course.day,
            #     'Ruangan': course.room,
            #     'Dosen1': course.lecturer1,
            #     'Kelas': course.kelas,
            #     'Semester': course.semester
            # }
            # courses_data_T.append(course_dict)
        return Response( status=status.HTTP_200_OK)
    


