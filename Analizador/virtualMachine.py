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
	lectura = input('$>')
	value = ''
	try:
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
			'goto': goto,
			'gotoF': gotoF
		}
		current = Quads[quadNum]
		fun = switcher.get(current[0], "No existe la operacion")
		res = fun(current[1], current[2], current[3])
		if(res != None):
			quadNum = res
		else:
			quadNum = quadNum + 1

ejecutaQuadruplos()