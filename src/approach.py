# from process import preprocess
from process   import process
from lifecycle import preprocess_size
from lifecycle import process_size
from graph     import preprocess_neo4j

from datetime import datetime


''' The main function '''
def main():

# Common Processing
	# clusters
	# preprocess()
	# process()

# Processing for Lifecycle
	# lifecycle
	# preprocess_size()
	# process_size()

# Processing for Graph Analysis
	preprocess_neo4j()



if __name__ == '__main__':
	main()