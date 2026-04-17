# Punto 2 – Implementación del Parser NoSQL con PLY (YACC/BISON en Python)

## Descripción

Se implementó la gramática del Punto 1 usando **PLY** (Python Lex-Yacc),
que es el equivalente Python de **BISON + LEX**. PLY usa las mismas
técnicas de análisis LALR(1) que YACC/BISON, pero en Python.

El parser incluye:
- **Lexer** (analizador léxico) — equivalente a LEX/FLEX
- **Parser** (analizador sintáctico) — equivalente a YACC/BISON
- **Motor de ejecución** — simula una base de datos NoSQL en memoria

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `nosql_parser.py` | Implementación completa: lexer + parser + motor |

---

## Requisitos

```bash
pip install ply
```

---

## Ejecución

```bash
python3 nosql_parser.py
```

---

## Resultados de las Pruebas

Todas las pruebas pasaron exitosamente:

| # | Test | Resultado |
|---|------|-----------|
| 1 | Crear colección | ✅ Colección creada |
| 2 | Insertar documentos (x3) | ✅ 3 docs insertados |
| 3 | FIND sin filtro | ✅ 3 resultados |
| 4 | FIND con filtro `edad >= 18 AND activo == true` | ✅ 1 resultado (Ana) |
| 5 | FIND con LIMIT | ✅ 2 resultados |
| 6 | FIND con SORT BY nombre ASC | ✅ Ordenado correctamente |
| 7 | UPDATE `activo = false WHERE edad < 18` | ✅ 1 doc actualizado (Luis) |
| 8 | Verificar UPDATE | ✅ 2 docs con activo=false |
| 9 | DELETE WHERE `activo == false` | ✅ 2 docs eliminados |
| 10 | Verificar DELETE | ✅ 1 doc restante (Ana) |
| 11 | Inserción múltiple con arreglo `[{},{}]` | ✅ 2 docs insertados |
| 12 | DROP COLLECTION | ✅ Colección eliminada |
| 13 | FIND en colección inexistente | ✅ Error controlado |

---

## Arquitectura

```
Código fuente NoSQL
        ↓
   [LEXER - PLY lex]
   Tokenización
        ↓
   [PARSER - PLY yacc]
   Árbol de análisis (AST en tuplas Python)
        ↓
   [MOTOR NoSQLEngine]
   Ejecución sobre diccionarios en memoria
```

### Tokens del Lexer

El lexer reconoce:
- **Palabras clave**: `CREATE`, `INSERT`, `FIND`, `UPDATE`, `DELETE`, `DROP`, `WHERE`, `AND`, `OR`, `NOT`, `IN`, `EXISTS`, `LIMIT`, `SORT`, `BY`, `ASC`, `DESC`
- **Operadores**: `==`, `!=`, `<`, `<=`, `>`, `>=`, `=`
- **Delimitadores**: `{`, `}`, `[`, `]`, `(`, `)`, `;`, `,`, `:`
- **Literales**: números, cadenas (con comillas simples o dobles), booleanos, null
- **Identificadores**: `[a-zA-Z_][a-zA-Z0-9_]*`
- **Comentarios**: `//...` y `/* ... */` (ignorados)

### Reglas del Parser

La gramática es **LALR(1)** (igual que BISON/YACC). Las reglas principales:

```yacc
program     → statement_list
statement   → create_stmt | insert_stmt | find_stmt |
              update_stmt | delete_stmt | drop_stmt
find_stmt   → FIND FROM IDENTIFIER
            | FIND FROM IDENTIFIER WHERE filter_expr
            | FIND FROM IDENTIFIER LIMIT NUMBER
            | ...
filter_expr → filter_expr AND filter_expr
            | filter_expr OR filter_expr
            | NOT filter_expr
            | condition
```

### Representación del AST

El AST se representa como tuplas anidadas de Python:

```python
# FIND FROM usuarios WHERE edad >= 18 AND activo == true
('FIND', 'usuarios',
    ('AND',
        ('COND', 'edad', '>=', 18),
        ('COND', 'activo', '==', True)
    ),
    None, None, None)
```

---

## Comparación PLY vs BISON

| Característica | BISON/YACC | PLY |
|----------------|-----------|-----|
| Lenguaje | C/C++ | Python |
| Algoritmo | LALR(1) | LALR(1) |
| Acciones semánticas | Bloques `{ código C }` | Funciones Python |
| Tokens | Archivo `.l` separado | Funciones `t_*` |
| Velocidad | Muy alta | Media |
| Facilidad | Media | Alta |

---

## Ejemplo de Uso Directo

```python
from nosql_parser import parser, lexer, NoSQLEngine

engine = NoSQLEngine()

query = """
    CREATE COLLECTION productos;
    INSERT INTO productos VALUES {"nombre": "Laptop", "precio": 2500000, "stock": 10};
    FIND FROM productos WHERE precio > 1000000;
"""

ast = parser.parse(query, lexer=lexer)
results = engine.execute(ast)
for r in results:
    print(r)
```
