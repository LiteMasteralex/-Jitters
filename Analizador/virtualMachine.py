import numpy as np

Memoria = {
	'Global': {},
	'Local': {},
	'Temporal': {},
	'Constante': {}
}

MemoriaTemp = {
	'Global': {},
	'Local': {},
	'Temporal': {},
	'Constante': {}
}

NextContext = []

LastContext = []

currentFunct = ''

# Esta funcion borra la memoria asignada
# Parametros: None
# Returns: None
# Usage: Se utiliza cuando finaliza la ejecucion de la maquina virtual
def clearMemTemp():
	global MemoriaTemp
	MemoriaTemp = {
		'Global': {},
		'Local': {},
		'Temporal': {},
		'Constante': {}
	}

# Esta funcion inicializa la memoria
# Parametros contexto : str, tipo : str, size : int
# Returns: None
# Usage: Se utiliza cuando se quiere seperar memoria en el contexto actual, esto se hace cada vez que se cambia de contexto
def separaMemoria(contexto, tipo, size):
	inicio = DefMemoria[contexto][tipo]
	# Para cada espacio de meoria inicializalo segun el tipo que recibiste
	for loc in range(inicio, inicio + int(size)):
		if(tipo == 'int'):
			MemoriaTemp[contexto][str(loc)] = 0
		elif(tipo == 'float'):
			MemoriaTemp[contexto][str(loc)] = 0.0
		elif(tipo == 'char'):
			MemoriaTemp[contexto][str(loc)] = ''
		elif(tipo == 'bool'):
			MemoriaTemp[contexto][str(loc)] = False
		else:
			MemoriaTemp[contexto][str(loc)] = 0

# Esta funcion regresa el contexto de una ubicacion segun el rango donde esta
# Paramentos: loc : int
# Returns: str : contexto de la ubicacion en memoria
# Usage: Esta funcion se utiliza cuando se quiera indexar memoria ya que para esto se necesita el contexto donde esta 
def obtenContexto(loc):
	# La memoria se indexa como str pero la comparacion debe ser en int
	loc = int(loc)
	if(loc < 4000): # Limite de la memoria Global
		return 'Global'
	elif(loc < 7000): # Limite de la memoria Local
		return 'Local'
	elif(loc < 12000): # Limite de la meoria Temporal
		return 'Temporal'
	else:
		return 'Constante'

# Esta funcion incializa la memoria cuando se genera un contexto usa la funcion funciona como un builder para la estructura de Memoria
# Parametros: nombre : str, contexto : str
# Returns: None
# Usage: Esta funcion se usa cuando se cambia un contexto y al inicio de la ejecucion
def initContexto(nombre, contexto):
	# Se usa contexto para poder inicializar las globales al inicio de la ejecuccion
	separaMemoria(contexto, 'int', TablaFunciones[nombre]['int'])
	separaMemoria(contexto, 'float', TablaFunciones[nombre]['float'])
	separaMemoria(contexto, 'char', TablaFunciones[nombre]['char'])
	# Aqui se inicializa el contexto temporal para cada funcion
	separaMemoria('Temporal', 'int', TablaFunciones[nombre]['tint'])
	separaMemoria('Temporal', 'float', TablaFunciones[nombre]['tfloat'])
	separaMemoria('Temporal', 'char', TablaFunciones[nombre]['tchar'])
	separaMemoria('Temporal', 'bool', TablaFunciones[nombre]['bool'])
	separaMemoria('Temporal', 'addr', TablaFunciones[nombre]['addr'])

# Esta funcion asigna los parametros como variables en el nuevo contexto
# Parametros: lista : list, params : 
# Returns: None
# Usage: Esta funcion se utiliza cuando hay un cambio de contexto y sirve para traducir los parametros a su memoria correspondiente
def asignaParametros(lista, params):
	# Obtiene las direcciones basicas de las variables locales ya que los paramentros siempre son las primeras direcciones
	countI = DefMemoria['Local']['int']
	countF = DefMemoria['Local']['float']
	countC = DefMemoria['Local']['char']
	# Para cada parametro verifica su tipo y definelo en su memoria correspondiente
	for idx in range(len(lista)):
		if(lista[idx] == 'i'):
			Memoria['Local'][str(countI)] = params[idx]
			countI = countI + 1
		if(lista[idx] == 'f'):
			Memoria['Local'][str(countF)] = params[idx]
			countF = countF + 1
		if(lista[idx] == 'c'):
			Memoria['Local'][str(countC)] = params[idx]
			countC = countC + 1
# Esta funcion recupera el contexto anterior y remplaza el actual
# Parametros: None
# Returns: int : numero de cuaddruplo al que se tiene que regresar la ejecuccion
# Usage: Esta funcion se llama cuando se termina de ejecutar una funcion ya sea con un ENPORC o con un regresa
def returnContext():
	global currentFunct, Memoria
	# Obten la memoria del stack
	last = LastContext.pop()
	# Remplaza la memoria del contexto
	Memoria['Local'] = last['memoria']['Local']
	Memoria['Temporal'] = last['memoria']['Temporal']
	# Actualiza el contexo
	currentFunct = last['nombre']
	return last['quad']

# Esta funcion convierte de una direccion de tipo Adrr a la direccion actual de memoria
# Parametros: left : str, right : str, res : str
# Returns: list : lista que contienen las nuevas direcciones a usar en ejecucion
# Usage: Esta funcion es usada en cada cuadruplo para verificar cuando se esten usando dirreciones
def addrCheck(left, right, res):
	# Agrega las direcciones a convertir a una lista para poder iterar sobre ellas
	params = [left, right, res]
	results = [] # Resultado final que se regresa
	for var in params:
		try: # Se hace un try porque no todo lo que viene en un cuadruplo de puede convertir a int
			value = int(var)
		except:
			value = 0
		if(value >= 11000 and value < 12000): # Se compara contra el rango de las temporales de tipo addr
			results.append(Memoria['Temporal'][str(value)]) # Se obtiene el valor de la direccion actual
		else:
			results.append(var)
	return results

# Esta funcion reconstruye una matriz dada su direccion base y su tamaño
# Parametros: loc : int, x : int, y : int
# Return np.array : matriz reconstruida con los valores de memoria
# Usage: Esta funcion es usada cuando se hacen operaciones en las cuales nuestros operadores se manejan como matrizes
def recoverMatrix(loc, x, y):
	locCont = obtenContexto(loc) # Obten el contexto para sacar el valor
	result = [] # El resultado es una matriz
	for idxX in range(x): # Se indexa como normalmente se indexaria una matriz
		row = [] # El renglon de la matriz
		for idxY in range(y):
			# el offset que se calcual es el siguiente:  direccion base + indice en X * tamaño del renglon + indice en y
			row.append(Memoria[locCont][str(int(loc) + (idxX*y) + idxY)])
		result.append(row)
	return np.array(result)

# Esta funcion pasa los valores de una matriz memoria dada una direccion base
# Parametros: loc : str, arr : np.array
# Returns : None
# Usage: Esta funcion se usa cuando se quiere guardar en memoria una variable dimensionada
def moveToMemory(loc, arr):
	locCont = obtenContexto(loc)
	for x in range(len(arr)) :
		for y in range(len(arr[x])):
			# el offset que se calcual es el siguiente:  direccion base + indice en X * tamaño del renglon + indice en y
			Memoria[locCont][str(int(loc) + (x * len(arr)) + y)] = arr[x][y]

class ExecuteError(Exception): pass

# Esta funcion suma los valores de las direcciones en memoria y las guarda en una memoria 
# Parametros: left_op : str, right_op : str, res : str
# Returns: None
# Usage: Esta funcion se usa cuando se encuentra un cuadruplo de suma en ejecucion
# Notas: Esta misma estructura se usa en Resta, Multiplicacion y Asignacion lo unico que cambia es la operacion que se hace.
# 			El retorno es None pero como todas forman parte de un switch se puede regresar tambien un numero de cuadruplo al
#			que se debe de mover
def suma(left_op, right_op, res):
	global  left_dim, right_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	right_mat = recoverMatrix(right_op, right_dim[0], right_dim[1])
	result = left_mat + right_mat
	moveToMemory(res, result)
	return None

def resta(left_op, right_op, res):
	global  left_dim, right_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	right_mat = recoverMatrix(right_op, right_dim[0], right_dim[1])
	result = left_mat - right_mat
	moveToMemory(res, result)
	return None

def multi(left_op, right_op, res):
	global  left_dim, right_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	right_mat = recoverMatrix(right_op, right_dim[0], right_dim[1])
	if(right_dim == [1, 1]):
		result = left_mat * right_mat
	else:
		result = np.matmul(left_mat, right_mat)
	moveToMemory(res, result)
	return None

# Esta funcion realiza la operacion de dividir dos valores de memoria y guardar el resultado en memoria
# Parametros: left_op : str, right_op : str, res : str
# Returns: None
# Usage: Esta funcion se usa cuando se encuentra un cuadruplo de division en ejecucion
# Notas: Esta misma estructura se usa en la mayoria de las operaciones en los cuadruplos lo unico que cambia es la operacion
#			que se hace. El retorno es None pero como todas forman parte de un switch se puede regresar tambien un numero de 
#			cuadruplo al que se debe de mover, la diferencia entre esta y la suma es que los operadores no se manejan como matrizes
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
	global  left_dim, right_dim
	right_mat = recoverMatrix(right_op, right_dim[0], right_dim[1])
	moveToMemory(left_op, right_mat)
	
	return None


def escribe(left_op, right_op, res):
	if(left_op == 'ENDLINE'):
		print()
	#elif(type(left_op) == str): TODO: Implementar constantes de tipo letrero que se usan para imprimir
		#print(left_op)
	else:
		leftCont = obtenContexto(left_op)
		print(Memoria[leftCont][left_op], end=" ")
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
	if(not Memoria[leftCont][left_op]):
		return res
	return None

def era(left_op, right_op, res):
	global NextContext, MemoriaTemp
	initContexto(left_op, 'Local')
	NextContext.append({'nombre': left_op,
						'memoria': {'Local': MemoriaTemp['Local'],
									'Temporal': MemoriaTemp['Temporal']},
						'parametros': []})
	clearMemTemp()
	return None

def parametro(left_op, right_op, res):
	leftCont = obtenContexto(left_op)
	NextContext[-1]['parametros'].append(Memoria[leftCont][left_op])
	return None

def gosub(left_op, right_op, res):
	global LastContext, auxQuad, currentFunct, Memoria
	LastContext.append({'quad': auxQuad + 1,
						'memoria': {'Local': Memoria['Local'], 'Temporal':Memoria['Temporal']},
						'nombre': currentFunct})
	current = NextContext.pop()
	currentFunct = current['nombre']
	Memoria['Local'] = current['memoria']['Local']
	Memoria['Temporal'] = current['memoria']['Temporal']
	asignaParametros(TablaFunciones[current['nombre']]['parametros'], current['parametros'])
	return TablaFunciones[current['nombre']]['start']

def endproc(left_op, right_op, res):
	return returnContext()

def regresa(left_op, right_op, res):
	loc = TablaFunciones[currentFunct]['loc']
	resCont = obtenContexto(res)
	Memoria['Global'][loc] = Memoria[resCont][res]
	return returnContext()

def sumaAddr(left_op, right_op, res):
	leftCont, resCont = obtenContexto(left_op), obtenContexto(res)
	Memoria[resCont][res] = str(Memoria[leftCont][left_op] + int(right_op))
	return None

def ver(left_op, right_op, res):
	leftCont, rightCont, resCont = obtenContexto(left_op), obtenContexto(right_op), obtenContexto(res)
	valor, valorInf, valorSup = Memoria[leftCont][left_op], Memoria[rightCont][right_op], Memoria[resCont][res]
	if(valor < valorSup and valor >= valorInf):
		return None
	else:
		raise ExecuteError('Index fuera del rango')

def dim(left_op, right_op, res):
	global left_dim, right_dim, res_dim
	left_op = left_op.split(',')
	left_dim = [int(left_op[0]), int(left_op[1])]
	right_op = right_op.split(',')
	if(len(right_op) > 1):
		right_dim = [int(right_op[0]), int(right_op[1])]
	res = res.split(',')
	if(len(res) > 1) :
		 res_dim = [int(res[0]), int(res[1])]
	return None

def deter(left_op, right_op, res):
	global  left_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	result = np.linalg.det(left_mat)
	moveToMemory(res, [[result]])
	return None

def inverse(left_op, right_op, res):
	global  left_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	result = np.linalg.inv(left_mat)
	moveToMemory(res, result)
	return None

def trans(left_op, right_op, res):
	global left_dim
	left_mat = recoverMatrix(left_op, left_dim[0], left_dim[1])
	result = left_mat.transpose()
	moveToMemory(res, result)

# Esta funcion es la prncipal que ejecuta el codigo con la cual hace todas las operaciones
def ejecutaQuadruplos():
	global auxQuad
	quadNum = 0
	# Para cada quad que se genero en memoria se realiza una operacion
	while quadNum < len(Quads):
		# Esta estructura sirve com nuestro switch principal, segun la llave que se le de regresa una funcion a la cual llamar
		switcher = {
			'+': suma,
			'-': resta,
			'*': multi,
			'/': divi,
			'>': mayor,
			'<': menor,
			'~=': igual,
			'!=': noIgual,
			'&': And,
			'|': Or,
			'=': asigna,
			'ESCRITURA': escribe,
			'LEE': lee,
			'Goto': goto,
			'GotoF': gotoF,
			'ERA': era,
			'parametro': parametro,
			'GOSUB': gosub,
			'ENDPROC': endproc,
			'regresa': regresa,
			'+Addr': sumaAddr,
			'VER': ver,
			'dim': dim,
			'$': deter,
			'?': inverse,
			'¡': trans
		}
		current = Quads[quadNum]
		auxQuad = quadNum
		# obten la funcion segun el resultado del switcher
		fun = switcher.get(current[0], 'err')
		# Valida las direcciones 
		left_op, right_op, res = addrCheck(current[1], current[2], current[3])
		if(current[0] == '+Addr'): # Caso especial donde queremos que la direccion se tome literalmente
			res = current[3]
		res = fun(left_op, right_op, res) # Llama a la funcion 
		if(res != None): # El None se recibe cuando no se requier hace salto a otra instruccion
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
	#Obten el archivo y define las estructuras que se usaran
	global Quads, TablaFunciones, TablaConstantes, MemoriaTemp, Memoria
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
	Memoria = MemoriaTemp
	clearMemTemp()
	Memoria['Constante'] = TablaConstantes

	# Inizializacion Quads
	for qpos in range(pos, len(fl)):
		quad = (fl[qpos].split())
		Quads.append(quad)
	

	ejecutaQuadruplos()

	
if __name__ == "__main__":
    main()