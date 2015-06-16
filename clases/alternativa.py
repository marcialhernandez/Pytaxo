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

class alternativa:
    
    def __init__(self, llave, tipo, puntaje,glosa, **kwargs):
        atributos=kwargs.keys()
        self.llave=llave
        self.tipo=tipo
        if 'numeracion' in atributos:
            self.numeracion=kwargs['numeracion']
        else:
            self.numeracion=None
        self.puntaje=puntaje
        self.glosa=glosa
        if 'comentario' in atributos:
            self.comentario=kwargs['comentario']
    
    def identificador(self):
        if 'numeracion' != None:
            if self.tipo=='solucion':
                return 'alt'+'Tipo'+str(self.tipo[0]).upper()+'='+'Num'+str(self.numeracion)+' '
            else:
                return 'alt'+'Tipo'+str(self.tipo[0]).upper()+'='+'F'+str(self.llave)+'Num'+str(self.numeracion)+' '
        #alternativa tipo S/D (distractor/solucion) = F llave (refiere a que alternativa) + N numeracion (refiere a que sinonimo)
        else: #Caso Terminos pareados
            if self.tipo=='solucion':
                return 'alt'+'Tipo'+str(self.tipo[0]).upper()+'='+'F'+str(self.llave)+' '
            
    
    def imprimeAlternativa(self):
        return str(self.glosa)+' ' #str(self.llave)+' '+str(self.tipo)+' '+str(self.puntaje)+' ' +str(self.glosa)