# Punto 3 – Demostración que la Gramática es LL(1)

## Gramática a Analizar

```
S → AaAb | BbBa
A → ε
B → ε
```

---

## Herramienta

Script Python `ll1_demo.py` que:
1. Calcula los conjuntos **FIRST**
2. Calcula los conjuntos **FOLLOW**
3. Construye la **tabla de análisis LL(1)**
4. Detecta **conflictos** automáticamente
5. **Simula** el parser con cadenas de prueba

---

## Ejecución

```bash
python3 ll1_demo.py
```

---

## Paso a Paso

### 1. Conjuntos FIRST

| No terminal | FIRST |
|-------------|-------|
| `A` | `{ ε }` |
| `B` | `{ ε }` |
| `S` | `{ a, b }` |

**Cálculo:**
- `A → ε` ⟹ `FIRST(A) = {ε}`
- `B → ε` ⟹ `FIRST(B) = {ε}`
- `S → AaAb`: como `ε ∈ FIRST(A)`, se "traspasa" y se incluye el terminal que sigue: `a` → `FIRST(S) ⊇ {a}`
- `S → BbBa`: como `ε ∈ FIRST(B)`, se incluye `b` → `FIRST(S) ⊇ {b}`
- `ε ∉ FIRST(S)` porque siempre hay un terminal concreto que sigue a A o B

---

### 2. Conjuntos FOLLOW

| No terminal | FOLLOW |
|-------------|--------|
| `S` | `{ $ }` |
| `A` | `{ a, b }` |
| `B` | `{ a, b }` |

**Cálculo:**
- `FOLLOW(S) = { $ }` (regla del símbolo inicial)
- En `S → AaAb`:
  - Primera `A` (posición 0): después viene `a` → `FOLLOW(A) ⊇ {a}`
  - Segunda `A` (posición 2): después viene `b` → `FOLLOW(A) ⊇ {b}`
- En `S → BbBa`:
  - Primera `B` (posición 0): después viene `b` → `FOLLOW(B) ⊇ {b}`
  - Segunda `B` (posición 2): después viene `a` → `FOLLOW(B) ⊇ {a}`

---

### 3. Tabla de Análisis LL(1)

| NT | `a` | `b` | `$` |
|----|-----|-----|-----|
| `S` | `S → AaAb` | `S → BbBa` | — |
| `A` | `A → ε` | `A → ε` | — |
| `B` | `B → ε` | `B → ε` | — |

**Construcción:**  
Para cada producción `A → α`:
1. Para cada `t ∈ FIRST(α) - {ε}`: agregar `A → α` en `M[A, t]`
2. Si `ε ∈ FIRST(α)`: para cada `t ∈ FOLLOW(A)`, agregar `A → α` en `M[A, t]`

---

### 4. Verificación Formal de LL(1)

Para que una gramática sea LL(1) debe cumplirse, para cada `A` con `A → α₁ | α₂ | ... | αₙ`:

1. **Sin ambigüedad en FIRST**: `FIRST(αᵢ) ∩ FIRST(αⱼ) = ∅` para `i ≠ j`
2. **Sin conflicto con ε**: si `ε ∈ FIRST(αᵢ)`, entonces `FIRST(αⱼ) ∩ FOLLOW(A) = ∅` para `j ≠ i`

**Para `S → AaAb | BbBa`:**

| | Valor |
|-|-------|
| `FIRST(AaAb)` | `{a}` (A→ε, sigue 'a') |
| `FIRST(BbBa)` | `{b}` (B→ε, sigue 'b') |
| Intersección | `{a} ∩ {b} = ∅` ✅ |

**Para `A → ε` y `B → ε`:** solo una producción cada uno, imposible conflicto. ✅

**Conclusión: La gramática NO tiene conflictos. Es LL(1). ✅**

---

### 5. Simulaciones del Parser LL(1)

#### Entrada `ab` → ✅ ACEPTADA

```
Pila: S$        Entrada: ab$   → Aplica S → A a A b
Pila: AaAb$     Entrada: ab$   → Aplica A → ε
Pila: aAb$      Entrada: ab$   → Match 'a'
Pila: Ab$       Entrada: b$    → Aplica A → ε
Pila: b$        Entrada: b$    → Match 'b'
Pila: $         Entrada: $     → ACEPTADO ✅
```

#### Entrada `ba` → ✅ ACEPTADA

```
Pila: S$        Entrada: ba$   → Aplica S → B b B a
Pila: BbBa$     Entrada: ba$   → Aplica B → ε
Pila: bBa$      Entrada: ba$   → Match 'b'
Pila: Ba$       Entrada: a$    → Aplica B → ε
Pila: a$        Entrada: a$    → Match 'a'
Pila: $         Entrada: $     → ACEPTADO ✅
```

#### Entrada `aa` → ❌ RECHAZADA

```
...
Pila: b$        Entrada: a$    → Error: esperaba 'b', encontró 'a'
```

`aa` no pertenece al lenguaje porque `S` solo genera `ab` o `ba`.

---

## Lenguaje que genera esta gramática

El lenguaje de esta gramática es simplemente `L = { ab, ba }`.  
Esto se debe a que `A → ε` y `B → ε` son las únicas producciones, por lo que:
- `S → AaAb → ε a ε b → ab`
- `S → BbBa → ε b ε a → ba`
