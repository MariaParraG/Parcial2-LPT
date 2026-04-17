# Punto 4 – Parser CYK vs Parser Predictivo para Calculadora

## Descripción

Se implementaron **dos parsers** para una calculadora aritmética:

1. **Parser CYK** (Cocke-Younger-Kasami) — algoritmo de reconocimiento
   para gramáticas en Forma Normal de Chomsky (CNF).
2. **Parser Predictivo LL(1)** — descendente recursivo, evalúa
   la expresión directamente durante el análisis.

Se realizó un **benchmark de rendimiento** comparando ambos enfoques.

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `cyk_vs_ll.py` | Implementación de ambos parsers + benchmark |

---

## Ejecución

```bash
python3 cyk_vs_ll.py
```

No requiere dependencias externas (solo Python estándar).

---

## Gramáticas Utilizadas

### Gramática Original de la Calculadora

```
E → E + T | E - T | T
T → T * F | T / F | F
F → ( E ) | num
```

### Gramática en CNF (para CYK)

El algoritmo CYK requiere que la gramática esté en **Forma Normal de Chomsky (CNF)**, donde cada producción es de la forma `A → BC` o `A → a`. La gramática original se transforma así:

```
E      → E PLUS_T | E MINUS_T | T
T      → T MUL_F  | T DIV_F   | F
F      → LPAREN E_RP | num
PLUS_T  → + T
MINUS_T → - T
MUL_F   → * T
DIV_F   → / T
E_RP    → E )
```

### Gramática LL(1) (sin recursión izquierda)

```
E  → T E'
E' → + T E' | - T E' | ε
T  → F T'
T' → * F T' | / F T' | ε
F  → ( E ) | num
```

---

## Algoritmo CYK

### Descripción

El CYK es un algoritmo de **programación dinámica** bottom-up:

1. Se llena una tabla triangular `T[i][j]` donde `T[i][j]` contiene el conjunto de variables que pueden derivar la subcadena `tokens[i..j]`.
2. **Inicialización**: `T[i][i]` = variables que derivan `tokens[i]` (terminales).
3. **Recurrencia**: para longitud `l = 2..n`, para cada par `(i,j)` con `j-i+1 = l`, se prueban todas las divisiones `k ∈ [i, j-1]`:
   - Si `B ∈ T[i][k]` y `C ∈ T[k+1][j]` y `A → BC` es una regla, entonces `A ∈ T[i][j]`.
4. **Resultado**: La cadena es válida si y solo si `S ∈ T[0][n-1]`.

### Complejidad

| Aspecto | Valor |
|---------|-------|
| Tiempo | O(n³ · \|G\|) |
| Espacio | O(n² · \|V\|) |

---

## Parser Predictivo LL(1)

### Descripción

Descendente recursivo con funciones mutuamente recursivas:

```python
def E():  result = T();  while peek in ('+','-'): ...
def T():  result = F();  while peek in ('*','/'): ...
def F():  consume('num') OR consume('('); E(); consume(')')
```

### Complejidad

| Aspecto | Valor |
|---------|-------|
| Tiempo | O(n) |
| Espacio | O(n) — pila de recursión |

---

## Resultados de Pruebas de Corrección

Ambos parsers reconocen/evalúan correctamente:

| Expresión | CYK | LL | Resultado |
|-----------|-----|----|-----------|
| `3 + 4` | ✅ | ✅ | 7 |
| `2 + 3 * 5` | ✅ | ✅ | 17 (precedencia correcta) |
| `(2+3)*5` | ✅ | ✅ | 25 |
| `10 - 3 + 2` | ✅ | ✅ | 9 |
| `6 * 3 / 2` | ✅ | ✅ | 9.0 |

---

## Resultados del Benchmark (300 expresiones por nivel)

| Profundidad | n promedio | CYK (ms) | LL (ms) | Ratio |
|-------------|-----------|----------|---------|-------|
| 1 | 2.3 | 0.0187 | 0.0017 | **10.7x** |
| 2 | 3.6 | 0.0504 | 0.0026 | **19.6x** |
| 3 | 4.9 | 0.1313 | 0.0034 | **39.1x** |
| 4 | 5.7 | 0.3025 | 0.0038 | **78.8x** |
| 5 | 7.2 | 0.6801 | 0.0049 | **138.1x** |

El ratio crece de forma consistente, reflejando la diferencia O(n³) vs O(n).

---

## Gráfica de Complejidad

```
Tiempo
  │                              ●  CYK ≈ O(n³)
  │                           ●
  │                        ●
  │                     ●
  │                  ●
  │  ●●●●●●●●●●●●●●●●●●●●●●●●●  LL  ≈ O(n)
  └──────────────────────────── n (tokens)
```

---

## Comparación Final

| Característica | CYK | LL Predictivo |
|----------------|-----|---------------|
| Complejidad tiempo | O(n³) | O(n) |
| Complejidad espacio | O(n²) | O(n) |
| Tipo de gramática | Cualquier GLC en CNF | Sin rec. izquierda, sin ambigüedad |
| Evaluación directa | ❌ (solo reconoce) | ✅ |
| Manejo de ambigüedad | ✅ | ❌ |
| Uso práctico | NLP, bioinformática | Compiladores, intérpretes |
| Mejor para | Gramáticas generales | Gramáticas bien estructuradas |

### ¿Cuándo usar cada uno?

- **CYK**: cuando la gramática es ambigua, no es LL ni LR, o se necesita
  análisis de **todas las derivaciones posibles** (como en PLN).
- **LL Predictivo**: cuando la gramática está bien diseñada y se
  prioriza **velocidad** (compiladores, intérpretes).
