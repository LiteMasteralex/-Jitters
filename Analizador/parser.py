# Parsing rules

# Tablas
TablaVariables = {}
TablaFunciones = {}
current_type = 'void'

# PROGRAMA
def p_programa(t):
    '''programa : PROGRAMA ID SEMICOLON variables funciones PRINCIPAL LPAREN RPAREN LCORCHETE estatuto RCORCHETE'''
    t[0] = "COMPILADO" # t[0] es lo que tiene como valor programa
    TablaFunciones[t[2]] = {'tipo': current_type, 'variables': ''}

# VARIABLES
def p_variables(t):
    '''variables : VAR tipo COLON lista_ids SEMICOLON variables_1
                | empty'''
def p_variables_1(t):
    '''variables_1 : tipo COLON lista_ids SEMICOLON variables_1
                    | empty'''

# LISTA_IDS
def p_lista_ids(t):
    '''lista_ids : identificadores lista'''

def p_lista(t):
    '''lista : COMMA identificadores lista
            | empty'''

# FUNCIONES
def p_funciones(t):
    '''funciones : FUNCION tipo_retorno ID LPAREN parametros RPAREN SEMICOLON variables LCORCHETE estatuto RCORCHETE funciones
                | empty'''
    if(t[1] == 'funcion'):
        TablaFunciones[t[3]] = {'tipo': t[2], 'variables': ''}

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
    '''asignacion : identificadores ASIGNAR expresiones SEMICOLON'''

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
    TablaVariables[t[1]] = {'tipo': current_type, 'dimension': dimension}

# TERMINOS
def p_terminos(t):
    '''terminos : LPAREN expresiones RPAREN 
                | identificadores
                | var_cte 
                | funcion_retorno'''


# ESPECIALES
def p_especiales(t):
    '''especiales : terminos
                    | terminos especiales_1'''
def p_especiales_1(t):
    '''especiales_1 : DETERMINANTE
                    | TRANSPUESTA
                    | INVERSA'''

# FACTORES
def p_factores(t):
    '''factores : especiales
                | especiales factores_1 factores'''
def p_factores_1(t):
    '''factores_1 : TIMES 
                  | DIVIDE'''

# ARITMETICOS
def p_aritmeticos(t):
    '''aritmeticos : factores
                    | factores aritmeticos_1 aritmeticos'''
def p_aritmeticos_1(t):
    '''aritmeticos_1 : PLUS 
                     | MINUS'''

# LOGICOS
def p_logicos(t):
    '''logicos : aritmeticos
                    | aritmeticos logicos_1 logicos'''
def p_logicos_1(t):
    '''logicos_1 : LESS 
                    | GREATER
                    | EQUALS
                    | NOTEQUAL'''

# EXPRESIONES
def p_expresiones(t):
    '''expresiones : logicos
                    | logicos expresiones_1 expresiones'''
def p_expresiones_1(t):
    '''expresiones_1 : AND 
                     | OR'''

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
    '''decision : SI LPAREN expresiones RPAREN ENTONCES LCORCHETE estatuto RCORCHETE decision_1'''
def p_decision_1(t):
    '''decision_1 : SINO LCORCHETE estatuto RCORCHETE
                    | empty'''

# REPETICION
def p_repeticion(t):
    '''repeticion : repeticion_cond 
                  | repeticion_no_cond'''
def p_repeticion_cond(t):
    '''repeticion_cond : MIENTRAS LPAREN expresiones RPAREN HAZ LCORCHETE estatuto RCORCHETE'''
def p_repeticion_no_cond(t):
    '''repeticion_no_cond : DESDE asignacion HASTA expresiones HACER LCORCHETE estatuto RCORCHETE'''

#VAR_CTE
def p_var_cte(t):
    '''var_cte : CTECH
               | CTEI
               | CTEF'''

# EMPTY
def p_empty(t):
    '''empty :'''
    pass

# SACADOS DE EJEMPLO CALC.PY http://www.dabeaz.com/ply/example.html

def p_error(t):
    print("Syntax error at '%s'" % t.value)


import sys
import ply.yacc as yacc

from lexer import tokens

parser = yacc.yacc()

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
            print(TablaFunciones)
            print(TablaVariables)
    except EOFError:
        print(EOFError)
    if not s: continue
    