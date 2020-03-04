import numpy as np
import pandas as pd
import PyPDF2
import requests
import time
import unidecode
from itertools import cycle
from itertools import chain
import sys
import os
sys.setrecursionlimit(10000)

### Parte Uno: Establecemos los nombres de los estados en una lista de objetos, la cual usamos para generar el
### dataframe

estados = ['Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche', 'Coahuila',
           'Colima', 'Chiapas', 'Chihuahua', 'Ciudad de México', 'Durango', 'Guanajuato', 'Guerrero',
           'Hidalgo', 'Jalisco', 'México', 'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca',
           'Puebla', 'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa', 'Sonora', 'Tabasco',
           'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas', 'TOTAL']

## Para propositos de este trabajo, se uso el ejemplo para extraer la información correspondiente a diabetes
diabetes = pd.DataFrame()
diabetes['Estados'] = estados

### Parte Dos: Lectura de la página correspondiente al Boletín de Epidemiología
## La siguiente función usa de argumento la dirección de la carpeta con los archivos <dir>,
## el nombre del archivo <filename> y el número de la página que se desea extraer la info <pagenumber>
def openfile(dir, filename, pagenumber):
    os.chdir(dir)
    data = open(filename, 'rb')
    dataread = PyPDF2.PdfFileReader(data)
    page = dataread.getPage(pagenumber - 1) # El número de página se le resta 1 por la manera en que Python maneja el indexado
    page_content = page.extractText() # Función para extraer el texto completo de la página en el pdf
    page_content = page_content.split(' ') # Se para la información encontrada por un espacio <' '>
    page_content = list(filter(None, page_content)) # Queremos que nos organize toda la información en una lista
    page = page_content
    return page

## El objeto page consiste en la información completa de la página en forma de lista
page = openfile('C:/Users/Aldo/PycharmProjects/Web_Scrapping/PDF_Scrapping', '2018_52.pdf', 45)

## La siguiente función nos va a tomar nuestra lista con el fin de comenzar a separar la información
def strip_page(obj):
    contenido = []
    for i in range(len(obj)):
        contenido.append(obj[i].strip()) # Argumento strip() nos permite quitar los espacios en blanco de los strings en la lista
    value = []
    for i in range(len(contenido)):
        value.append(contenido[i].split()) # Argumento split() nos permite separar el contenido de la lista
    return value

## Objeto value que contiene la información en forma de lista y separada
value = strip_page(page)

## La función anterior nos generó un doble indexado de listas (una lista dentro de una lista)
## La función chain.from_iterable() nos permite quitar ese doble indexado
value = list(chain.from_iterable(value))



### Parte Tres: Aislamiento de la información por estado

## La siguiente función nos permite buscar en todos los elementos de la lista del pdf y compararlos
## con el nombre de los estados. Esto nos permite extraer la información y aislar el nombre del
## estado para saber que información le corresponde
def set_estados(List):
    for i in range(len(List)):
        for estado in estados:
            if str(estado) == List[i]:
                break
            elif str(estado) in List[i]: ## Se compara si existe la palabra estado en algún string de la lista. Sirve para nombres mayores de una palabra
                List[i] = List[i].split(str(estado))
                for j in range(len(List[i])):
                    if List[i][j] == "":
                        List[i][j] = str(estado)

set_estados(value)

## La siguiente función nos permite separar los numeros que se encuentran indexados con el nombre de algún otro string
## Separar los nombres de estados con números
## La función empieza a buscar desde 1000 hasta 0, y solo separa el primer número con el que se topa
def sep_numbers(List):
    for i in range(len(List)):
        for number in range(1000, -1, -1): #Esta manera haces un rango que comienza en 1000 y va reduciendo de un número en uno
            if str(number) == List[i]:
                break
            elif type(List[i]) != list and str(number) in List[i]:
                List[i] = List[i].split(str(number))
                for j in range(len(List[i])):
                    if List[i][j] == "":
                        List[i][j] = str(number)

sep_numbers(value)

## No recuerdo bien para que era este for, pero funciona hahaha
for i in range(len(value)):
    for j in range(len(value[i])):
        if value[i][j].startswith('0') or value[i][j].startswith('00'):
            value[i] = ''.join(value[i])


### Parte 4: Resolver el nesting (doble indexado de listas).

## Usualmente se usaría la función chain.from_iterable(), pero en el estado en que tenemos la lista comenzaría
## a separar elemento individuales. Se define la siguiente función que usa recursividad

output = []
def removenesting(L):
    for i in L:
        if type(i) == list:
            removenesting(i)
        else:
            output.append(i)

removenesting(value)

## Por valores prácticos, vamos a reescribir el valor de value con el valor de output, dado que vamos a volver a usar la función
value = output

### Parte Cinco: Limpiar los nombres de los estados
## En ciertas ocasiones, los estados se encuentran separados de manera no grata, particularmente
## aquellos que tienen más de una palabra en su nombre, ej "Baja California".
## La siguiente función nos permite identificar los elementos de la lista y unirlos de acuerdo a su estado
def straight_estados(List):
    for i in range(len(List)):
        if List[i] == 'Baja' and List[i + 2] != 'Sur':
            List[i] = List[i] + " " + List[i + 1]
            List.remove(List[i + 1])
        elif List[i] == 'Baja' and List[i + 2] == 'Sur':
            List[i] = List[i] + " " + List[i + 1] + " " + List[i + 2]
            List.remove(List[i + 2])
            List.remove(List[i + 1])
        elif 'Baja California' in List[i] and 'Sur' in List[i + 1]:
            List[i] = List[i] + List[i + 1]
            List.remove(List[i + 1])
        elif List[i] == 'Ciudad':
            List[i] = List[i] + " " + List[i + 1] + " " + List[i + 2]
            List.remove(List[i + 2])
            List.remove(List[i + 1])
        elif List[i] == 'Nuevo':
            List[i] = List[i] + " " + List[i + 1]
            List.remove(List[i + 1])
        elif List[i] == 'Quintana':
            List[i] = List[i] + " " + List[i + 1]
            List.remove(List[i + 1])
        elif List[i] == 'San':
            List[i] = List[i] + " " + List[i + 1] + " " + List[i + 2]
            List.remove(List[i + 2])
            List.remove(List[i + 1])

straight_estados(value)

## Nuevamente, algunos estados se encuentran separados en su nombre, como "Chia, pas"
## El siguiente loop busca estos elementos si es que logra hacer un match de algún elemento
## con el nombre de un estado.
## Esencial el uso de startswith() y endswith()

for i in range(len(value)):
    for estado in estados:
        if value[i] == str(estado):
            break
        elif value[i] in str(estado) and value[i + 1].endswith('-'):
            value[i] = value[i] + value[i + 1]
            value.remove(value[i + 1])

## Se han limpiado los nombres de algunos de los estados, por lo que se requiere usar nuevamente la
## función de set_estados()
set_estados(value)

## Esto ha generado un nesting (doble indexado), por lo que se tiene que resolver con resolvenesting()
output = []
removenesting(value)
value = output

#Correr otra vez la función para arreglar los estados
straight_estados(value)

### Parte Seis: Trabajar con guiones
## Los guione representan información de casos que no se reportaron, por lo que es importante separarlos
## Función para limpiar los guiones
for i in range(len(value)):
    if len(value[i]) > 1 and "-" in value[i]:
        value[i] = list(value[i])

## Función para limpiar los nesting
output = []
removenesting(value)

## Parte Siete: Agregar la información al dataframe. De ahora en adelante vamos a trabajar con output
## Después vamos a hacer una condicional donde comparemos la longitud del vector con el número max de

## Se define la siguiente función, la cual nos va a ayudar resolver casos que sean >999. Se introduce
## como argumento la lista y el contador
def clean_numbers(List, i):
    if len(List) == 12:
        return List
    elif len(List) == 13 and i >= 11:
        if len(List[i]) <= 2 and List[i] == List[11]:
            List[i] = List[i] + List[i + 1]
            del List[i + 1]
        return List
    elif len(List) == 14 and i >= 10:
        if len(List[i]) <= 2 and List[i] == List[10]:
            List[i] = List[i] + List[i + 1]
            del List[i + 1]
        return List
    elif len(List) == 15 and i >= 9:
        if len(List[i]) <= 2 and List[i] == List[9]:
            List[i] = List[i] + List[i + 1]
            del List[i + 1]
        return List

## El siguiente loop nos va a permitir generar una lista conocida como vec_number, la cual va a contener
## la información de donde comienza el indexado por estado
vec_number = []
for i in output:
    for estado in diabetes['Estados']:
        if str(i) == estado:
            vec_number.append(output.index(i))

## Vec_estado nos va a recuperar la información que viene por cada estado, incluyendo su nombre
vec_estado = []
for i in range(len(vec_number)):
    for n in range(vec_number[i], vec_number[i + 1]):
        vec_estado.append(output[n])
    ## A vec_estado vamos a borrar el primer index [0], para tener una lista con 15 objetos
    vec_estado.remove(vec_estado[0])

    str(vec_estado)
    for j in range(12):
        clean_numbers(vec_estado, j)

    ## Parte de la función para agregar la información al dataframe
    diabetes.loc[i, 'Sem1'] = vec_estado[0]
    diabetes.loc[i, 'M1'] = vec_estado[1]
    diabetes.loc[i, 'F1'] = vec_estado[2]
    diabetes.loc[i, 'Acum1'] = vec_estado[3]
    diabetes.loc[i, 'Sem2'] = vec_estado[4]
    diabetes.loc[i, 'M2'] = vec_estado[5]
    diabetes.loc[i, 'F2'] = vec_estado[6]
    diabetes.loc[i, 'Acum2'] = vec_estado[7]
    diabetes.loc[i, 'Sem3'] = vec_estado[8]
    diabetes.loc[i, 'M3'] = vec_estado[9]
    diabetes.loc[i, 'F3'] = vec_estado[10]
    diabetes.loc[i, 'Acum3'] = vec_estado[11]

    vec_estado = []

## Ahora el dataframe debería de estar completo :)



