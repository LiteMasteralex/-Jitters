>Funciones
p: myProgram
tipo  :  void
int  :  2
float  :  0
char  :  0
tint  :  1
tfloat  :  0
tchar  :  0
bool  :  0
addr  :  0
p: fibonacciPos
tipo  :  int
parametros  :  i
num_parametros  :  1
num_temporales  :  0
start  :  1
loc  :  1001
int  :  2
float  :  0
char  :  0
tint  :  5
tfloat  :  0
tchar  :  0
bool  :  3
addr  :  0
>Constantes
1
loc  :  12000
tipo  :  int
2
loc  :  12001
tipo  :  int
Hasta que número de serie fibonacci quieres?
loc  :  15000
tipo  :  str
El número en la posición
loc  :  15001
tipo  :  str
es:
loc  :  15002
tipo  :  str
>Quads
Goto _ _ 24
< 4000 12000 10000
~= 4000 12000 10001
| 10000 10001 10002
GotoF 10002 _ 6
regresa _ _ 4000
ERA fibonacciPos _ _
dim 1,1 1,1 1,1
- 4000 12000 7000
parametro 7000 _ param0
GOSUB fibonacciPos _ _
dim 1,1 1,1 _
= 7001 1001 _
ERA fibonacciPos _ _
dim 1,1 1,1 1,1
- 4000 12001 7002
parametro 7002 _ param0
GOSUB fibonacciPos _ _
dim 1,1 1,1 _
= 7003 1001 _
dim 1,1 1,1 1,1
+ 7001 7003 7004
regresa _ _ 7004
ENDPROC _ _ _
ESCRITURA 15000 _ _
ESCRITURA ENDLINE _ _
LEE 1000 _ _
ESCRITURA 15001 _ _
ESCRITURA 1000 _ _
ESCRITURA 15002 _ _
ERA fibonacciPos _ _
parametro 1000 _ param0
GOSUB fibonacciPos _ _
dim 1,1 1,1 _
= 7000 1001 _
ESCRITURA 7000 _ _
ESCRITURA ENDLINE _ _
