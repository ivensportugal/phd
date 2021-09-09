import os
import shutil

from constant import file_suffix

def identify_trajectories(dir):
  files = []
  for file in os.listdir(dir):
    if file.endswith(file_suffix):
      files.append(file)
  return files

def identify_clusters(dir):
	return identify_trajectories(dir)


def save_relation(path, s):
 	f = open(path, 'a')
	f.write(s + '\n')
	f.close()


def create_folder(path):
  if not os.path.exists(path): os.makedirs(path)
def delete_folder(path): shutil.rmtree(path)