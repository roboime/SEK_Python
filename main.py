#!/usr/bin/env python3
# coding: utf-8

import ev3dev.ev3 as ev3
from .Robot import Robot
from .Andador import Andador

if __name__ == '__main__':
    andador = Andador()
    andador.avancar()