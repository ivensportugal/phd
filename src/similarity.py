import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# read file
df = pd.read_csv('/Users/Ivens/Downloads/sizes.csv')

# preprocess by transforming string to list of ints
df['Sizes'] = [[int(n) for n in x.strip('[]').split(',')] for x in df['Sizes']]

# run fastdtw
n = len(df['Sizes'])

distances=[]
for i in range(n):
	row = df['Sizes'][i]
	for j in range(n):
		column = df['Sizes'][j]
		distance = 0
		if(j > i): distance = 999
		elif(row[1]  == column[1]): distance = 999
		elif(row[-1] == column[-1]): distance = 999
		else: distance = fastdtw(row, column)[0]
		distances.append([df['Path'][i],df['Path'][j],str(row),str(column),distance])

d = pd.DataFrame(distances)
d.columns = ['Path1','Path2','Size1','Size2','Distance']

# print satisfying cases to the user
# print(d[d['Distance']<10])

d10 = d[d['Distance']<10]
d15 = d[d['Distance']<15]
d20 = d[d['Distance']<20]

# print reports to the user
print('Number of cases where distance < 10: ' + str(len(d10)))
print('Number of cases where distance < 15: ' + str(len(d15)))
print('Number of cases where distance < 20: ' + str(len(d20)))

# export the result
d10.to_csv('/Users/Ivens/Downloads/distances10.csv', index=None)
d15.to_csv('/Users/Ivens/Downloads/distances15.csv', index=None)
d20.to_csv('/Users/Ivens/Downloads/distances20.csv', index=None)