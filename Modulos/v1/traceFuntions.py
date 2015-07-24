import inspect, types, sys
contadorCantidadLineasTrazaPython=0
limiteContadorCantidadLineasTrazaPython=300
sysenv = globals().copy() 
EXCLUDED_TYPES = set([types.ModuleType])
def traceFunctions(frame, event, arg):
    global contadorCantidadLineasTrazaPython, limiteContadorCantidadLineasTrazaPython
    try:
        contadorCantidadLineasTrazaPython=contadorCantidadLineasTrazaPython+1
    except:
        pass
    if contadorCantidadLineasTrazaPython>limiteContadorCantidadLineasTrazaPython:
        dicPrint=dict()
        dicPrint["cantidadLineasTraza"]=limiteContadorCantidadLineasTrazaPython
        dicPrint["evento"]="return"
        dicPrint["funcionProcedencia"]=frame.f_code.co_name
        dicPrint["retorno"]="infinito"
        dicPrint["numLinea"]=str(frame.f_lineno)
        try:
            print dicPrint
        except:
            pass
        try:
            exit()
        except:
            exit()
    if event == 'return':
        dicPrint=dict()
        dicPrint["cantidadLineasTraza"]=contadorCantidadLineasTrazaPython
        dicPrint["evento"]=event
        dicPrint["funcionProcedencia"]=frame.f_code.co_name
        dicPrint["retorno"]=str(arg)
        dicPrint["numLinea"]=str(frame.f_lineno)
        try:
            print dicPrint            
        except:
            pass
    elif event == 'exception':
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        exc_type, exc_value, exc_traceback = arg
        dicPrint=dict()
        dicPrint["cantidadLineasTraza"]=contadorCantidadLineasTrazaPython
        dicPrint["evento"]=event
        dicPrint["tipo"]=exc_type.__name__
        dicPrint["glosa"]= exc_value
        dicPrint["numLinea"]=str(line_no)
        dicPrint["funcionProcedencia"]=func_name
        dicPrint["linea"]=''.join(inspect.getframeinfo(frame).code_context).rstrip()
        cuentaIdentacion=0
        for caracter in dicPrint["linea"]:
            if caracter==' ':
                cuentaIdentacion+=1
            else:
                break
        dicPrint["identacion"]=cuentaIdentacion
        dicPrint["linea"]=dicPrint["linea"].lstrip()
        try:
            print dicPrint
        except:
            pass
    elif event == 'call':
        dicPrint=dict()
        dicPrint["cantidadLineasTraza"]=contadorCantidadLineasTrazaPython
        dicPrint["evento"]=event
        dicPrint["invocacion"]=frame.f_code.co_name
        dicPrint["numLinea"]=str(frame.f_lineno)
        try:
            print dicPrint
        except:
            pass
    elif event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        varGlobals=frame.f_globals
        variablesGlobales=dict()
        for key, value in varGlobals.items():
            if not key.startswith('__') and not key.startswith('_') and type(value) not in EXCLUDED_TYPES and not key=='EXCLUDED_TYPES' and not key=='traceit' and not key=='traceFunctions' and not key=='sysenv' and type(value) is not type(traceFunctions):
                variablesGlobales[key] = value
        dicPrint=dict()
        dicPrint["cantidadLineasTraza"]=contadorCantidadLineasTrazaPython
        dicPrint["evento"]=event
        dicPrint["scope"]=name
        dicPrint["numLinea"]=str(lineno)
        dicPrint["linea"]=''.join(inspect.getframeinfo(frame).code_context).rstrip()
        cuentaIdentacion=0
        for caracter in dicPrint["linea"]:
            if caracter==' ':
                cuentaIdentacion+=1
            else:
                break
        dicPrint["identacion"]=cuentaIdentacion
        dicPrint["linea"]=dicPrint["linea"].lstrip()
        dicPrint["argumentos"]=str(inspect.getargvalues(frame).args)
        dicPrint["varLocales"]=str(inspect.getargvalues(frame).locals)
        dicPrint["varGlobales"]=str(variablesGlobales)
        dicPrint["funcionProcedencia"]=frame.f_code.co_name
        try:
            print dicPrint
        except:
            pass
    return traceFunctions