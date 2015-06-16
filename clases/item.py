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

class item:
    #atributos estaticos
    
    #atributos de la clase
    def __init__(self,nombrePregunta,resultado,falla):
        if len(resultado)==0:
            self.resultado=None
        else:
            self.resultado=resultado
        if len(falla)==0:
            self.falla=None
        else:
            self.falla=falla
            
        self.nombre=nombrePregunta
    
    def printModuloPregunta(self):
        mensaje="Pregunta tipo: {nombre} \nResultado Obtenido: {resultado}\nFalla obtenida: {falla} "
        print mensaje.format(nombre=self.nombre,resultado=self.resultado, falla=self.falla)
        pass