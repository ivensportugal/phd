import os

from constant import file_suffix

def identify_trajectories(dir):
  files = []
  for file in os.listdir(dir):
    if file.endswith(file_suffix):
      files.append(file)
  return files