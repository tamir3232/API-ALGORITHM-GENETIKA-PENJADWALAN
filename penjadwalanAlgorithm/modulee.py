import random
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import datetime
import pandas as pd
import time
from penjadwalanAlgorithm.models import *



class Course:
    def __init__(self, kode_matakuliah, nama_matakuliah, jenis, times, days, rooms, lecturer1, kelas, semester,sks, endTimes, contraint, jadwalExist):
        self.kode_matakuliah = kode_matakuliah
        self.nama_matakuliah = nama_matakuliah
        self.jenis = jenis
        self.times = times
        self.days = days
        self.rooms = rooms
        self.lecturer1 = lecturer1
        self.kelas = kelas
        self.semester = semester
        self.sks = sks
        self.endTimes = endTimes
        self.contraint = contraint
        self.jadwalExist = jadwalExist
        self.time = None
        self.room = None
        self.day = None


def generate_course_list(dataset, array_ruangan, array_hari, Times, endTimes, jadwalExist):
    courses = []
    randomHari = random.choice(array_hari)
    
    for row in dataset:
        print(row.matakuliah.status)
        print(row.matakuliah.semester)
        print("----------------------------")
        haris = array_hari.copy()
        dosen = Dosen.objects.filter(name = row.dosen).first()

        contraint = Contraint.objects.filter(dosen_id = dosen.id).values_list('jam__awal','jam__akhir','hari__nama')
        # print(contraint)
        getall=[]
        if contraint:    
            for item in contraint:
                # Memisahkan jam dan hari
                jam, hari = item[:-1], item[-1]
    
                # Menggabungkan jam dan hari dalam satu elemen array
                getall.append([f'{jam[0]} - {jam[1]}', hari])
      

            # getall = [' - '.join(map(str,item[:2])) + ' ' + item[2] for item in contraint]
            # print((getall)
      
      
        if(row.matakuliah.semester <=4):
            haris.remove('Senin')
            haris.remove('Selasa')
        if(row.matakuliah.semester >=5):
            haris.remove('Jumat')
        courses.append(Course(row.matakuliah.kode_matkul, row.matakuliah.nama, row.matakuliah.status, Times , haris, array_ruangan, row.dosen ,row.kelas.nama, row.matakuliah.semester,row.matakuliah.sks, endTimes, getall,jadwalExist))
      
        
        
        
     
    return courses

def pembagi_waktu(jadwal):
    
    mulai, selesai = jadwal.split('-')
    selesai = selesai.replace(".", ":")
    selesai = datetime.datetime.strptime(selesai.strip(), '%H:%M')
    mulai = mulai.replace(".", ":")
    mulai = datetime.datetime.strptime(mulai.strip(), '%H:%M')
    
    # Rentang waktu per 50 menit
    time_interval = timedelta(minutes=50)

    # Menghitung rentang waktu
    current_time = mulai

    # Mengonversi dan mencetak waktu dalam format yang diinginkan
    time = []
    while current_time < selesai:
        time.append(current_time.strftime('%H:%M').replace(":", "."))
        current_time += time_interval
    return time
    


def is_jadwal_berdekatan(jadwal_array, batas_waktu=timedelta(minutes=50)):
    """
    Fungsi untuk mengecek apakah dua jadwal berdekatan dalam batas waktu tertentu.

    Parameters:
    - jadwal1: String waktu pertama dalam format HH:mm
    - jadwal2: String waktu kedua dalam format HH:mm
    - batas_waktu: Batas waktu dalam bentuk timedelta, default 1 jam

    Returns:
    - True jika jadwal berdekatan, False jika tidak
    """
    # Konversi string waktu menjadi objek datetime
    mulai_1, selesai_1 = jadwal_array[0].split('-')
    selesai_1 = selesai_1.replace(".", ":")
    selesai_1 = datetime.datetime.strptime(selesai_1.strip(), '%H:%M')

    # Ekstrak waktu mulai dari rentang kedua
    mulai_2, selesai_2 = jadwal_array[1].split('-')
    mulai_2 = mulai_2.replace(".", ":")
    mulai_2 = datetime.datetime.strptime(mulai_2.strip(), '%H:%M')
    
    # Hitung selisih waktu
    selisih_waktu = abs(selesai_1 - mulai_2)
    
    # Periksa apakah selisih waktu dalam batas waktu yang ditentukan
    return selisih_waktu < batas_waktu
        

def is_overlap(times):
    datetime_slots = []
    # print(times)
    for time_slot in times:
        start, end = time_slot.split('-')
        start = start.replace(".", ":")
        start = datetime.datetime.strptime(start.strip(), '%H:%M')
        
        end = end.replace(".", ":")
        end = datetime.datetime.strptime(end.strip(), '%H:%M')
        datetime_slots.append((start, end))

    for i in range(len(datetime_slots)):
        for j in range(i+1, len(datetime_slots)):
            start1, end1 = datetime_slots[i]
            start2, end2 = datetime_slots[j]  
            if (start1 <= start2 and start2 < end1) or (start2 <= start1 and start1 < end2):
                return True
           
    return False


def generate_hash(schedule):
    return hash(tuple((course.kode_matakuliah, course.time, course.day, course.room) for course in schedule))


def parse_time_string(time_string):
    start_time_str, end_time_str = time_string.split("-")
    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
    return start_time, end_time


def fitness_func(schedule):
    conflicts = 0
    n = len(schedule)
    jumat = '11.40 - 14.10'
    for i in range(n):
        
        course1 = schedule[i]
        for j in range(i + 1, n):
            conflict = False
            course2 = schedule[j]
            overlap = is_overlap([course1.time, course2.time])
            same_day = course1.day == course2.day
            same_class = course1.kelas == course2.kelas
            same_semester = course1.semester == course2.semester
            same_room = course1.room == course2.room
            same_lecturer1 = course1.lecturer1 == course2.lecturer1
            same_subject = course1.nama_matakuliah == course2.nama_matakuliah
            same_semester = course1.semester == course2.semester
            diferent_day = course1.day != course2.day
            same_subject_type = (course1.jenis == course2.jenis) and (course1.jenis == 'PEMINATAN')
            jadwal_berdekatan = is_jadwal_berdekatan([course1.time, course2.time])
           
            
            if overlap and same_day and same_room:
                conflict = True
            
            if jadwal_berdekatan and same_lecturer1 and same_day:
                conflict = True
            
                
            # if (same_subject_type and same_semester) and diferent_day:
            #     conflict = True
                
            if overlap and same_day and same_lecturer1:
                conflict = True
                
            if overlap and same_day and same_class and same_semester:
                conflict = True
            

            if conflict:
                conflicts += 1
                break
        
        if(len(course1.contraint) >= 1):
            for i in range(0, len(course1.contraint)):                
                constDay = course1.day == course1.contraint[i][1]
                cekTime = course1.contraint[i][0]
                
                constTime = is_overlap([course1.time,cekTime])
          
                if(constDay and constTime ):
                    conflicts += 1
                    break
        if(len(course1.jadwalExist)>=1):
            for i in range(0, len(course1.jadwalExist)):
                sameday = course1.day == course1.jadwalExist[i][1]
                overlap = is_overlap([course1.time,course1.jadwalExist[i][0]])
                sameroom = course1.room == course1.jadwalExist[i][2]
                
                if sameday and overlap and sameroom:
                    conflict+=1

                
                
        cek_jumat = (course1.day == "Jumat") and is_overlap([course1.time, jumat])
        
      
        if cek_jumat:
            conflicts +=1

            
    fitness_result = 1 / (1 + conflicts)
    return fitness_result


def generate_schedule(courses):
    schedule = []
    for course in courses:
        
   
        lastElement =[]
        sks = course.sks
        times=course.times
        for i in range(sks-1) :
            lastElement.insert(0,times.pop())
            if(i == sks-1): break
        awal = random.choice(times)
        times.extend(lastElement)
        JamPenentu = awal
        if(JamPenentu == '07.30'):
            akhir = course.endTimes[course.endTimes.index('08.20')+(sks-1)]
        else:
            akhir = course.endTimes[course.endTimes.index(JamPenentu)+(sks)]
        
     
        time = awal + " - " + akhir
        
        
    
      
        day = random.choice(course.days)
        code = course.kode_matakuliah
        lecturer1 = course.lecturer1
        subject_name = course.nama_matakuliah
        kelas = course.kelas
        semester = course.semester
        jenis = course.jenis
        available_rooms = course.rooms
        room = random.choice(available_rooms)
        
        #testing

        course_obj = Course(code, subject_name, jenis, times, course.days,
                            course.rooms, lecturer1, kelas, semester, sks, course.endTimes, course.contraint, course.jadwalExist)
        
        course_obj.time = time
        course_obj.room = room
        course_obj.day = day
        schedule.append(course_obj)
    return schedule


def mutate(schedule):
    
    course = random.choice(schedule)
    lastElement =[]
    sks = course.sks
    times=course.times
    for i in range(sks-1) :
        lastElement.insert(0,times.pop())
        if(i == sks-1): break
    awal = random.choice(times)
    # print(times)
    # print(lastElement)
    #masukan element terakhir lagi

    times.extend(lastElement)
    JamPenentu = awal
    
    if(JamPenentu == '07.30'):
        akhir = course.endTimes[course.endTimes.index('08.20')+(sks-1)]
    else:
        akhir = course.endTimes[course.endTimes.index(JamPenentu)+(sks)]
    
    # print(sks)
    # print("awal: " ,awal)
    # print("akhir: " ,akhir)
    

    time = awal + " - " + akhir
    
    course.time = time
    course.room = random.choice(course.rooms)
    course.day = random.choice(course.days)
    return schedule


def crossover(schedule1, schedule2):
    crossover_point = random.randint(1, len(schedule1) - 1)
    new_schedule = schedule1[:crossover_point] + schedule2[crossover_point:]
    return new_schedule


def select_parents(population):
    total_fitness = sum([fitness_func(schedule) for schedule in population])
    probabilities = [fitness_func(
        schedule) / total_fitness for schedule in population]
    parent1, parent2 = random.choices(population, probabilities, k=2)
    return parent1, parent2


def create_child(population):
    parent1, parent2 = select_parents(population)
    child = crossover(parent1, parent2)
    if random.random() < 0.9:
        mutate(child)
    return child


def create_children(population, num_children):
    with ProcessPoolExecutor() as executor:
        return list(executor.map(create_child, [population] * num_children))


def genetic_algorithm(courses, population_size, generations):
    
    population = [generate_schedule(courses) for _ in range(population_size)]
    
    fitness_cache = [(generate_hash(schedule), fitness_func(schedule))
                     for schedule in population]
   
    best_fitness_per_generation = []
    # for gen in range(generations):
    status = True
    gen = 0
    while status :
        gen += 1
        print(f"Gen {gen} processing...")
        new_population = []

        elitism_size = int(population_size * 0.1)
        new_population.extend(sorted(population, key=lambda x: [
                              y[1] for y in fitness_cache if y[0] == generate_hash(x)][0], reverse=True)[:elitism_size])

        num_children = population_size - elitism_size
        children = create_children(population, num_children)
        # print(children)
        new_population.extend(children)
        new_population_with_fitness = []
        # print(new_population)
        for child in new_population:
            child_key = generate_hash(child)
           
            if child_key in [x[0] for x in fitness_cache]:
                fitness = [x[1] for x in fitness_cache if x[0] == child_key][0]
            else:
                fitness = fitness_func(child)
                print(fitness)
                fitness_cache.append((child_key, fitness))

            new_population_with_fitness.append((child, fitness))
        new_population_with_fitness.sort(key=lambda x: x[1], reverse=True)
        population = [x[0] for x in new_population_with_fitness]
        best_fitness_per_generation.append(new_population_with_fitness[0][1])
        print(new_population_with_fitness[0][1])
        if(new_population_with_fitness[0][1] == 1.0):
            status = False

    best_schedule = max(population, key=fitness_func)
    return best_schedule, best_fitness_per_generation
