# Parsing rules

# Tablas
TablaFunciones = {}
TablaVariables = {}
TablaGlobales = {}

# Quadruplos
OpStack = []
OperStack = []
TypeStack = []
JumpStack = []
ForStack = []
Quad = []

#Memoria
countTemporales = 0
countConstantes = 0

# Auxiliares
current_type = 'void'
const_flag = True

def clearEverything():
    # Tablas
    global TablaFunciones, TablaVariables, TablaGlobales
    TablaFunciones = {}
    TablaVariables = {}
    TablaGlobales = {}

    # Quadruplos
    OpStack.clear()
    OperStack.clear()
    TypeStack.clear()
    Quad.clear()

    #Memoria
    global countTemporales, countConstantes
    countTemporales = 0
    countConstantes = 0

    # Auxiliares
    global current_type, const_flag
    current_type = 'void'
    const_flag = True

# PROGRAMA
def p_programa(t):
    '''programa : PROGRAMA define_global SEMICOLON variables define_var_global funciones PRINCIPAL LPAREN RPAREN LCORCHETE estatuto RCORCHETE'''
    t[0] = "COMPILADO" # t[0] es lo que tiene como valor programa

def p_define_global(t):
    '''define_global : ID'''
    global TablaFunciones
    TablaFunciones[t[1]] = {'tipo': 'void'}

def p_define_var_global(t):
    '''define_var_global :'''
    global TablaGlobales, TablaVariables
    TablaGlobales = TablaVariables
    TablaVariables = {}

# VARIABLES
def p_variables(t):
    '''variables : VAR tipo COLON lista_ids SEMICOLON variables_1
                | empty'''
    global TablaVariables
    if(t[1] != None):
        for var in t[4]:
            if var['name'] not in TablaVariables:
                TablaVariables[var['name']] = {'tipo': t[2], 'dimension': var['dimension']}
            else:
                print("La variable ", var['name'], " ya esta definida")

def p_variables_1(t):
    '''variables_1 : tipo COLON lista_ids SEMICOLON variables_1
                    | empty'''
    global TablaVariables
    if(t[1] != None):
        for var in t[3]:
            if var['name'] not in TablaVariables:
                TablaVariables[var['name']] = {'tipo': t[1], 'dimension': var['dimension']}
            else:
                print("La variable ", var['name'], " ya esta definida")


# LISTA_IDS
def p_lista_ids(t):
    '''lista_ids : identificadores lista'''
    #Check if id is in current
    array = t[2]
    objeto = t[1]
    array.append(objeto)

    t[0] = array

def p_lista(t):
    '''lista : COMMA identificadores lista
            | empty'''
    if(t[1] == ','):
        array = t[3]
        objeto = t[2]
        array.append(objeto)

        t[0] = array
    else:
        lst = []
        t[0] = lst
        #print(t[0])

# FUNCIONES
def p_funciones(t):
    '''funciones : FUNCION define_funct LPAREN parametros RPAREN SEMICOLON variables LCORCHETE estatuto RCORCHETE clear_vars funciones
                | empty'''

def p_define_funct(t):
    '''define_funct : tipo_retorno ID'''
    global TablaFunciones
    if(t[2] not in TablaFunciones):
        TablaFunciones[t[2]] = {'tipo': t[1]}
    else:
        print("La funcion ", t[2], " ya esta definida")

def p_clear_vars(t):
    '''clear_vars :'''
    global TablaVariables
    TablaVariables = {}

# TIPO_RETORNO
def p_tipo_retorno(t):
    '''tipo_retorno : INT 
                    | FLOAT 
                    | CHAR 
                    | VOID'''
    t[0] = t[1]

# TIPO
def p_tipo(t):
    '''tipo : INT 
            | FLOAT 
            | CHAR'''
    t[0] = t[1]

#PARAMETROS
def p_parametros(t):
    '''parametros : tipo COLON ID variables_2
                    | empty'''
def p_variables_2(t):
    '''variables_2 : COMMA tipo COLON variables_2
                    | empty'''

#ESTATUTO
def p_estatuto(t):
    '''estatuto : estatuto_1 estatuto 
                | empty'''
def p_estatuto_1(t):
    '''estatuto_1 : asignacion 
                    | funcion_void 
                    | retorno 
                    | lectura
                    | escritura 
                    | decision 
                    | repeticion'''

#ASIGNACION
def p_asignacion(t):
    '''asignacion : check_id ASIGNAR expresiones SEMICOLON'''
    # TODO: Verificar que existan los operadores y que la semantica se pueda
    quad = [t[2], t[1]['name'], OpStack.pop()]
    Quad.append(quad)
    t[0] = t[1]['name']

def p_check_id(t):
    '''check_id : identificadores'''
    # Buscar en tablas de variables
    global current_type
    if t[1]['name'] in TablaVariables:
        current_type = TablaVariables[t[1]['name']]['tipo']
    elif t[1]['name'] in TablaGlobales:
        current_type = TablaGlobales[t[1]['name']]['tipo']
    else:
        print("La variable ", t[1]['name'], " no esta definida") 
    t[0] = t[1]

# IDENTIFICADORES
def p_identificadores(t):
    '''identificadores : ID LBRACKET CTEI RBRACKET LBRACKET CTEI RBRACKET
                        | ID LBRACKET CTEI RBRACKET
                        | ID '''
    global current_type
    dimension = 0
    if(len(t) > 2):
        dimension = 1
    if(len(t) > 5):
        dimension = 2
    t[0] = {'name':t[1], 'dimension': dimension}

# TERMINOS
def p_terminos(t):
    '''terminos : LPAREN expresiones RPAREN 
                | identificadores
                | var_cte 
                | funcion_retorno'''
    global current_type, const_flag
    if(t[1] != '('):
        if(const_flag):
            # Buscar en tablas de variables
            if t[1]['name'] in TablaVariables:
                current_type = TablaVariables[t[1]['name']]['tipo']
            elif t[1]['name'] in TablaGlobales:
                current_type = TablaGlobales[t[1]['name']]['tipo']
            else:
                print("La variable ", t[1]['name'], " no esta definida") 
        const_flag = True
        OpStack.append(t[1]['name'])
        TypeStack.append(current_type)


# ESPECIALES TODO: Ver como se va a estar manejando matrizes (incluye tambien en las otras reglas)
def p_especiales(t):
    '''especiales : terminos
                    | terminos especiales_1'''
def p_especiales_1(t):
    '''especiales_1 : DETERMINANTE
                    | TRANSPUESTA
                    | INVERSA'''
    OperStack.append(t[1])

# FACTORES
def p_factores(t):
    '''factores : especiales
                | especiales factores_1 factores'''
    global countTemporales
    if(len(t) > 2):
        if(OperStack[-1] == '*' or OperStack[-1] == '/'):
            right_op = OpStack.pop() # TODO: ver si se puede pasar toda esta logica a una funcion para simplificar el codifo
            right_type = TypeStack.pop()
            left_op = OpStack.pop()
            left_type = TypeStack.pop()
            oper = OperStack.pop()
            res_type = Semantica[right_type][left_type][oper]
            if(res_type == 'err'):
                print("Error de semantica!!!! ", right_type, left_type, oper)
            result = 'temp' + str(countTemporales)
            countTemporales = countTemporales + 1
            quad = [oper, left_op, right_op, result]
            Quad.append(quad)
            OpStack.append(result)
            TypeStack.append(res_type)


def p_factores_1(t):
    '''factores_1 : TIMES 
                  | DIVIDE'''
    OperStack.append(t[1])

# ARITMETICOS
def p_aritmeticos(t):
    '''aritmeticos : factores
                    | factores aritmeticos_1 aritmeticos'''
    global countTemporales
    if(len(t) > 2):
        if(OperStack[-1] == '+' or OperStack[-1] == '-'):
            right_op = OpStack.pop()
            right_type = TypeStack.pop()
            left_op = OpStack.pop()
            left_type = TypeStack.pop()
            oper = OperStack.pop()
            res_type = Semantica[right_type][left_type][oper]
            if(res_type == 'err'):
                print("Error de semantica!!!!", right_type, left_type, oper)
            result = 'temp' + str(countTemporales)
            countTemporales = countTemporales + 1
            quad = [oper, left_op, right_op, result]
            Quad.append(quad)
            OpStack.append(result)
            TypeStack.append(res_type)
def p_aritmeticos_1(t):
    '''aritmeticos_1 : PLUS 
                     | MINUS'''
    OperStack.append(t[1])

# LOGICOS
def p_logicos(t):
    '''logicos : aritmeticos
                    | aritmeticos logicos_1 logicos'''
    global countTemporales
    if(len(t) > 2):
        if(OperStack[-1] == '<' or OperStack[-1] == '>' or OperStack[-1] == '==' or OperStack[-1] == '!='):
            right_op = OpStack.pop()
            right_type = TypeStack.pop()
            left_op = OpStack.pop()
            left_type = TypeStack.pop()
            oper = OperStack.pop()
            res_type = Semantica[right_type][left_type][oper]
            if(res_type == 'err'):
                print("Error de semantica!!!!", right_type, left_type, oper)
            result = 'temp' + str(countTemporales)
            countTemporales = countTemporales + 1
            quad = [oper, left_op, right_op, result]
            Quad.append(quad)
            OpStack.append(result)
            TypeStack.append(res_type)
def p_logicos_1(t):
    '''logicos_1 : LESS 
                    | GREATER
                    | EQUALS
                    | NOTEQUAL'''
    OperStack.append(t[1])

# EXPRESIONES
def p_expresiones(t):
    '''expresiones : logicos
                    | logicos expresiones_1 expresiones'''
    global countTemporales
    if(len(t) > 2):
        if(OperStack[-1] == '&' or OperStack[-1] == '|'):
            right_op = OpStack.pop()
            right_type = TypeStack.pop()
            left_op = OpStack.pop()
            left_type = TypeStack.pop()
            oper = OperStack.pop()
            res_type = Semantica[right_type][left_type][oper]
            if(res_type == 'err'):
                print("Error de semantica!!!!", right_type, left_type, oper)
            result = 'temp' + str(countTemporales)
            countTemporales = countTemporales + 1
            quad = [oper, left_op, right_op, result]
            Quad.append(quad)
            OpStack.append(result)
            TypeStack.append(res_type)
def p_expresiones_1(t):
    '''expresiones_1 : AND 
                     | OR'''
    OperStack.append(t[1])

# FUNCION RETORNO
def p_funcion_retorno(t):
    '''funcion_retorno : ID LPAREN lista_ids RPAREN
                        | ID LPAREN RPAREN'''

# FUNCION VOID
def p_funcion_void(t):
    '''funcion_void : ID LPAREN lista_ids RPAREN SEMICOLON
                        | ID LPAREN RPAREN SEMICOLON'''

# RETORNO
def p_retorno(t):
    '''retorno : REGRESA LPAREN expresiones RPAREN SEMICOLON'''

# LECTURA
def p_lectura(t):
    '''lectura : LEE LPAREN lista_ids RPAREN SEMICOLON'''

# ESCRITURA
def p_escritura(t):
    '''escritura : ESCRIBE LPAREN escritura_1 RPAREN SEMICOLON'''
def p_escritura_1(t):
    '''escritura_1 : STRING escritura_2
                    | expresiones escritura_2'''
def p_escritura_2(t):
    '''escritura_2 : COMMA escritura_1 
                    | empty'''

# DECISION
def p_decision(t):
    '''decision : SI LPAREN expresiones RPAREN if_jump ENTONCES LCORCHETE estatuto RCORCHETE decision_1'''
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)
def p_decision_1(t):
    '''decision_1 : if_else SINO LCORCHETE estatuto RCORCHETE
                    | empty'''

def p_if_jump(t):
    '''if_jump :'''
    exp_type = TypeStack.pop()
    if(exp_type != 'bool'):
        print("Type-mismatch")
    else:
        result = OpStack.pop()
        quad = ['GotoF', result, '', '____']
        Quad.append(quad)
        JumpStack.append(len(Quad) - 1)

def p_if_else(t):
    '''if_else :'''
    jump_idx = JumpStack.pop()
    quad = ['Goto', '', '', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)
    Quad[jump_idx][-1] = len(Quad)


# REPETICION
def p_repeticion(t):
    '''repeticion : repeticion_cond 
                  | repeticion_no_cond'''
def p_repeticion_cond(t):
    '''repeticion_cond : mark_tag MIENTRAS LPAREN expresiones RPAREN if_jump HAZ LCORCHETE estatuto RCORCHETE'''
    end = JumpStack.pop()
    return_ = JumpStack.pop()
    quad = ['Goto', '', '', return_]
    Quad.append(quad)
    Quad[end][-1] = len(Quad)


def p_mark_tag(t):
    '''mark_tag :'''
    JumpStack.append(len(Quad))

def p_repeticion_no_cond(t):
    '''repeticion_no_cond : DESDE iter_desde HASTA comparacion_desde HACER LCORCHETE estatuto jump_back RCORCHETE'''

def p_iter_desde(t):
    '''iter_desde : asignacion'''
    global countTemporales
    quad = ['Goto', '', '', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)
    left_op = t[1]
    left_type = current_type
    right_op = 1
    right_type = 'int'
    oper = '+'
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de semantica!!!!", right_type, left_type, oper)
    result = 'temp' + str(countTemporales)
    countTemporales = countTemporales + 1
    quad = [oper, left_op, right_op, result]
    #Jump
    ForStack.append(len(Quad))
    Quad.append(quad)
    quad = ['=', t[1], result]
    Quad.append(quad)
    OpStack.append(t[1])
    TypeStack.append(left_type)

def p_comparacion_desde(t):
    '''comparacion_desde : expresiones'''
    global countTemporales
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    oper = '<'
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de semantica!!!!", right_type, left_type, oper)
    result = 'temp' + str(countTemporales)
    countTemporales = countTemporales + 1
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)
    quad = [oper, left_op, right_op, result]
    Quad.append(quad)
    quad = ['GotoF', result, '', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)

def p_jump_back(t):
    '''jump_back :'''
    quad = ['Goto', '', '', ForStack.pop()]
    Quad.append(quad)
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)



#VAR_CTE
def p_var_cte(t):
    '''var_cte : CTECH
               | CTEI
               | CTEF'''
    global const_flag, current_type #TODO: Ver como se va a terminar haciendo, como esta actualmente es un patch para que funcione con lo que tenemos
    if(isinstance(t[1], int)):
        current_type = 'int'
    elif(isinstance(t[1], str)):
        current_type = 'char'
    elif(isinstance(t[1], float)):
        current_type = 'float'

    t[0] = {'name': t[1]}
    const_flag = False

# EMPTY
def p_empty(t):
    '''empty :'''
    pass

# SACADOS DE EJEMPLO CALC.PY http://www.dabeaz.com/ply/example.html

def p_error(t):
    print("Syntax error at '%s'" % t.value)


# Definicion de Cubo Semantico
# Cubo Semantico
Semantica = {
    # INT
    'int': {
        'int': {
            '+': 'int',
            '-': 'int',
            '*': 'int',
            '/': 'float',
            '>': 'bool', 
            '<': 'bool',
            '!=': 'bool',
            '==': 'bool',
            '&': 'err',
            '|': 'err',
            '=': 'int'
        },
        'float': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'char': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'bool': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        }
    },
    #Float
    'float': {
        'int': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '>': 'bool', 
            '<': 'bool',
            '!=': 'bool',
            '==': 'bool',
            '&': 'err',
            '|': 'err',
            '=': 'float'
        },
        'float': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '>': 'bool', 
            '<': 'bool',
            '!=': 'bool',
            '==': 'bool',
            '&': 'err',
            '|': 'err',
            '=': 'float'
        },
        'char': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'bool': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        }
    },
    # CHAR
    'char': {
        'int': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'float': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'char': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'bool',
            '==': 'bool',
            '&': 'err',
            '|': 'err',
            '=': 'char'
        },
        'bool': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        }
    },
    # BOOL
    'bool': {
        'int': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'float': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'char': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'err',
            '==': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'bool': {
            '+': 'err',
            '-': 'err',
            '*': 'err',
            '/': 'err',
            '>': 'err', 
            '<': 'err',
            '!=': 'bool',
            '==': 'bool',
            '&': 'bool',
            '|': 'bool',
            '=': 'bool'
        }
    }
}


import sys
import pprint
import ply.yacc as yacc

from lexer import tokens

parser = yacc.yacc()
pp = pprint.PrettyPrinter(indent=4)

while True:
    try:
        s = input('!Jitters > ') # solo 'input()' para py3
        file = str(s)
        if s == "":
            sys.exit('bye')
        f = open(file, 'r')
        data = f.read()
        f.close()
        if parser.parse(data) == "COMPILADO":
            print("Se compilo exitosamente.")
            print('===== Funciones =====')
            pp.pprint(TablaFunciones)
            print('===== QUADS =====')
            for i in range(len(Quad)):
                print(i, Quad[i])
            clearEverything()
    except EOFError:
        print(EOFError)
    if not s: continue
    