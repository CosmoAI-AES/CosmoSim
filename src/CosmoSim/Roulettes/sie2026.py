# ---
# jupyter:
#   jupytext:
#     default_lexer: ipython3
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.4
#   kernelspec:
#     display_name: Python [conda env:base] *
#     language: python
#     name: conda-base-py
# ---

# %%
import numpy as np
from scipy.special import factorial


# %%
# These functions serve to simplify the g(xi)-functions.
# Defines a function which removes zero terms within the components.
# One component is one part in the sum for g(xi), shown at (24) in the documentation. 
def zero_term_remove(exponents_inter,coefficients_inter):
    width=8
    s=0
    for i in range(len(coefficients_inter)):
        if not coefficients_inter[i]==0:
            s+=1
    exponents=np.zeros((s,width))
    coefficients=np.zeros(s)
    t=0
    for i in range(len(coefficients_inter)):
        if not coefficients_inter[i]==0:
            coefficients[t]=coefficients_inter[i]
            exponents[t]=exponents_inter[i]
            t+=1
    return exponents,coefficients

# Sums components which have the same exponents
def sum_components(exponents_inter1,coefficients_inter1,width):
    exponents_inter2=np.zeros((len(coefficients_inter1),width))
    coefficients_inter2=np.zeros(len(coefficients_inter1))
    index_used=np.zeros(len(coefficients_inter1))
    s=0
    t=0
    for i in range(len(coefficients_inter1)):
        if i not in index_used or i==0:
            index_used[s]=i
            s+=1
            coefficients_inter2[t]=coefficients_inter1[i]
            exponents_inter2[t]=exponents_inter1[i]
            for j in range(len(coefficients_inter1)-i-1):
                for k in range(width):
                    if not exponents_inter2[t][k]==exponents_inter1[j+i+1][k]:
                        break
                    elif (k+1)==width:
                        coefficients_inter2[t]+=coefficients_inter1[j+i+1]
                        index_used[s]=j+i+1
                        s+=1
            t+=1
    return zero_term_remove(exponents_inter2,coefficients_inter2)

# The next three function combined uses relations between the elements with the components (x,y,x_prime,y_prime,f,f_prime,R,R_prime).
# It can only compare two components. Allowing for more would further simplify the final g(xi)-functions.
# match_case_formula lists the possible convertions
def match_case_formula(mode):
    match mode:
        case 0:
            # Checks from a component g(~)*f^2 to find a component g(~)*f'^2, the sum of which results in g(~)
            return np.array([0,0,0,0,2,0,0,0]),np.array([0,0,0,0,0,2,0,0]),np.array([0,0,0,0,0,0,0,0]),1,1,1
        case 1:
            # Checks from a component g(~)*x^2 to find a component g(~)*y^2, the sum of which results in g(~)*R^2
            return np.array([2,0,0,0,0,0,0,0]),np.array([0,2,0,0,0,0,0,0]),np.array([0,0,0,0,0,0,2,0]),1,1,1
        case 2:
            # Checks from a component g(~)*x'^2 to find a component g(~)*y'^2, the sum of which results in g(~)*R^2
            return np.array([0,0,2,0,0,0,0,0]),np.array([0,0,0,2,0,0,0,0]),np.array([0,0,0,0,0,0,2,0]),1,1,1
        case 3:
            # Checks from a component g(~)*x'^2 to find a component g(~)*y'^2*f^2, the sum of which results in g(~)*R'^2
            return np.array([0,0,2,0,0,0,0,0]),np.array([0,0,0,2,2,0,0,0]),np.array([0,0,0,0,0,0,0,2]),1,1,1
        case 4:
            # Checks from a component g(~)*R^2*f^2 to find a component g(~)*x'^2*f'^2, the sum of which results in g(~)*R'^2
            return np.array([0,0,0,0,2,0,2,0]),np.array([0,0,2,0,0,2,0,0]),np.array([0,0,0,0,0,0,0,2]),1,1,1
        case 5:
            # Checks from a component g(~)*R^2 to find a component -g(~)*y'^2*f'^2, the sum of which results in g(~)*R'^2
            return np.array([0,0,0,0,0,0,2,0]),np.array([0,0,0,2,0,2,0,0]),np.array([0,0,0,0,0,0,0,2]),1,-1,1
        # If an exact match is not confirmed
        case _:
            return "ERROR"

# match_case_arangment lists the possible arrangements of the convertions
def match_case_arangment(arangment,x01,x02,x03,sign01,sign02,sign03):
    match arangment:
        case 0:
            # x+y=z
            return x01,x02,x03,sign01,sign02,sign03
        case 1:
            # y+x=z
            return x02,x01,x03,sign02,sign01,sign03
        case 2:
            # z-y=x
            return x03,x02,x01,sign03,-sign02,sign01
        case 3:
            # y-z=-x
            return x02,x03,x01,sign02,-sign03,-sign01
        case 4:
            # z-x=y
            return x03,x01,x02,sign03,-sign01,sign02
        case 5:
            # x-z=-y
            return x01,x03,x02,sign01,-sign03,-sign02
        # If an exact match is not confirmed
        case _:
            return "ERROR"

# formula_simplification is responsible for the actual simplififaction
def formula_simplification(exponents_inter1,coefficients_inter1,width,mode,arangment):
    exponents_inter2=np.zeros((len(coefficients_inter1),width))
    coefficients_inter2=np.zeros(len(coefficients_inter1))
    x01,x02,x03,sign01,sign02,sign03=match_case_formula(mode)
    x1,x2,x3,sign1,sign2,sign3=match_case_arangment(arangment,x01,x02,x03,sign01,sign02,sign03)
    index_used=np.zeros(len(coefficients_inter1))
    s=0
    t=0
    for i in range(len(coefficients_inter1)):
        if i not in index_used or i==0:
            coefficients_inter1[i]
            index_used[s]=i
            s+=1
            coefficients_inter2[t]=coefficients_inter1[i]
            exponents_inter2[t]=exponents_inter1[i]
            for j in range(len(coefficients_inter1)-i-1):
                if j+i+1 not in index_used:
                    for k in range(width+1):
                        if not k==width:
                            if not (exponents_inter2[t][k]-x1[k])==(exponents_inter1[j+i+1][k]-x2[k]):
                                break
                        elif ((not coefficients_inter2[t]/sign1==coefficients_inter1[j+i+1]/sign2)):
                            break
                        else:
                            coefficients_inter2[t]=(sign3/sign1)*coefficients_inter2[t]
                            exponents_inter2[t]=exponents_inter2[t]+x3-x1
                            index_used[s]=j+i+1
                            s+=1
            t+=1
    return zero_term_remove(exponents_inter2,coefficients_inter2)

# combines the functions in this block to preform the overall simplififaction
def optimize_function(exponents_inter,coefficients_inter):
    width=8
    # Components with coefficients of 0 are removed
    exponents_inter1,coefficients_inter1=zero_term_remove(exponents_inter,coefficients_inter)
    # Components with identical exponents are summed and otherwise simplified
    # Runs until no simplification can be done
    N0=0
    N1=1
    while(not N0==N1):
        N0=len(coefficients_inter1)
        exponents_inter1,coefficients_inter1=sum_components(exponents_inter1,coefficients_inter1,width)
        for i in range(6):
            for j in range(6):
                exponents_inter1,coefficients_inter1=formula_simplification(exponents_inter1,coefficients_inter1,width,i,j)
        N1=len(coefficients_inter1)
    return exponents_inter1,coefficients_inter1


# %%
# Completes the g(xi) to g'(xi) convertion shown in (22) in the documentation
def der_1( ls, d ):
    """
    The derivative of g(xi) is calculated.
    Spesifically, the derivative of g multiplied by R^2
    """

    rs = []
    for cof,exp in ls:
        terms = [ (  exp[0]*cof, exp+[-1,0,0,0,0,0,2,0] )
                , ( ( exp[2]+ exp[3]+ exp[6]+ exp[7])*cof
                    , exp+[1,0,0,0,0,0,0,0] )
                , (  exp[2]*cof, exp+[0,1,-1,1,0,0,0,0] )
                , ( - exp[3]*cof, exp+[0,1,1,-1,0,0,0,0] )
                , (  exp[7]*cof,  exp+[0,1,1,1,0,2,0,-2] ) ]
        terms = [ (x,y) for (x,y) in terms if x != 0 ]
        rs.extend( terms )

    rr = [ ( cof, exp+np.array([0,0,0,0,0,0,2,2]) ) for cof,exp in ls ]
    # The g(xi) to g'(xi) conversion is preformed
    for cof,exp in rs:
        rr.extend( [ ( -(2*d-3)*cof*3, exp+np.array([1,0,0,0,0,0,2,2]) )
                    , ( -(2*d-3)*cof, exp+np.array([0,1,1,1,0,2,2,0]) ) ] )

    # return optimize_function(exponents_inter,coefficients_inter)
    cof1 = np.array( [ x for x in rr[0] ] )
    exp1 = np.array( [ x for x in rr[1] ] )
    return optimize_function(exp1,cof1)

# Completes the g(xi) to g'(xi) convertion shown in (23) in the documentation
def der_2( ls, d ):
    """
    The derivative of g(xi) is calculated.
    Spesifically, the derivative of g multiplied by R^2
    """
    rs = []
    for cof,exp in ls:
        terms = [ ( cof*exp[1],  exp + [0,-1,0,0,0,0,2,0] )
                , ( (exp[2]+exp[3]+exp[6]+exp[7])*cof
                    , exp + [0,1,0,0,0,0,0,0] )
                , ( -exp[2]*cof, exp+[1,0,-1,1,0,0,0,0] )
                , ( exp[3]*cof, exp+[1,0,1,-1,0,0,0,0] )
                , ( -exp[7]*cof, exp+[1,0,1,1,0,2,0,-2] )
                 ]
        terms = [ (x,y) for (x,y) in terms if x != 0 ]
        rs.extend( terms )

    rr = [ ( cof, exp+np.array([0,0,0,0,0,0,2,2]) ) for cof,exp in ls ]
    # The g(xi) to g'(xi) conversion is preformed
    for cof,exp in ls:
        rr.extend( [ ( -(2*d-3)*cof*3, exp+np.array([0,1,0,0,0,0,2,2]) )
                   , ( (2*d-3)*cof, exp+np.array([1,0,1,1,0,2,2,0]) )
                   ] )
    cof1 = np.array( [ x for x in rr[0] ] )
    exp1 = np.array( [ x for x in rr[1] ] )
    return optimize_function(exp1,cof1)


# %%
# der_1 and der_2 are used to calculate the g(xi)-functions for all the derivatives of the lens potential up to and including
# what is set by the order variable. The variable width determines how many components in g(xi) there can be.
# It is kept as low as possible to avoid storage of needless values. 

def find_exp_cof( order=10 ):

    dd = { (2,0) : [ (  1, np.array( [0,2,0,0,0,0,0,0] ) ) ],
           (1,1) : [ ( -1, np.array( [1,1,0,0,0,0,0,0] ) ) ],
           (0,2) : [ (  1, np.array( [2,0,0,0,0,0,0,0] ) ) ] }

    # Compute $\partial^d/(\partial x^i\partial y^j) \psi$

    for d in range(3,order+1):
        for j in range(d+1):

            i = d-j

            if i >= j:
                ls = dd[ (i-1, j) ]
                exp_out,cof_out = der_1( ls, d-1 )
            else:
                ls = dd[ (i, j-1) ]
                exp_out,cof_out = der_2( ls, d-1 )

            dd[(i,j)] = list( zip( cof_out, exp_out ) )

    return dd


import json
print( json.dumps( find_exp_cof() ) )
