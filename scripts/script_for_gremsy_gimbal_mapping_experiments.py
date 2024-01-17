import numpy as np

def distance_3_sensitivity(delta_a_i, a0, alphas, betas, gammas, N):
    
    a_plus_1_prime = [1]*(N+1)
    a_plus_1_prime[0] = a0 + delta_a_i
    
    b_prime = [1]*N
    
    for idx in range(1, N+1):
        a_plus_1_prime[idx] = a_plus_1_prime[idx-1] * (np.sin(betas[idx-1])/np.sin(gammas[idx-1]))
        b_prime[idx-1] = a_plus_1_prime[idx-1]*(np.sin(alphas[idx-1])/np.sin(gammas[idx-1]))
    
    print(" a' : ", a_plus_1_prime[1:])
    print(" b' : ", b_prime)

# Refer to Excel document with the experiment setup
a = [1.985, 1.955, 1.93, 1.91, 1.895, 1.884, 1.878, 1.879, 1.882, 1.892, 1.906, 1.926, 1.949]
b = [0.1]*(len(a)-1)
N = len(b)

alphas = []
betas = []
gammas = []
for idx, val in enumerate(b):
    alphas.append( ((a[idx]**2) + (a[idx+1]**2) - (val**2))/ (2 * a[idx] * a[idx+1]) )
    betas.append( ((val**2) + (a[idx]**2) - (a[idx+1]**2))/ (2 * val * a[idx]) )
    gammas.append( ((val**2) + (a[idx+1]**2) - (a[idx]**2))/ (2 * val * a[idx+1]) )
    
alphas = np.arccos(alphas)
betas = np.arccos(betas)
gammas = np.arccos(gammas)

for i in range(len(alphas)):
    print('Idx: ', i+1, ', ALPHAS: ', np.rad2deg(alphas[i]), ', BETAS: ', np.rad2deg(betas[i]), ', GAMMAS: ', np.rad2deg(gammas[i]))

print('CHECK TRIANGLE ANGLE SUM: ', np.rad2deg(alphas+betas+gammas))

distance_3_sensitivity(150, a[0], alphas, betas, gammas, N)