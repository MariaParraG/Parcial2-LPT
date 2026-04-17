"""
Punto 2 – Implementación del parser NoSQL usando PLY (Python Lex-Yacc)
PLY es el equivalente Python de BISON/YACC + LEX.
Implementa la gramática definida en el Punto 1.
"""

import ply.lex as lex
import ply.yacc as yacc
import sys
import json

# ==============================================================
# LEXER (equivalente a LEX / FLEX)
# ==============================================================

reserved = {
    'CREATE': 'CREATE', 'create': 'CREATE',
    'INSERT': 'INSERT', 'insert': 'INSERT',
    'FIND':   'FIND',   'find':   'FIND',
    'UPDATE': 'UPDATE', 'update': 'UPDATE',
    'DELETE': 'DELETE', 'delete': 'DELETE',
    'DROP':   'DROP',   'drop':   'DROP',
    'COLLECTION': 'COLLECTION', 'collection': 'COLLECTION',
    'INTO':   'INTO',   'into':   'INTO',
    'FROM':   'FROM',   'from':   'FROM',
    'VALUES': 'VALUES', 'values': 'VALUES',
    'WHERE':  'WHERE',  'where':  'WHERE',
    'SET':    'SET',    'set':    'SET',
    'AND':    'AND',    'and':    'AND',
    'OR':     'OR',     'or':     'OR',
    'NOT':    'NOT',    'not':    'NOT',
    'IN':     'IN',     'in':     'IN',
    'EXISTS': 'EXISTS', 'exists': 'EXISTS',
    'LIMIT':  'LIMIT',  'limit':  'LIMIT',
    'SORT':   'SORT',   'sort':   'SORT',
    'BY':     'BY',     'by':     'BY',
    'ASC':    'ASC',    'asc':    'ASC',
    'DESC':   'DESC',   'desc':   'DESC',
    'true':   'TRUE',   'True':   'TRUE',   'TRUE': 'TRUE',
    'false':  'FALSE',  'False':  'FALSE',  'FALSE': 'FALSE',
    'null':   'NULL',   'NULL':   'NULL',
}

tokens = list(set(reserved.values())) + [
    'IDENTIFIER', 'NUMBER', 'STRING',
    'EQ', 'NEQ', 'LE', 'GE', 'LT', 'GT', 'ASSIGN',
    'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'LPAREN', 'RPAREN', 'SEMICOLON', 'COMMA', 'COLON',
]

# Reglas de tokens simples
t_EQ       = r'=='
t_NEQ      = r'!='
t_LE       = r'<='
t_GE       = r'>='
t_LT       = r'<'
t_GT       = r'>'
t_ASSIGN   = r'='
t_LBRACE   = r'\{'
t_RBRACE   = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_SEMICOLON = r';'
t_COMMA    = r','
t_COLON    = r':'
t_ignore   = ' \t\r\n'

def t_COMMENT(t):
    r'//[^\n]*'
    pass

def t_MCOMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass

def t_STRING(t):
    r'"[^"]*"|\'[^\']*\''
    t.value = t.value[1:-1]  # quitar comillas
    return t

def t_NUMBER(t):
    r'-?[0-9]+(\.[0-9]+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_error(t):
    print(f"[LEXER ERROR] Carácter ilegal: '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# ==============================================================
# PARSER (equivalente a YACC / BISON)
# ==============================================================

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

errors = []

def p_program(p):
    """program : statement_list"""
    p[0] = ('program', p[1])

def p_statement_list(p):
    """statement_list : statement_list statement
                      | statement"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    """statement : create_stmt SEMICOLON
                 | insert_stmt SEMICOLON
                 | find_stmt   SEMICOLON
                 | update_stmt SEMICOLON
                 | delete_stmt SEMICOLON
                 | drop_stmt   SEMICOLON"""
    p[0] = p[1]

# ---- CREATE ----
def p_create_stmt(p):
    """create_stmt : CREATE COLLECTION IDENTIFIER"""
    p[0] = ('CREATE', p[3])

# ---- INSERT ----
def p_insert_stmt(p):
    """insert_stmt : INSERT INTO IDENTIFIER VALUES document
                   | INSERT INTO IDENTIFIER VALUES LBRACKET doc_list RBRACKET"""
    if len(p) == 6:
        p[0] = ('INSERT', p[3], [p[5]])
    else:
        p[0] = ('INSERT', p[3], p[6])

def p_doc_list(p):
    """doc_list : doc_list COMMA document
                | document"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# ---- FIND ----
def p_find_stmt_simple(p):
    """find_stmt : FIND FROM IDENTIFIER"""
    p[0] = ('FIND', p[3], None, None, None, None)

def p_find_stmt_where(p):
    """find_stmt : FIND FROM IDENTIFIER WHERE filter_expr"""
    p[0] = ('FIND', p[3], p[5], None, None, None)

def p_find_stmt_limit(p):
    """find_stmt : FIND FROM IDENTIFIER LIMIT NUMBER"""
    p[0] = ('FIND', p[3], None, int(p[5]), None, None)

def p_find_stmt_where_limit(p):
    """find_stmt : FIND FROM IDENTIFIER WHERE filter_expr LIMIT NUMBER"""
    p[0] = ('FIND', p[3], p[5], int(p[7]), None, None)

def p_find_stmt_where_sort(p):
    """find_stmt : FIND FROM IDENTIFIER WHERE filter_expr SORT BY IDENTIFIER order"""
    p[0] = ('FIND', p[3], p[5], None, p[8], p[9])

def p_find_stmt_sort(p):
    """find_stmt : FIND FROM IDENTIFIER SORT BY IDENTIFIER order"""
    p[0] = ('FIND', p[3], None, None, p[6], p[7])

def p_order(p):
    """order : ASC
             | DESC"""
    p[0] = p[1]

# ---- UPDATE ----
def p_update_stmt(p):
    """update_stmt : UPDATE IDENTIFIER SET set_list
                   | UPDATE IDENTIFIER SET set_list WHERE filter_expr"""
    cond = p[6] if len(p) == 7 else None
    p[0] = ('UPDATE', p[2], p[4], cond)

def p_set_list(p):
    """set_list : set_list COMMA set_expr
                | set_expr"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_set_expr(p):
    """set_expr : IDENTIFIER ASSIGN value"""
    p[0] = (p[1], p[3])

# ---- DELETE ----
def p_delete_stmt(p):
    """delete_stmt : DELETE FROM IDENTIFIER
                   | DELETE FROM IDENTIFIER WHERE filter_expr"""
    cond = p[5] if len(p) == 6 else None
    p[0] = ('DELETE', p[3], cond)

# ---- DROP ----
def p_drop_stmt(p):
    """drop_stmt : DROP COLLECTION IDENTIFIER"""
    p[0] = ('DROP', p[3])

# ---- FILTROS ----
def p_filter_expr_binop(p):
    """filter_expr : filter_expr AND filter_expr
                   | filter_expr OR filter_expr"""
    p[0] = (p[2].upper(), p[1], p[3])

def p_filter_expr_not(p):
    """filter_expr : NOT filter_expr"""
    p[0] = ('NOT', p[2])

def p_filter_expr_paren(p):
    """filter_expr : LPAREN filter_expr RPAREN"""
    p[0] = p[2]

def p_filter_expr_cond(p):
    """filter_expr : condition"""
    p[0] = p[1]

def p_condition_cmp(p):
    """condition : IDENTIFIER comparator value"""
    p[0] = ('COND', p[1], p[2], p[3])

def p_condition_in(p):
    """condition : IDENTIFIER IN LBRACKET value_list RBRACKET"""
    p[0] = ('IN', p[1], p[4])

def p_condition_exists(p):
    """condition : IDENTIFIER EXISTS"""
    p[0] = ('EXISTS', p[1])

def p_comparator_eq(p):
    """comparator : EQ"""
    p[0] = p[1]

def p_comparator_neq(p):
    """comparator : NEQ"""
    p[0] = p[1]

def p_comparator_lt(p):
    """comparator : LT"""
    p[0] = p[1]

def p_comparator_le(p):
    """comparator : LE"""
    p[0] = p[1]

def p_comparator_gt(p):
    """comparator : GT"""
    p[0] = p[1]

def p_comparator_ge(p):
    """comparator : GE"""
    p[0] = p[1]

# ---- DOCUMENTOS ----
def p_document(p):
    """document : LBRACE field_list RBRACE
                | LBRACE RBRACE"""
    p[0] = p[2] if len(p) == 4 else {}

def p_field_list(p):
    """field_list : field_list COMMA field
                  | field"""
    if len(p) == 4:
        p[1].update(p[3]); p[0] = p[1]
    else:
        p[0] = p[1]

def p_field(p):
    """field : STRING COLON value"""
    p[0] = {p[1]: p[3]}

def p_value_num(p):
    """value : NUMBER"""
    p[0] = p[1]

def p_value_str(p):
    """value : STRING"""
    p[0] = p[1]

def p_value_bool_true(p):
    """value : TRUE"""
    p[0] = True

def p_value_bool_false(p):
    """value : FALSE"""
    p[0] = False

def p_value_null(p):
    """value : NULL"""
    p[0] = None

def p_value_doc(p):
    """value : document"""
    p[0] = p[1]

def p_value_array(p):
    """value : LBRACKET value_list RBRACKET
             | LBRACKET RBRACKET"""
    p[0] = p[2] if len(p) == 4 else []

def p_value_list(p):
    """value_list : value_list COMMA value
                  | value"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_error(p):
    if p:
        msg = f"Error de sintaxis en '{p.value}' (línea {p.lineno})"
    else:
        msg = "Error de sintaxis: fin de entrada inesperado"
    errors.append(msg)
    print(f"[PARSER ERROR] {msg}")

parser = yacc.yacc(debug=False, write_tables=False)

# ==============================================================
# MOTOR DE EJECUCIÓN (simulación en memoria)
# ==============================================================

class NoSQLEngine:
    def __init__(self):
        self.collections = {}

    def execute(self, ast):
        results = []
        for stmt in ast[1]:
            r = self._exec_stmt(stmt)
            results.append(r)
        return results

    def _exec_stmt(self, stmt):
        op = stmt[0]
        if op == 'CREATE':
            return self._create(stmt[1])
        elif op == 'INSERT':
            return self._insert(stmt[1], stmt[2])
        elif op == 'FIND':
            return self._find(*stmt[1:])
        elif op == 'UPDATE':
            return self._update(stmt[1], stmt[2], stmt[3])
        elif op == 'DELETE':
            return self._delete(stmt[1], stmt[2])
        elif op == 'DROP':
            return self._drop(stmt[1])

    def _create(self, name):
        if name in self.collections:
            return f"⚠️  Colección '{name}' ya existe."
        self.collections[name] = []
        return f"✅ Colección '{name}' creada."

    def _insert(self, col, docs):
        if col not in self.collections:
            self.collections[col] = []
        self.collections[col].extend(docs)
        return f"✅ {len(docs)} documento(s) insertado(s) en '{col}'."

    def _find(self, col, cond, limit, sort_field, order):
        if col not in self.collections:
            return f"❌ Colección '{col}' no existe."
        docs = [d for d in self.collections[col] if self._eval_filter(d, cond)]
        if sort_field:
            reverse = (order == 'DESC' or order == 'desc')
            docs.sort(key=lambda d: d.get(sort_field, ''), reverse=reverse)
        if limit:
            docs = docs[:limit]
        return {'collection': col, 'count': len(docs), 'results': docs}

    def _update(self, col, set_list, cond):
        if col not in self.collections:
            return f"❌ Colección '{col}' no existe."
        count = 0
        for doc in self.collections[col]:
            if self._eval_filter(doc, cond):
                for field, val in set_list:
                    doc[field] = val
                count += 1
        return f"✅ {count} documento(s) actualizado(s) en '{col}'."

    def _delete(self, col, cond):
        if col not in self.collections:
            return f"❌ Colección '{col}' no existe."
        before = len(self.collections[col])
        self.collections[col] = [d for d in self.collections[col]
                                  if not self._eval_filter(d, cond)]
        removed = before - len(self.collections[col])
        return f"✅ {removed} documento(s) eliminado(s) de '{col}'."

    def _drop(self, col):
        if col not in self.collections:
            return f"❌ Colección '{col}' no existe."
        del self.collections[col]
        return f"✅ Colección '{col}' eliminada."

    def _eval_filter(self, doc, cond):
        if cond is None:
            return True
        op = cond[0]
        if op == 'COND':
            field, comp, val = cond[1], cond[2], cond[3]
            dval = doc.get(field)
            if dval is None:
                return False
            if comp == '==': return dval == val
            if comp == '!=': return dval != val
            if comp == '<':  return dval < val
            if comp == '<=': return dval <= val
            if comp == '>':  return dval > val
            if comp == '>=': return dval >= val
        elif op == 'IN':
            return doc.get(cond[1]) in cond[2]
        elif op == 'EXISTS':
            return cond[1] in doc
        elif op == 'AND':
            return self._eval_filter(doc, cond[1]) and self._eval_filter(doc, cond[2])
        elif op == 'OR':
            return self._eval_filter(doc, cond[1]) or self._eval_filter(doc, cond[2])
        elif op == 'NOT':
            return not self._eval_filter(doc, cond[1])
        return True


# ==============================================================
# PROGRAMA PRINCIPAL
# ==============================================================

def run_query(source, engine, show_ast=False):
    global errors
    errors = []
    ast = parser.parse(source, lexer=lexer)
    if errors or ast is None:
        print("  No se puede ejecutar debido a errores de análisis.\n")
        return
    if show_ast:
        print(f"  AST: {ast}")
    results = engine.execute(ast)
    for r in results:
        if isinstance(r, dict):
            print(f"  → {r['count']} resultado(s):")
            for doc in r['results']:
                print(f"     {json.dumps(doc, ensure_ascii=False)}")
        else:
            print(f"  → {r}")
    print()


if __name__ == '__main__':
    engine = NoSQLEngine()

    tests = [
        ("Crear colección",
         "CREATE COLLECTION usuarios;"),

        ("Insertar documentos",
         """INSERT INTO usuarios VALUES {"nombre": "Ana", "edad": 30, "activo": true};
            INSERT INTO usuarios VALUES {"nombre": "Luis", "edad": 17, "activo": true};
            INSERT INTO usuarios VALUES {"nombre": "María", "edad": 25, "activo": false};"""),

        ("FIND sin filtro",
         "FIND FROM usuarios;"),

        ("FIND con filtro AND",
         "FIND FROM usuarios WHERE edad >= 18 AND activo == true;"),

        ("FIND con LIMIT",
         "FIND FROM usuarios LIMIT 2;"),

        ("FIND con SORT",
         "FIND FROM usuarios SORT BY nombre ASC;"),

        ("UPDATE con WHERE",
         "UPDATE usuarios SET activo = false WHERE edad < 18;"),

        ("Verificar UPDATE",
         "FIND FROM usuarios WHERE activo == false;"),

        ("DELETE con WHERE",
         "DELETE FROM usuarios WHERE activo == false;"),

        ("Verificar DELETE",
         "FIND FROM usuarios;"),

        ("Inserción múltiple",
         """INSERT INTO usuarios VALUES [
             {"nombre": "Carlos", "edad": 40, "activo": true},
             {"nombre": "Sofía", "edad": 22, "activo": true}
         ];"""),

        ("DROP COLLECTION",
         "DROP COLLECTION usuarios;"),

        ("Verificar DROP (debe dar error)",
         "FIND FROM usuarios;"),
    ]

    print("=" * 60)
    print("  PRUEBAS DEL PARSER NoSQL")
    print("=" * 60)
    for name, query in tests:
        print(f"\n[TEST] {name}")
        print(f"  Query: {query.strip()[:80]}...")
        run_query(query, engine)
