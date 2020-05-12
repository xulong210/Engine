#__author:"xulong"
#date:   2020/2/2

arr = [1,2,4,1,7,8,3]

def sort(arr,i):
    if i == 0:
        return arr[0]
    if i == 1:
        return max(arr[0],arr[1])
    else:
        A = sort(arr,i-2) + arr[i]
        B = sort(arr,i-1)
        return max(A,B)

import numpy as np
def Sort(arr):
    opt = np.zeros(len(arr))
    opt[0] = arr[0]
    opt[1] = max(arr[0],arr[1])
    for i in range(2,len(arr)):
        A = opt[i-2] + arr[i]
        B = opt[i-1]
        opt[i] = max(A,B)
    return opt[len(arr) - 1]

if __name__ == "__main__":
    print(Sort(arr))
