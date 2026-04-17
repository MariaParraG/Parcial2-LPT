// Gramática ANTLR4 para lenguaje de consultas NoSQL (estilo MongoDB)
// Soporta operaciones CRUD: CREATE, READ (FIND), UPDATE, DELETE
// Autor: Parcial 2 - Lenguajes de Programación

grammar NoSQLCRUD;

// ==================== REGLAS DEL PARSER ====================

program
    : statement+ EOF
    ;

statement
    : createStatement SEMICOLON
    | insertStatement SEMICOLON
    | findStatement SEMICOLON
    | updateStatement SEMICOLON
    | deleteStatement SEMICOLON
    | dropStatement SEMICOLON
    ;

// ---- CREATE (crear colección) ----
createStatement
    : CREATE COLLECTION IDENTIFIER
    ;

// ---- INSERT (insertar documento) ----
insertStatement
    : INSERT INTO IDENTIFIER VALUES document
    | INSERT INTO IDENTIFIER VALUES LBRACKET documentList RBRACKET
    ;

// ---- FIND (leer / consultar) ----
findStatement
    : FIND FROM IDENTIFIER
    | FIND FROM IDENTIFIER WHERE filterExpr
    | FIND FROM IDENTIFIER WHERE filterExpr LIMIT NUMBER
    | FIND FROM IDENTIFIER WHERE filterExpr SORT BY IDENTIFIER order
    | FIND FROM IDENTIFIER SORT BY IDENTIFIER order
    | FIND FROM IDENTIFIER LIMIT NUMBER
    ;

order
    : ASC
    | DESC
    ;

// ---- UPDATE (actualizar) ----
updateStatement
    : UPDATE IDENTIFIER SET setExprList
    | UPDATE IDENTIFIER SET setExprList WHERE filterExpr
    ;

setExprList
    : setExpr (COMMA setExpr)*
    ;

setExpr
    : IDENTIFIER ASSIGN value
    ;

// ---- DELETE (eliminar) ----
deleteStatement
    : DELETE FROM IDENTIFIER
    | DELETE FROM IDENTIFIER WHERE filterExpr
    ;

// ---- DROP (eliminar colección) ----
dropStatement
    : DROP COLLECTION IDENTIFIER
    ;

// ---- Filtros / condiciones ----
filterExpr
    : filterExpr AND filterExpr
    | filterExpr OR filterExpr
    | NOT filterExpr
    | LPAREN filterExpr RPAREN
    | condition
    ;

condition
    : IDENTIFIER comparator value
    | IDENTIFIER IN LBRACKET valueList RBRACKET
    | IDENTIFIER EXISTS
    ;

comparator
    : EQ | NEQ | LT | LE | GT | GE
    ;

// ---- Documentos JSON ----
document
    : LBRACE fieldList RBRACE
    | LBRACE RBRACE
    ;

fieldList
    : field (COMMA field)*
    ;

field
    : STRING COLON value
    ;

documentList
    : document (COMMA document)*
    ;

value
    : NUMBER
    | STRING
    | BOOLEAN
    | NULL
    | document
    | LBRACKET valueList RBRACKET
    ;

valueList
    : value (COMMA value)*
    ;

// ==================== REGLAS DEL LEXER ====================

// Palabras clave
CREATE      : 'CREATE' | 'create' ;
INSERT      : 'INSERT' | 'insert' ;
FIND        : 'FIND'   | 'find'   ;
UPDATE      : 'UPDATE' | 'update' ;
DELETE      : 'DELETE' | 'delete' ;
DROP        : 'DROP'   | 'drop'   ;
COLLECTION  : 'COLLECTION' | 'collection' ;
INTO        : 'INTO'   | 'into'   ;
FROM        : 'FROM'   | 'from'   ;
VALUES      : 'VALUES' | 'values' ;
WHERE       : 'WHERE'  | 'where'  ;
SET         : 'SET'    | 'set'    ;
AND         : 'AND'    | 'and'    ;
OR          : 'OR'     | 'or'     ;
NOT         : 'NOT'    | 'not'    ;
IN          : 'IN'     | 'in'     ;
EXISTS      : 'EXISTS' | 'exists' ;
LIMIT       : 'LIMIT'  | 'limit'  ;
SORT        : 'SORT'   | 'sort'   ;
BY          : 'BY'     | 'by'     ;
ASC         : 'ASC'    | 'asc'    ;
DESC        : 'DESC'   | 'desc'   ;
BOOLEAN     : 'true' | 'false' | 'TRUE' | 'FALSE' ;
NULL        : 'null' | 'NULL'  ;

// Operadores de comparación
EQ   : '==' ;
NEQ  : '!=' ;
LE   : '<=' ;
GE   : '>=' ;
LT   : '<'  ;
GT   : '>'  ;
ASSIGN : '=' ;

// Símbolos
LBRACE    : '{' ;
RBRACE    : '}' ;
LBRACKET  : '[' ;
RBRACKET  : ']' ;
LPAREN    : '(' ;
RPAREN    : ')' ;
SEMICOLON : ';' ;
COMMA     : ',' ;
COLON     : ':' ;

// Literales
NUMBER     : '-'? [0-9]+ ('.' [0-9]+)? ;
STRING     : '"' (~["\r\n])* '"' | '\'' (~['\r\n])* '\'' ;
IDENTIFIER : [a-zA-Z_][a-zA-Z0-9_]* ;

// Ignorar espacios y comentarios
WS         : [ \t\r\n]+ -> skip ;
COMMENT    : '//' ~[\r\n]* -> skip ;
MCOMMENT   : '/*' .*? '*/' -> skip ;
