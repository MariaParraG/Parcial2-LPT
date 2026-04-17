"""
Punto 4 – Parser CYK para calculadora vs Parser Predictivo (LL)
Comparación de rendimiento entre ambos enfoques.

La gramática de la calculadora en CNF (Forma Normal de Chomsky) para CYK:
Operaciones: suma, resta, multiplicación, división

Gramática original:
    E → E + T | E - T | T
    T → T * F | T / F | F
    F → ( E ) | num

Gramática equivalente en CNF (para CYK):
    E  → ET1 | ET2 | TF | num
    ET1 → E P1   (E + T)
    ET2 → E P2   (E - T)
    P1  → add T  → necesita binarización...
    ...

Se usa una CNF simplificada para la calculadora aritmética.
"""

import time
import random
import sys

# ======================================================
# GRAMÁTICA EN FORMA NORMAL DE CHOMSKY (CNF)
# ======================================================
#
# Variables: E, T, F, EP, TP
# Terminales: num, +, -, *, /, (, )
#
# Binarización:
#   E  → E PLUS_T     (representa E + T)
#   E  → E MINUS_T    (representa E - T)
#   E  → T
#   PLUS_T  → PLUS T
#   MINUS_T → MINUS T
#   T  → T MUL_F      (representa T * F)
#   T  → T DIV_F      (representa T / F)
#   T  → F
#   MUL_F → MUL F
#   DIV_F → DIV F
#   F  → LPAREN E_RPAREN
#   F  → num
#   E_RPAREN → E RPAREN
#
# Representamos cada terminal como un "símbolo hoja" único.

CNF_RULES = {
    'E': [('E', 'PLUS_T'), ('E', 'MINUS_T'), ('T',)],
    'T': [('T', 'MUL_F'),  ('T', 'DIV_F'),   ('F',)],
    'F': [('LPAREN', 'E_RP'), ('NUM',)],
    'PLUS_T':  [('+', 'T')],
    'MINUS_T': [('-', 'T')],
    'MUL_F':   [('*', 'T')],
    'DIV_F':   [('/', 'T')],
    'E_RP':    [('E', 'RPAREN')],
}

# Mapeo terminal → variables (para la tabla inicial del CYK)
TERM_TO_VAR = {
    'num':  {'NUM'},
    '+':    {'+'},
    '-':    {'-'},
    '*':    {'*'},
    '/':    {'/'},
    '(':    {'LPAREN'},
    ')':    {'RPAREN'},
}

# ======================================================
# PARSER CYK
# ======================================================

def cyk_parse(tokens, start='E'):
    """
    Algoritmo CYK (Cocke-Younger-Kasami).
    Entrada: lista de tokens
    Salida: True si la cadena pertenece al lenguaje, False si no.
    Complejidad: O(n³ · |G|)
    """
    n = len(tokens)
    if n == 0:
        return False

    # Tabla[i][j] = conjunto de variables que derivan tokens[i..j]
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Llenar diagonal (substrings de longitud 1)
    for i, tok in enumerate(tokens):
        table[i][i] = TERM_TO_VAR.get(tok, set()).copy()
        # Propagación de reglas unitarias (E→T, T→F, etc.)
        _close_unit_rules(table[i][i])

    # Llenar para longitudes 2..n
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                left  = table[i][k]
                right = table[k+1][j]
                for var, prods in CNF_RULES.items():
                    for prod in prods:
                        if len(prod) == 2:
                            B, C = prod
                            if B in left and C in right:
                                table[i][j].add(var)
            _close_unit_rules(table[i][j])

    return start in table[0][n-1], table


def _close_unit_rules(var_set):
    """Aplica reglas unitarias (A → B) iterativamente."""
    changed = True
    while changed:
        changed = False
        additions = set()
        for var, prods in CNF_RULES.items():
            for prod in prods:
                if len(prod) == 1:
                    b = prod[0]
                    if b in var_set and var not in var_set:
                        additions.add(var)
        if additions:
            var_set |= additions
            changed = True


# ======================================================
# PARSER PREDICTIVO LL(1) PARA CALCULADORA
# ======================================================
#
# Gramática LL (sin recursión izquierda):
#   E  → T E'
#   E' → + T E' | - T E' | ε
#   T  → F T'
#   T' → * F T' | / F T' | ε
#   F  → ( E ) | num

class PredictiveParser:
    """Parser LL(1) descendente recursivo para expresiones aritméticas."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.calls = 0      # contador de llamadas recursivas

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return '$'

    def consume(self, expected=None):
        tok = self.tokens[self.pos] if self.pos < len(self.tokens) else '$'
        if expected and tok != expected:
            raise SyntaxError(f"Esperaba '{expected}', encontró '{tok}'")
        self.pos += 1
        return tok

    def parse(self):
        self.calls = 0
        result = self._E()
        if self.peek() != '$':
            raise SyntaxError(f"Token inesperado: '{self.peek()}'")
        return result

    def _E(self):
        self.calls += 1
        result = self._T()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self._T()
            if op == '+':
                result += right
            else:
                result -= right
        return result

    def _T(self):
        self.calls += 1
        result = self._F()
        while self.peek() in ('*', '/'):
            op = self.consume()
            right = self._F()
            if op == '*':
                result *= right
            else:
                if right == 0:
                    raise ZeroDivisionError("División por cero")
                result /= right
        return result

    def _F(self):
        self.calls += 1
        tok = self.peek()
        if tok == '(':
            self.consume('(')
            result = self._E()
            self.consume(')')
            return result
        elif tok == 'num':
            self.consume('num')
            return self._get_value()
        else:
            raise SyntaxError(f"Token inesperado en factor: '{tok}'")

    def _get_value(self):
        # Retorna el valor numérico del token anterior
        return self.values[self.pos - 1]

    def parse_with_values(self, values):
        """Parsea con valores reales para los 'num'."""
        self.values = values
        return self.parse()


# ======================================================
# GENERADOR DE EXPRESIONES DE PRUEBA
# ======================================================

def generate_expression(depth=1):
    """Genera tokens y valores para una expresión aritmética de prueba."""
    tokens = []
    values = {}

    def gen(d):
        if d <= 0 or random.random() < 0.4:
            idx = len(tokens)
            tokens.append('num')
            values[idx] = random.randint(1, 20)
        else:
            if random.random() < 0.3:
                tokens.append('(')
                gen(d - 1)
                tokens.append(')')
            else:
                gen(d - 1)
                op = random.choice(['+', '-', '*', '/'])
                tokens.append(op)
                gen(d - 1)

    gen(depth)
    return tokens, values


def simple_expressions():
    """Expresiones fijas para pruebas deterministas."""
    return [
        (['num', '+', 'num'],                     {0: 3, 2: 4},          "3 + 4"),
        (['num', '+', 'num', '*', 'num'],          {0: 2, 2: 3, 4: 5},   "2 + 3 * 5"),
        (['(', 'num', '+', 'num', ')', '*', 'num'], {1: 2, 3: 3, 6: 5},  "(2+3)*5"),
        (['num', '-', 'num', '+', 'num'],          {0: 10, 2: 3, 4: 2},  "10 - 3 + 2"),
        (['num', '*', 'num', '/', 'num'],          {0: 6, 2: 3, 4: 2},   "6 * 3 / 2"),
    ]


# ======================================================
# BENCHMARK
# ======================================================

def benchmark(n_runs=500):
    """Compara tiempos de CYK vs Parser Predictivo."""
    print("=" * 65)
    print("  PUNTO 4 – COMPARACIÓN CYK vs PARSER PREDICTIVO (LL)")
    print("=" * 65)

    # ---- Pruebas deterministas ----
    print("\n📌 PRUEBAS DE CORRECCIÓN:")
    for tokens, values, label in simple_expressions():
        # CYK
        accepted, _ = cyk_parse(tokens)
        # LL
        pp = PredictiveParser(tokens)
        try:
            result = pp.parse_with_values(values)
            ll_ok = True
        except Exception as e:
            ll_ok = False
            result = str(e)

        cyk_sym = "✅" if accepted else "❌"
        ll_sym  = "✅" if ll_ok else "❌"
        print(f"   {label:<25} CYK: {cyk_sym}  LL: {ll_sym}  Resultado: {result}")

    # ---- Benchmark de rendimiento ----
    print(f"\n📌 BENCHMARK DE RENDIMIENTO ({n_runs} expresiones por tamaño):")
    print(f"   {'Tamaño':>8} | {'CYK (ms)':>12} | {'LL (ms)':>12} | {'Ratio CYK/LL':>14} | {'CYK calls O(n³)':>16} | {'LL calls':>10}")
    print("   " + "-" * 85)

    results = []
    for depth in [1, 2, 3, 4, 5]:
        cyk_times = []
        ll_times = []
        avg_n = []
        avg_ll_calls = []

        for _ in range(n_runs):
            tokens, values = generate_expression(depth)
            n = len(tokens)
            avg_n.append(n)

            # CYK
            t0 = time.perf_counter()
            cyk_parse(tokens)
            cyk_times.append(time.perf_counter() - t0)

            # LL
            pp = PredictiveParser(tokens)
            pp.values = {i: values.get(i, 1) for i in range(n)}
            t0 = time.perf_counter()
            try:
                pp.parse()
            except:
                pass
            ll_times.append(time.perf_counter() - t0)
            avg_ll_calls.append(pp.calls)

        avg_cyk = sum(cyk_times) / len(cyk_times) * 1000
        avg_ll  = sum(ll_times)  / len(ll_times)  * 1000
        avg_size = sum(avg_n) / len(avg_n)
        avg_calls = sum(avg_ll_calls) / len(avg_ll_calls)
        ratio = avg_cyk / avg_ll if avg_ll > 0 else float('inf')
        n3_approx = avg_size ** 3

        print(f"   {depth:>4} (n≈{avg_size:4.1f}) | {avg_cyk:>12.4f} | {avg_ll:>12.4f} | {ratio:>14.1f}x | {n3_approx:>16.0f} | {avg_calls:>10.1f}")
        results.append((depth, avg_size, avg_cyk, avg_ll, ratio))

    print("\n📌 ANÁLISIS DE COMPLEJIDAD:")
    print("""
   ┌─────────────────────────────────────────────────────────────────┐
   │  Algoritmo CYK (Cocke-Younger-Kasami)                          │
   │  • Complejidad temporal: O(n³ · |G|)                           │
   │  • Complejidad espacial: O(n² · |V|)                           │
   │  • Funciona con CUALQUIER gramática libre de contexto en CNF   │
   │  • No requiere que la gramática sea LL(k) ni LR(k)             │
   │  • Reconocimiento puro (no evalúa directamente)                │
   │                                                                 │
   │  Parser Predictivo LL(1) (Descendente Recursivo)               │
   │  • Complejidad temporal: O(n)                                  │
   │  • Complejidad espacial: O(n) — profundidad de recursión       │
   │  • Requiere gramática sin ambigüedad y sin recursión izquierda │
   │  • Evalúa directamente durante el análisis                     │
   │  • Mucho más eficiente en la práctica                          │
   └─────────────────────────────────────────────────────────────────┘
""")
    print("📌 CONCLUSIÓN:")
    if results:
        last = results[-1]
        print(f"""
   Para expresiones de profundidad {last[0]} (n ≈ {last[1]:.0f} tokens):
   • CYK tardó    ≈ {last[2]:.4f} ms por expresión
   • LL tardó     ≈ {last[3]:.4f} ms por expresión
   • CYK es ≈ {last[4]:.1f}x más lento que LL

   Esto refleja la diferencia teórica: O(n³) vs O(n).
   El parser LL es claramente superior para gramáticas bien definidas.
   CYK es valioso cuando la gramática es ambigua o no es LL/LR.
""")


if __name__ == '__main__':
    random.seed(42)
    benchmark(n_runs=300)
