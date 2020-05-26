Memoria = {
	5000: 0,
	5001: 0,
	7000: 0,
	12000: 10
}
Quads = [['goto', '', '', 2], ['LEE', 5000, '', ''], ['+', 5000, 12000, 13000], ['=', 13000, '', 5001], ['ESCRIBE', 5001, '', '']]


class ExecuteError(Exception): pass

def suma(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] + Memoria[right_op]
	return None

def resta(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] - Memoria[right_op]
	return None

def multi(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] * Memoria[right_op]
	return None

def divi(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] / Memoria[right_op]
	return None

def mayor(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] > Memoria[right_op]
	return None

def menor(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] < Memoria[right_op]
	return None

def igual(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] == Memoria[right_op]
	return None

def noIgual(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] != Memoria[right_op]
	return None

def And(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] and Memoria[right_op]
	return None

def Or(left_op, right_op, res):
	Memoria[res] = Memoria[left_op] or Memoria[right_op]
	return None

def asigna(left_op, right_op, res):
	Memoria[res] = Memoria[left_op]
	return None

def escribe(left_op, right_op, res):
	if(left_op == 'ENDLINE'):
		print()
	elif(type(left_op) == str):
		print(left_op)
	else:
		print(Memoria[left_op])
	return None

def lee(left_op, right_op, res):
	lectura = input('!>')
	value = ''
	try:
		print('Memo:',Memoria)
		value = type(Memoria[left_op])(lectura)
	except:
		raise ExecuteError('Error de lectura')
	Memoria[left_op] = value
	return None

def goto(left_op, right_op, res):
	return res


def gotoF(left_op, right_op, res):
	if(left_op):
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
			'ESCRIBE': escribe,
			'LEE': lee,
			'Goto': goto,
			'GotoF': gotoF,
			'ERA': era
		}
		current = Quads[quadNum]
		fun = switcher.get(current[0], 'err')
		print(fun)
		res = fun(current[1], current[2], current[3])
		if(res != None):
			quadNum = int(res)
		else:
			quadNum = quadNum + 1


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
	
	while fl[pos] != '>Constantes':
		name = fl[pos].split()[-1]
		TablaFunciones[name] = {} 
		pos = pos + 1
		while 'p:' not in fl[pos].split() and fl[pos] != '>Constantes' :
			values = fl[pos].split()
			TablaFunciones[name][values[0]] = values[-1]
			pos = pos + 1

	pos = pos + 1

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

	for qpos in range(pos, len(fl)):
		quad = (fl[qpos].split())
		Quads.append(quad)
	
	print(TablaConstantes)
	print()
	print(TablaFunciones)
	print()
	print(Quads)

	#ejecutaQuadruplos()

	
		

		
				
						
						
				

		
		
		



	
			
					
				

if __name__ == "__main__":
    main()