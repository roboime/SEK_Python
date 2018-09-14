#!/usr/bin/env python3
# coding: utf-8

import ev3dev.ev3 as ev3
from multiprocessing import Process
from time import sleep

#--------------------------------------------------------------
#------#######------- SENSORES E MOTORES ----------------------
#--------------------------------------------------------------

motorEsq = ev3.LargeMotor('outC'); assert motorEsq.connected
motorDir = ev3.LargeMotor('outB'); assert motorDir.connected
##motorGarra = ev3.MediumMotor('outA'); assert motorGarra.connected

## Sensores de cor
corEsq = ev3.ColorSensor('in1'); assert corEsq.connected
corEsq.mode = 'COL-COLOR'

corDir = ev3.ColorSensor('in4'); assert corDir.connected
corDir.mode = 'COL-COLOR'

corCheck = ev3.ColorSensor('in2'); assert corCheck.connected
corCheck.mode = 'COL-COLOR'

#--------------------------------------------------------------
#------#######------- SENSORES E MOTORES ----------------------
#--------------------------------------------------------------

velocidade = -300    
delta = 150         # delta de velocidade ao ajeitar caminho
v_curva = -200      # velocidade em curvas

pos_dir = 425      # as curvas
pos_esq = pos_dir
pos_volta = 2 * pos_dir     # quantidade angular de giro dos motores para

cores = []              # usa o codigo de cor

t = 100                 # tempo do andaReto()
t_recuo = 300           # tempo de recuo
x_avancar = 200         # avanco ao chegar na lajota

class Robot():
    def __init__(self):
        self.corAntiga = 0      # ao chegar em cor, indica o valor da cor vista antes (pode ser preto)
        self.contador = 0       ## conta quantas vezes o robot testou a cor; se acertar a direcao, zera o contador
        self.ida = 0            # Faremos ida = False quando chegarmos na rampa
        self.ladrilhos = 0      # Checa numero de ladrilhos

robot = Robot()

def tocaMusiquinha(tupla):
    while True:
        ev3.Sound.play_song(tupla).wait()
        sleep(1)

starWars = (('D4', 'e3'),      # intro anacrouse
        ('D4', 'e3'),
        ('D4', 'e3'),
        ('G4', 'h'),       # meas 1
        ('D5', 'h'),
        ('C5', 'e3'),      # meas 2
        ('B4', 'e3'),
        ('A4', 'e3'),
        ('G5', 'h'),
        ('D5', 'q'),
        ('C5', 'e3'),      # meas 3
        ('B4', 'e3'),
        ('A4', 'e3'),
        ('G5', 'h'),
        ('D5', 'q'),
        ('C5', 'e3'),      # meas 4
        ('B4', 'e3'),
        ('C5', 'e3'),
        ('A4', 'h.'),)

beethoven = (
            ('E4', 'q'),
            ('E4', 'q'),
            ('F4', 'q'),
            ('G4', 'q'),
            ('G4', 'q'),
            ('F4', 'q'),
            ('E4', 'q'),
            ('D4', 'q'),
            ('C4', 'q'),
            ('C4', 'q'),
            ('D4', 'q'),
            ('E4', 'q'),
            ('E4', 'h'),
            ('D4', 'e3'),
            ('D4', 'h'),)

def abrirAprendizado():
    ## try: tenta abrir um arquivo de aprendizado
    try:
        with open("aprendizado.txt", "r") as ft:            # a lista de aprendizado serah "direita,frente,esquerda"
            aprendizado = ft.read().split(',')              # aqui, criamos uma lista de strings, cada elemento eh a cor
            aprendizado.pop()
            aprendizado = [int(x) for x in aprendizado]     # tornamos as strings em inteiros
    except:
        aprendizado = [0, 0, 0]                         # caso nao haja arquivo, criamos a lista
    # [direita, frente, esquerda] com o codigo da cor
    # basta reverter a lista pra usar pra "volta" (robot.ida == False)
    return aprendizado                                  # Retorna a lista "aprendizado"

def salvarAprendizado(aprendizado):
    with open("aprendizado.txt", "w") as fw:
        for cor in aprendizado:
            fw.write("%s," % cor)

aprendizado = abrirAprendizado()

def andaReto():
    # Testar NO-COLOR nos sensores para ajeitar o caminho
    if corDir.value() == 0:
        motorEsq.run_timed(speed_sp = velocidade + delta, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade - delta, time_sp = t)

    if corEsq.value() == 0:
        motorDir.run_timed(speed_sp = velocidade + delta, time_sp = t)
        motorEsq.run_timed(speed_sp = velocidade - delta, time_sp = t)
    
    else:
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)

def saindoReto():
    print("saindo reto")
    while(corCheck.value() != 6): 
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)
            
            # Testar NO-COLOR nos sensores para ajeitar o caminho
        if corDir.value() == 0:
            motorEsq.run_timed(speed_sp = velocidade + delta, time_sp = t)
            motorDir.run_timed(speed_sp = velocidade - delta, time_sp = t)
            
        if corEsq.value() == 0:
            motorDir.run_timed(speed_sp = velocidade + delta, time_sp = t)
            motorEsq.run_timed(speed_sp = velocidade - delta, time_sp = t)

#funcao seguir frente dependendo da necessidade

def avancar(x_avancar):
    print("avancando")
    motorDir.run_to_rel_pos(position_sp = -x_avancar, speed_sp = velocidade)
    motorEsq.run_to_rel_pos(position_sp = -x_avancar, speed_sp = velocidade)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva direita

def curvaDir():
    print("curva direita")
    motorDir.run_to_rel_pos(position_sp = pos_dir, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = -pos_dir, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva esquerda

def curvaEsq():
    print("curva esquerda")
    motorDir.run_to_rel_pos(position_sp = - pos_esq, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_esq, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

def meiaVolta():
    print("meia volta")
    motorDir.run_to_rel_pos(position_sp = pos_volta, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = - pos_volta, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

def recuar():
    print("recuando")
    motorEsq.run_timed(speed_sp = -velocidade, time_sp = t_recuo, stop_action = "brake")
    motorDir.run_timed(speed_sp = -velocidade, time_sp = t_recuo, stop_action = "brake")
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao parar

def parar():
    print("parou")
    motorDir.stop()
    motorEsq.stop()
    
def traduzCor(cor):
    return {
        0: "no-color",
        1: "preto",
        2: "azul",
        3: "verde",
        4: "amarelo",
        5: "vermelho",
        6: "branco",
        7: "marrom"
    }[cor]

def falaCor(cor):
    ev3.Sound.speak( traduzCor(cor) )

def salvaCor(cor):
    with open("cores.txt", "a") as fw:
        fw.write(cor)

def imprimeCores():
    corCur = corCheck.value()
    print( traduzCor(corCur) )
    while True:
        if corCheck.value() != corCur:
            corCur = corCheck.value()
            print( traduzCor(corCur) )
            salvaCor( traduzCor(corCur) + '\n' )
            #falaCor( corCur )

def sabeCor(cor):
    return cor in aprendizado     # retorna True se a cor foi aprendida

def executaCor(cor):
    if aprendizado.index(cor) == 0:         # aprendizado.index(cor) da o indice da 'cor'
        curvaDir()                          # temos indice 0 pra direita, 1 pra frente, 2 pra esquerda 
        saindoReto()
    elif aprendizado.index(cor) == 1:
        saindoReto()
    elif aprendizado.index(cor) == 2:
        curvaEsq()
        saindoReto()

#def testar(count):          # 
#    if count == 0:
#        curvaDir()
#        saindoReto()
#    elif count == 1:
#        saindoReto()
#    elif count == 2:
#        curvaEsq()
#        saindoReto()
    
def aprender(aprendizado):
    print("aprendeu")
    aprendizado[robot.contador] = robot.corAntiga
    salvarAprendizado(aprendizado)
    robot.contador = 0

def rampa_ida():
    print("na rampa")
    recuar()
    recuar()
    meiaVolta()
    saindoReto()
    robot.ida += 1
    avancar(1000)
    aprendizado.reverse()

def testaCor(cor):          # retorna True se a variável 'cor' for cor
    if cor in (2,3,4,5):   # azul verde amarelo vermelho
        return cor
    else:
        return 9

def testaRampa():
    cor1 = [0,0,0]   # Vou testar 3 leituras de cor
    cor1[0] = corCheck.value()
    avancar(x_avancar/2)
    cor1[1] = corCheck.value()
    avancar(x_avancar/2)
    cor1[2] = corCheck.value()

    if cor1[0] == cor1[1]:
        return False
    else:
        if cor1[1] == cor1[2]:
            return False
        else:
            return True

def vendoBranco():
    andaReto()          # Quando ve branco, anda reto

def vendoPreto():
    parar()                 # ao ver preto, o robot para
    avancar(20)
    if corCheck.value() == 1:
        recuar()                # anda um pouco pra tras antes de dar meia volta
        meiaVolta()             # da meia volta
        saindoReto()            # sai do ladrilho colorido se ajeitando, ate enxergar branco
        robot.corAntiga = 1     # sabera que saiu de um ladrilho preto na proxima intersecao
    else:
        print(corCheck.value())

def vendoCor():
    corAtual = corCheck.value()                             # corAtual eh a cor vista no ladrilho
    if sabeCor( corAtual ):                                 # testa se conhece a corAtual
        cores.append(corAtual)
        if not sabeCor( robot.corAntiga ):
            aprender(aprendizado)
        executaCor( corCheck.value() )
        if robot.ida == 0:
            robot.ladrilhos += 1
        if robot.ida == 1:
            robot.ladrilhos -= 1
        robot.corAntiga = corAtual
    else:
        if robot.corAntiga == 1:
            robot.contador += 1
            #testar(robot.contador)
            curvaDir()
            saindoReto()
            robot.corAntiga = corAtual
        else:
            cores.append(corAtual)
            robot.ladrilhos += 1
            if not sabeCor( robot.corAntiga ):
                aprender(aprendizado)
            #testar(robot.contador)
            curvaDir()
            saindoReto()
            robot.corAntiga = corAtual


def vendoNada():                # Quando ve no-color
    pass                        # o termo 'pass' indica que a funcao nao fara nada

def interpretaCor(cor):         # sendo 'cor' a cor vista por corCheck
    if cor == 0:                # se cor == 0 (no color), executa vendoNada()
        vendoNada()
    elif cor == 1:
        vendoPreto()            # se cor == 1 (preto), executa vendoPreto()
    elif cor == 6:
        vendoBranco()           # se cor == 6 (branco), executa vendoBranco() ( andaReto() )
    else:
        if testaRampa() == False:
            vendoCor()              # qualquer outra vai ser uma cor: executa vendoCor()
        else:
            if not sabeCor( robot.corAntiga ):
                aprender(aprendizado)
            rampa_ida()

def pegaBonecos():
    tocaMusiquinha(starWars)

# -------------------------------------
#------- Main comeca aqui! ------------
# -------------------------------------

p1 = Process(target = imprimeCores)
p1.start()

#p2 = Process(target = tocaMusiquinha)
#p2.start()

#btn = ev3.Button()

while True:
    if robot.ida == 0:                            # Enquanto o robot estiver na ida
        interpretaCor( corCheck.value() )       # interpreta a cor do corCheck (veja interpretaCor)
    if robot.ida == 1:
        while robot.ladrilhos !=0:
            interpretaCor( corCheck.value() )
        meiaVolta()
        aprendizado.reverse()
        robot.ida=2
    if robot.ida == 2:
        pegaBonecos()