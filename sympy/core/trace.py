from sympy import Expr, Add, Mul, Matrix, Pow, sympify, Matrix

def _is_scalar(e):
    """ Helper method used in Tr"""

    # sympify to set proper attributes
    e = sympify(e)
    if isinstance(e, Expr):
        if (e.is_Integer or e.is_Float or
            e.is_Rational or e.is_Number or
            (e.is_Symbol and e.is_commutative)
            ):
            return True

    return False

def _cycle_permute(l):
    """ Cyclic permutations based on canonical ordering"""

    min_item = min(l)
    indices = [i for i, x in enumerate(l) if x ==  min_item]

    le = list(l)
    le.extend(l) # duplicate and extend string for easy processing

    # adding the first min_item index back for easier looping
    indices.append(len(l) + indices[0])

    # create sublist of items with first item as min_item and last_item
    # in each of the sublist is item just before the next occurence of
    # minitem in the cycle formed.
    sublist = [[le[indices[i]:indices[i+1]]] for i in
               xrange(len(indices)-1)]

    # we do comparison of strings by comparing elements
    # in each sublist
    idx = sublist.index(min(sublist))
    ordered_l = le[indices[idx]:indices[idx]+len(l)]

    return ordered_l

class Tr(Expr):
    """ Generic Trace operation than can trace over:

    a) sympy matrix
    b) operators
    c) outer products

    Parameters
    ==========
    o : operator, matrix, expr
    i : indices (optional)

    Examples
    ========

    # TODO: Need to handle printing

    a) Trace(A+B) = Tr(A) + Tr(B)
    b) Trace(scalar*Operator) = scalar*Trace(Operator)

    >>> from sympy.core.trace import Tr
    >>> from sympy import symbols, Matrix
    >>> a, b = symbols('a b', commutative=True)
    >>> A, B = symbols('A B', commutative=False)
    >>> Tr(a*A,2)
    a*Tr(A, 2)
    >>> m = Matrix([[1,2],[1,1]])
    >>> Tr(m)
    2

    """

    def __new__(cls, *args):
        """ Construct a Trace object.

        """
        expr = args[0]
        indices = args[1] if len(args) == 2 else -1 #-1 indicates full trace
        if isinstance(expr, Matrix):
            return expr.trace()
        elif hasattr(expr, 'trace') and callable(t.x):
            #for any objects that have trace() defined e.g numpy
            return expr.trace()
        elif isinstance(expr, Add):
            return Add(*[Tr(arg, indices) for arg in expr.args])
        elif isinstance(expr, Mul):
            c_part, nc_part = expr.args_cnc()
            if len(nc_part) == 0:
                return Mul(*c_part)
            else:
                # cyclic permute nc_part for canonical ordering
                nc_part_ordered = _cycle_permute(nc_part)
                return Mul(*c_part) * Expr.__new__(cls, Mul(*nc_part_ordered),
                                                   indices)
        elif isinstance(expr, Pow):
            if (_is_scalar(expr.args[0]) and
                _is_scalar(expr.args[1])):
                return expr
            else:
                return Expr.__new__(cls, expr, indices)
        else:
            if (_is_scalar(expr)):
                return expr
            return Expr.__new__(cls, expr, indices)

    def doit(self,**kwargs):
        """ Perform the trace operation.

        #TODO: Current version ignores the indices set for partial trace.

        >>> from sympy.core.trace import Tr
        >>> from sympy.physics.quantum.operator import OuterProduct
        >>> from sympy.physics.quantum.spin import JzKet, JzBra
        >>> t = Tr(OuterProduct(JzKet(1,1), JzBra(1,1)))
        >>> t.doit()
        1

        """
        if hasattr(self.args[0], '_eval_trace'):
            return self.args[0]._eval_trace()

        return self

    @property
    def is_number(self):
        #TODO : This function to be reviewed
        # and implementation improved.

        return True
