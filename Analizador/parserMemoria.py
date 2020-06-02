# Parsing rules

# Tablas
TablaFunciones = {}
TablaVariables = {}
TablaGlobales = {}
TablaConstantes = {}

# Quadruplos
OpStack = []
OperDimStack = []
OperStack = []
TypeStack = []
JumpStack = []
ForStack = []
Quad = []
DimenIdentStack = []
DimensionStack = []
DimensionNumStack = []

#Memoria
countParams = 0

# Auxiliares
current_type = 'void'
current_function = ''
current_params = ''
has_return = False
is_global = True
isMatrix = False

# Esta funcion regresa la memoria Local y Temporal a su estado original
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


# Esta funcion limpia todas las tablas y constantes que se usaron para asegurar que no haya nada resiudal si se quiere seguir compliando
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

    # Auxiliares
    global current_type
    current_type = 'void'

# Esta funcion regresa el numero de variables de un tipo segun el contexto
def countMemoria(contexto, tipo):
    return Memoria[contexto][tipo] - (LimiteMemoria[contexto][tipo] - 1000)

# Esta funcion le asigna a una variable la direccion donde empieza su memoria y el tamaño de esta memoria
def asignarMemoria(contexto, tipo, dimension):
    global Memoria, LimiteMemoria
    ubicacion = Memoria[contexto][tipo]
    size = 1
    while(dimension != None):
        size = size * dimension['sup']
        dimension = dimension['nxt']
    Memoria[contexto][tipo] = ubicacion + size
    if(ubicacion >= LimiteMemoria[contexto][tipo]):
        print("No hay mas espacios de tipo", tipo) #Este error no deberia de causarse en compliacion solo nos sirve a nosotros para definir los limites de memoria de cada tipo
        raise ParserError()
    return ubicacion, size

# Esta funcion regresa una nueva variable con la estructura completa que se necesita para agregarla a la Tabla de funciones
def defineVariable(nombre, dimension):
    global is_global, current_type
    if(is_global):
        memoria, size = asignarMemoria('Global', current_type, dimension)
        return {'name': nombre, 'loc': memoria, 'nxt': dimension, 'size': size}
    else:
        memoria, size = asignarMemoria('Local', current_type, dimension)
        return {'name': nombre, 'loc': memoria, 'nxt': dimension, 'size': size}

# Busca la variable en las definiciones actuales y regresa su valor
def obtenVariable(nombre, lineNo):
    variable = ''
    if nombre in TablaVariables:
        variable = TablaVariables[nombre]
    elif nombre in TablaGlobales:
        variable = TablaGlobales[nombre]
    else:
        print("La variable '{0}' no esta definida en la linea {1}".format(nombre, lineNo))
        raise ParserError()
    return variable
# Esta funcion realiza la generacion de cuadruplos para las operaciones normales en las expresiones
def cuadruplosOperaciones(lineNo):
    operNorm = ['/', '<', '>', '!=', '~=', '&', '|']
    right_op = OpStack.pop()
    right_type = TypeStack.pop()
    right_dim = OperDimStack.pop()
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    left_dim = OperDimStack.pop()
    oper = OperStack.pop()
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de Semantica en la linea {0}: la operacion '{1} {2} {3}' no esta permitida".format(lineNo, left_type, oper, right_type))
        raise ParserError()
    # Verificar que la op se pueda completar con las dims
    res_dim = semanticaDimension(oper, left_dim, right_dim)
    if(res_dim == 'err') :
        print("Error de dimensones en la linea {0}: la operacion con dim '{1}' y dim '{3}' para '{2}' no esta permitida".format(lineNo, left_dim, oper, right_dim))
        raise ParserError()
    # Genera el cuadruplo que define las dims a usar
    if(oper not in operNorm) :
        str_left_dim = str(left_dim[0]) + ',' + str(left_dim[1])
        str_right_dim = str(right_dim[0]) + ',' + str(right_dim[1])
        str_res_dim = str(res_dim[0]) + ',' + str(res_dim[1])
        quad = ['dim', str_left_dim, str_right_dim, str_res_dim]
        Quad.append(quad)
    if(oper == '=') :
        result = '_'
    else :
        dimension = obtenDim(res_dim[0], res_dim[1])
        result, size = asignarMemoria('Temporal', res_type, dimension)
        TypeStack.append(res_type)
        OperDimStack.append(res_dim)
        OpStack.append(result)
    quad = [oper, left_op, right_op, result]
    Quad.append(quad)

# Esta funcion realiza la generacion de cuadruplos para las operaciones normales en las expresiones
def cuadruplosEspeciales(lineNo):
    left_op = OpStack.pop()
    left_type = TypeStack.pop()
    left_dim = OperDimStack.pop()
    oper = OperStack.pop()
    res_type = Semantica[left_type][oper]
    if(res_type == 'err'):
        print("Error de Semantica en la linea {0}: la operacion '{1} {2}' no esta permitida".format(lineNo, left_type, oper))
        raise ParserError()
    # Verificar que la op se pueda completar con las dims
    res_dim = semanticaDimension(oper, left_dim, [1, 1])
    if(res_dim == 'err') :
        print("Error de dimensones en la linea {0}: la operacion con dim '{1}' para '{2}' no esta permitida".format(lineNo, left_dim, oper))
        raise ParserError()
    # Genera el cuadruplo que define las dims a usar
    str_left_dim = str(left_dim[0]) + ',' + str(left_dim[1])
    str_res_dim = str(res_dim[0]) + ',' + str(res_dim[1])
    quad = ['dim', str_left_dim, '_', str_res_dim]
    Quad.append(quad)
    dimension = obtenDim(res_dim[0], res_dim[1])
    result, size = asignarMemoria('Temporal', res_type, dimension)
    TypeStack.append(res_type)
    OperDimStack.append(res_dim)
    OpStack.append(result)
    quad = [oper, left_op, '_', result]
    Quad.append(quad)    
    

def obtenDim(x, y) : 
    dim1 = {'inf' : 0, 'sup': x, 'nxt': None}
    dim2 = {'inf' : 0, 'sup': y, 'nxt': dim1}
    return dim2
    

def semanticaDimension(op, dim1, dim2):
    if(op == '+' or op == '-'):
        if(dim1[0] == dim2[0] and dim1[1] == dim2[1]) :
            return dim1
        elif(dim2[0] == dim2[1] == 1) :
            return dim1
    elif(op == '*'):
        if(dim1[1] == dim2[0]) :
            return [dim1[0], dim2[1]]
        elif(dim2[0] == dim2[1] == 1):
            return dim1
    elif(op == '='):
        if(dim1[0] == dim2[0] and dim1[1] == dim2[1]) :
            return dim1
    elif(op == '$'):
        if(dim1[0] == dim1[1]):
            return dim2
    elif(op == '?'):
        if(dim1[0] == dim1[1]):
            return dim1
    elif(op == '¡'):
        return [dim1[1], dim1[0]]
    elif(dim1 == dim2 == [1, 1]) :
        return dim1
    return ('err')

# Aqui inician las reglas gramaticales que se usan en el parser
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
    TablaFunciones[t[1]] = {'tipo': 'void'}
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
    global TablaVariables, TablaFunciones, TablaFunciones
    if(len(t) > 2):
        size = t[6]
        for var in t[4]:
            if var['name'] not in TablaVariables:
                if var['name'] in TablaFunciones:
                    print("La variable '{0}' no puede tener el nombre de una fucion en la linea {1}".format(var['name'], t.lineno(3)))
                    raise ParserError()
                TablaVariables[var['name']] = {'tipo': t[2], 'nxt': var['nxt'], 'loc': var['loc']}
                size = size + var['size']
            else:
                print("La variable '{0}' ya esta defnida en la linea {1}".format(var['name'], t.lineno(4)))
                raise ParserError()

def p_variables_1(t):
    '''variables_1 : tipo COLON lista_ids SEMICOLON variables_1
                    | empty'''
    global TablaVariables, TablaFunciones
    if(len(t) > 2):
        size = t[5]
        for var in t[3]:
            if var['name'] not in TablaVariables:
                if var['name'] in TablaFunciones:
                    print("La variable '{0}' no puede tener el nombre de una fucion en la linea {1}".format(var['name'], t.lineno(3)))
                    raise ParserError()
                TablaVariables[var['name']] = {'tipo': t[1], 'nxt': var['nxt'], 'loc': var['loc']}
                size = size + var['size']
            else:
                print("La variable '{0}' ya esta defnida en la linea {1}".format(var['name'], t.lineno(3)))
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
    global TablaFunciones, current_function, TablaGlobales, is_global, current_type
    if(t[2] not in TablaFunciones):
        if(t[2] in TablaGlobales):
            print("La funcion '{0}' no puede tener el nombre de una variable en la linea {1}".format(t[2], t.lineno(2)))
            raise ParserError()
        TablaFunciones[t[2]] = {'tipo': t[1], 
                                'parametros': '', 
                                'num_parametros': 0, 
                                'num_temporales': 0,
                                'start':0}
        current_function = t[2]
        if(t[1] != 'void'):
            is_global = True
            current_type = t[1]
            variable = defineVariable(t[2], None)
            TablaGlobales[t[2]] = variable
            is_global = False
            TablaFunciones[t[2]]['loc'] = variable['loc']

    else:
        print("La funcion '{0}' ya esta definida en la linea {1}".format(t[2], t.lineno(2)))
        raise ParserError()

def p_clear_vars(t):
    '''clear_vars :'''
    global TablaVariables, TablaFunciones, current_function, has_return
    TablaVariables = {}
    quad = ['ENDPROC', '_', '_', '_']
    Quad.append(quad)
    func_type = TablaFunciones[current_function]['tipo']
    if(not has_return and func_type != 'void'):
        print("La funcion '{0}' espera un valor de retorno de tipo '{1}' pero ninguno fue recibido".format(current_function, func_type))
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
        print("La variable '{0}' ya esta definida en la linea {1}".format(t[3], t.lineno(3)))
        raise ParserError()
    else:
        loc, size = asignarMemoria('Local', t[1], None)
        TablaVariables[t[3]] = {'loc': loc, 'tipo':t[1], 'nxt': None}
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
    OperStack.append(t[2])
    cuadruplosOperaciones(t.lineno(1))
    t[0] = t[1]

def p_check_id(t):
    '''check_id : ID'''
    # Buscar en tablas de variables
    variable = obtenVariable(t[1], t.lineno(1))
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
            print("Error de indexamiento en la linea {0}: Los indices no pueden ser negativos".format(t.lineno(1)))
            raise ParserError()
        dimension = {
            'inf': 0,
            'sup': t[3],
            'off': 0,
            'nxt': None
        }
    if(len(t) > 5):
        if(t[3] < 0 or t[6] < 0):
            print("Error de indexamiento en la linea {0}: Los indices no pueden ser negativos".format(t.lineno(1)))
            raise ParserError()
        dimension = {
            'inf': 0,
            'sup': t[3],
            'off': t[6],
            'nxt': {
                'inf': 0,
                'sup': t[6],
                'off': 0,
                'nxt': None
            }
        }
    t[0] = {'name':t[1], 'nxt': dimension} 

def p_ident_exp(t):
    '''ident_exp : matriz
                    | arreglo
                    | check_id'''
    global isMatrix
    x = 1
    y = 1
    DimenIdentStack.pop()
    dimension = DimensionStack.pop()
    DimensionNumStack.pop()
    if(dimension != None):
        x = dimension['sup']
        # Obtener dimension del operador
        if(dimension['nxt'] != None):
            y = dimension['nxt']['sup']
    OperDimStack.append([x,y])
    t[0] = t[1]['loc']

def p_matriz(t):
    '''matriz :  check_id es_dim check_dim LBRACKET expresiones index_dim RBRACKET check_dim  LBRACKET expresiones index_dim RBRACKET off_set_dir'''
    t[0] = t[1]

def p_arreglo(t):
    '''arreglo : check_id es_dim check_dim LBRACKET expresiones index_dim RBRACKET off_set_dir'''
    t[0] = t[1]

def p_es_dim(t):
    '''es_dim : '''
    OpStack.pop()

def p_off_set_dir(t):
    '''off_set_dir : '''
    aux = OpStack.pop()
    variable = obtenVariable(DimenIdentStack[-1], t.lineno)
    res, size = asignarMemoria('Temporal', 'addr', None)
    quad = ['+Addr', aux, variable['loc'], res]
    Quad.append(quad)
    OpStack.append(res)



def p_check_dim(t):
    '''check_dim :'''
    name = DimenIdentStack[-1]
    dimension = DimensionStack[-1]
    num_dim = DimensionNumStack[-1]
    if(dimension == None):
        print("La variable '{0}' es de {1} dimensiones en la linea {2}".format(name, num_dim, t.lineno(0)))
        raise ParserError()


def p_index_dim(t):
    '''index_dim :'''
    global DimensionStack, DimensionNumStack, isMatrix
    dimension = DimensionStack[-1]
    num_dim = DimensionNumStack[-1]
    tipo = TypeStack.pop()
    if(tipo != 'int'):
        print("Error de indexamiento en la linea {0}: solo se puede indexar con valores de tipo int".format(t.lineno(0)))
        raise ParserError()
    if(dimension['inf'] in TablaConstantes):
        locInf = TablaConstantes[dimension['inf']]['loc']
    else:
        locInf, size = asignarMemoria('CTE', current_type, None)
        TablaConstantes[dimension['inf']] = {'loc': locInf, 'tipo': current_type}
    if(dimension['sup'] in TablaConstantes):
        locSup = TablaConstantes[dimension['sup']]['loc']
    else:
        locSup, size = asignarMemoria('CTE', current_type, None)
        TablaConstantes[dimension['sup']] = {'loc': locSup, 'tipo': current_type}
    quad = ['VER', OpStack[-1], locInf, locSup]
    Quad.append(quad)
    if(dimension['nxt'] != None):
        left_op = OpStack.pop()
        result, size = asignarMemoria('Temporal', 'int', None)
        if(dimension['off'] in TablaConstantes):
            off = TablaConstantes[dimension['off']]['loc']
        else:
            off, size = asignarMemoria('CTE', current_type, None)
            TablaConstantes[dimension['off']] = {'loc': off, 'tipo': current_type}
        quad = ['dim', '1,1', '1,1', '1,1']
        Quad.append(quad)
        quad = ['*', left_op, off, result]
        Quad.append(quad)
        OpStack.append(result)
        isMatrix = True
    elif(isMatrix):
        aux2, aux1 = OpStack.pop(), OpStack.pop()
        result, size = asignarMemoria('Temporal', 'int', None)
        quad = ['dim', '1,1', '1,1', '1,1']
        Quad.append(quad)
        quad = ['+', aux1, aux2, result]
        Quad.append(quad)
        OpStack.append(result)
        isMatrix = False
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
    if(len(t) > 2):
        if(OperStack[-1] == '$' or OperStack[-1] == '¡' or OperStack[-1] == '?'):
            cuadruplosEspeciales(t.lineno(1))

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
            cuadruplosOperaciones(t.lineno(1))


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
            cuadruplosOperaciones(t.lineno(1))
def p_aritmeticos_1(t):
    '''aritmeticos_1 : PLUS 
                     | MINUS'''
    OperStack.append(t[1])

# LOGICOS
def p_logicos(t):
    '''logicos : aritmeticos
                    | aritmeticos logicos_1 logicos'''
    if(len(t) > 2):
        if(OperStack[-1] == '<' or OperStack[-1] == '>' or OperStack[-1] == '~=' or OperStack[-1] == '!='):
            cuadruplosOperaciones(t.lineno(1))
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
            cuadruplosOperaciones(t.lineno(1))
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
        loc = TablaFunciones[t[1]]['loc']
        locTemp, size = asignarMemoria('Temporal', tipo, None)
        quad = ['dim', '1,1', '1,1', '_']
        quad.append(quad)
        quad = ['=', locTemp, loc, '_']
        Quad.append(quad)
        OpStack.append(locTemp)
        TypeStack.append(tipo)
        
    else:
        print("La funcion '{0}' espera {1} parametros, pero recibio {2} en la linea {3}".format(t[1], len(current_params), countParams, t.lineno(3)))
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
        if(current_params[countParams] == 'i'):
            tipo = 'int'
        elif(current_params[countParams] == 'f'):
            tipo = 'float'
        else:
            tipo = 'char'
        print("Se esperaba un parametro de tipo '{0}' pero se recibio un tipo '{1}' en la linea {2}".format(tipo, exp_type, t.lineno(1)))
        raise ParserError()


# FUNCION VOID
def p_funcion_void(t):
    '''funcion_void : check_function LPAREN lista_exp RPAREN SEMICOLON'''
    global countParams, current_params
    if(countParams == len(current_params)):
        quad = ['GOSUB', t[1], '_', '_']
        Quad.append(quad)
    else:
        print("La funcion '{0}' espera {1} parametros, pero recibio {2} en la linea {3}".format(t[1], len(current_params), countParams, t.lineno(3)))
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
        print("La funcion '{0}' no existe en la linea {1}".format(t[1], t.lineno(1)))
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
            print("La funcion '{0}' es de tipo '{1}' y no acepta valores de retorno en la linea {2}".format(current_function, func_type, t.lineno(1)))
            raise ParserError()
        else:
            print("La funcion '{0}' espera un valor de tipo '{1}' y el retorno es de tipo '{2}' en la linea {3}".format(current_function, func_type, tp, t.lineno(1)))
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
        dim = OperDimStack.pop()
        if(dim != [1, 1]):
            print("No se pueden leer variables dimensionadas en la linea {0}".format(t.lineno(1)))
            raise ParserError
        quad = ['LEE', exp , '_', '_']
        Quad.append(quad)

# ESCRITURA
def p_escritura(t):
    '''escritura : ESCRIBE LPAREN escritura_1 RPAREN SEMICOLON'''
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
    if(t[1] == None):
        exp = OpStack.pop()
        dim = OperDimStack.pop()
        if(dim != [1, 1]):
            print("No se puede imprimir variables dimensionadas en la linea {0}".format(t.lineno(1)))
            raise ParserError
        TypeStack.pop()
        quad = ['ESCRITURA', exp , '_', '_']
        Quad.append(quad)
    else:
        string = t[1].replace('"', '')
        if(string in TablaConstantes):
            loc = TablaConstantes[string]['loc']
        else:
            loc, size = asignarMemoria('CTE', 'str', None)
            TablaConstantes[string] = {'loc': loc, 'tipo': 'str'}
        quad = ['ESCRITURA', loc , '_', '_']
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
        print("La expresion condicional necesita ser de tipo 'bool' pero es de tipo '{0}' en la linea {1}".format(exp_type, t.lineno(0)))
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
    if(Quad[-2][1] != '1,1') :
        print(Quad[-2])
        print("Error de iteracion en linea {0}: solo se puede iterar sobre valores no dimensionados".format(t.lineno(1)))
        raise ParserError()
    quad = ['Goto', '_', '_', '____']
    Quad.append(quad)
    JumpStack.append(len(Quad) - 1)
    left_op = t[1]
    left_type = current_type
    if(1 in TablaConstantes):
        loc = TablaConstantes[1]['loc']
    else:
        loc, size = asignarMemoria('CTE', current_type, None)
        TablaConstantes[1] = {'loc': loc, 'tipo': current_type}
    right_op = loc
    right_type = 'int'
    oper = '+'
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("La variable de control debe ser de tipo 'int' pero es de tipo '{0}' en la linea {1}".format(right_type, t.lineno(1)))
        raise ParserError()
    result, size = asignarMemoria('Temporal', res_type, None)
    #Jump
    ForStack.append(len(Quad))
    quad = ['dim', '1,1', '1,1', '1,1']
    Quad.append(quad)
    quad = [oper, left_op, right_op, result]
    Quad.append(quad)
    quad = ['dim', '1,1', '1,1', '_']
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
    oper = '>'
    res_type = Semantica[right_type][left_type][oper]
    if(res_type == 'err'):
        print("Error de Semantica en la linea {0}: la operacion '{1} {2} {3}' no esta permitida".format(t.lineno(1), right_type, oper, left_type))
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
    OperDimStack.append([1,1])

# EMPTY
def p_empty(t):
    '''empty :'''
    t[0] = 0
    pass

# SACADOS DE EJEMPLO CALC.PY http://www.dabeaz.com/ply/example.html

def p_error(t):
    print("Error de syntaxis en la linea {0}: valor no esperado '{1}'".format(t.lineno, t.value) )
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
            '~=': 'bool',
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
            '~=': 'bool',
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
            '~=': 'err',
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
            '~=': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        '$': 'float',
        '?': 'int',
        '¡': 'int'
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
            '~=': 'bool',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        'float': {
            '+': 'float',
            '-': 'float',
            '*': 'float',
            '/': 'float',
            '>': 'bool', 
            '<': 'bool',
            '!=': 'bool',
            '~=': 'bool',
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
            '~=': 'err',
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
            '~=': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        '$': 'float',
        '?': 'float',
        '¡': 'float'
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
            '~=': 'err',
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
            '~=': 'err',
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
            '~=': 'bool',
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
            '~=': 'err',
            '&': 'err',
            '|': 'err',
            '=': 'err'
        },
        '$': 'err',
        '?': 'char',
        '¡': 'char'
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
            '~=': 'err',
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
            '~=': 'err',
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
            '~=': 'err',
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
            '~=': 'bool',
            '&': 'bool',
            '|': 'bool',
            '=': 'bool'
        },
        '$': 'err',
        '?': 'err',
        '¡': 'err'
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
        'char': 14000,
        'str': 15000
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
        'char': 15000,
        'str': 16000
    }
}

class ParserError(Exception): pass

import sys
import ply.yacc as yacc

from lexer import tokens

parser = yacc.yacc()

if __name__ == '__main__':

    if len(sys.argv) == 2:
        file = str(sys.argv[1])
        try:
            f = open(file, 'r', encoding='utf-8')
            data = f.read()
            f.close()
            try:
                result = parser.parse(data, tracking=True)
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
    elif len(sys.argv) < 2:
        print("No se ingreso el archivo a compilar")
    else :
        print("Se ingresaron argumentos no solicitados")
            
    