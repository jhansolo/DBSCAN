# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 15:22:17 2019

independednt implememntation of DBSCAN using only numpy and pandas
no scikit-learn involved

testing data from http://cs.joensuu.fi/sipu/datasets/

currently using 2D training and testing data. Can also use higher-dimensional vectors 

good performance on irregular groupings (concavity, linear formation, etc)

next iteration: speed optimization and hyperparameter automation

@author: jh
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import copy
 

def loadData():
    """load training data. in my case, points generated in CAD and coordinates 
    written to a text file. refer to "points.csv" for formatting"""
    
    path=r"points.csv"
    points=pd.read_csv(path).astype(float)
    dim=points.shape[1]
    points['clusterId']=0                               #adding cluster ID column for tagging each point
    points['status']=0                                  # 1=core pt, 2=border pt, 3=outlier
    
    return points, np.array([points['x'],points['y']]).T, dim   # return a pd dataframe as well as a numpy array of the coordinates since it's faster to work with

def calcDist(centerIndex,points,dim):
    """basic Euclidean norm operation"""
    center=points[centerIndex]
    distVec=points-center
    return np.linalg.norm(distVec,axis=1)

def find(seed,frame,pts,dim,eps,minPts,clusterId):
    """finds all the neighboring points within the eps radius of the starting 'seed' point"""
    for i in seed:
        dist=calcDist(i,pts,dim)
        currentNodes=np.argwhere(dist<eps).flatten('F') 
        ptCount=(len(currentNodes))
        if ptCount>=minPts:
            frame.loc[i,'status']=1
            frame.loc[i,'clusterId']=clusterId
        elif ptCount>1:
            frame.loc[i,'status']=2
            frame.loc[i,'clusterId']=clusterId
        else:
            frame.loc[i,'status']=3
        branch.update(currentNodes)             #set containing the newly found neighbors
        core.update(seed)                       #update the set containing seed pts
        diff=branch.difference(core)            #find differene between original seed set and new set with newly found neighbors. will use this differene again
#    print(core)
    return core,diff,ptCount

def singleCluster(seed,frame,pts,dim,eps,minPts,clusterId):
    """recursively expand the neighborhood"""
    core,diff,count=find(seed,frame,pts,dim,eps,minPts,clusterId)
    while len(diff)!=0: #still room to expand
        seed=copy.deepcopy(diff)
        core,diff,count=find(seed,frame,pts,dim,eps,minPts,clusterId)
        print(core)
    return core


"""loading data"""
frame,pts,dim=loadData()        #frame = pd dataframe, pts=numpy array, dim = scalar
core=set()                      #set containig starting pts
branch=set()                    #set containing new neighbors

"""hyper parameters, to be optimized and automated in next iteration"""
eps=20000
minPts=80

"""initial cluster ID, starting at 1"""
clusterId=1

"""cycle through all points, expand if not already tagged and possible"""
for i in range(len(frame)):
    if frame.loc[i,'clusterId']==0:
        seed=[i]
        core=singleCluster(seed,frame,pts,dim,eps,minPts,clusterId)
        clusterId+=1        #update the cluster ID after having exahusted searching and tagging one cluster

"""plotting"""    
clusterIds=frame['clusterId'].unique() #list of unique cluster IDs
clusterNum=len(clusterIds)              # number of unique clusters

"""normalizing: if there are outliers, their clusterId will be 0. this is 
problematic for plotting if the other clusters have id of up to 10, 20....100
since the colors are applied based on the value of the clusterIds. It would skew
the entire colormap spectrum. The lines below linearizes the differene between
all the different cluster Ids. Purely for plotting reasons"""

remapIds=np.linspace(1,clusterNum,clusterNum)

for i in range(len(clusterIds)):
    frame.loc[frame['clusterId']==clusterIds[i],'clusterId']=remapIds[i]

clusterIds2=frame['clusterId'].unique()


plt.style.use('classic')
plt.clf()
plt.scatter(x=frame['x'],y=frame['y'],s=20,c=frame['clusterId'],cmap=cm.get_cmap('rainbow',clusterNum))
plt.axes().set_aspect('equal', 'datalim')
plt.axis('off')