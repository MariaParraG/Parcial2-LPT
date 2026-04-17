# 🧠 Parcial 2 – Lenguajes de Programación (2026-1)

Implementación completa de los cinco puntos del segundo parcial de la asignatura
**Lenguajes de Programación**. El proyecto cubre diseño de gramáticas, parsers,
algoritmos de análisis sintáctico y comparativas de rendimiento.

---

## 📁 Estructura del Repositorio

```
parcial/
├── punto1/
│   ├── grammar_nosql.g4       # Gramática ANTLR4 para lenguaje NoSQL
│   └── README.md
├── punto2/
│   ├── nosql_parser.py        # Implementación con PLY (YACC/BISON en Python)
│   └── README.md
├── punto3/
│   ├── ll1_demo.py            # Demostración formal LL(1)
│   └── README.md
├── punto4/
│   ├── cyk_vs_ll.py           # CYK vs Parser Predictivo + benchmark
│   └── README.md
└── punto5/
    ├── bool_calc.py           # Calculadora booleana en YACC
    └── README.md
```

---

## 📌 Descripción de los Puntos

### Punto 1 – Gramática NoSQL CRUD

Se diseñó una gramática formal en formato **ANTLR4** para un lenguaje de
consultas sobre bases de datos **no relacionales** (estilo MongoDB).

El lenguaje soporta las cuatro operaciones CRUD:

| Operación | Comando |
|-----------|---------|
| Create    | `CREATE COLLECTION nombre` |
| Read      | `FIND FROM col WHERE condicion SORT BY campo ASC LIMIT 10` |
| Update    | `UPDATE col SET campo = valor WHERE condicion` |
| Delete    | `DELETE FROM col WHERE condicion` / `DROP COLLECTION col` |

Adicionalmente soporta documentos JSON anidados, arreglos, filtros compuestos
con `AND`, `OR`, `NOT` e `IN`, y comentarios de línea y bloque.

---

### Punto 2 – Implementación del Parser en PLY (BISON/YACC)

Se implementó la gramática del Punto 1 usando **PLY** (Python Lex-Yacc),
que utiliza el mismo algoritmo **LALR(1)** que BISON y YACC, pero en Python.

El parser incluye un **motor de ejecución en memoria** que simula las
operaciones sobre colecciones y documentos. Se ejecutaron 13 pruebas de
integración que verifican cada operación del lenguaje.

**Resultados:** 13/13 pruebas pasadas ✅

---

### Punto 3 – Demostración LL(1)

Se demostró formal y computacionalmente que la gramática:

```
S → AaAb | BbBa
A → ε
B → ε
```

es **LL(1)**, calculando:

- **FIRST**: `FIRST(S) = {a, b}`, `FIRST(A) = FIRST(B) = {ε}`
- **FOLLOW**: `FOLLOW(A) = FOLLOW(B) = {a, b}`, `FOLLOW(S) = {$}`
- **Tabla LL(1)**: sin conflictos en ninguna celda
- **Condición clave**: `FIRST(AaAb) ∩ FIRST(BbBa) = {a} ∩ {b} = ∅`

Se incluye una simulación paso a paso del parser con cadenas de prueba
(`ab` ✅, `ba` ✅, `aa` ❌).

---

### Punto 4 – CYK vs Parser Predictivo

Se implementaron dos parsers para una **calculadora aritmética** y se
comparó su rendimiento:

| Parser | Complejidad | Gramática requerida |
|--------|-------------|---------------------|
| CYK    | O(n³ · \|G\|) | Cualquier GLC en CNF |
| LL(1) Predictivo | O(n) | Sin recursión izquierda, sin ambigüedad |

**Resultados del benchmark** (300 expresiones por nivel de profundidad):

| n promedio | CYK (ms) | LL (ms) | Ratio |
|-----------|----------|---------|-------|
| 2.3 | 0.0187 | 0.0017 | 10.7x |
| 4.9 | 0.1313 | 0.0034 | 39.1x |
| 7.2 | 0.6801 | 0.0049 | **138.1x** |

El parser LL es ampliamente superior para gramáticas bien definidas.
CYK es útil cuando la gramática es ambigua o no cumple las restricciones LL/LR.

---

### Punto 5 – Calculadora Booleana en YACC

Se implementó una calculadora de escritorio para **expresiones booleanas**
usando PLY/YACC. Soporta:

- Operadores: `AND`, `OR`, `NOT`, `XOR`, `NAND`, `NOR`, `->` (implica), `<->` (bicondicional)
- Operadores relacionales: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Variables con asignación: `x = true; x AND NOT x`
- Paréntesis y precedencia completa
- Modo REPL interactivo

El parser generado es **LALR(1)**, lo que permite manejo declarativo de
precedencia de operadores y evaluación directa durante el análisis sintáctico.

**Resultados:** 12/12 pruebas pasadas ✅

---

## ⚙️ Requisitos e Instalación

**Python 3.10+** y la librería PLY:

```bash
pip install ply
```

> Para el Punto 1 (gramática ANTLR4), si se desea compilar con la herramienta
> oficial se necesita Java 11+ y el JAR de ANTLR4. La implementación ejecutable
> está en el Punto 2 con PLY.

---

## ▶️ Ejecución Rápida

```bash
# Punto 2 – Parser NoSQL (13 pruebas)
python3 parcial/punto2/nosql_parser.py

# Punto 3 – Demostración LL(1)
python3 parcial/punto3/ll1_demo.py

# Punto 4 – Benchmark CYK vs LL
python3 parcial/punto4/cyk_vs_ll.py

# Punto 5 – Calculadora booleana (pruebas + REPL interactivo)
python3 parcial/punto5/bool_calc.py

# Punto 5 – Solo pruebas automatizadas
python3 parcial/punto5/bool_calc.py --test
```

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Rol |
|-------------|-----|
| **ANTLR4** | Notación formal de la gramática (Punto 1) |
| **PLY** (Python Lex-Yacc) | Implementación de parsers LALR(1) (Puntos 2 y 5) |
| **Python 3** | Lenguaje de implementación general |
| Algoritmo **CYK** | Análisis sintáctico general O(n³) (Punto 4) |
| Parser **LL(1) Recursivo** | Análisis descendente O(n) (Puntos 3 y 4) |

---

## 📚 Conceptos Clave

- **Gramática Libre de Contexto (GLC)**: formalismo base para describir la
  sintaxis de los lenguajes.
- **FIRST / FOLLOW**: conjuntos usados para construir tablas de análisis LL.
- **LL(1)**: parser descendente que usa 1 símbolo de anticipación; requiere
  gramática sin recursión izquierda y sin ambigüedad.
- **LALR(1)**: parser ascendente (usado por YACC/BISON/PLY); más potente
  que LL(1), acepta una clase mayor de gramáticas.
- **CYK**: algoritmo de programación dinámica que reconoce cualquier GLC en
  CNF con complejidad O(n³).
- **CNF (Forma Normal de Chomsky)**: representación de GLC donde cada
  producción es `A → BC` o `A → a`.
