"""
Punto 5 – Calculadora de escritorio booleana en YACC (PLY)
Evalúa expresiones booleanas con operadores lógicos, relacionales
y soporte de variables.

Operadores soportados:
  Lógicos:    AND, OR, NOT, XOR, NAND, NOR
  Relacionales: ==, !=, <, <=, >, >=
  Agrupación: ( )
  Literales:  true, false
  Variables:  letras

Ejemplos:
  true AND false            → false
  NOT true OR false         → false
  (true OR false) AND true  → true
  x = true; x AND NOT x    → false
  5 > 3 AND 2 < 4           → true
"""

import ply.lex as lex
import ply.yacc as yacc
import sys

# ======================================================
# LEXER
# ======================================================

reserved = {
    'and':  'AND',   'AND':  'AND',
    'or':   'OR',    'OR':   'OR',
    'not':  'NOT',   'NOT':  'NOT',
    'xor':  'XOR',   'XOR':  'XOR',
    'nand': 'NAND',  'NAND': 'NAND',
    'nor':  'NOR',   'NOR':  'NOR',
    'true': 'TRUE',  'True': 'TRUE',  'TRUE': 'TRUE',
    'false':'FALSE', 'False':'FALSE', 'FALSE':'FALSE',
}

tokens = [
    'IDENTIFIER', 'NUMBER',
    'AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR',
    'TRUE', 'FALSE',
    'EQ', 'NEQ', 'LT', 'LE', 'GT', 'GE',
    'ASSIGN',
    'LPAREN', 'RPAREN',
    'SEMICOLON',
    'IMPLIES',   # ->
    'IFF',       # <->
]

t_EQ       = r'=='
t_NEQ      = r'!='
t_IMPLIES  = r'->'
t_IFF      = r'<->'
t_LE       = r'<='
t_GE       = r'>='
t_LT       = r'<'
t_GT       = r'>'
t_ASSIGN   = r'='
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_SEMICOLON= r';'
t_ignore   = ' \t\r\n'

def t_COMMENT(t):
    r'//[^\n]*'
    pass

def t_NUMBER(t):
    r'-?[0-9]+(\.[0-9]+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_error(t):
    print(f"  [LEX ERROR] Carácter ilegal: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# ======================================================
# PARSER (YACC)
# ======================================================
# Precedencia (menor a mayor):
#   IFF  (bicondicional)
#   IMPLIES (implicación)
#   OR
#   XOR
#   NOR
#   AND
#   NAND
#   NOT  (unario)
#   Relacionales ==, !=, <, <=, >, >=

precedence = (
    ('right', 'ASSIGN'),
    ('left',  'IFF'),
    ('right', 'IMPLIES'),
    ('left',  'OR'),
    ('left',  'XOR'),
    ('left',  'NOR'),
    ('left',  'AND'),
    ('left',  'NAND'),
    ('right', 'NOT'),
    ('left',  'EQ', 'NEQ'),
    ('left',  'LT', 'LE', 'GT', 'GE'),
)

# Tabla de variables globales
variables = {}

def p_program(p):
    """program : statement_list"""
    p[0] = p[1]

def p_stmt_list_multi(p):
    """statement_list : statement_list SEMICOLON statement"""
    p[0] = p[1] + [p[3]]

def p_stmt_list_single(p):
    """statement_list : statement"""
    p[0] = [p[1]]

def p_stmt_assign(p):
    """statement : IDENTIFIER ASSIGN expr"""
    variables[p[1]] = p[3]
    p[0] = ('assign', p[1], p[3])

def p_stmt_expr(p):
    """statement : expr"""
    p[0] = ('expr', p[1])

# ---- Expresiones booleanas ----

def p_expr_and(p):
    """expr : expr AND expr"""
    p[0] = bool(p[1]) and bool(p[3])

def p_expr_or(p):
    """expr : expr OR expr"""
    p[0] = bool(p[1]) or bool(p[3])

def p_expr_xor(p):
    """expr : expr XOR expr"""
    p[0] = bool(p[1]) ^ bool(p[3])

def p_expr_nand(p):
    """expr : expr NAND expr"""
    p[0] = not (bool(p[1]) and bool(p[3]))

def p_expr_nor(p):
    """expr : expr NOR expr"""
    p[0] = not (bool(p[1]) or bool(p[3]))

def p_expr_not(p):
    """expr : NOT expr"""
    p[0] = not bool(p[2])

def p_expr_implies(p):
    """expr : expr IMPLIES expr"""
    p[0] = (not bool(p[1])) or bool(p[3])

def p_expr_iff(p):
    """expr : expr IFF expr"""
    p[0] = bool(p[1]) == bool(p[3])

# ---- Operadores relacionales ----

def p_expr_eq(p):
    """expr : expr EQ expr"""
    p[0] = p[1] == p[3]

def p_expr_neq(p):
    """expr : expr NEQ expr"""
    p[0] = p[1] != p[3]

def p_expr_lt(p):
    """expr : expr LT expr"""
    p[0] = p[1] < p[3]

def p_expr_le(p):
    """expr : expr LE expr"""
    p[0] = p[1] <= p[3]

def p_expr_gt(p):
    """expr : expr GT expr"""
    p[0] = p[1] > p[3]

def p_expr_ge(p):
    """expr : expr GE expr"""
    p[0] = p[1] >= p[3]

# ---- Agrupación ----

def p_expr_paren(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]

# ---- Literales y variables ----

def p_expr_true(p):
    """expr : TRUE"""
    p[0] = True

def p_expr_false(p):
    """expr : FALSE"""
    p[0] = False

def p_expr_number(p):
    """expr : NUMBER"""
    p[0] = p[1]

def p_expr_id(p):
    """expr : IDENTIFIER"""
    name = p[1]
    if name not in variables:
        print(f"  [WARN] Variable '{name}' no definida, asumiendo False")
        p[0] = False
    else:
        p[0] = variables[name]

def p_error(p):
    if p:
        print(f"  [PARSE ERROR] Token inesperado: '{p.value}'")
    else:
        print("  [PARSE ERROR] Fin de entrada inesperado")

parser = yacc.yacc(debug=False, write_tables=False)

# ======================================================
# EVALUADOR
# ======================================================

def evaluate(source):
    """Evalúa una expresión o programa booleano."""
    result = parser.parse(source, lexer=lexer)
    outputs = []
    if result:
        for stmt in result:
            if stmt[0] == 'assign':
                outputs.append(f"  {stmt[1]} = {fmt(stmt[2])}")
            else:
                outputs.append(f"  → {fmt(stmt[1])}")
    return outputs

def fmt(val):
    if isinstance(val, bool):
        return 'true' if val else 'false'
    return str(val)

# ======================================================
# MODO INTERACTIVO + PRUEBAS
# ======================================================

def run_tests():
    global variables
    print("=" * 60)
    print("  PUNTO 5 – CALCULADORA BOOLEANA (YACC / PLY)")
    print("=" * 60)

    test_cases = [
        # (descripción, código, resultado esperado)
        ("Literal true",                 "true",                               "true"),
        ("Literal false",                "false",                              "false"),
        ("NOT true",                     "NOT true",                           "false"),
        ("NOT false",                    "NOT false",                          "true"),
        ("true AND true",                "true AND true",                      "true"),
        ("true AND false",               "true AND false",                     "false"),
        ("false OR true",                "false OR true",                      "true"),
        ("false OR false",               "false OR false",                     "false"),
        ("true XOR true",                "true XOR true",                      "false"),
        ("true XOR false",               "true XOR false",                     "true"),
        ("true NAND true",               "true NAND true",                     "false"),
        ("false NOR false",              "false NOR false",                    "true"),
        ("true IMPLIES false",           "true -> false",                      "false"),
        ("false IMPLIES true",           "false -> true",                      "true"),
        ("true IFF true",                "true <-> true",                      "true"),
        ("true IFF false",               "true <-> false",                     "false"),
        ("Paréntesis",                   "(true OR false) AND (NOT true)",     "false"),
        ("Precedencia NOT > AND",        "NOT false AND true",                 "true"),
        ("Relacional: 5 > 3",            "5 > 3",                             "true"),
        ("Relacional: 2 >= 5",           "2 >= 5",                            "false"),
        ("Relacional con booleano",      "5 > 3 AND 2 < 4",                   "true"),
        ("Asignación y uso",             "x = true; x AND NOT x",             "false"),
        ("Variables múltiples",          "a = true; b = false; a OR b",       "true"),
        ("De Morgan: NOT(A AND B)",      "NOT (true AND false)",              "true"),
        ("De Morgan: NOT A OR NOT B",    "NOT true OR NOT false",             "true"),
        ("Tautología: A OR NOT A",       "true OR NOT true",                  "true"),
        ("Contradicción: A AND NOT A",   "false AND NOT false",               "false"),
        ("Expresión compleja",
         "p = true; q = false; (p -> q) <-> (NOT p OR q)",                    "true"),
    ]

    passed = 0
    for desc, code, expected in test_cases:
        variables = {}
        outputs = evaluate(code)
        # El último resultado de la expresión final
        last = outputs[-1].strip() if outputs else ""
        last_val = last.replace("→ ", "").strip()
        ok = last_val == expected
        symbol = "✅" if ok else "❌"
        if ok:
            passed += 1
        print(f"  {symbol} {desc:<38} {code:<40} → {last_val} (esp: {expected})")

    print(f"\n  Resultado: {passed}/{len(test_cases)} pruebas pasadas")

    print("\n" + "=" * 60)
    print("  MODO INTERACTIVO (escribe 'salir' para terminar)")
    print("=" * 60)
    print("  Operadores: AND, OR, NOT, XOR, NAND, NOR, ->, <->")
    print("  Relacionales: ==, !=, <, <=, >, >=")
    print("  Variables: x = true; x AND NOT x")
    print()

    variables = {}
    while True:
        try:
            line = input("  booleana> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  ¡Hasta luego!")
            break
        if not line:
            continue
        if line.lower() in ('salir', 'exit', 'quit'):
            print("  ¡Hasta luego!")
            break
        outputs = evaluate(line)
        for out in outputs:
            print(out)


def run_tests_only():
    """Ejecuta solo las pruebas sin modo interactivo."""
    global variables
    print("=" * 60)
    print("  PUNTO 5 – CALCULADORA BOOLEANA (YACC / PLY)")
    print("=" * 60)

    tests = [
        ("NOT true",            "NOT true",          "false"),
        ("true AND false",      "true AND false",     "false"),
        ("false OR true",       "false OR true",      "true"),
        ("true XOR false",      "true XOR false",     "true"),
        ("true NAND true",      "true NAND true",     "false"),
        ("false NOR false",     "false NOR false",    "true"),
        ("true -> false",       "true -> false",      "false"),
        ("true <-> true",       "true <-> true",      "true"),
        ("5 > 3 AND 2 < 4",     "5 > 3 AND 2 < 4",   "true"),
        ("Tautología",          "true OR NOT true",   "true"),
        ("Variables",           "x = true; x AND NOT x", "false"),
        ("De Morgan",           "NOT (true AND false)","true"),
    ]

    passed = 0
    for desc, code, expected in tests:
        variables = {}
        outputs = evaluate(code)
        last_val = outputs[-1].replace("→ ", "").strip() if outputs else ""
        ok = last_val == expected
        passed += int(ok)
        print(f"  {'✅' if ok else '❌'} {desc:<30} → {last_val}")

    print(f"\n  {passed}/{len(tests)} pruebas pasadas")


if __name__ == '__main__':
    if '--test' in sys.argv or not sys.stdin.isatty():
        run_tests_only()
    else:
        run_tests()
