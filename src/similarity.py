import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# read file
df = pd.read_csv('/Users/Ivens/Downloads/sizes.csv')

# preprocess by transforming string to list of ints
df['Sizes'] = [[int(n) for n in x.strip('[]').split(',')] for x in df['Sizes']]

# run fastdtw (use third method for tests)
n = len(df['Sizes'])

distances=[]
for i in range(n):
	row = []
	for j in range(n):
		distance = 0
		if(j > i): distance = 999
		elif(df['Sizes'][i][1]  == df['Sizes'][j][1]): distance = 999
		elif(df['Sizes'][i][-1] == df['Sizes'][j][-1]): distance =  999
		else: distance = fastdtw(df['Sizes'][i], df['Sizes'][j])[0]
		row.append(distance)
	distances.append(row)



# add headers to the columns and lines
d = pd.DataFrame(distances)

# print some reports to user
print('Number of cases: ' + str((d < 10).sum(axis=1).sum()))

d.columns = df.iloc[:len(d),0]
d.insert(0,'Path',df['Path'],True)

# export the result
d.to_csv('/Users/Ivens/Downloads/distances.csv', index=None)