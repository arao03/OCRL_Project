import numpy as np
from numpy import linalg
from math import pi,exp,sqrt,isnan
from scipy.stats import multivariate_normal
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def GPUpdate(distrib, X, Y, xyGP, zGP, t, ell, dt):

	newUtilities = np.zeros((zGP.size,X.shape[0],X.shape[1]))

	j = 0
	nums = range(1,zGP.size)
	I0 = [i for i, e in enumerate(zGP) if e == 0]
	I1 = [i for i, e in enumerate(zGP) if e != 0]

	neutralCost = 0.3
	Norm0 = 1 / (ell[1] * ell[2] * 2*pi)
	Norm1 = 1 / (ell[1] * ell[2] * 2*pi)

	#update 0 measurements -> 0 utility
	for i in I0:
		t0 = xyGP[i,0]
		mu = [xyGP[i,1], xyGP[i,2]]
		Sigma = [[(ell[1])**2,0], [0, (ell[2])**2]]

		temp1=np.matrix(np.reshape(X,X.size))
		temp2=np.matrix(np.reshape(Y,Y.size))
		x=np.matrix(np.zeros((X.size,2)))
		x[:,0]=temp1.T
		x[:,1]=temp2.T
		
		mvn1 = multivariate_normal(mu,Sigma)
		F = mvn1.pdf(x)
		F=np.matrix(np.reshape(F,X.shape))
		tt = (1 - F/(Norm0 + .00000000000000000000003*(t - t0)))
		newUtilities[j,:,:] = np.multiply(neutralCost, np.clip(tt, None, 1))

		j = j + 1
	
	#update 1 measurements -> 0 utility if new, 1 if old
	for i in I1:
		t0 = xyGP[i,0]
		
		mu = [xyGP[i,1], xyGP[i,2]]
		
		Sigma = np.multiply(((ell[1]*(max(dt,(t-t0)))/ell[0])**2), np.identity(2))
		
		temp1=np.matrix(np.reshape(X,X.size))
		temp2=np.matrix(np.reshape(Y,Y.size))
		x=np.matrix(np.zeros((X.size,2)))
		x[:,0]=temp1.T
		x[:,1]=temp2.T
		
		mvn1 = multivariate_normal(mu,Sigma)
		F = mvn1.pdf(x)
		F=np.matrix(np.reshape(F,X.shape))
		
		newUtilities[j,:,:] = np.add(neutralCost, np.multiply((1-neutralCost), F/Norm1))
		j = j + 1


	# Normalize utility map
	alphas = abs(np.subtract(newUtilities, neutralCost))
	#alphas[alphas == 0] = np.nan

	newUtility = np.divide(np.sum(np.multiply(alphas, newUtilities), axis = 0), np.sum(alphas, axis = 0))
	newUtility[np.isnan(newUtility)] = neutralCost

	normalizedNewUtility = newUtility - neutralCost
	normalizedNewUtility /= newUtility.sum()

	finalUtility = np.clip((distrib + 2*normalizedNewUtility),0,1)
	finalUtility /= finalUtility.sum()

	return finalUtility

"""if __name__ == "__main__":
	# Gridsize
	nx = 50
	ny = 50
	xyGP = np.matrix([[6, 5, 5], [6, 20, 10], [6, 30, 30]]) # xyGP[i,0] = time of observation, xyGP[i,1] = mean_x, xyGP[i,2] = mean_y
	zGP = np.array([1, 0, 1]) # Records a positive (1) or negative (0) observation
	t = 11 # Current time
	ell = np.array([5, 6, 5]) # Standard deviation
	dt = 1
	x = np.linspace(0, nx, 51)
	y = np.linspace(0, ny, 51)
	X, Y = np.meshgrid(x, y)
	newUtility = GPUpdate(X, Y, xyGP, zGP, t, ell, dt)

	#dx, dy = X[1,2] - X[1,1], Y[2,1] - Y[1,1]
	#newUtility /= dx * dy * np.sum(newUtility)
	print(np.sum(newUtility))

	fig = plt.figure()
	ax = fig.gca(projection='3d')
	surf = ax.plot_surface(X, Y, newUtility, cmap=cm.coolwarm,linewidth=0)
	plt.show()"""
