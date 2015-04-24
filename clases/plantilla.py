

class plantilla:
    #atributos estaticos
    
    #atributos de la clase
#     def __init__(self,nombrePregunta,tipo,puntaje,termino,definicion,alternativas):
    def __init__(self,tipo,enunciado,**kwargs):
        self.tipo=tipo
        self.enunciado=enunciado
        