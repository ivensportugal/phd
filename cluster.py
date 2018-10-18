import numpy as np
from sklearn.cluster import DBSCAN

def dbscan(datapoints):

  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  X = [[(row[2] - datetime(1970,1,1)).total_seconds()] for row in datapoints]
  if(X == []): return
  db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)

  return db