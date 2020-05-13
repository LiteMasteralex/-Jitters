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
countParams = 0

# Auxiliares
current_type = 'void'
current_function = ''
const_flag = True
current_params = ''

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
    '''programa : PROGRAMA define_global SEMICOLON variables define_var_global funciones PRINCIPAL resolve_jump LPAREN RPAREN LCORCHETE estatuto RCORCHETE'''
    t[0] = "COMPILADO" # t[0] es lo que tiene como valor programa

def p_define_global(t):
    '''define_global : ID'''
    global TablaFunciones, current_function
    TablaFunciones[t[1]] = {'tipo': 'void', 'num_variables': 0}
    current_function = t[1]
    quad = ['Goto', '', '', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)

def p_define_var_global(t):
    '''define_var_global :'''
    global TablaGlobales, TablaVariables
    TablaGlobales = TablaVariables
    TablaVariables = {}

def p_resolve_jump(t):
    '''resolve_jump :'''
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)

# VARIABLES
def p_variables(t):
    '''variables : VAR tipo COLON lista_ids SEMICOLON variables_1
                | empty'''
    global TablaVariables, TablaFunciones, current_function
    if(len(t) > 2):
        for var in t[4]:
            if var['name'] not in TablaVariables:
                TablaVariables[var['name']] = {'tipo': t[2], 'dimension': var['dimension']}
            else:
                print("La variable ", var['name'], " ya esta definida")
        TablaFunciones[current_function]['num_variables'] = t[6] + 1

def p_variables_1(t):
    '''variables_1 : tipo COLON lista_ids SEMICOLON variables_1
                    | empty'''
    global TablaVariables
    if(len(t) > 2):
        for var in t[3]:
            if var['name'] not in TablaVariables:
                TablaVariables[var['name']] = {'tipo': t[1], 'dimension': var['dimension']}
                t[0] = t[5] + 1
            else:
                print("La variable ", var['name'], " ya esta definida")
    else:
        t[0] = t[1]


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
    '''funciones : FUNCION define_funct LPAREN parametros RPAREN SEMICOLON variables set_start LCORCHETE estatuto RCORCHETE clear_vars funciones
                | empty'''

def p_define_funct(t):
    '''define_funct : tipo_retorno ID'''
    global TablaFunciones, current_function
    if(t[2] not in TablaFunciones):
        TablaFunciones[t[2]] = {'tipo': t[1], 
                                'parametros': '', 
                                'num_parametros': 0, 
                                'num_variables': 0,
                                'num_temporales': 0,
                                'start':0}
        current_function = t[2]
    else:
        print("La funcion ", t[2], " ya esta definida")

def p_clear_vars(t):
    '''clear_vars :'''
    global TablaVariables, TablaFunciones, current_function, countTemporales
    TablaVariables = {}
    quad = ['ENDPROC', '', '', '']
    Quad.append(quad)
    TablaFunciones[current_function]['num_temporales'] = countTemporales
    countTemporales = 0


def p_set_start(t):
    '''set_start :'''
    global TablaFunciones, current_function
    TablaFunciones[current_function]['start'] = len(Quad)

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
    '''parametros : def_parameters variables_2
                    | empty'''
    global TablaFunciones, current_function
    if(len(t) > 2):
        TablaFunciones[current_function]['num_parametros'] = t[2] + 1
def p_variables_2(t):
    '''variables_2 : COMMA def_parameters variables_2
                    | empty'''
    if len(t) > 2:
        t[0] = t[3] + 1
    else:
        t[0] = t[1]

def p_def_parameters(t):
    '''def_parameters : tipo COLON ID'''
    global TablaVariables, TablaFunciones, current_function
    if t[3] in TablaVariables:
        print("La variable", t[3], 'ya esta definida')
    else:
        TablaVariables[t[3]] = {'tipo': t[1]}
        TablaFunciones[current_function]['parametros'] = TablaFunciones[current_function]['parametros'] + t[1][0]

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
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    res_type = Semantica[right_type][left_type]['=']
    if(res_type != 'err'):
        quad = ['=', left_op, right_op, '   ']
        Quad.append(quad)
    t[0] = t[1]

def p_check_id(t):
    '''check_id : identificadores'''
    # Buscar en tablas de variables
    current_type = ''
    if t[1]['name'] in TablaVariables:
        current_type = TablaVariables[t[1]['name']]['tipo']
    elif t[1]['name'] in TablaGlobales:
        current_type = TablaGlobales[t[1]['name']]['tipo']
    else:
        print("La variable ", t[1]['name'], " no esta definida")
    OpStack.append(t[1]['name'])
    TypeStack.append(current_type)
    t[0] = t[1]['name']

# IDENTIFICADORES
def p_identificadores(t):
    '''identificadores : ID LBRACKET CTEI RBRACKET LBRACKET CTEI RBRACKET
                        | ID LBRACKET CTEI RBRACKET
                        | ID '''
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


# ESPECIALES TODO: Ver como se va a estar manejando matrices (incluye tambien en las otras reglas)
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
            right_op = OpStack.pop() # TODO: ver si se puede pasar toda esta logica a una funcion para simplificar el codigo
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
    '''funcion_retorno : check_function LPAREN lista_exp RPAREN'''
    global countParams, current_params, TablaVariables, TablaFunciones
    if(countParams == len(current_params)):
        quad = ['GOSUB', t[1], '', '']
        Quad.append(quad)
        TablaVariables[t[1]] = {'tipo': TablaFunciones[t[1]]['tipo'], 'dimensiones': 0}
        t[0] = {'name': t[1]}
    else:
        print("Missing params or something like that")

def p_lista_exp(t):
    '''lista_exp : check_param lista_exp_1
                    | empty'''

def p_lista_exp_1(t):
    '''lista_exp_1 : COMMA check_param lista_exp_1
                    | empty'''

def p_check_param(t):
    '''check_param : expresiones'''
    global countParams, current_params
    exp = OpStack.pop()
    exp_type = TypeStack.pop()
    if(current_params[countParams] == exp_type[0]):
        quad = ['parametro', exp, '', 'param' + str(countParams)]
        Quad.append(quad)
        countParams = countParams + 1


# FUNCION VOID
def p_funcion_void(t):
    '''funcion_void : check_function LPAREN lista_exp RPAREN SEMICOLON'''
    global countParams, current_params
    if(countParams == len(current_params)):
        quad = ['GOSUB', t[1], '', '']
        Quad.append(quad)
    else:
        print("Missing params or something like that")

def p_check_function(t):
    '''check_function : ID'''
    global countParams, current_params
    if t[1] in TablaFunciones:
        quad = ['ERA', t[1], '', '']
        Quad.append(quad)
        countParams = 0
        current_params = TablaFunciones[t[1]]['parametros']
    else:
        print("La funcion", t[1], "no existe")
    t[0] = t[1]

# RETORNO
def p_retorno(t):
    '''retorno : REGRESA LPAREN expresiones RPAREN SEMICOLON'''

# LECTURA
def p_lectura(t):
    '''lectura : LEE LPAREN lectura_1 RPAREN SEMICOLON'''
def p_lectura_1(t):
    '''lectura_1 : expresiones lectura_2'''
    if(len(OpStack) > 0):
        exp = OpStack.pop()
        quad = ['LEE', exp , '', '']
        Quad.append(quad)
def p_lectura_2(t):
    '''lectura_2 : COMMA lectura_1
                   | empty'''

# ESCRITURA
def p_escritura(t):
    '''escritura : ESCRIBE LPAREN escritura_1 RPAREN SEMICOLON'''
def p_escritura_1(t):
    '''escritura_1 : imprimir escritura_2'''
    
def p_escritura_2(t):
    '''escritura_2 : COMMA escritura_1 
                    | empty'''
    if(t[1] != ','):
        quad = ['ESCRITURA', '\n', '', '']
        Quad.append(quad)

def p_imprimir(t):
    '''imprimir : STRING
                  | expresiones'''
    if(len(OpStack) > 0):
        exp = OpStack.pop()
        quad = ['ESCRITURA', exp , '', '']
        Quad.append(quad)
    else:
        quad = ['ESCRITURA', t[1] , '', '']
        Quad.append(quad)
    
    
    

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
    t[0] = 0
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
    