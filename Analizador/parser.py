# Parsing rules

# PROGRAMA
def p_programa(t):
    '''programa : PROGRAMA ID SEMICOLON variables funciones PRINCIPAL LPAREN RPAREN LCORCHETE estatuto RCORCHETE'''
    t[0] = "COMPILADO" # t[0] es lo que tiene como valor programa

# VARIABLES
def p_variables(t):
    '''variables : VAR tipo : lista_ids SEMICOLON variables_1
                | empty'''
def p_variables_1(t):
    '''variables_1 : tipo : lista_ids SEMICOLON variables_1
                    | empty'''
                    
# LISTA_IDS
def p_lista_ids(t):
    '''lista_ids : identificadores lista'''

def p_lista(t):
    '''lista : COMMA identificadores lista
            | empty'''

# FUNCIONES

# TIPO_RETORNO

# TIPO

#PARAMETROS

#ESTATUTO

#ASIGNACION

# IDENTIFICADORES
def p_identificadores(t):
    '''identificadores : ID LBRACKET CTEI RBRACKET LBRACKET CTEI RBRACKET
                        | ID LBRACKET CTEI RBRACKET
                        | ID '''

# TERMINOS


# ESPECIALES

# FACTORES

# ARITMETICOS

# LOGICOS

# EXPRESIONES

# FUNCION RETORNO

# FUNCION VOID

# RETORNO

# LECTURA

# ESCRITURA

# DECISION

# REPETICION

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
        s = input('!Jitters > ') # raw_input para py2
        file = s
        f = open(file, 'r')
        data = f.read()
        f.close()
        if parser.parse(data) == "ACEPTADO":
            print("ACEPTADO")
    except EOFError:
        print(EOFError)
    if not s: continue
    