import inspect, types, sys
sysenv = globals().copy() 
EXCLUDED_TYPES = set([types.ModuleType])
def traceFunctions(frame, event, arg):
    if event == 'return':
        print '{"evento":"%s", "funcionProcedencia":"%s", "retorno":"%s"}' % \
        (event,frame.f_code.co_name, arg)
    elif event == 'exception':
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        exc_type, exc_value, exc_traceback = arg
        print '{"evento":"%s"; "tipo":"%s"; "glosa":"%s"; "numLinea":%s; "funcionProcedencia":"%s"}' % \
        (event,exc_type.__name__, exc_value, line_no, func_name)
        pass
    elif event == 'call':
        print '{"evento":"%s"; "invocacion":"%s"; "numLinea":%s}' % \
        (event,frame.f_code.co_name, frame.f_lineno)
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
            if not key.startswith('__') and type(value) not in EXCLUDED_TYPES and not key=='EXCLUDED_TYPES' and not key=='traceit' and not key=='funcion' :
                variablesGlobales[key] = value
        print '{"evento":"%s"; "scope":"%s"; "numLinea":%s; "linea":"%s"; "argumentos":"%s"; "varLocales":%s; "funcionProcedencia":"%s"}' % \
        (event,name, lineno,inspect.getframeinfo(frame).code_context[0].rstrip(), ','.join(inspect.getargvalues(frame).args), str(inspect.getargvalues(frame).locals).replace("\'",""), frame.f_code.co_name)
    return traceFunctions
sys.settrace(traceFunctions)