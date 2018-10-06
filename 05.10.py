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
motorGarra = ev3.MediumMotor('outA'); assert motorGarra.connected
## Sensores de cor
corEsq = ev3.ColorSensor('in1'); assert corEsq.connected
corEsq.mode = 'COL-COLOR'

corDir = ev3.ColorSensor('in4'); assert corDir.connected
corDir.mode = 'COL-COLOR'

#corCheck = ev3.ColorSensor('in2'); assert corCheck.connected
#corCheck.mode = 'COL-COLOR'

corCheck = ev3.Sensor(address = 'in2', driver_name = 'ht-nxt-color-v2')
corCheck.mode = 'ALL'

##Sensor de Ultrassom
ultrassom = ev3.UltrasonicSensor('in3'); assert ultrassom.connected
ultrassom.mode = 'US-DIST-CM'

#--------------------------------------------------------------
#------#######------- SENSORES E MOTORES ----------------------
#--------------------------------------------------------------

velocidade = 400    
deltaDir = 150         # delta de velocidade ao ajeitar caminho
deltaEsq = 150
fator = 1
v_curva = 300       # velocidade em curvas

pos_dir = 445       # as curvas
pos_esq = pos_dir
pos_volta = 2 * pos_dir     # quantidade angular de giro dos motores para

cores = []              # usa o codigo de cor

t = 100                 # tempo do andaReto()
t_recuo = 300           # tempo de recuo
x_avancar = 250         # avanco ao chegar na lajota

garra_pos = 700
garra_speed = 1500

avanco_bonecos = 500
avanco_pre = 350
dist_bonecos = 100

branco = [11, 12, 13, 14, 15, 16, 17]

class Robot:
    def __init__(self):
        self.corAntiga = -1      # ao chegar em cor, indica o valor da cor vista antes (pode ser preto)
        self.contador = 0       ## conta quantas vezes o robot testou a cor; se acertar a direcao, zera o contador
        self.ida = 0            # Faremos ida += 1 quando chegarmos no fim do percurso
        self.ladrilhos = 0      # Checa numero de ladrilhos
        self.bonecos = 0

robot = Robot()

def tocaMusica(tupla):
    while True:
        ev3.Sound.play_song(tupla).wait()
        sleep(1)

def tocaMusiquinha():
    tocaMusica(starWars)

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
        aprendizado = [-1, -1, -1]                         # caso nao haja arquivo, criamos a lista
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
        motorEsq.run_timed(speed_sp = velocidade - deltaEsq/fator, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade + deltaDir, time_sp = t)

    if corEsq.value() == 0:
        motorDir.run_timed(speed_sp = velocidade - deltaDir/fator, time_sp = t)
        motorEsq.run_timed(speed_sp = velocidade + deltaEsq, time_sp = t)
    
    else:
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)

def saindoReto():
    print("saindo reto")
    while(corCheck.value() not in branco):                                       ## MUDOU: era != 6 agora é not in branco 
        motorEsq.run_timed(speed_sp = velocidade, time_sp = t)
        motorDir.run_timed(speed_sp = velocidade, time_sp = t)
            
            # Testar NO-COLOR nos sensores para ajeitar o caminho
        if corDir.value() == 0:
            motorEsq.run_timed(speed_sp = velocidade - deltaEsq/fator, time_sp = t)
            motorDir.run_timed(speed_sp = velocidade + deltaDir, time_sp = t)
            
        if corEsq.value() == 0:
            motorDir.run_timed(speed_sp = velocidade - deltaDir/fator, time_sp = t)
            motorEsq.run_timed(speed_sp = velocidade + deltaEsq, time_sp = t)

#funcao seguir frente dependendo da necessidade

def avancar(x_avancar):
    print("avancando")
    motorDir.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
    motorEsq.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva direita

def curvaDir():
    print("curva direita")
    motorDir.run_to_rel_pos(position_sp = - pos_dir, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = pos_dir, speed_sp = v_curva)
    motorDir.wait_while("running")
    motorEsq.wait_while("running")

#funcao curva esquerda

def curvaEsq():
    print("curva esquerda")
    motorDir.run_to_rel_pos(position_sp = pos_esq, speed_sp = v_curva)
    motorEsq.run_to_rel_pos(position_sp = - pos_esq, speed_sp = v_curva)
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
    
#def traduzCor(cor):
#    return {
#        0: "no-color",
#        1: "preto",
#        2: "azul",
#        3: "verde",
#        4: "amarelo",
#        5: "vermelho",
#        6: "branco",
#        7: "marrom"
#    }[cor]

#def falaCor(cor):
#    ev3.Sound.speak( traduzCor(cor) )

def salvaCor(cor):
    with open("cores.txt", "a") as fw:
        fw.write(cor)

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
    
def aprender(aprendizado):
    print("aprendeu")
    aprendizado[robot.contador] = robot.corAntiga
    salvarAprendizado(aprendizado)
    robot.contador = 0

def rampa_ida():
    print("na rampa")
    recuar();    recuar();    recuar()
    recuar();    recuar();    recuar()
    meiaVolta()
    saindoReto()
    robot.ida += 1
    aprendizado.reverse()
##    saindoReto()
    #avancar(1000)

def testaCor(cor):          # retorna True se a variável 'cor' for cor
    if cor in (2,3,4,5):   # azul verde amarelo vermelho
        return cor
    else:
        return 9

def atribuiCor(cor):
    if cor in [2, 3]:
        return 2
    if cor in [8, 9, 10]:
        return 8
    if cor in [4, 5]:
        return 4
    if cor in branco:
        return 17

def testaRampa():
    cor1 = [-1,-1,-1]   # Vou testar 3 leituras de cor
    cor1[0] = atribuiCor( corCheck.value() )
    print("cores de rampa", cor1[0])
    avancar(x_avancar/2)
    cor1[1] = atribuiCor( corCheck.value() )
    print("cores de rampa", cor1[1])
    avancar(x_avancar/2)
    cor1[2] = atribuiCor( corCheck.value() )
    print("cores de rampa", cor1[2])

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
    if corCheck.value() == 0:   # se vê preto (zero é preto)
        recuar()                # anda um pouco pra tras antes de dar meia volta
        meiaVolta()             # da meia volta
        saindoReto()            # sai do ladrilho colorido se ajeitando, ate enxergar branco
        robot.corAntiga = 0     # sabera que saiu de um ladrilho preto na proxima intersecao
    else:
        print("Nao era preto", corCheck.value())

def testarDirecao(robot, aprendizado):          # 
    if aprendizado[robot.contador] == -1:
        curvaDir()
        saindoReto()
    elif aprendizado[robot.contador + 1] == -1:
        robot.contador += 1
        saindoReto()
    elif aprendizado[robot.contador + 2] == -1:
        robot.contador += 2
        curvaEsq()
        saindoReto()
        
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
        if robot.corAntiga == 0:                ## PRETO EH ZERO
            robot.contador += 1
            testarDirecao(robot, aprendizado)
            robot.corAntiga = corAtual

        else:
            cores.append(corAtual)
            robot.ladrilhos += 1
            if not sabeCor( robot.corAntiga ):
                aprender(aprendizado)       # robot.contador = 0
            testarDirecao(robot, aprendizado)
            robot.corAntiga = corAtual


def vendoNada():                # Quando ve no-color
    pass                        # o termo 'pass' indica que a funcao nao fara nada

def interpretaCor(cor):         # sendo 'cor' a cor vista por corCheck
    #if cor == 0:                # se cor == 0 (no color), executa vendoNada()
    #    vendoNada()
    if cor == 0:
        vendoPreto()            # se cor == 0 (preto), executa vendoPreto()
    elif cor in branco:
        vendoBranco()           # se cor in branco, executa vendoBranco() ( andaReto() )
    else:
        if testaRampa() == False:
#            recuar()
            vendoCor()              # qualquer outra vai ser uma cor: executa vendoCor()
        else:
            if not sabeCor( robot.corAntiga ):
                aprender(aprendizado)
            rampa_ida()

def sobe(garra_pos = 800, garra_speed = 1500):
    motorGarra.run_to_rel_pos(position_sp = garra_pos, speed_sp = garra_speed)
    motorGarra.wait_while("running")

def desce(garra_pos = 800, garra_speed = 1500):
    motorGarra.run_to_rel_pos(position_sp = -garra_pos, speed_sp = garra_speed)
    motorGarra.wait_while("running")

def pegaBonecos():
    avancar(avanco_pre)
    curvaDir()
    desce()
    avancar(avanco_bonecos)
    parar()
    sobe()
    desce(150)
    sobe(200)
    recuar();    recuar();    recuar()
    recuar();    recuar()
    curvaEsq()
    robot.bonecos += 1

def imprimeCores():
    cl = corCheck
    while True:
        print(cl.value(0), '(',  cl.value(1), cl.value(2), cl.value(3), ')', "ultrassom", ultrassom.value())
        sleep(0.4)

def imprimiDistancia():
    while True:
        print(ultrassom.value())
        sleep(0.5)

# -------------------------------------
#------- Main comeca aqui! ------------
# -------------------------------------

p1 = Process(target = imprimeCores)
p1.start()

#def roboContador():
#    while True:
#        print("contador", robot.contador)
#        sleep(2)

#p2 = Process(target = imprimiDistancia)
#p2.start()

#p2 = Process(target = tocaMusiquinha)
#p2.start()

while True:
    if robot.ida == 0:                            # Enquanto o robot estiver na ida
        interpretaCor( corCheck.value() )       # interpreta a cor do corCheck (veja interpretaCor)
    if robot.ida == 1:
        print("vou voltar")
        while robot.ladrilhos !=0:
            interpretaCor( corCheck.value() )
        meiaVolta()
        aprendizado.reverse()
        robot.ida = 2
    if robot.ida == 2:
        if ultrassom.value() < dist_bonecos and robot.bonecos < 2:
            pegaBonecos()
        else:
            interpretaCor(corCheck.value())




