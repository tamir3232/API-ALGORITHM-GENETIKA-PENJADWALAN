import random
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
import datetime
import pandas as pd
from numba import jit, cuda


class Course:
    def __init__(self, kode_matakuliah, nama_matakuliah, jenis, times, days, rooms, lecturer1, kelas, semester):
        self.kode_matakuliah = kode_matakuliah
        self.nama_matakuliah = nama_matakuliah
        self.jenis = jenis
        self.times = times
        self.days = days
        self.rooms = rooms
        self.lecturer1 = lecturer1
        self.kelas = kelas
        self.semester = semester
        self.time = None
        self.room = None
        self.day = None


def generate_course_list(dataset, array_ruangan, array_hari, grouped_jam):
    courses = []
    # print(grouped_jam)
    for row in dataset:
        combined_times = []
        if(row.matakuliah.sks == 2):
            for i in range(0, len(grouped_jam) - 1, 2):
                start_time1, end_time1 = grouped_jam[i].split(' - ')
                start_time2, end_time2 = grouped_jam[i + 1].split(' - ')

                # Gabungkan waktu awal dan waktu akhir
                combined_start_time = start_time1
                combined_end_time = end_time2

                # Tambahkan waktu gabungan ke daftar gabungan
                combined_times.append(f'{combined_start_time} - {combined_end_time}')
        if(row.matakuliah.sks == 3):
            for i in range(0, len(grouped_jam) - 2, 3):
                start_time1, end_time1 = grouped_jam[i].split(' - ')
                start_time2, end_time2 = grouped_jam[i + 2].split(' - ')

                # Gabungkan waktu awal dan waktu akhir
                combined_start_time = start_time1
                combined_end_time = end_time2

                # Tambahkan waktu gabungan ke daftar gabungan
                combined_times.append(f'{combined_start_time} - {combined_end_time}')

            # print(combined_times)
        print(combined_times)
        courses.append(Course(row.matakuliah.kode_matkul, row.matakuliah.nama, row.matakuliah.status, combined_times , array_hari, array_ruangan, row.dosen ,row.kelas.nama, row.kelas.semester))
    return courses


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

    for i in range(n):
        course1 = schedule[i]
        for j in range(i + 1, n):
            course2 = schedule[j]

            overlap = is_overlap([course1.time, course2.time])
            same_day = course1.day == course2.day
            same_semester = course1.semester == course2.semester
            same_room = course1.room == course2.room
            same_lecturer1 = course1.lecturer1 == course2.lecturer1
            same_subject = course1.nama_matakuliah == course2.nama_matakuliah
            same_subject_type = course1.jenis == course2.jenis
            different_semester = course1.semester == course2.semester

            conflict = False
            if overlap and same_day and different_semester:
                conflict = True

            if conflict:
                conflicts += 1
                break
    fitness_result = 1 / (1 + conflicts)
    return fitness_result


def generate_schedule(courses):
    schedule = []
    for course in courses:
        time = random.choice(course.times)
        day = random.choice(course.days)
        code = course.kode_matakuliah
        lecturer1 = course.lecturer1
        subject_name = course.nama_matakuliah
        kelas = course.kelas
        semester = course.semester
        jenis = course.jenis
        available_rooms = course.rooms

        room = random.choice(available_rooms)

        course_obj = Course(code, subject_name, jenis, course.times, course.days,
                            course.rooms, lecturer1, kelas, semester)
        course_obj.time = time
        course_obj.room = room
        course_obj.day = day
        schedule.append(course_obj)
    return schedule


def mutate(schedule):
    course = random.choice(schedule)
    course.time = random.choice(course.times)
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
    if random.random() < 0.2:
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
