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