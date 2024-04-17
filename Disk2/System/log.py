def write(text="Script name: log.py\nFunction: write()\n", fname="log.txt", rej="w", cod="utf8"):
# Функция сохраняет данные в файл
    try:
        f = open(fname, rej, encoding=cod)
        f.write(text)
        f.close()
        return 1
    except Exception as e:
        return str(e)

def read(fname="log.txt", rej="r", cod="utf8"):
# Функция считывает данные из файла
    try:
        f = open(fname, rej)
        text = f.read()
        f.close()
        return text
    except:
        try:
            f = open(fname, rej, encoding=cod)
            text = f.read()
            f.close()
            return text
        except Exception as e:
            return str(e)

def CommandExecutionP(command=""):
# Функция использует устаревшую функцию "popen" из модуля os, однако это работает и вполне удобно
    import os
    result = os.popen(command).read()
    return result

def getDate():
# Функция возвращает текущую дату
    import datetime
    MyDate = datetime.date.today()
    return MyDate

def getTime():
# Функция возвращает текущее время
    import datetime
    MyTime = datetime.datetime.today().strftime("%H:%M:%S")
    return MyTime