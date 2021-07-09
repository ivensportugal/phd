from sklearn import metrics
import numpy as np
from sklearn.neighbors import DistanceMetric

# Calculates validation metrics at each interaction of the approach
def validate(distances, labels):

  # cohesions   = calculate_cohesion(clusters)
  # separations = calculate_separation(clusters)
  silhouettes = calculate_silhouette(distances, labels)


# # Calculates cohesion
# def calculate_cohesion(clusters):
# 	print('cohesion')



# # Calculates separation
# def calculate_separation(clusters):
# 	print('separation')


# Calculates silhouette
def calculate_silhouette(datapoints, labels):

	# at this point, datapoints wiht a negative label are noise
	# positive labels are clusters.
	# we remove negative labels and associated data from the computation

	valid = np.where(labels >= 0)
	labels = labels[valid]
	datapoints = datapoints[valid]

	# silhouette is defined for more than one cluster
	if len(np.unique(labels)) <= 1:
		return None


	# calculates distances
	metric   = DistanceMetric.get_metric('haversine')
	distances = metric.pairwise(np.radians(datapoints)) * 6371000 # Radius of earth in kilometers * 1000 to get meters



	a = metrics.silhouette_score(distances, labels, metric='precomputed')
	print('silhouette')
	print(a)
	print('end of silhouette')