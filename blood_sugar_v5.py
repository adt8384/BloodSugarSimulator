import sys
import datetime, time
from intervaltree import Interval, IntervalTree
import matplotlib.pyplot as plt
#import numpy
from matplotlib.dates import DateFormatter
import csv


class BloodSugarSimulator:

	def __init__(self, input_file, fooddb_filename, exerdb_filename,
				 duration=1800):
		self.input_file = input_file
		self.fooddb_filename = fooddb_filename
		self.exerdb_filename = exerdb_filename
		
		# Initialize blood sugar count to 80.
		self.blood_sugar_count = 80
		self.glycation_threshold = 150
		self.int_tree = None
		self.ts1 = 0.0
		self.ts2 = 0.0
		# glycation
		self.glycation = 0
		# change interval for plotting graph.
		# default set to 1800s or 30 minutes.
		self.duration = duration
		# Internal data structures used.
		self.x = []
		self.y = []
		self.x1 = []
		self.y1 = []
		self.food_dict = dict()
		self.exer_dict = dict()
		self.food_db = None
		self.exer_db = None
						
	# convert to epoch time
	@staticmethod
	def get_date_time_ts(dt, tm):
		d_fields = dt.split('-')
		tm_fields = tm.split(':')
		t = datetime.datetime(int(d_fields[2]), int(d_fields[0]), int(d_fields[1]),
						  	  int(tm_fields[0]), int(tm_fields[1]))
		return float(time.mktime(t.timetuple()))
	
	# convert to timestr
	@staticmethod
	def get_date_time_hhmm(ts):
		return datetime.datetime.fromtimestamp(ts)

	# load csv into tuple
	@staticmethod
	def load_db_dict (filename):
		dbdict = dict()
		try:
			with open(filename, 'r') as f:
  				reader = csv.reader(f)
  				db = tuple(reader)	
  			if not db:
				raise Exception("No data found in file %s" % filename)		
		
			# build hash table 
			for tup in db:
				if len(tup) !=	3:
					raise Exception("CSV file %s have missing fields." % filename)
				dbdict[tup[0]] = [tup[1], tup[2]]
		
		except Exception as e:
			if isinstance(e, IOError):
				print "Failed to open the input file %s" % filename
			else:
				print "Exception occured %s" % str(e)
			sys.exit(1)
		
		return dbdict

	def load_food_exer_files(self):
		self.food_dict= BloodSugarSimulator.load_db_dict (self.fooddb_filename)
		# get exercise data
		self.exer_dict = BloodSugarSimulator.load_db_dict (self.exerdb_filename)
		
	# create interval tree 
	def create_int_tree(self):
		self.int_tree = IntervalTree()
		currentdate = None
		try:
			# create interval tree from input file activity.out
			fd = open(self.input_file, 'r')
		
			for line in fd:
				fields = line.split()
		
				#set current date for input
				if (currentdate):
					# input can be only for same day
					if (currentdate != fields[0]):
						print "Usage: Enter data for same day only"
						sys.exit(1)
				else:
					# initialise current date
					currentdate = fields[0]	
					# initialise ts1 to beginning of day 9 am
					self.ts1 = BloodSugarSimulator.get_date_time_ts(fields[0], '9:00')
					# initialise ts2 to end of day 7 pm
					self.ts2 = BloodSugarSimulator.get_date_time_ts(fields[0], '19:00')
		
				# check input is Food or Exercise	
				if fields[2] == 'F':
					begin = BloodSugarSimulator.get_date_time_ts(fields[0], fields[1])
					# end time for food is 2 hours.
					end = begin + 7200
					glycemicIndex = self.food_dict[fields[3]][1]
					# check formula 
					data = round((float(glycemicIndex) / 120.0), 2)
					self.int_tree[begin:end] = data
				elif fields[2] == 'E':
					begin = BloodSugarSimulator.get_date_time_ts(fields[0], fields[1])
					# end time for exercise is 1 hour.
					end = begin + 3600
					exerIndex = self.exer_dict[fields[3]][1]
					data = round((float(exerIndex) / 60.0), 2)
					self.int_tree[begin:end] = -data
				else:
					print "Usage: Input can only be of type F or E"
					sys.exit(1)
					
			#first point for blood sugar graph
			self.y.append(self.blood_sugar_count)		
			customdate = BloodSugarSimulator.get_date_time_hhmm(self.ts1)
			self.x.append(customdate)
	
			#first point for glycation graph
			self.y1.append(self.glycation)
			self.x1.append(customdate)		
	
		except Exception as e:
			if isinstance(e, IOError):
				print "Failed to open the input file %s" % input_file
			if isinstance(e, KeyError):
				print "Invalid ID  %s" % str(e)
			else:
				print "Exception occured %s" % str(e)
			sys.exit(1)
	
	
	# create interval tree 
	def compute_values(self):
		# no of seconds 
		secs = 0
		curr_ts = self.ts1
		blood_sugar_count = self.blood_sugar_count
		glycation = self.glycation
		try:
			#while not end of day
			while curr_ts < self.ts2:
				#look up intervals for current timestamp
				ivs = self.int_tree.search(curr_ts)
				if not ivs:
					if (blood_sugar_count - 1) > self.blood_sugar_count:
						blood_sugar_count -= 1
					elif (blood_sugar_count + 1) < self.blood_sugar_count:
						blood_sugar_count += 1
					else:
						blood_sugar_count = self.blood_sugar_count
				else:
					for iv in ivs:
						blood_sugar_count += iv.data
				#compute glycation
				if blood_sugar_count > self.glycation_threshold :
					glycation = glycation + 1
			
				#enter data every 30 mins for graphs
				if ( secs % self.duration == 0):
					#print "%s -> %s -> %s" %(time.strftime('%m-%d-%Y %H:%M', 
					#				time.localtime(ts1)), blood_sugar_count, glycation) 
					#blood sugar
					self.y.append(blood_sugar_count)		
					customdate = BloodSugarSimulator.get_date_time_hhmm(curr_ts)
					self.x.append(customdate)
			
					#glycation
					self.y1.append(glycation)
					self.x1.append(customdate)
		
				#compute values every minute
				curr_ts += 60
		except Exception as e:
			print "Exception occured %s" % str(e)
			sys.exit(1)
	

	def plot_graph_blood_sugar(self):
		b = plt.figure(1)
		formatter = DateFormatter('%H:%M')
		plt.plot(self.x,self.y)
		plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
		plt.xlabel('Time')
		plt.ylabel('Blood Sugar')
		b.show()

	def plot_graph_glycation(self):
		b = plt.figure(2)
		formatter = DateFormatter('%H:%M')
		plt.plot(self.x1,self.y1)
		plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
		plt.xlabel('Time')
		plt.ylabel('Glycation Index')
		b.show()

if len(sys.argv) < 4:
	print "Usage: python compute_blood_sugar.py <input_file> <food_db_file> <exer_db_file"
	exit()

input_file = sys.argv[1]
food_db_file = sys.argv[2]
exer_db_file = sys.argv[3]
try:

	sim = BloodSugarSimulator(input_file, food_db_file, exer_db_file)
	# get food data
	sim.load_food_exer_files()

  	#create interval tree
	sim.create_int_tree()
	
	#compute values for blood sugar count and glycation index
	sim.compute_values()
	
	sim.plot_graph_blood_sugar()
	sim.plot_graph_glycation()
	plt.show()
	
	
except Exception as e:
	print "Exception occured %s" % str(e)
	sys.exit(1)
