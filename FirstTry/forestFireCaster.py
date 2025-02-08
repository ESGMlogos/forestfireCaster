import numpy as np
import random
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# 1: On Fire
# 0: Unburnt
# -1: Burnt
Lattice = np.zeros((120,120))
Lattice[60,60] = 1
cmap = ListedColormap(["black","green","yellow"])
print(Lattice)
plt.imshow(Lattice,interpolation = "nearest", cmap = cmap)
plt.colorbar()
plt.show()

def ignite(i,j, Lattice = Lattice):
    try:
        if Lattice[i,j] == 0:
            Lattice[i,j] = 1
    except:
        pass

stop = False

def spread(p, Lattice = Lattice):
    global stop
    stop = False
    Probabilities = np.arange(0.01, 1.01, 0.01)
    Fire = []
    for i in range(Lattice.shape[0]):
        for j in range(Lattice.shape[1]):
            if Lattice[i,j] == 1:
                Fire.append((i,j))
                Lattice[i,j] = -1
    if len(Fire) == 0:
        stop = True
    for tree in Fire:
        p_t = np.random.choice(Probabilities)
        if p_t <= p:
            spread = True
        else:
            spread = False
        if spread:
            ignite(tree[0]+1, tree[1])
            ignite(tree[0]-1, tree[1])
            ignite(tree[0], tree[1]+1)
            ignite(tree[0], tree[1]-1)
    return Lattice


# n = 1
# while n <= 100 and not stop:
#     Lattice = spread(0.67)
#     print("n = ", n)
#     plt.imshow(Lattice, interpolation = "nearest", cmap = cmap)
#     plt.colorbar()
#     plt.show()
#     if stop:
#         print(f"Fire died out at the n = {n} iteration")
#         plt.imshow(Lattice,interpolation = "nearest", cmap = cmap)
#         plt.colorbar()
#         plt.show()
#     n += 1


n = 1
while (not stop) and (n <= 100):
    Lattice = spread(0.58
                     )
    if n == 10 or n == 20 or n == 40 or n == 60 or n == 100:
        print("n = ", n)
        plt.imshow(Lattice,interpolation = "nearest", cmap = cmap)
        plt.colorbar()
        plt.show()
    if stop:
        print(f"Fire died out at the n = {n} iteration")
        plt.imshow(Lattice,interpolation = "nearest", cmap = cmap)
        plt.colorbar()
        plt.show()
    n += 1


