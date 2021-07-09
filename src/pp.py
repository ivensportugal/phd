f = open('../data/trucks/Trucks.txt', 'r')
for line in f:
  datapoint = line.split(';')
  _id = datapoint[0]
  f2 = open('../process/preprocessed/'+_id+'.txt', 'a')
  f2.write(line)

f.close()
f2.close() 
