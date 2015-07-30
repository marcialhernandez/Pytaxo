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

import itertools, hashlib
from archivos import nombres

class xmlEntrada:
    #atributos estaticos
    
    #atributos de la clase
    def __init__(self,nombre,tipo,puntaje,alternativas,cantidadAlternativas,shuffleanswers,penalty,answernumbering,**kwargs):
        #Atributos en comun
        self.nombre=nombre
        self.tipo=tipo
        self.puntaje=puntaje
        self.alternativas=alternativas
        self.cantidadAlternativas=cantidadAlternativas
        self.shuffleanswers=shuffleanswers
        self.penalty=penalty
        self.answernumbering=answernumbering
        self.id="NULL"
        if 'idOrigenEntrada' in kwargs.keys():
            self.idOrigenEntrada=kwargs['idOrigenEntrada']
        else:
            self.idOrigenEntrada="NULL"
        #Atributos solo de preguntas tipo Definicion
        if self.tipo=="definicion":
            self.termino=kwargs['termino']
            self.id=hashlib.sha256(self.termino).hexdigest()
            #Lista de alternativas de la forma [distractor,{'ponderacion':ponderacion}]
        elif (self.tipo=="pythonTraza" or self.tipo=="pythonIterativo" or self.tipo=="pythonIterativoInvertido") and "codigos" in kwargs.keys():
            self.codigos=kwargs['codigos']

        elif self.tipo=="pythonCompara":
            self.codigos=kwargs['codigos']
            self.comentarios=kwargs['comentarios']

        elif self.tipo=="enunciadoIncompleto":
            #Lista donde cada elemento es parte del enunciado ordenado de forma
            #secuencial
            self.enunciado=kwargs['enunciado']
            self.id=hashlib.sha256(self.enunciado).hexdigest()
            #self.id=hashlib.sha256(self.enunciadoIncompleto).hexdigest()
            #Lista donde cada elemento son las respuestas del enunciado
            #ordenadas de forma secuencial
            #self.respuestas=kwargs['respuestas']
        elif self.tipo=='definicionPareada':
            #La id de este tipo de pregunta se genera cuando tambien lo hace el item
            #Debido a que el ordenamiento de las definiciones expuestas en la parte izquierda
            #Cambian de orden
            self.criterioOrdenDistractores=kwargs['criterioOrdenDistractores']
            self.composicionDistractores=kwargs['composicionDistractores']
            self.ordenTerminos=kwargs['ordenTerminos']
            self.cantidadCombinacionesDefiniciones=kwargs['cantidadCombinacionesDefiniciones']
            self.parcialScore=kwargs['parcialScore']
    
    def printContenidoEntrada(self):
        mensaje="Nombre entrada: {nombre} \nPuntaje: {puntaje}\nTermino: {termino}\nDefinicion: {definicion}\nDistractores: {alternativas} "
        print mensaje.format(nombre=self.nombre,puntaje=self.puntaje, termino=self.termino, definicion=self.definicion,alternativas=self.alternativas)
        pass
    
    #No se sabe si es necesario crear este tipo pues es para un tipo especifico de pregunta
    def preguntaDefSimpleIntoXml(self):
        nombreDirectorioEntradas='./Plantillas'
        if nombres.validaExistenciaArchivo(nombreDirectorioEntradas)==True and nombres.validaCantidadContenido(nombreDirectorioEntradas)==True:
            print nombres.especificDirectoryNames(nombreDirectorioEntradas)
            #falta recoger la informacion y formar la pregunta a partir de la plantilla
        pass
    
    def retornaEnunciadoIncompleto(self):
        return " ".join(self.enunciadoIncompleto)
        
    def retornaAlternativas(self):
        ponderacion={'ponderacion':self.puntaje}
        alternativaCorrecta=list()
        if self.tipo=="definicion":
            alternativaCorrecta.append(self.definicion)
        if self.tipo=="enunciadoIncompleto":
            alternativaCorrecta.append('-'.join(self.respuestas))
        alternativaCorrecta.append(ponderacion)
        alternativas=list()
        alternativas.append(alternativaCorrecta)
        for elem in self.alternativas:
            alternativas.append(elem)
        return alternativas
    #falta reordenar las alternativas pues en este caso siempre la correcta sera la primera
    
    def agrupamientoAlternativas(self,cantidadAlternativas):
        if cantidadAlternativas<=1:
            return list()
        listaDeListaDeAlternativas=list()
        listaDeAlternativasValidas=list()
        for llave in self.alternativas.keys():
            listaDeListaDeAlternativas.append(self.alternativas[llave])
        for posiblesCombinacionesAlternativas in list(itertools.combinations(listaDeListaDeAlternativas,cantidadAlternativas)):
            banderaPresentaACorrecta=False
            for alternativas in posiblesCombinacionesAlternativas:
                if alternativas[0].tipo=='solucion':
                    banderaPresentaACorrecta=True
            if banderaPresentaACorrecta==True:                          
                for posiblesConjuntos in list(itertools.product(*posiblesCombinacionesAlternativas)):
                    listaDeAlternativasValidas.append(posiblesConjuntos)
        #print len(listaDeAlternativasValidas)
        return listaDeAlternativasValidas
    
    def agrupamientoAlternativas2(self,cantidadAlternativas):
        if cantidadAlternativas<=1:
            return list()
        listaDeListaDeAlternativas=list()
        listaDeSoluciones=None
        listaDeAlternativasValidas=list()
        for llave in self.alternativas.keys():
            if self.alternativas[llave][0].tipo=='solucion':
                listaDeSoluciones=self.alternativas[llave]
            else:
                listaDeListaDeAlternativas.append(self.alternativas[llave])      
        for posiblesCombinacionesAlternativas in list(itertools.combinations(listaDeListaDeAlternativas,cantidadAlternativas-1)): 
            posiblesCombinacionesAlternativas=list(posiblesCombinacionesAlternativas)
            posiblesCombinacionesAlternativas.append(listaDeSoluciones)
            try:
                for posiblesConjuntos in list(itertools.product(*posiblesCombinacionesAlternativas)):
                    listaDeAlternativasValidas.append(posiblesConjuntos)
            #Esta falla es producida por un mal nombramiento del atributo tipo en el tag alternativa
            except:
                print "Error1: El atributo tipo contiene un nombre distinto de 'solucion' o 'distractor'"
                exit()
        #print len(listaDeAlternativasValidas)
        return listaDeAlternativasValidas
    
    def barajaDefiniciones(self):
        return list(itertools.permutations(self.alternativas['terminos'].keys()))