from .Robot import Robot

class Andador(Robot):
    def __init__(self):
        Robot.__init__(self)

    def parar(self):
        print("parou")
        self.motorDir.stop()
        self.motorEsq.stop()

    def avancar(self, x_avancar = 250, velocidade = 400):
        print("avancando")
        self.motorDir.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
        self.motorEsq.run_to_rel_pos(position_sp = x_avancar, speed_sp = velocidade)
        self.motorDir.wait_while("running")
        self.motorEsq.wait_while("running")

    #funcao curva direita

    def curvaDir(self, pos_dir = 445, v_curva = 300):
        print("curva direita")
        self.motorDir.run_to_rel_pos(position_sp = - pos_dir, speed_sp = v_curva)
        self.motorEsq.run_to_rel_pos(position_sp = pos_dir, speed_sp = v_curva)
        self.motorDir.wait_while("running")
        self.motorEsq.wait_while("running")
