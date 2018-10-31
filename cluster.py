import numpy as np
from sklearn.cluster import DBSCAN

from constant import eps
from constant import min_samples

def dbscan(datapoints):

  ## Transform the timestamp above to seconds since Epoch (for Euclidean dist)
  if(datapoints == []): return
  db = DBSCAN(eps=eps, min_samples=min_samples).fit(datapoints)

  return db