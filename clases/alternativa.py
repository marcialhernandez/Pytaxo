

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