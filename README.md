# Punto 5 – Calculadora Booleana en YACC (PLY)

## Descripción

Se implementó una **calculadora de escritorio para expresiones booleanas**
usando **PLY** (Python Lex-Yacc), el equivalente Python de **YACC**.

El programa evalúa expresiones lógicas completas incluyendo:
- Operadores lógicos clásicos y extendidos
- Operadores relacionales (para comparar valores numéricos)
- Variables con asignación
- Paréntesis para agrupar
- Modo interactivo (REPL)

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `bool_calc.py` | Implementación completa: lexer + parser + evaluador + REPL |

---

## Requisitos

```bash
pip install ply
```

---

## Ejecución

```bash
# Modo interactivo (con pruebas automáticas)
python3 bool_calc.py

# Solo pruebas automatizadas
python3 bool_calc.py --test
```

---

## Operadores Soportados

| Operador | Símbolo | Ejemplo | Resultado |
|----------|---------|---------|-----------|
| AND (conjunción) | `AND` | `true AND false` | `false` |
| OR (disyunción) | `OR` | `false OR true` | `true` |
| NOT (negación) | `NOT` | `NOT true` | `false` |
| XOR (disyunción exclusiva) | `XOR` | `true XOR true` | `false` |
| NAND | `NAND` | `true NAND true` | `false` |
| NOR | `NOR` | `false NOR false` | `true` |
| Implicación | `->` | `true -> false` | `false` |
| Bicondicional | `<->` | `true <-> true` | `true` |
| Igual | `==` | `5 == 5` | `true` |
| Diferente | `!=` | `3 != 4` | `true` |
| Menor | `<` | `2 < 5` | `true` |
| Mayor | `>` | `5 > 2` | `true` |
| Asignación | `=` | `x = true` | — |

---

## Tabla de Verdad Incorporada

| A | B | A AND B | A OR B | A XOR B | A NAND B | A NOR B | A→B | A↔B |
|---|---|---------|--------|---------|----------|---------|-----|-----|
| T | T | T | T | F | F | F | T | T |
| T | F | F | T | T | T | F | F | F |
| F | T | F | T | T | T | F | T | F |
| F | F | F | F | F | T | T | T | T |

---

## Precedencia de Operadores (de menor a mayor)

```
<->  (bicondicional)     — más baja
->   (implicación)
OR
XOR
NOR
AND
NAND
NOT                      — unario
==, !=, <, <=, >, >=     — relacionales
(  )                     — más alta
```

Esta precedencia es análoga a las reglas estándar del álgebra booleana.

---

## Resultados de Pruebas (12/12 ✅)

| Expresión | Resultado |
|-----------|-----------|
| `NOT true` | `false` |
| `true AND false` | `false` |
| `false OR true` | `true` |
| `true XOR false` | `true` |
| `true NAND true` | `false` |
| `false NOR false` | `true` |
| `true -> false` | `false` |
| `true <-> true` | `true` |
| `5 > 3 AND 2 < 4` | `true` |
| `true OR NOT true` (tautología) | `true` |
| `x = true; x AND NOT x` | `false` |
| `NOT (true AND false)` (De Morgan) | `true` |

---

## Ejemplos de Uso

```
booleana> true AND false
  → false

booleana> NOT (true OR false)
  → false

booleana> 5 > 3 AND 10 != 9
  → true

booleana> p = true; q = false; p -> q
  p = true
  q = false
  → false

booleana> (true -> false) <-> (NOT true OR false)
  → true

booleana> true OR NOT true
  → true
```

---

## Desempeño del Analizador Sintáctico

### Tipo de parser generado

PLY/YACC genera un parser **LALR(1)** (Look-Ahead LR con 1 símbolo de
anticipación). Este es el mismo tipo que usa BISON. Sus características son:

### Fortalezas para este programa

1. **Manejo automático de precedencia**: la tabla `precedence` de PLY resuelve
   automáticamente ambigüedades como `NOT false AND true` → `(NOT false) AND true`,
   sin necesidad de refactorizar la gramática.

2. **Acciones semánticas inmediatas**: cada regla evalúa la expresión
   directamente (la acción `p[0] = ...` corre en tiempo de parsing).
   No se construye un AST intermedio.

3. **Complejidad O(n)**: para expresiones booleanas lineales, el parser
   LALR(1) procesa cada token exactamente una vez.

4. **Manejo de errores**: el token especial `error` de PLY permite recuperación
   ante expresiones mal formadas sin detener el programa completo.

### Limitaciones

- No soporta gramáticas ambiguas sin declarar precedencias explícitas.
- No detecta tautologías/contradicciones (eso requeriría un verificador
  semántico adicional, como un SAT solver).
- La gramática debe ser LALR(1); gramáticas más complejas requieren LALR(k)
  o GLR.

### Comparación con otros enfoques

| Aspecto | YACC/PLY (LALR) | LL Recursivo | CYK |
|---------|-----------------|--------------|-----|
| Complejidad | O(n) | O(n) | O(n³) |
| Precedencia | Tabla declarativa | Manual | N/A |
| Evaluación | Inmediata (bottom-up) | Inmediata (top-down) | Solo reconocimiento |
| Ideal para | Calculadoras, compiladores | Expresiones simples | Gramáticas generales |

El parser YACC/LALR es la **elección óptima** para una calculadora booleana:
eficiente, robusto y con manejo declarativo de la precedencia de operadores.
