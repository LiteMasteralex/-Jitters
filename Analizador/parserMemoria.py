# Parsing rules

# Tablas
TablaFunciones = {}
TablaVariables = {}
TablaGlobales = {}
TablaConstantes = {}

# Quadruplos
OpStack = []
OperStack = []
TypeStack = []
JumpStack = []
ForStack = []
Quad = []
DimenIdentStack = []
DimensionStack = []
DimensionNumStack = []

#Memoria
countConstantes = 0
countParams = 0

# Auxiliares
current_type = 'void'
current_function = ''
current_params = ''
has_return = False
is_global = True

def clearLocales():
    global Memoria
    Memoria['Local'] = {
        'int': 4000,
        'float': 5000,
        'char': 6000
    }

    Memoria['Temporal'] = {
        'int': 7000,
        'float': 8000,
        'char': 9000,
        'bool': 10000,
        'addr': 11000
    }



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
    global iGlobales, fGlobales, cGlobales, bGlobales
    iGlobales = 1000
    fGlobales = 2000
    cGlobales = 3000
    bGlobales = 4000

    clearLocales()

    global countConstantes
    countConstantes = 0

    # Auxiliares
    global current_type
    current_type = 'void'

def countMemoria(contexto, tipo):
    return Memoria[contexto][tipo] - (LimiteMemoria[contexto][tipo] - 1000)

def asignarMemoria(contexto, tipo, dimension):
    global Memoria, LimiteMemoria
    ubicacion = Memoria[contexto][tipo]
    size = 1
    while(dimension != None):
        size = size * dimension['sup']
        dimension = dimension['nxt']
    Memoria[contexto][tipo] = ubicacion + size
    if(ubicacion >= LimiteMemoria[contexto][tipo]):
        print("ran out of memory") #TODO: definir bein el error
        raise ParserError()
    return ubicacion, size

def defineVariable(nombre, dimension):
    global is_global, current_type
    if(is_global):
        memoria, size = asignarMemoria('Global', current_type, dimension)
        return {'name': nombre, 'loc': memoria, 'nxt': dimension, 'size': size}
    else:
        memoria, size = asignarMemoria('Local', current_type, dimension)
        return {'name': nombre, 'loc': memoria, 'nxt': dimension, 'size': size}

def obtenVariable(nombre):
    variable = ''
    if nombre in TablaVariables:
        variable = TablaVariables[nombre]
    elif nombre in TablaGlobales:
        variable = TablaGlobales[nombre]
    else:
        print("La variable ", nombre, " no esta definida")
        raise ParserError()
    return variable

def cuadruplosOperaciones():
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    oper = OperStack.pop()
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de semantica!!!! ", right_type, left_type, oper)
        raise ParserError()
    result, size = asignarMemoria('Temporal', res_type, None)
    quad = [oper, left_op, right_op, result]
    Quad.append(quad)
    OpStack.append(result)
    TypeStack.append(res_type)
# PROGRAMA
def p_programa(t):
    '''programa : PROGRAMA define_global SEMICOLON variables define_var_global funciones PRINCIPAL resolve_jump LPAREN RPAREN LCORCHETE estatuto RCORCHETE'''
    t[0] = "COMPILADO" # t[0] es lo que tiene como valor programa
    TablaFunciones[t[2]]['int'] = countMemoria('Global', 'int')
    TablaFunciones[t[2]]['float'] = countMemoria('Global', 'float')
    TablaFunciones[t[2]]['char'] = countMemoria('Global', 'char')
    TablaFunciones[t[2]]['tint'] = countMemoria('Temporal', 'int')
    TablaFunciones[t[2]]['tfloat'] = countMemoria('Temporal', 'float')
    TablaFunciones[t[2]]['tchar'] = countMemoria('Temporal', 'char')
    TablaFunciones[t[2]]['bool'] = countMemoria('Temporal', 'bool')
    TablaFunciones[t[2]]['addr'] = countMemoria('Temporal', 'addr')
    


def p_define_global(t):
    '''define_global : ID'''
    global TablaFunciones, current_function
    TablaFunciones[t[1]] = {'tipo': 'void', 'memory_size': 0}
    current_function = t[1]
    quad = ['Goto', '_', '_', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)
    t[0] = t[1]

def p_define_var_global(t):
    '''define_var_global :'''
    global TablaGlobales, TablaVariables, is_global
    TablaGlobales = TablaVariables
    TablaVariables = {}
    is_global = False

def p_resolve_jump(t):
    '''resolve_jump :'''
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)

# VARIABLES
def p_variables(t):
    '''variables : VAR tipo COLON lista_ids SEMICOLON variables_1
                | empty'''
    global TablaVariables, TablaFunciones, current_function, TablaFunciones
    if(len(t) > 2):
        size = t[6]
        for var in t[4]:
            if var['name'] not in TablaVariables:
                if var['name'] in TablaFunciones:
                    print("No pueden haber variables con nombre de funciones:", var['name'])
                    raise ParserError()
                TablaVariables[var['name']] = {'tipo': t[2], 'nxt': var['nxt'], 'loc': var['loc']}
                size = size + var['size']
            else:
                print("La variable ", var['name'], " ya esta definida")
                raise ParserError()
        TablaFunciones[current_function]['memory_size'] = TablaFunciones[current_function]['memory_size'] + size

def p_variables_1(t):
    '''variables_1 : tipo COLON lista_ids SEMICOLON variables_1
                    | empty'''
    global TablaVariables, TablaFunciones
    if(len(t) > 2):
        size = t[5]
        for var in t[3]:
            if var['name'] not in TablaVariables:
                if var['name'] in TablaFunciones:
                    print("No pueden haber variables con nombre de funciones:", var['name'])
                    raise ParserError()
                TablaVariables[var['name']] = {'tipo': t[1], 'nxt': var['nxt'], 'loc': var['loc']}
                size = size + var['size']
            else:
                print("La variable ", var['name'], " ya esta definida")
                raise ParserError()
    else:
        size = t[1]
    t[0] = size


# LISTA_IDS
def p_lista_ids(t):
    '''lista_ids : identificadores lista'''
    #Check if id is in current
    array = t[2]
    objeto = defineVariable(t[1]['name'], t[1]['nxt'])
    array.append(objeto)

    t[0] = array

def p_lista(t):
    '''lista : COMMA identificadores lista
            | empty'''
    if(t[1] == ','):
        array = t[3]
        objeto = defineVariable(t[2]['name'], t[2]['nxt'])
        array.append(objeto)

        t[0] = array
    else:
        lst = []
        t[0] = lst

# FUNCIONES
def p_funciones(t):
    '''funciones : FUNCION define_funct LPAREN parametros RPAREN SEMICOLON variables set_start LCORCHETE estatuto RCORCHETE clear_vars funciones
                | empty'''

def p_define_funct(t):
    '''define_funct : tipo_retorno ID'''
    global TablaFunciones, current_function, TablaGlobales
    if(t[2] not in TablaFunciones):
        if(t[2] in TablaGlobales):
            print("No pueden existir funciones con nombres de variables:", t[2])
            raise ParserError()
        TablaFunciones[t[2]] = {'tipo': t[1], 
                                'parametros': '', 
                                'num_parametros': 0, 
                                'memory_size': 0,
                                'num_temporales': 0,
                                'start':0}
        current_function = t[2]
    else:
        print("La funcion ", t[2], " ya esta definida")
        raise ParserError()

def p_clear_vars(t):
    '''clear_vars :'''
    global TablaVariables, TablaFunciones, current_function, has_return
    TablaVariables = {}
    quad = ['ENDPROC', '_', '_', '_']
    Quad.append(quad)
    func_type = TablaFunciones[current_function]['tipo']
    if(not has_return and func_type != 'void'):
        print("La funcion", current_function, "espera un valor de retorno de tipo", func_type, "pero ninguno fue recibido")
        raise ParserError()
    has_return = False
    TablaFunciones[current_function]['int'] = countMemoria('Local', 'int')
    TablaFunciones[current_function]['float'] = countMemoria('Local', 'float')
    TablaFunciones[current_function]['char'] = countMemoria('Local', 'char')
    TablaFunciones[current_function]['tint'] = countMemoria('Temporal', 'int')
    TablaFunciones[current_function]['tfloat'] = countMemoria('Temporal', 'float')
    TablaFunciones[current_function]['tchar'] = countMemoria('Temporal', 'char')
    TablaFunciones[current_function]['bool'] = countMemoria('Temporal', 'bool')
    TablaFunciones[current_function]['addr'] = countMemoria('Temporal', 'addr')
    clearLocales()


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
    global current_type
    current_type = t[1]
    t[0] = t[1]

#PARAMETROS
def p_parametros(t):
    '''parametros : def_parameters variables_2
                    | empty'''
    global TablaFunciones, current_function
    if(len(t) > 2):
        TablaFunciones[current_function]['num_parametros'] = t[2] + 1
        TablaFunciones[current_function]['memory_size'] = TablaFunciones[current_function]['memory_size'] + t[2] + 1
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
        raise ParserError()
    else:
        loc, size = asignarMemoria('Local', t[1], None)
        TablaVariables[t[3]] = {'loc': loc, 'tipo':t[1], 'nxt': 0}
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
    '''asignacion : ident_exp ASIGNAR expresiones SEMICOLON'''
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    res_type = Semantica[left_type][right_type]['=']
    if(res_type == 'err'):
        print('No se le puede asignar un', right_type, 'a un', left_type)
        print('Type Missmatch:','La variable no es tipo', right_type)
        raise ParserError()
    quad = ['=', left_op, right_op, '_']
    Quad.append(quad)
    t[0] = t[1]

def p_check_id(t):
    '''check_id : ID'''
    # Buscar en tablas de variables
    variable = obtenVariable(t[1])
    OpStack.append(variable['loc'])
    TypeStack.append(variable['tipo'])
    DimenIdentStack.append(t[1])
    DimensionStack.append(variable['nxt'])
    DimensionNumStack.append(0)
    t[0] = {'name': t[1], 'loc': variable['loc']}

# IDENTIFICADORES
def p_identificadores(t):
    '''identificadores : ID LBRACKET CTEI RBRACKET LBRACKET CTEI RBRACKET
                        | ID LBRACKET CTEI RBRACKET
                        | ID '''
    dimension = None
    if(len(t) > 2):
        if(t[3] < 0):
            print("Las variables dimensionadas no pueden utilizar indices negativos")
            raise ParserError()
        dimension = {
            'inf': 0,
            'sup': t[3],
            'nxt': None
        }
    if(len(t) > 5):
        if(t[3] < 0 or t[6] < 0):
            print("Las variables dimensionadas no pueden utilizar indices negativos")
            raise ParserError()
        dimension = {
            'inf': 0,
            'sup': t[3],
            'nxt': {
                'inf': 0,
                'sup': t[6],
                'nxt': None
            }
        }
    t[0] = {'name':t[1], 'nxt': dimension} 

def p_indent_exp(t):
    '''ident_exp : matriz
                    | arreglo
                    | check_id'''
    DimensionStack.pop()
    DimensionNumStack.pop()
    DimenIdentStack.pop()
    t[0] = t[1]['loc']

def p_matriz(t):
    '''matriz : check_id check_dim LBRACKET expresiones index_dim RBRACKET check_dim LBRACKET expresiones index_dim RBRACKET'''
    
    aux = OpStack.pop()
    variable = obtenVariable(DimenIdentStack[-1])
    res, size = asignarMemoria('Temporal', 'addr', None)
    quad = ['+Addr', aux, variable['loc'], res]
    Quad.append(quad)
    OpStack.append(res)
    t[0] = t[1]


def p_arreglo(t):
    '''arreglo : check_id check_dim LBRACKET expresiones index_dim RBRACKET'''
    name = DimenIdentStack[-1]
    dimension = DimensionStack[-1]
    num_dim = DimensionNumStack[-1]
    variable = obtenVariable(DimenIdentStack[-1])
    res, size = asignarMemoria('Temporal', 'addr', None)
    if(dimension != None):
        print("La variable", name, "no es de", num_dim, "dimensiones")
        raise ParserError()
    aux = OpStack.pop()
    quad = ['+Addr', aux, variable['loc'], res]
    Quad.append(quad)
    OpStack.append(res)
    t[0] = t[1]



def p_check_dim(t):
    '''check_dim :'''
    name = DimenIdentStack[-1]
    dimension = DimensionStack[-1]
    num_dim = DimensionNumStack[-1]
    if(dimension == None):
        print("La variable", name, "es de", num_dim, "dimensiones")
        raise ParserError()


def p_index_dim(t):
    '''index_dim :'''
    global DimensionStack, DimensionNumStack
    dimension = DimensionStack[-1]
    num_dim = DimensionNumStack[-1]
    tipo = TypeStack.pop()
    if(tipo != 'int'):
        print("Las variables dimensionadas solo pueden ser indexadas con valores de tipo int")
        raise ParserError()
    quad = ['verify', OpStack[-1], dimension['inf'], dimension['sup']]
    if(dimension['nxt'] != None):
        left_op = OpStack.pop()
        result, size = asignarMemoria('Temporal', 'int', None)
        quad = ['*', left_op, dimension['sup'], result]
        Quad.append(quad)
        OpStack.append(result)
    else:
        aux2, aux1 = OpStack.pop(), OpStack.pop()
        result, size = asignarMemoria('Temporal', 'int', None)
        quad = ['+', aux1, aux2, result]
        Quad.append(quad)
        OpStack.append(result)
    DimensionStack[-1] = dimension['nxt']
    DimensionNumStack[-1] = num_dim + 1


# TERMINOS
def p_terminos(t):
    '''terminos : LPAREN expresiones RPAREN 
                | ident_exp
                | var_cte 
                | funcion_retorno'''



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
    if(len(t) > 2):
        if(OperStack[-1] == '*' or OperStack[-1] == '/'):
            cuadruplosOperaciones()


def p_factores_1(t):
    '''factores_1 : TIMES 
                  | DIVIDE'''
    OperStack.append(t[1])

# ARITMETICOS
def p_aritmeticos(t):
    '''aritmeticos : factores
                    | factores aritmeticos_1 aritmeticos'''
    if(len(t) > 2):
        if(OperStack[-1] == '+' or OperStack[-1] == '-'):
            cuadruplosOperaciones()
def p_aritmeticos_1(t):
    '''aritmeticos_1 : PLUS 
                     | MINUS'''
    OperStack.append(t[1])

# LOGICOS
def p_logicos(t):
    '''logicos : aritmeticos
                    | aritmeticos logicos_1 logicos'''
    if(len(t) > 2):
        if(OperStack[-1] == '<' or OperStack[-1] == '>' or OperStack[-1] == '==' or OperStack[-1] == '!='):
            cuadruplosOperaciones()
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
    if(len(t) > 2):
        if(OperStack[-1] == '&' or OperStack[-1] == '|'):
            cuadruplosOperaciones()
def p_expresiones_1(t):
    '''expresiones_1 : AND 
                     | OR'''
    OperStack.append(t[1])

# FUNCION RETORNO
def p_funcion_retorno(t):
    '''funcion_retorno : check_function LPAREN lista_exp RPAREN'''
    global countParams, current_params, TablaVariables, TablaFunciones
    if(countParams == len(current_params)):
        quad = ['GOSUB', t[1], '_', '_']
        Quad.append(quad)
        tipo = TablaFunciones[t[1]]['tipo']
        loc, size = asignarMemoria('Local', tipo, None)
        TablaVariables[t[1]] = {'loc': loc, 'tipo': tipo, 'dimensiones': 0}
        OpStack.append(loc)
        TypeStack.append(tipo)
        
    else:
        print("La funcion", t[1], "espera", len(current_params), "parametros, pero recibio", countParams)
        raise ParserError()

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
        quad = ['parametro', exp, '_', 'param' + str(countParams)]
        Quad.append(quad)
        countParams = countParams + 1
    else:
        print("Se esperaba un parametro de tipo", current_params[countParams], "pero se recibio un tipo", exp_type)
        raise ParserError()


# FUNCION VOID
def p_funcion_void(t):
    '''funcion_void : check_function LPAREN lista_exp RPAREN SEMICOLON'''
    global countParams, current_params
    if(countParams == len(current_params)):
        quad = ['GOSUB', t[1], '_', '_']
        Quad.append(quad)
    else:
        print("La funcion", t[1], "espera", len(current_params), "parametros, pero recibio", countParams)
        raise ParserError()

def p_check_function(t):
    '''check_function : ID'''
    global countParams, current_params
    if t[1] in TablaFunciones:
        quad = ['ERA', t[1], '_', '_']
        Quad.append(quad)
        countParams = 0
        current_params = TablaFunciones[t[1]]['parametros']
    else:
        print("La funcion", t[1], "no existe")
        raise ParserError()
    t[0] = t[1]

# RETORNO
def p_retorno(t):
    '''retorno : REGRESA LPAREN expresiones RPAREN SEMICOLON'''
    global current_function, has_return
    op = OpStack.pop()
    tp = TypeStack.pop()
    func_type = TablaFunciones[current_function]['tipo']
    has_return = True
    if(tp == func_type):
        quad = ['regresa', '_', '_', op]
        Quad.append(quad)
    else:
        if(func_type == 'void'):
            print("La funcion", current_function, "es de tipo", func_type, "y no acepta valores de retorno")
            raise ParserError()
        else:
            print("La funcion", current_function, "espera un valor de tipo", func_type, "y el retorno es de tipo", tp)
            raise ParserError()


# LECTURA
def p_lectura(t):
    '''lectura : LEE LPAREN lectura_1 RPAREN SEMICOLON'''
def p_lectura_1(t):
    '''lectura_1 : valor_lectura lectura_2'''

def p_lectura_2(t):
    '''lectura_2 : COMMA lectura_1
                   | empty'''

def p_valor_lectura(t):
    '''valor_lectura : ident_exp 
                        | empty'''
    if(t[1] != 0):
        TypeStack.pop()
        exp = OpStack.pop()
        quad = ['LEE', exp , '_', '_']
        Quad.append(quad)

# ESCRITURA
def p_escritura(t):
    '''escritura : ESCRIBE LPAREN escritura_1 RPAREN SEMICOLON'''
    TypeStack.pop()
def p_escritura_1(t):
    '''escritura_1 : imprimir escritura_2'''
    
def p_escritura_2(t):
    '''escritura_2 : COMMA escritura_1 
                    | empty'''
    if(t[1] != ','):
        quad = ['ESCRITURA', 'ENDLINE', '_', '_']
        Quad.append(quad)

def p_imprimir(t):
    '''imprimir : STRING
                  | expresiones'''
    if(len(OpStack) > 0):
        exp = OpStack.pop()
        quad = ['ESCRITURA', exp , '_', '_']
        Quad.append(quad)
    else:
        quad = ['ESCRITURA', t[1] , '_', '_']
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
        raise ParserError()
    else:
        result = OpStack.pop()
        quad = ['GotoF', result, '_', '____']
        Quad.append(quad)
        JumpStack.append(len(Quad) - 1)

def p_if_else(t):
    '''if_else :'''
    jump_idx = JumpStack.pop()
    quad = ['Goto', '_', '_', '____']
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
    quad = ['Goto', '_', '_', return_]
    Quad.append(quad)
    Quad[end][-1] = len(Quad)


def p_mark_tag(t):
    '''mark_tag :'''
    JumpStack.append(len(Quad))

def p_repeticion_no_cond(t):
    '''repeticion_no_cond : DESDE iter_desde HASTA comparacion_desde HACER LCORCHETE estatuto jump_back RCORCHETE'''

def p_iter_desde(t):
    '''iter_desde : asignacion'''
    quad = ['Goto', '_', '_', '____']
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
        raise ParserError()
    result, size = asignarMemoria('Temporal', res_type, None)
    quad = [oper, left_op, right_op, result]
    #Jump
    ForStack.append(len(Quad))
    Quad.append(quad)
    quad = ['=', t[1], result, '_']
    Quad.append(quad)
    OpStack.append(t[1])
    TypeStack.append(left_type)

def p_comparacion_desde(t):
    '''comparacion_desde : expresiones'''
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    oper = '<'
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de semantica!!!!", right_type, left_type, oper)
        raise ParserError()
    result, size = asignarMemoria('Temporal', res_type, None)
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)
    quad = [oper, left_op, right_op, result]
    Quad.append(quad)
    quad = ['GotoF', result, '_', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)

def p_jump_back(t):
    '''jump_back :'''
    quad = ['Goto', '_', '_', ForStack.pop()]
    Quad.append(quad)
    jump_idx = JumpStack.pop()
    Quad[jump_idx][-1] = len(Quad)



#VAR_CTE
def p_var_cte(t):
    '''var_cte : CTECH
               | CTEI
               | CTEF'''
    global current_type #TODO: Ver si el current_type se utiliza en otro lado o es solo global
    if(isinstance(t[1], int)):
        current_type = 'int'
    elif(isinstance(t[1], str)):
        current_type = 'char'
    elif(isinstance(t[1], float)):
        current_type = 'float'
    
    if(t[1] in TablaConstantes):
        loc = TablaConstantes[t[1]]['loc']
    else:
        loc, size = asignarMemoria('CTE', current_type, None)
        TablaConstantes[t[1]] = {'loc': loc, 'tipo': current_type}
    OpStack.append(loc)
    TypeStack.append(current_type)

# EMPTY
def p_empty(t):
    '''empty :'''
    t[0] = 0
    pass

# SACADOS DE EJEMPLO CALC.PY http://www.dabeaz.com/ply/example.html

def p_error(t):
    print("Syntax error at '%s'" % t.value)
    raise ParserError()


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
            '>': 'bool', 
            '<': 'bool',
            '!=': 'bool',
            '==': 'bool',
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

Memoria = {
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

    },
    'CTE': {
        'int': 12000,
        'float': 13000,
        'char': 14000
    }
}

LimiteMemoria = {
    'Global': {
        'int': 2000,
        'float': 3000,
        'char': 4000
    },
    'Local': {
        'int': 5000,
        'float': 6000,
        'char': 7000
    },
    'Temporal': {
        'int': 8000,
        'float': 9000,
        'char': 10000,
        'bool': 11000,
        'addr': 12000,
    },
    'CTE': {
        'int': 13000,
        'float': 14000,
        'char': 15000
    }
}

class ParserError(Exception): pass

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
        try:
            result = parser.parse(data)
        except ParserError:
            result = "err"
        if result == "COMPILADO":
            print("Se compilo exitosamente.")
            orig_stdout = sys.stdout
            f = open('!jitters.out', 'w')
            sys.stdout = f
            print('>Funciones')
            for program in TablaFunciones:
                print ('p:',program)
                for var in TablaFunciones[program]:
                    print (var,' : ',TablaFunciones[program][var])
            print('>Constantes')
            for const in TablaConstantes:
                print (str(const))
                for var in TablaConstantes[const]:
                    print (var,' : ',TablaConstantes[const][var])
            print('>Quads')
            for i in range(len(Quad)):
                print(Quad[i][0], Quad[i][1], Quad[i][2], Quad[i][3])
            sys.stdout = orig_stdout
            f.close()
        clearEverything()
    except EOFError:
        print(EOFError)
    if not s: continue
    