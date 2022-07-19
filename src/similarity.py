import pandas as pd
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

# read file
df = pd.read_csv('/Users/Ivens/Downloads/sizes.csv')

# preprocess by transforming string to list of ints
df['Sizes'] = [[int(n) for n in x.strip('[]').split(',')] for x in df['Sizes']]

# run fastdtw (use third method for tests)
n = len(df['Sizes'])
distances = [[fastdtw(df['Sizes'][i], df['Sizes'][j], dist=euclidean)[0] if (df['Sizes'][i][-1] != df['Sizes'][j][-1]) else 999 for j in range(i+1)] for i in range(n)]
# distances = [[fastdtw(x, y, dist=euclidean)[0] for y in df['Sizes']] for x in df['Sizes']]
# distances = [[fastdtw(x, y, dist=euclidean)[0] for y in df.iloc[0:10,1]] for x in df.iloc[0:10,1]]

# add headers to the columns and lines
d = pd.DataFrame(distances)
d.columns = df.iloc[:len(d),0]
d.insert(0,'Path',df['Path'],True)

# export the result
d.to_csv('/Users/Ivens/Downloads/distances.csv', index=None)