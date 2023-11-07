from django.shortcuts import render
from django.http import HttpResponse
import matplotlib.pyplot as plt
import pandas as pd
from penjadwalanAlgorithm import modulee as md
from penjadwalanAlgorithm.models import *
from numba import jit, cuda




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
def template(request):
    print('mulai')
    df_dataset_T = Pengampu.objects.all()
    df_ruangan = Ruangan.objects.all()
    df_hari = Hari.objects.all()
    df_jam = Jam.objects.all()

    
    ruangan_list =  list(df_ruangan)
    array_ruangan = [d.nama for d in ruangan_list]
    hari_list = list(df_hari)
    array_hari = [h.nama for h in hari_list]
    
    
    mapped_jam = list(df_jam)
    awal_akhir_array = ["{} - {}".format(jam.awal, jam.akhir) for jam in mapped_jam]
    # print(awal_akhir_array)
    # print(awal_jam)
   
    
    # print(mapped_jam)
    # print(mapped_jam)
    
    courses_T = md.generate_course_list(
        df_dataset_T, array_ruangan, array_hari, awal_akhir_array)
    # print(courses_T)
    population = md.generate_schedule(courses_T)
    # print(population)

    best_schedule_T, best_fitness_per_generation_T = md.genetic_algorithm(
        courses_T, 100, 2)

    plt.plot(best_fitness_per_generation_T)
    plt.xlabel("Generation")
    plt.ylabel("Best Fitness")
    plt.title("Best Fitness per Generation For Theory")
    # plt.savefig("migration/Theory.png")


    for value in population:
        print(value.kode_matakuliah)

    days_order = {'Senin': 1, 'Selasa': 2,
                    'Rabu': 3, 'Kamis': 4, 'Jumat': 5}

    best_schedule_T.sort(key=lambda x: (days_order[x.day], x.time))
    courses_data_T = []
    for course in best_schedule_T:
        print('---------------------')
        print(f'Kode matakuliah\t:{course.kode_matakuliah}')
        print(f'Nama matakuliah\t:{course.nama_matakuliah}')
        print(f'Jenis\t\t:{course.jenis}')
        print(f'Jam\t\t:{course.time}')
        print(f'Hari\t\t:{course.day}')
        print(f'Ruangan\t\t:{course.room}')
        print(f'Dosen1\t\t:{course.lecturer1}')
        print(f'Kelas\t\t:{course.kelas}')
        print(f'Semester\t:{course.semester}')
        print('---------------------')
        course_dict = {
            'Kode matakuliah': course.kode_matakuliah,
            'Nama matakuliah': course.nama_matakuliah,
            'Jenis': course.jenis,
            'Jam': course.time,
            'Hari': course.day,
            'Ruangan': course.room,
            'Dosen1': course.lecturer1,
            'Kelas': course.kelas,
            'Semester': course.semester
        }
        courses_data_T.append(course_dict)
   

    df_predict = pd.DataFrame(courses_data_T )

    df_predict_T = pd.DataFrame(courses_data_T)
    df_predict_T = df_predict[['Jam', 'Hari', 'Semester', 'Kode matakuliah', 'Nama matakuliah', 'Jenis', 'Ruangan',
                                'Dosen1', 'Kelas',]]
    df_predict_T.sort_values(by=['Jam', 'Semester', 'Hari'])


    df_predict = df_predict.to_html(
        index=False, classes="table table-responsive table-striped")
    df_predict_T = df_predict_T.to_html(
        index=False, classes="table table-responsive table-striped")
    

    return render_template("schedule.html",
                            theory_graph="static/Theory.png",
                            practicum_graph="static/Practicum.png",
                            df_predict=df_predict,
                            df_predict_T=df_predict_T,
    )

