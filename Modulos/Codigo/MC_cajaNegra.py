from archivos import nombres
from archivos import acceso

nombreDirectorioEntradas="./Entradas/Codigo"
nombreCompilador="python"

if nombres.validaExistenciasSubProceso(nombreDirectorioEntradas)==True:
    for codigoEntrada in nombres.fullEspecificDirectoryNames(nombreDirectorioEntradas):
        acceso.obtenerResultadosEntrada(nombres.directorioReal(codigoEntrada),nombreCompilador).printContenidoEntrada()
    
