#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)

Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use. 

NonCommercial — You may not use the material for commercial purposes.

NoDerivatives — If you remix, transform, or build upon the material, you may not distribute the modified material. 

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits. 

https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode#languages

Copyright (C)
@author: Marcial Hernandez Sanchez
@date: 16/6/2015
University of Santiago, Chile (Usach)"""

class plantilla:
    #atributos estaticos
    
    #atributos de la clase
#     def __init__(self,nombrePregunta,tipo,puntaje,termino,definicion,alternativas):
    def __init__(self,tipo,enunciado,**kwargs):
        self.taxo="Null"
        self.tipo=tipo
        self.enunciado=enunciado
        if 'taxo' in kwargs.keys():
            self.taxo=kwargs['taxo']
        