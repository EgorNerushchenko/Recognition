import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
import tkinter as tk
from itertools import product
from PIL import Image, ImageTk
import time
font = cv2.FONT_HERSHEY_SIMPLEX
EPS = 0.005

IX = []
JY = []
JC = [0, 1, 0, -1]
IC = [1, 0, -1, 0]
JCC = [0, 1, 1, 1, 0, -1, -1, -1]
ICC = [1, 1, 0, -1, -1, -1, 0, 1]
KET1 = 5
KET2 = 29
tex = ['1','2','3','4','5']
DES = np.zeros((200, 256)).astype(int)
# Единичный квадрат разбитый на 16x16 пикселей

def SEARCH(TX, TY, P, k1, k2):
    max = 0

    for i in range(k1+1, k2):
        a = math.sqrt(pow(TX[k1]-TX[i], 2) + pow(TY[k1]-TY[i], 2))
        b = math.sqrt(pow(TX[k2]-TX[i], 2) + pow(TY[k2]-TY[i], 2))
        r = a + b
        if r > max:
            max = r
            i1 = i
            a1 = a
            b1 = b
    c = math.sqrt(pow(TX[k2]-TX[k1], 2) + pow(TY[k2]-TY[k1], 2))
    p = (a1 + b1 + c) / 2
    h = (2 * math.sqrt(p * (p - a1) * (p - b1) * (p - c))) / c
    #EPS1 = (a1 + b1 - c)/c
    EPS1 = h/c
    if (EPS1 > EPS) and (a1 > 5.0) and (b1 > 5.0):
        P[i1] = 1
    else:
        for i2 in range(k1+1, k2):
            P[i2] = 2

def OBR(RR, w1, h1, ris):
    RUV = np.zeros((16, 16)).astype(int)
    R1 = np.zeros((h1, w1)).astype(int)

    #Выделение только внешнего контура
    for pos in product(range(h1), range(w1)):
        pixel = RR.item(pos)
        if pixel == 1:
            for k in range(len(JC)):
                if RR[np.add(pos[0], JC[k]), np.add(pos[1], IC[k])] == 0:
                    R1[pos[0], pos[1]] = 1
                    break

    #plt.imshow(R1, cmap='gray')
    #plt.show()

    #Поиск самой первой точки контура
    flag = None
    for j in range(R1.shape[0]):
        for i in range(R1.shape[1]):
            if R1[j, i] == 1:
                flag = True
                j1 = j
                i1 = i
                break
        if flag:
            break

    #Вторая точка контура (где-то нужна будет возможно)
    for k in range(len(JC)):
        if RR[j1 + JC[k], i1 + IC[k]] == 1:
            pointY = j1 + JC[k]
            pointX = i1 + IC[k]
            break

    JPR = 0 #Условие выхода из цикла while

    j0 = j1
    i0 = i1

    TY = []
    TX = []

    while JPR == 0:
        R1[j1, i1] = 2
        TY.append(j1)
        TX.append(i1)
        for k in range(9):
            if k < 8:
                if R1[j1 + JCC[k], i1 + ICC[k]] == 1:
                    j1 = j1 + JCC[k]
                    i1 = i1 + ICC[k]
                    break
                if j1 + JCC[k] == j0 and i1 + ICC[k] == i0:
                    JPR = 1
                    break

    xy = list(zip(TX, TY))

    #Нахождение центра контура
    sumx = 0
    sumy = 0
    for k in range(len(TX)):
        sumx += TX[k]
        sumy += TY[k]
    XC = sumx / len((TX))
    YC = sumy / len((TY))
    point_center = [int(YC), int(XC)]
    #print(f'Center in: {point_center}')

    #Нахождение главного диаметра контура
    max1 = 0
    for a in range(len(TX)):
        x = TX[a]
        y = TY[a]
        dx = x - point_center[0]
        dy = y - point_center[1]
        r1 = dx * dx + dy * dy
        if r1 > max1:
            max1 = r1
            d1 = TX[a]
            d2 = TY[a]
            k1 = a

    max2 = 0
    for b in range(len(TX)):
        dx = TX[b] - d1
        dy = TY[b] - d2
        r2 = dx * dx + dy * dy
        if r2 > max2:
            max2 = r2
            d3 = TX[b]
            d4 = TY[b]
            k2 = b

    #print(f'Point1 in: {[d1, d2]}')
    #print(f'Point2 in: {[d3, d4]}')

    #Удвоение массивов для того, чтобы можно было пройти по координатам контура от k1 до k2 и от k2 до k1
    #P - массив признаков того, что точка характеристическая
    n = len(TX)
    TX1 = TX.copy()
    TX = TX + TX1
    TY1 = TY.copy()
    TY = TY + TY1
    P = TY.copy()

    for k in range(n):
        TX[k + n] = TX[k]
        TY[k + n] = TY[k]
        P[k] = 0
        P[k + n] = 0

    P[k1] = 1
    P[k1 + n] = 1
    # print(TX[k1], TY[k1], TX[k1+n], TX[k1+n], P[k1])
    P[k2] = 1
    P[k2 + n] = 1
    # print(TX[k2], TY[k2], TX[k2+n], TY[k2+n], P[k2])

    #Индексы точек главного диаметра k1 - k2 - k1
    main_points = []
    i = 0
    for k in range(len(P)):
        if i == 3:
            break
        if P[k] == 1:
            main_points.append(k)
            i += 1

    #Поиск всех характеристических точек
    IPR = 0
    while IPR == 0:
        k = main_points[0]
        k1 = k
        for i in range(k1, len(TX)):
            if P[i] == 0:
                k1 = i - 1
                j = i
                break
        for i1 in range(j, len(TX)):
            if P[i1] == 1:
                k2 = i1
                break

        SEARCH(TX, TY, P, k1, k2)

        for k3 in range(main_points[0] + 1, main_points[2]):
            if P[k3] == 0:
                IPR = 0
            else:
                IPR = 1

    #Заполнение массивов координат характеристических точек
    TDJ = TX.copy()
    TDI = TY.copy()
    LD = 0

    for k in range(main_points[0], main_points[2] + 1):
        if P[k] == 1:
            TDJ[LD] = TY[k]
            TDI[LD] = TX[k]
            LD += 1

    TDJ = TDJ[0:LD]
    TDI = TDI[0:LD]

    TDJ.insert(0, TDJ[-2])
    TDI.insert(0, TDI[-2])

    #Переход в новую систему координат с областью определения [0...1]
    U = TDJ.copy()
    V = TDI.copy()

    for k in range(1, len(TDJ) - 1):
        X1 = (TDI[k - 1] + TDI[k + 1]) / 2.0
        Y1 = (TDJ[k - 1] + TDJ[k + 1]) / 2.0
        D = math.sqrt(pow(TDJ[k] - Y1, 2) + pow(TDI[k] - X1, 2))
        A = math.sqrt(pow(TDJ[k + 1] - TDJ[k], 2) + pow(TDI[k + 1] - TDI[k], 2))
        B = math.sqrt(pow(TDJ[k - 1] - TDJ[k], 2) + pow(TDI[k - 1] - TDI[k], 2))
        C = math.sqrt(pow(TDJ[k - 1] - TDJ[k + 1], 2) + pow(TDI[k - 1] - TDI[k + 1], 2))
        if RR[math.trunc(Y1), math.trunc(X1)] == 1:
            R3 = 0.0
        else:
            R3 = 1.0
        min_side = min(A, B)
        max_side = max(A, B)
        V[k] = 0.5 * (R3 + C / (D + C))
        U[k] = 0.5 * (R3 + min_side / max_side)

    U = U[1:-1]
    V = V[1:-1]

    for k in range(len(U)):
        C = math.trunc(15.9 * U[k])
        D = math.trunc(15.9 * V[k])
        RUV[C, D] = RUV[C, D] + 1

    contour = np.array(xy)
    cv2.fillPoly(ris, pts=[contour], color=(0, 0, 255))

    for j in range(1, h1):
        for i in range(1, w1):
            if (ris[j, i, 0] == 0) and (ris[j, i, 1] == 0) and (ris[j, i, 2] == 255):
                RR[j, i] = 0

    return RUV, pointX, pointY

ris = cv2.imread('C:\Files\diplom\example_pics/st.bmp') #BGR
ris1 = cv2.imread('C:\Files\diplom\example_pics/met.bmp') #BGR

RR = np.zeros((ris.shape[0], ris.shape[1]), dtype=np.uint8)

w = ris.shape[1]
h = ris.shape[0]

w1 = ris1.shape[1]
h1 = ris1.shape[0]

teach = tk.Tk()

screen_width = teach.winfo_screenwidth()
screen_height = teach.winfo_screenheight()
teach.configure(background='white')
teach.title("ОБУЧЕНИЕ")
teach.geometry(f'{screen_width}x{screen_height}')

ex_tk = ImageTk.PhotoImage(image=Image.fromarray(ris))
label = tk.Label(teach, image=ex_tk)
label.place(x=0, y=0)
teach.update()
teach.after(1)

for pos in product(range(h), range(w)):
        if ris[pos[0], pos[1], 2] > 0:
            RR[pos[0], pos[1]] = 0
        else:
            RR[pos[0], pos[1]] = 1

for N in range(0, KET1):
    RUV, a, b = OBR(RR, w, h, ris)
    for j in range(16):
        for i in range(16):
            DES[N, 16*j+i] = RUV[j, i]
    ex_tk = ImageTk.PhotoImage(image=Image.fromarray(ris))
    label = tk.Label(teach, image=ex_tk)
    label.place(x=0, y=0)
    teach.update()

text = ''
DES_ch = []

for k in range(0, KET1):
    for i in range(DES.shape[1]):
        if DES[k, i] == 0:
            ch = '.'
        else:
            ch = '|'
        text += ch
    DES_ch += [text]
    text = ''

Label_DES = tk.Label(teach, text="ДЕСКРИПТОРЫ", font="Helvetica 16 bold", bg='white')
Label_DES.place(x=label.winfo_width() + 800, y=label.winfo_height() // 2 - 300)

pos = label.winfo_height()//2 - 250
y = 0

for k in range(0, KET1):
    #label1 = tk.Label(teach, bg='gray', fg='black', font=('Arial', 14), justify='left', text=DES_ch[k])
    #label1.place(x=label.winfo_width() + 10, y=0)
    if k > 0:
        pos = pos + 4*y
    Label=tk.Label(teach,text=f"{k+1}) {DES_ch[k]}", font="Helvetica 14 bold", bg='white')
    Label.place(x=label.winfo_width() + 200, y=pos)
    teach.update()
    y=Label.winfo_height()
    teach.update()

time.sleep(3)

teach.destroy()

teach.mainloop()

recognition = tk.Tk()
recognition.title("РАСПОЗНАВАНИЕ")
recognition.configure(bg='white')
recognition.geometry(f'{screen_width}x{screen_height}')
ex_tk1 = ImageTk.PhotoImage(image=Image.fromarray(ris1))
rec1 = tk.Label(recognition, image=ex_tk1)
rec1.place(x=ris1.shape[1]+ris1.shape[1]//4, y=100)
recognition.update()

RR1 = np.zeros((ris1.shape[0], ris1.shape[1]), dtype=np.uint8)
for pos in product(range(h1), range(w1)):
        if ris1[pos[0], pos[1], 2] > 0:
            RR1[pos[0], pos[1]] = 0
        else:
            RR1[pos[0], pos[1]] = 1

for N in range(0, KET2):
    RUV, pointX, pointY = OBR(RR1, w1, h1, ris1)
    IX.append(pointX)
    JY.append(pointY)
    for j in range(16):
        for i in range(16):
            DES[N+KET1, 16*j+i] = RUV[j, i]
    ex_tk1 = ImageTk.PhotoImage(image=Image.fromarray(ris1))
    rec1 = tk.Label(recognition, image=ex_tk1)
    rec1.place(x=ris1.shape[1] + ris1.shape[1] // 4, y=100)
    recognition.update()
    
recognition.mainloop()


