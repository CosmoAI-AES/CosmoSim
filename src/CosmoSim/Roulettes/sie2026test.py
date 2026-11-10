# This is Martin's code for comparison with sie2026.py

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
def der_1(exponents_inp,coefficients_inp,d):
    # The derivative of g(xi) is calculated. Spesifically, the derivative of g multiplied by R^2
    der_exponents_inp=np.zeros((5*len(exponents_inp),8))
    der_coefficients_inp=np.zeros(5*len(coefficients_inp))
    k=0
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[-1,0,0,0,0,0,2,0]
        der_coefficients_inp[k]=exponents_inp[i][0]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[1,0,0,0,0,0,0,0]
        der_coefficients_inp[k]=(exponents_inp[i][2]+exponents_inp[i][3]+exponents_inp[i][6]+exponents_inp[i][7])*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[0,1,-1,1,0,0,0,0]
        der_coefficients_inp[k]=exponents_inp[i][2]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[0,1,1,-1,0,0,0,0]
        der_coefficients_inp[k]=-exponents_inp[i][3]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[0,1,1,1,0,2,0,-2]
        der_coefficients_inp[k]=exponents_inp[i][7]*coefficients_inp[i]
        k+=1
    der_exponents_inp,der_coefficients_inp=zero_term_remove(der_exponents_inp,der_coefficients_inp)
    exponents_inter=np.zeros((7*len(exponents_inp),8))
    coefficients_inter=np.zeros(7*len(coefficients_inp))
    # The g(xi) to g'(xi) conversion is preformed
    k=0
    for i in range(len(der_coefficients_inp)):
        coefficients_inter[k]=der_coefficients_inp[i]
        exp=der_exponents_inp[i]+np.array([0,0,0,0,0,0,2,2])
        exponents_inter[k]=exp
        k+=1
    for i in range(len(coefficients_inp)):
        coefficients_inter[k]=-(2*d-3)*coefficients_inp[i]*3
        exp=exponents_inp[i]+np.array([1,0,0,0,0,0,2,2])
        exponents_inter[k]=exp
        k+=1
    for i in range(len(coefficients_inp)):
        coefficients_inter[k]=-(2*d-3)*coefficients_inp[i]
        exp=exponents_inp[i]+np.array([0,1,1,1,0,2,2,0])
        exponents_inter[k]=exp
        k+=1
    return optimize_function(exponents_inter,coefficients_inter)

# Completes the g(xi) to g'(xi) convertion shown in (23) in the documentation
def der_2(exponents_inp,coefficients_inp,d):
    # The derivative of g(xi) is calculated. Spesifically, the derivative of g multiplied by R^2
    der_exponents_inp=np.zeros((5*len(exponents_inp),8))
    der_coefficients_inp=np.zeros(5*len(coefficients_inp))
    k=0
    for i in range(len(coefficients_inp)):
        der_exponents_inp[i]=exponents_inp[i]+[0,-1,0,0,0,0,2,0]
        der_coefficients_inp[i]=exponents_inp[i][1]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[0,1,0,0,0,0,0,0]
        der_coefficients_inp[k]=(exponents_inp[i][2]+exponents_inp[i][3]+exponents_inp[i][6]+exponents_inp[i][7])*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[1,0,-1,1,0,0,0,0]
        der_coefficients_inp[k]=-exponents_inp[i][2]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[1,0,1,-1,0,0,0,0]
        der_coefficients_inp[k]=exponents_inp[i][3]*coefficients_inp[i]
        k+=1
    for i in range(len(coefficients_inp)):
        der_exponents_inp[k]=exponents_inp[i]+[1,0,1,1,0,2,0,-2]
        der_coefficients_inp[k]=-exponents_inp[i][7]*coefficients_inp[i]
        k+=1
    der_exponents_inp,der_coefficients_inp=zero_term_remove(der_exponents_inp,der_coefficients_inp)
    exponents_inter=np.zeros((7*len(exponents_inp),8))
    coefficients_inter=np.zeros(7*len(coefficients_inp))
    # The g(xi) to g'(xi) conversion is preformed
    k=0
    for i in range(len(der_coefficients_inp)):
        coefficients_inter[k]=der_coefficients_inp[i]
        exp=der_exponents_inp[i]+np.array([0,0,0,0,0,0,2,2])
        exponents_inter[k]=exp
        k+=1
    for i in range(len(coefficients_inp)):
        coefficients_inter[k]=-(2*d-3)*coefficients_inp[i]*3
        exp=exponents_inp[i]+np.array([0,1,0,0,0,0,2,2])
        exponents_inter[k]=exp
        k+=1
    for i in range(len(coefficients_inp)):
        coefficients_inter[k]=(2*d-3)*coefficients_inp[i]
        exp=exponents_inp[i]+np.array([1,0,1,1,0,2,2,0])
        exponents_inter[k]=exp
        k+=1
    return optimize_function(exponents_inter,coefficients_inter)


# %%
# der_1 and der_2 are used to calculate the g(xi)-functions for all the derivatives of the lens potential up to and including
# what is set by the order variable. The variable width determines how many components in g(xi) there can be.
# It is kept as low as possible to avoid storage of needless values. 

def find_exp_cof():
    # The highest order derivative of the lens potential calculated. Higher orders take longer to calculate.
    order=10
    # Width must be increaced if higher orders are calculated
    width=320
    # Creates the list of derivatives that will be calculated.
    N=order-1
    derivatives=np.array([[0,0],[1,0],[0,1]])
    for i in range(N):
        for j in range(i+3):
            derivatives=np.concatenate((derivatives,[[i+2-j,j]]))
    exponents_list=np.zeros((len(derivatives),width,8))
    coefficients_list=np.zeros((len(derivatives),width))
    # The starting second order derivatives of the potential are put into the list
    g11_exponents=np.array([[0,2,0,0,0,0,0,0]])
    g11_coefficients=[1]
    g12_exponents=np.array([[1,1,0,0,0,0,0,0]])
    g12_coefficients=[-1]
    g22_exponents=np.array([[2,0,0,0,0,0,0,0]])
    g22_coefficients=[1]
    for i in range(len(g11_coefficients)):
        exponents_list[3][i]=g11_exponents[i]
        coefficients_list[3][i]=g11_coefficients[i]
        exponents_list[4][i]=g12_exponents[i]
        coefficients_list[4][i]=g12_coefficients[i]
        exponents_list[5][i]=g22_exponents[i]
        coefficients_list[5][i]=g22_coefficients[i]
    # The g(xi)-functions for all the derivatives of the lens potential are calculated. 
    for i in range(len(derivatives)-6):
        der=derivatives[i+6]
        print( "[find_exp_cof]", der )
        d=der[0]+der[1]
        der_x=der-[1,0]
        der_y=der-[0,1]
        if (der[0]<=der[1] or der[1]==0) and not der[0]==0 :
            d1=d-1
            index=int(d1*(d1+1)/2+der_x[1])
            x=True
        else:
            d1=d-1
            index=int(d1*(d1+1)/2+der_y[1])
            x=False
        exp=exponents_list[index]
        cof=coefficients_list[index]
        for j in range(len(cof)):
            if cof[j]==0:
                index=j
                break
        exp=exp[:index]
        cof=cof[:index]
        if x==True:
            exp_out,cof_out=der_1(exp,cof,d-1)
        else:
            exp_out,cof_out=der_2(exp,cof,d-1)
        for j in range(len(cof_out)):
            exponents_list[i+6][j]=exp_out[j]
            coefficients_list[i+6][j]=cof_out[j]

    exponents_list=exponents_list.astype(np.int64)
    coefficients_list=coefficients_list.astype(np.int64)
    
    return exponents_list,coefficients_list,derivatives

# The output is made into global variables
exponents_list,coefficients_list,derivatives=find_exp_cof()
