import pandas as pd
import random

# Función para leer y procesar los datos del Excel
def read_and_process_excel(filepath):
    # Leer el archivo Excel
    sheet = pd.read_excel(filepath, header=None)
    
    # Leer la disponibilidad de los recursos (columna B)
    recursos_data = sheet.iloc[1:31, 1].values  
    
    # Crear una lista para almacenar los datos de las fábricas
    fabricas_data = []
    
    # Iterar sobre cada bloque de datos de fábricas
    i = 31  # Iniciar después de la sección de disponibilidad de recursos, no aumentar los recursos si no se rompera
    while i < len(sheet):
        # Buscar la fila que contiene el nombre de la fábrica
        if isinstance(sheet.iloc[i, 0], str) and sheet.iloc[i, 0].startswith("Fabrica"):
            fabrica_name = sheet.iloc[i, 0]
            i += 1  # Mover a la fila con los encabezados
            headers = sheet.iloc[i, 1:-1].values  # Encabezados de R1 a R30 (ignorar AF)
            i += 1  # Mover a la fila con los datos
            
            # Leer las alternativas para esta fábrica
            alternativas = []
            while i < len(sheet) and not pd.isna(sheet.iloc[i, 0]):
                alternativas.append(sheet.iloc[i, 1:-1].values)  # Guardar los datos de la alternativa (ignorar AF)
                i += 1
            
            # Convertir las alternativas en un DataFrame
            alternativas_df = pd.DataFrame(alternativas, columns=headers)
            
            # Guardar los datos de la fábrica
            fabricas_data.append((fabrica_name, alternativas_df))
        
        i += 1  # Mover al siguiente bloque
    
    return fabricas_data, recursos_data

# Función de fitness que maximiza el uso de cada recurso individualmente bajo su disponibilidad para cada fábrica
def fitness(individual, fabricas_data, recursos_data):
    total_score = 0
    
    # Evaluar cada fábrica de manera independiente
    for i in range(len(individual)):
        alternativa = fabricas_data[i][1].iloc[individual[i]]
        score = 0
        
        # Evaluar cada recurso individualmente para la fábrica
        for j in range(len(recursos_data)):
            if alternativa[j] <= recursos_data[j]:
                score += alternativa[j]  # Sumar al puntaje si no excede la disponibilidad
            else:
                score -= (alternativa[j] - recursos_data[j]) * 1000  # Penalización si excede

        total_score += score
    
    return total_score

# Generar un individuo aleatorio
def generate_individual(fabricas_data):
    return [random.randint(0, len(fabrica[1]) - 1) for fabrica in fabricas_data]

# Selección por torneo
def selection(population, fitnesses):
    tournament_size = 3
    selected = random.sample(list(zip(population, fitnesses)), tournament_size)
    return max(selected, key=lambda x: x[1])[0]

# Cruce de un punto
def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

# Mutación
def mutate(individual, fabricas_data):
    point = random.randint(0, len(individual) - 1)
    individual[point] = random.randint(0, len(fabricas_data[point][1]) - 1)
    return individual

# Algoritmo genético
def genetic_algorithm(fabricas_data, recursos_data, generaciones=100, tamano_poblacion=50, tasa_mutacion=0.1):
    # Inicializar la población
    population = [generate_individual(fabricas_data) for _ in range(tamano_poblacion)]
    
    for generation in range(generaciones):
        # Evaluar el fitness de cada individuo
        fitnesses = [fitness(ind, fabricas_data, recursos_data) for ind in population]
        
        # Mostrar el mejor de la generación actual
        best_individual = population[fitnesses.index(max(fitnesses))]
        best_fitness = max(fitnesses)
        print(f"Generación {generation}: Mejor fitness = {best_fitness}")
        
        # Crear nueva población mediante selección, cruce y mutación
        new_population = []
        while len(new_population) < tamano_poblacion:
            parent1 = selection(population, fitnesses)
            parent2 = selection(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            new_population.append(mutate(child1, fabricas_data) if random.random() < tasa_mutacion else child1)
            new_population.append(mutate(child2, fabricas_data) if random.random() < tasa_mutacion else child2)
        
        population = new_population[:tamano_poblacion]
    
    # Devolver el mejor individuo después de todas las generaciones
    fitnesses = [fitness(ind, fabricas_data, recursos_data) for ind in population]
    best_individual = population[fitnesses.index(max(fitnesses))]
    return best_individual, max(fitnesses)

# Imprimir los resultados por fábrica con detalles de los recursos utilizados
def print_best_alternative(best_individual, fabricas_data, recursos_data):
    total_recursos_usados = 0
    for i, choice in enumerate(best_individual):
        fabrica_name = fabricas_data[i][0]
        alternativa = fabricas_data[i][1].iloc[choice]
        total_recursos = alternativa.sum()
        total_recursos_usados += total_recursos
        
        # Mostrar detalles de los recursos utilizados
        recursos_detalle = alternativa.to_dict()
        
        print(f"{fabrica_name}: Mejor alternativa es la {choice + 1} con un uso total de recursos de {total_recursos}")
        print(f"  Detalle de recursos utilizados: {recursos_detalle}")
        print(f"  Disponibilidad máxima de recursos: {recursos_data}")
    
    print("-------------------------------------------------------------------")
    print(f"Suma total de recursos usados: {total_recursos_usados}")

# Ruta del archivo Excel
excel_file = 'tabla.xlsx'  # Cambia esto por la ruta correcta a tu archivo

# Leer y procesar los datos
fabricas_data, recursos_data = read_and_process_excel(excel_file)

# Ejecutar el algoritmo genético
mejor_solucion, mejor_fitness = genetic_algorithm(fabricas_data, recursos_data)

# Imprimir la mejor alternativa para cada fábrica
print_best_alternative(mejor_solucion, fabricas_data, recursos_data)
