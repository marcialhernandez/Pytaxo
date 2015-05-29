sys.settrace(traceFunctions)
try:
    x=funcion(x)
except:
    pass
finally:
    sys.exit(0)