import sys
import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# location of files
folder = '/Users/Ivens/Downloads/'

# read file
df = pd.read_csv(folder+'sizes'+sys.argv[0][-4]+'.csv')

# define min and max
nmin = int(sys.argv[1])
nmax = int(sys.argv[2])

# preprocess by transforming string to list of ints
df['Sizes'] = [[int(n) for n in x.strip('[]').split(',')] for x in df['Sizes']]

# run fastdtw
n = len(df['Sizes'])
nComparisons = 0

# optimized < n^2 comparisons
distances=[]
for i in range(nmin,min(nmax,n)):
	row = df['Sizes'][i]
	print(i)
	for j in range(n):
		if (j >= i): continue
		column = df['Sizes'][j]
		distance = 0
		# if(j >= i): continue
		# elif(len(list(set(df['Path'][i][1:-1].split(',')) & set(df['Path'][j][1:-1].split(',')))) > 1): continue # if they have 2 intersections
		# else: distance = fastdtw(row, column)[0]; nComparisons = nComparisons + 1
		distance = fastdtw(row, column)[0]; nComparisons = nComparisons + 1
		distances.append([df['Path'][i],df['Path'][j],str(row),str(column),distance])

# comparisons with only one case
# distances=[]
# for i in range(n):
# 	row = df['Sizes'][i]
# 	for j in range(1):
# 		column = [5, 5, 8, 8, 7, 7, 6, 6]
# 		distance = 0
# 		if(j > i): continue
# 		else: distance = fastdtw(row, column)[0]
# 		distances.append([[170228,170269,170315,170348],df['Path'][i],str(row),str(column),distance])

d = pd.DataFrame(distances)
d.columns = ['Path1','Path2','Size1','Size2','Distance']


# d10 = d[d['Distance']<10]
# d15 = d[(d['Distance']>=10) & (d['Distance']<15)]
# d20 = d[(d['Distance']>=15) & (d['Distance']<20)]

# print reports to the user
# print('Number of cases where distance < 10: ' + str(len(d10)))
# print('Number of cases where distance < 15: ' + str(len(d15)))
# print('Number of cases where distance < 20: ' + str(len(d20)))

# export the result
# d10.to_csv(folder+'distances10.csv', index=None)
# d15.to_csv(folder+'distances15.csv', index=None)
# d20.to_csv(folder+'distances20.csv', index=None)

# Case Study 3 Results
print('Case: ' + str(sys.argv[1] + ' - ' + str(sys.argv[2])))
print('')
print('Number of cluster paths           : ' + str(n))
print('Number of cluster path comparisons: ' + str(nComparisons))
print('Sum of distance values            : ' + str(d['Distance'].sum()))
print('Coefficient of similarity         : ' + str(nComparisons/d['Distance'].sum()))
