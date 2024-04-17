#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from time import sleep, time
import log
import threading

# def prot_first():
#     _PID = log.CommandExecutionP('tasklist /FO CSV').split('\n')
#     d = str(log.getDate())  # Получаем дату
#     t = str(log.getTime())  # Получаем время
#     d = d.split('-')  # Преобразуем вид даты (не обязательно, просто мне так уобнее)
#     d = d[2] + '-' + d[1] + '-' + d[0]
#     Filename = 'protocol_first.txt'
#     path = "Logs/"
#     if os.path.exists(path + Filename) == True:
#         os.remove(path + Filename)
#         for line in _PID:
#             # Цикл перебирает полученный список процессов
#             line = line.replace('"', '').split(
#                 ',')  # линию с информацией о процессе разбиваем на элементы и удаляем кавычки
#             if len(line) > 1:  # Если элементов в линии с информацие больше одного (то есть есть информация о процессе)
#
#                 log.write('+ \t' + line[0] + '\t' + line[1] + '\t' + line[4][:len(line[4]) - 2].replace('я',
#                                                                                                                 ' ') + 'Кб' + '\t' + t + '\t' + d.replace(
#                             '-', '.') + '\n', path + Filename,
#                               'at')
#     else:
#         for line in _PID:
#             # Цикл перебирает полученный список процессов
#             line = line.replace('"', '').split(
#                 ',')  # линию с информацией о процессе разбиваем на элементы и удаляем кавычки
#             if len(line) > 1:  # Если элементов в линии с информацие больше одного (то есть есть информация о процессе)
#
#                 log.write('+ \t' + line[0] + '\t' + line[1] + '\t' + line[4][:len(line[4]) - 2].replace('я',
#                                                                                                                 ' ') + 'Кб' + '\t' + t + '\t' + d.replace(
#                             '-', '.') + '\n', path + Filename,

# def PidDel(d, t, wr='y'):
# # Функция проверяет каких процессов больше нет в получееном списке, если находит, то удаляет их из нашего локального списка и записывает информацию в файл
#     for line in List:
#         line = line.replace('"','').split(',')
#         if len(line) > 1:
#             if not line[0] + ' ' + line[1] in List:
#                 List.remove(line[0] + ' ' + line[1])
#                 line = line.replace('"','').split(',')
#                 if wr == 'y' and line[3] != '0' and not line[0] in BlackList:
#                     log.write('- \t' + line[0] + '\t' + line[1] + '\t' + line[4][:len(line[4])-2].replace('я',' ') + 'Кб' + '\t' + t + '\t' + d.replace('-', '.') + '\n', path + Filename, 'a')
#     return List
#
# def PidSave(_PID="", d="", t="", wr='y'):
#     for line in _PID:
#     # Цикл перебирает полученный список процессов
#         line = line.replace('"','').split(',')# линию с информацией о процессе разбиваем на элементы и удаляем кавычки
#         if len(line) > 1: # Если элементов в линии с информацие больше одного (то есть есть информация о процессе)
#             if not line[0] + ' ' + line[1] in List: # Если имени процесса и его id нет в нашем списке процесссов
#                 List.append(line[0] + ' ' + line[1]) # то добавляем их в наш локальный список
#                 if wr == 'y' and line[3] != '0' and not line[0] in BlackList: # Если аргумент записи = y и это не Services
#                     log.write('+ \t' + line[0] + '\t' + line[1] + '\t' + line[4][:len(line[4])-2].replace('я',' ') + 'Кб' + '\t' + t + '\t' + d.replace('-', '.') + '\n', path + Filename, 'a') # то ДОзаписываем информацию информацию об этом в лог-файл
#     return List
#                               'at')

def PidRead():
    global Filename
    global List
    global List_proc
    global BlackList
    global path
    #prot_first()
    PID = log.CommandExecutionP('tasklist /FO CSV').split('\n')
    _PID = []
    List = open("Logs/protocol_first.txt", 'r', encoding='utf-8')
    List = List.read().split('\n')

    PID_start = []
    PID_con = []

    for x in range(len(List)):
        List[x] = List[x].split('\t')

    for y in PID:
        y = y.replace('"', '').split(',')
        _PID.append(y)

    for xx in List:
        if not '' in xx:
            print(xx)
            PID_start.append(xx[1])
        else:
            pass

    for yy in _PID:
        if not '' in yy:
            print(yy)
            PID_con.append(yy[1])


    List_proc = []
    path = "Logs/"
    Filename = 'protocol.txt'
    BlackList = log.read('blackList.conf').split('\n')
    d = str(log.getDate())  # Получаем дату
    t = str(log.getTime())  # Получаем время
    d = d.split('-')  # Преобразуем вид даты (не обязательно, просто мне так удобнее)
    d = d[2] + '-' + d[1] + '-' + d[0]
    per(_PID, PID_con, PID_start)
    # PidSave(_PID, d, t)
    # PidDel(d, t)



def per(_PID, PID_con, PID_start):
    result = list(set(PID_con) - set(PID_start))
    print(result)




PidRead()
# if __name__ == "__main__":
#main()