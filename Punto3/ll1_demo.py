"""
Punto 3 – Demostración que la gramática es LL(1)

Gramática:
    S → AaAb | BbBa
    A → ε
    B → ε

Herramienta: Cálculo manual de conjuntos FIRST, FOLLOW y tabla LL(1)
"""

# ======================================================
# REPRESENTACIÓN DE LA GRAMÁTICA
# ======================================================
# Terminales
# a, b
# No terminales
# S, A, B
# ε representado como None

EPSILON = 'ε'
EOF = '$'

grammar = {
    'S': [['A', 'a', 'A', 'b'],   # S → AaAb
          ['B', 'b', 'B', 'a']],  # S → BbBa
    'A': [[EPSILON]],             # A → ε
    'B': [[EPSILON]],             # B → ε
}

terminals = {'a', 'b', EOF}
non_terminals = {'S', 'A', 'B'}

# ======================================================
# CÁLCULO DEL CONJUNTO FIRST
# ======================================================

def first_of_string(symbols, first_sets):
    """Calcula FIRST de una cadena de símbolos."""
    result = set()
    for sym in symbols:
        if sym == EPSILON:
            result.add(EPSILON)
            break
        elif sym in terminals:
            result.add(sym)
            break
        else:  # no terminal
            f = first_sets[sym] - {EPSILON}
            result |= f
            if EPSILON not in first_sets[sym]:
                break
    else:
        result.add(EPSILON)
    return result


def compute_first(grammar):
    first = {nt: set() for nt in non_terminals}
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                add = first_of_string(prod, first)
                before = len(first[nt])
                first[nt] |= add
                if len(first[nt]) > before:
                    changed = True
    return first


# ======================================================
# CÁLCULO DEL CONJUNTO FOLLOW
# ======================================================

def compute_follow(grammar, first):
    follow = {nt: set() for nt in non_terminals}
    follow['S'].add(EOF)  # Símbolo inicial

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, sym in enumerate(prod):
                    if sym in non_terminals:
                        beta = prod[i+1:]
                        if beta:
                            first_beta = first_of_string(beta, first)
                            add = first_beta - {EPSILON}
                        else:
                            first_beta = {EPSILON}
                            add = set()
                        before = len(follow[sym])
                        follow[sym] |= add
                        if EPSILON in first_beta:
                            follow[sym] |= follow[nt]
                        if len(follow[sym]) > before:
                            changed = True
    return follow


# ======================================================
# CONSTRUCCIÓN DE LA TABLA LL(1)
# ======================================================

def build_ll1_table(grammar, first, follow):
    """
    Para cada producción A → α:
      1. Para cada terminal a ∈ FIRST(α), agregar A → α en M[A, a]
      2. Si ε ∈ FIRST(α), para cada terminal b ∈ FOLLOW(A), agregar A → α en M[A, b]
    """
    table = {}
    conflicts = []

    for nt, productions in grammar.items():
        for prod in productions:
            first_alpha = first_of_string(prod, first)
            for t in first_alpha - {EPSILON}:
                key = (nt, t)
                if key in table:
                    conflicts.append((nt, t, table[key], prod))
                table[key] = prod
            if EPSILON in first_alpha:
                for t in follow[nt]:
                    key = (nt, t)
                    if key in table:
                        conflicts.append((nt, t, table[key], prod))
                    table[key] = prod

    return table, conflicts


# ======================================================
# EJECUCIÓN Y REPORTE
# ======================================================

def prod_str(p):
    return ' '.join(p)


def run_demo():
    print("=" * 65)
    print("  DEMOSTRACIÓN LL(1) – Gramática S→AaAb|BbBa, A→ε, B→ε")
    print("=" * 65)

    print("\n📌 GRAMÁTICA:")
    for nt, prods in grammar.items():
        for prod in prods:
            print(f"   {nt} → {prod_str(prod)}")

    # 1. FIRST
    first = compute_first(grammar)
    print("\n📌 CONJUNTOS FIRST:")
    for nt in sorted(non_terminals):
        print(f"   FIRST({nt}) = {{ {', '.join(sorted(first[nt]))} }}")

    print("\n   Justificación:")
    print("   • A → ε  ⟹  FIRST(A) = {ε}")
    print("   • B → ε  ⟹  FIRST(B) = {ε}")
    print("   • S → AaAb: FIRST(A)={ε}, entonces incluimos 'a'; resultado FIRST(S) ⊇ {a}")
    print("   • S → BbBa: FIRST(B)={ε}, entonces incluimos 'b'; resultado FIRST(S) ⊇ {b}")
    print("   • En ningún caso ε queda en FIRST(S) porque tras A viene 'a' y tras B viene 'b'")

    # 2. FOLLOW
    follow = compute_follow(grammar, first)
    print("\n📌 CONJUNTOS FOLLOW:")
    for nt in sorted(non_terminals):
        print(f"   FOLLOW({nt}) = {{ {', '.join(sorted(follow[nt]))} }}")

    print("\n   Justificación:")
    print("   • FOLLOW(S) = {$}  (símbolo inicial)")
    print("   • En S → AaAb:  A aparece en posición 0 → FOLLOW(A) ⊇ FIRST('a') = {a}")
    print("                   A aparece en posición 2 → FOLLOW(A) ⊇ FIRST('b') = {b}")
    print("   • En S → BbBa:  B aparece en posición 0 → FOLLOW(B) ⊇ FIRST('b') = {b}")
    print("                   B aparece en posición 2 → FOLLOW(B) ⊇ FIRST('a') = {a}")
    print("   • Resultado: FOLLOW(A) = {a, b}  FOLLOW(B) = {a, b}")

    # 3. Tabla LL(1)
    table, conflicts = build_ll1_table(grammar, first, follow)

    print("\n📌 TABLA DE ANÁLISIS LL(1)  M[A, a]:")
    all_terminals = sorted(terminals)
    header = f"{'NT':>4} | " + " | ".join(f"{t:^20}" for t in all_terminals)
    print("   " + header)
    print("   " + "-" * len(header))
    for nt in sorted(non_terminals):
        row = f"{nt:>4} | "
        for t in all_terminals:
            cell = table.get((nt, t))
            cell_str = f"{nt}→{prod_str(cell)}" if cell else ""
            row += f"{cell_str:^20} | "
        print("   " + row)

    # 4. Verificación de conflictos
    print("\n📌 VERIFICACIÓN DE CONFLICTOS:")
    if conflicts:
        print("   ❌ Se encontraron conflictos — la gramática NO es LL(1):")
        for c in conflicts:
            nt, t, p1, p2 = c
            print(f"      M[{nt},{t}] tiene tanto {nt}→{prod_str(p1)} como {nt}→{prod_str(p2)}")
    else:
        print("   ✅ No hay conflictos: cada celda de la tabla tiene como máximo UNA producción.")
        print("   ✅ La gramática ES LL(1).")

    # 5. Análisis manual
    print("\n📌 ANÁLISIS FORMAL (condición LL(1)):")
    print("""
   Para que una gramática libre de contexto sea LL(1) se deben cumplir
   las siguientes condiciones para cada no terminal A con producciones
   A → α₁ | α₂ | ... | αₙ:

   1. FIRST(αᵢ) ∩ FIRST(αⱼ) = ∅  para i ≠ j
   2. Si ε ∈ FIRST(αᵢ), entonces FIRST(αⱼ) ∩ FOLLOW(A) = ∅  para j ≠ i

   Verificando para S → AaAb | BbBa:
     • FIRST(AaAb) = {a}    (porque A→ε, se toma el 'a' que sigue)
     • FIRST(BbBa) = {b}    (porque B→ε, se toma el 'b' que sigue)
     • FIRST(AaAb) ∩ FIRST(BbBa) = {a} ∩ {b} = ∅  ✅ Condición 1 cumplida

   Verificando para A → ε:
     • Solo hay una producción, no hay conflicto entre producciones. ✅

   Verificando para B → ε:
     • Solo hay una producción, no hay conflicto entre producciones. ✅

   Por lo tanto, la gramática cumple todas las condiciones LL(1).
""")

    # 6. Simulación del parser LL(1)
    print("📌 SIMULACIONES DEL PARSER LL(1):")
    test_inputs = ['ab', 'ba', 'aa']
    for inp in test_inputs:
        ok, trace = simulate_ll1(inp + '$', table, first, follow)
        status = "✅ ACEPTADA" if ok else "❌ RECHAZADA"
        print(f"\n   Entrada: '{inp}' → {status}")
        for step in trace:
            print(f"      {step}")


def simulate_ll1(input_str, table, first, follow):
    """Simula el parser LL(1) con una pila."""
    stack = ['$', 'S']
    inp = list(input_str)
    pos = 0
    trace = []
    MAX_STEPS = 50

    steps = 0
    while stack and steps < MAX_STEPS:
        steps += 1
        top = stack[-1]
        cur = inp[pos] if pos < len(inp) else '$'
        stack_str = ''.join(reversed(stack))
        inp_str = ''.join(inp[pos:])
        trace.append(f"Pila: {stack_str:<20} Entrada: {inp_str:<10}")

        if top == '$' and cur == '$':
            trace.append("→ Aceptado ✅")
            return True, trace
        elif top == cur:  # terminal match
            stack.pop()
            pos += 1
        elif top in terminals:
            trace.append(f"→ Error: esperaba '{top}', encontró '{cur}'")
            return False, trace
        elif top in non_terminals:
            prod = table.get((top, cur))
            if prod is None:
                trace.append(f"→ Error: no hay producción para M[{top},{cur}]")
                return False, trace
            stack.pop()
            if prod != [EPSILON]:
                for sym in reversed(prod):
                    stack.append(sym)
            trace.append(f"→ Aplica {top} → {prod_str(prod)}")
        else:
            return False, trace

    return False, trace + ["→ Timeout / error"]


if __name__ == '__main__':
    run_demo()
