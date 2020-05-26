Memoria = {
	'Global': {},
	'Local': {},
	'Temporal': {},
	'Constante': {}
}


def separaMemoria(contexto, tipo, size):
	inicio = DefMemoria[contexto][tipo]
	for loc in range(inicio, inicio + int(size)):
		if(tipo == 'int'):
			Memoria[contexto][str(loc)] = 0
		elif(tipo == 'float'):
			Memoria[contexto][str(loc)] = 0.0
		elif(tipo == 'char'):
			Memoria[contexto][str(loc)] = ''
		elif(tipo == 'bool'):
			Memoria[contexto][str(loc)] = False
		else:
			Memoria[contexto][str(loc)] = 0

def obtenContexto(loc):
	loc = int(loc)
	if(loc < 4000):
		return 'Global'
	elif(loc < 7000):
		return 'Local'
	elif(loc < 12000):
		return 'Temporal'
	else:
		return 'Constante'

def initContexto(nombre, contexto):
	separaMemoria(contexto, 'int', TablaFunciones[nombre]['int'])
	separaMemoria(contexto, 'float', TablaFunciones[nombre]['float'])
	separaMemoria(contexto, 'char', TablaFunciones[nombre]['char'])
	separaMemoria('Temporal', 'int', TablaFunciones[nombre]['tint'])
	separaMemoria('Temporal', 'float', TablaFunciones[nombre]['tfloat'])
	separaMemoria('Temporal', 'char', TablaFunciones[nombre]['tchar'])
	separaMemoria('Temporal', 'bool', TablaFunciones[nombre]['bool'])
	separaMemoria('Temporal', 'addr', TablaFunciones[nombre]['addr'])

class ExecuteError(Exception): pass

def suma(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] + Memoria[rightCont][right_op]
	return None

def resta(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] - Memoria[rightCont][right_op]
	return None

def multi(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] * Memoria[rightCont][right_op]
	return None

def divi(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] / Memoria[rightCont][right_op]
	return None

def mayor(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] > Memoria[rightCont][right_op]
	return None

def menor(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] < Memoria[rightCont][right_op]
	return None

def igual(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] == Memoria[rightCont][right_op]
	return None

def noIgual(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] != Memoria[rightCont][right_op]
	return None

def And(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] and Memoria[rightCont][right_op]
	return None

def Or(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	Memoria[resCont][res] = Memoria[leftCont][left_op] or Memoria[rightCont][right_op]
	return None

def asigna(left_op, right_op, res):
	leftCont, rightCont = obtenContexto(left_op), obtenContexto(right_op)
	Memoria[leftCont][left_op] = Memoria[rightCont][right_op]
	return None


def escribe(left_op, right_op, res):
	if(left_op == 'ENDLINE'):
		print()
	#elif(type(left_op) == str): TODO: Implementar constantes de tipo letrero que se usan para imprimir
		#print(left_op)
	else:
		leftCont = obtenContexto(left_op)
		print(Memoria[leftCont][left_op])
	return None

def lee(left_op, right_op, res):
	lectura = input('!>')
	value = ''
	leftCont = obtenContexto(left_op)
	try:
		value = type(Memoria[leftCont][left_op])(lectura)
	except:
		raise ExecuteError('Error de lectura')
	Memoria[leftCont][left_op] = value
	return None

def goto(left_op, right_op, res):
	return res


def gotoF(left_op, right_op, res):
	leftCont = obtenContexto(left_op)
	if(Memoria[leftCont][left_op]):
		return res
	return None

def era(left_op, right_op, res):
	return None

# TODO(Cristina): CHECAR RANGO Y DEPENDIENDO DE CUAL ES SABER A DONDE 
#		  DIRIGIRSE.
def ejecutaQuadruplos():
	quadNum = 0
	while quadNum < len(Quads):
		switcher = {
			'+': suma,
			'-': resta,
			'*': multi,
			'/': divi,
			'>': mayor,
			'<': menor,
			'==': igual,
			'!=': noIgual,
			'&': And,
			'|': Or,
			'=': asigna,
			'ESCRITURA': escribe,
			'LEE': lee,
			'Goto': goto,
			'GotoF': gotoF,
			'ERA': era
		}
		current = Quads[quadNum]
		fun = switcher.get(current[0], 'err')
		res = fun(current[1], current[2], current[3])
		if(res != None):
			quadNum = int(res)
		else:
			quadNum = quadNum + 1


DefMemoria = {
    'Global': {
        'int': 1000,
        'float': 2000,
        'char': 3000
    },
    'Local': {
        'int': 4000,
        'float': 5000,
        'char': 6000
    },
    'Temporal': {
        'int': 7000,
        'float': 8000,
        'char': 9000,
        'bool': 10000,
        'addr': 11000

    }
}


import sys
import os

def main():
	global Quads, TablaFunciones, TablaConstantes
	filepath = sys.argv[1]
	if not os.path.isfile(filepath):
		print("Error: el archivo {} no existe...".format(filepath))
		sys.exit()
	
	Quads = []
	TablaFunciones = {}
	TablaConstantes = {}

	pos = 1
	f = open(filepath, 'r')
	fl =f.readlines()

	for line in range(len(fl)):
		fl[line] = fl[line].rstrip()
	
	# Inizalizacion Tabla Funciones
	while fl[pos] != '>Constantes':
		name = fl[pos].split()[-1]
		TablaFunciones[name] = {} 
		pos = pos + 1
		while 'p:' not in fl[pos].split() and fl[pos] != '>Constantes' :
			values = fl[pos].split()
			TablaFunciones[name][values[0]] = values[-1]
			pos = pos + 1

	pos = pos + 1

	# Inizalicacion Constantes
	while fl[pos] != '>Quads':
		value = fl[pos]
		loc = fl[pos + 1].split()[-1]
		tipo = fl[pos + 2].split()[-1]
		if tipo == 'int':
			TablaConstantes[loc] = int(value)
		elif tipo == 'float':
			TablaConstantes[loc] = float(value)
		else :
			TablaConstantes[loc] = value
		pos = pos + 3

	pos = pos + 1

	# Inizalizacion contexto Global
	name = fl[1].split()[-1]
	initContexto(name, 'Global')
	Memoria['Constante'] = TablaConstantes

	# Inizializacion Quads
	for qpos in range(pos, len(fl)):
		quad = (fl[qpos].split())
		Quads.append(quad)
	
	print(TablaConstantes)
	print()
	print(TablaFunciones)
	print()
	print(Quads)
	print()
	print(Memoria)

	ejecutaQuadruplos()

	
		

		
				
						
						
				

		
		
		



	
			
					
				

if __name__ == "__main__":
    main()