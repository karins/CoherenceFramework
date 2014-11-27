"""

Input format (ignore the header and the first column, they are there just for illustration)

    e1 e2 e3
s1  S  -  O
s2  -  S  -
s3  S  O  X

"""

import numpy as np

r2i = {'S': 3, 'O': 2, 'X': 1, '-': 0}

doc = np.array([np.array([r2i[r] for r in line.strip().split()]) for line in D])
# if you want you can transpose it

# read all docs first into T

U = np.zeros(len(r2i), int)
# 0 0 0 0
B = np.zeros((len(r2i), len(r2i)), int)

# counts
for doc in corpus:
    for entity_roles in doc.transpose():
        for r in entity_roles:
            U[r] += 1
        for ri, rj in pairwise(entity_roles):
            B[ri,rj] += 1

# dump it somehow


