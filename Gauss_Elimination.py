# Gauss Elimination  method is one of well known methods to solve set of simultaneous equations

import numpy as np

a = np.array([[3,-2,5,0],[4,5,8,1],[1,1,2,1],[2,7,6,5]],float)

b = np.array([2,4,5,7],float)

n = len(b)
x=np.zeros(n,float)

# forward elimination technique to obtain lower diagonal matrix elements as zeros

# A.x=B
for k in range(n - 1):
    for i in range(k + 1, n):
        if a[i, k] == 0: continue
        factor = a[k, k] / a[i, k]
        for j in range(k, n):
            a[i, j] = (a[k, j] - factor * a[i, j])
        b[i] = b[k] - factor * b[i]

print(a)
print(b)

#backward substituion to computer the coefficients

# back substitution
x[n-1]=b[n-1]/a[n-1,n-1]


for i in range(n-2,-1,-1):
    sum=0
    for j in range(i+1,n):
        sum=sum+a[i,j]*x[j]
    x[i]=(b[i]-sum)/a[i,i]
print('The solution of the sytem')
print(x)

#The solution of the sytem
#[ 28.77777778   2.16666667 -16.           6.05555556
# verify with the equation
#output=2*28.77778 +7*2.166667 +6*(-16)+ 5*6.05556 = 6.9999