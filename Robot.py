import ev3dev.ev3 as ev3

class Robot:
    def __init__(self):
        self.motorEsq = ev3.LargeMotor('outC')
        self.motorDir = ev3.LargeMotor('outB')
        self.motorGarra = ev3.MediumMotor('outA')
        self.motorCacamba = ev3.MediumMotor('outD')        
                
        self.corEsq = ev3.ColorSensor('in1')
        self.corDir = ev3.ColorSensor('in4')
        self.corCheck = ev3.Sensor(address = 'in2', driver_name = 'ht-nxt-color-v2')
        self.ultrassom = ev3.UltrasonicSensor('in3')
        
        self.corAntiga = -1     # ao chegar em cor, indica o valor da cor vista antes (pode ser preto)
        self.contador = 0       # conta quantas vezes o robot testou a cor; se acertar a direcao, zera o contador
        self.ida = 0            # Faremos ida += 1 quando chegarmos no fim do percurso
        self.ladrilhos = 0      # Checa numero de ladrilhos
        self.bonecos = 0        # Conta o numero de bonecos pegos

    