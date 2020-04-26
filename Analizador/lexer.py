
# -----------------------------------------------------------------------------
# tarea.py
# Primer compilador usando gramatica de tarea 3 
# Referencias:
# https://www.dabeaz.com/ply/ply.html  
# http://www.dabeaz.com/ply/example.html
# -----------------------------------------------------------------------------
import ply.lex as lex

# Palabras reservadas
reserved = {
    'Programa': 'PROGRAMA',
    'funcion': 'FUNCION',
    'principal': 'PRINCIPAL',
    'var': 'VAR',
    'si': 'SI',
    'sino': 'SINO',
    'entonces': 'ENTONCES',
    'regresa': 'REGRESA',
    'desde': 'DESDE',
    'mientras': 'MIENTRAS',
    'haz': 'HAZ',
    'hasta': 'HASTA',
    'hacer': 'HACER',
    'escribe': 'ESCRIBE',
    'lee': 'LEE',
    'int': 'INT',
    'float': 'FLOAT',
    'char': 'CHAR',
    'void': 'VOID',
}

# Tokens
tokens = (
    'PROGRAMA', 'FUNCION', 'PRINCIPAL', 'VAR', #reservadas
    'SI', 'SINO', 'ENTONCES', 'REGRESA', 'DESDE', 'MIENTRAS','HAZ', 'HASTA', 'HACER', # para ciclos for, while, if else 
    'ESCRIBE', 'LEE', # funciones internas (print, read)
    'INT', 'FLOAT', 'CHAR', 'VOID', # relacionado con var y tipos de retorno
    'SEMICOLON', 'LCORCHETE', 'RCORCHETE', 'LPAREN', 'RPAREN', 'COLON', 'COMMA', 'LBRACKET', 'RBRACKET', # Generan orden
    'DETERMINANTE', 'TRANSPUESTA', 'INVERSA', # operadores especiales
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASIGNAR', # operadores normales?
    'GREATER', 'LESS', 'EQUALS', 'NOTEQUAL', 'AND', 'OR', # operadores logicos 
    'ID', 'CTEF', 'CTEI','CTECH', 'STRING'
    )

# Expresiones regulares

t_SEMICOLON = r'\;'
t_LCORCHETE = r'\{'
t_RCORCHETE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\[' #
t_RBRACKET = r'\]' #
t_COLON = r':'
t_COMMA = r'\,'
t_DETERMINANTE = r'\$' #
t_TRANSPUESTA = r'\¡' #
t_INVERSA = r'\?' #
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'\/'
t_ASIGNAR = r'\='
t_GREATER = r'>'
t_LESS = r'<'
t_EQUALS = r'==' #
t_NOTEQUAL = r'!=' #
t_AND = r'[&]' #
t_OR = r'[|]' #
t_STRING = r'\"[ -~]*\"'


# Define a ID
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# Define una variable float 
def t_CTEF(t):
    r'[0-9]+(.[0-9]+)*'
    t.value = float(t.value)
    return t


# Define una variable int
def t_CTEI(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Define una variable char
def t_CTECH(t):
    r"\'[A-Za-z]\'"
    t.value = t.value[1]
    return t

# Ignored characters
t_ignore = " \t"

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    
def t_error(t):
    print("Error Lexico ' {0} ' encontrado en linea ' {1} ' ".format(t.value[0], t.lineno))
    t.lexer.skip(1)

def t_comment(t):
    r'\#.*'
    pass

    
# Build the lexer
lexer = lex.lex()