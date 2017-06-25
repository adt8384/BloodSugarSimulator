import sys
import datetime, time
from intervaltree import Interval, IntervalTree
import matplotlib.pyplot as plt
#import numpy
from matplotlib.dates import DateFormatter



def get_date_time_ts(dt, tm):
	d_fields = dt.split('-')
	tm_fields = tm.split(':')
	t = datetime.datetime(int(d_fields[2]), int(d_fields[0]), int(d_fields[1]),
						  int(tm_fields[0]), int(tm_fields[1]))
	return float(time.mktime(t.timetuple()))
	

def get_date_time_hhmm(ts):
	return datetime.datetime.fromtimestamp(ts)

if len(sys.argv) < 2:
	print "Usage: python compute_blood_sugar.py <file_name> duration"
	exit()

input_file = sys.argv[1]
# change ts1 to beginning of day which is 9 am
#ts1 = 1498233600.0
#ts1 = get_date_time_ts(time.strftime("%m-%d-%Y"),'9:00')
# change ts2 to end of day.
#ts2 = get_date_time_ts(time.strftime("%m-%d-%Y"), '18:00')
ts1 = 0.0
ts2 = 0.0
# set it to 80 to blood sugar.
blood_sugar_count = 80
# glycation
glycation = 0
# change duration. default set to 1800s or 30 minutes.
duration = 1800
count = 0

x = []
y = []
x1 = []
y1 = []
currentdate = None
try:
	
	fd = open(input_file, 'r')
	int_tree = IntervalTree()
	for line in fd:
		fields = line.split()
		
		if (currentdate):
			if (currentdate != fields[0]):
				#currentdate = fields[0]
				#ts1 = get_date_time_ts(fields[0], '9:00')
				#ts2 = get_date_time_ts(fields[0], '18:00')
				print "Usage: Enter data for same day only"
				exit()
		else:
			currentdate = fields[0]	
			ts1 = get_date_time_ts(fields[0], '9:00')
			ts2 = get_date_time_ts(fields[0], '19:00')
			
		if fields[2] == 'F':
			begin = get_date_time_ts(fields[0], fields[1])
			# end time for food is 2 hours.
			end = begin + 7200
			# check formula 
			data = round((float(fields[3]) / 120.0), 2)
			int_tree[begin:end] = data
		elif fields[2] == 'E':
			begin = get_date_time_ts(fields[0], fields[1])
			# end time for exercise is 1 hour.
			end = begin + 3600
			data = round((float(fields[3]) / 60.0), 2)
			int_tree[begin:end] = -data
	#print int_tree
	
	#print "Blood Sugar Graph:"
	
	#first point for blood sugar
	y.append(blood_sugar_count)		
	customdate = get_date_time_hhmm(ts1)
	x.append(customdate)
	
	#first point for glycation
	y1.append(glycation)
	x1.append(customdate)
	
	
	while ts1 < ts2:
		ivs = int_tree.search(ts1)
		if not ivs:
			 if (blood_sugar_count - 1) > 80:
				blood_sugar_count -= 1
			 elif (blood_sugar_count + 1) < 80:
				blood_sugar_count += 1
			 else:
				blood_sugar_count = 80
		else:
			for iv in ivs:
				blood_sugar_count += iv.data
				#print blood_sugar_count
		
		if blood_sugar_count > 150:
			glycation = glycation + 1
			#print glycation
			
		
		if ( count % 1800 == 0):
			#print "%s -> %s -> %s" %(time.strftime('%m-%d-%Y %H:%M', 
			#				time.localtime(ts1)), blood_sugar_count, glycation) 
			#blood sugar
			y.append(blood_sugar_count)		
			customdate = get_date_time_hhmm(ts1)
			x.append(customdate)
			
			#glycation
			y1.append(glycation)
			x1.append(customdate)
		

		# reset glycation to zero after 1 day
		if (count % 86400 == 0):
			#glycation = 0
			count = 0	
		
		ts1 += 60
		count += 60
	
	# plot blood sugar
	b = plt.figure (1)
	formatter = DateFormatter('%H:%M')
	plt.plot(x,y)
	plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
	plt.xlabel('Time')
	plt.ylabel('Blood Sugar')
	#plt.show()	
	b.show()
	
	#plot glycation index
	g = plt.figure(2)
	formatter = DateFormatter('%H:%M')
	plt.plot(x1,y1)
	plt.gcf().axes[0].xaxis.set_major_formatter(formatter)
	plt.xlabel('Time')
	plt.ylabel('Glycation Index')
	g.show()
	
	plt.show()
	
except IOError as e:
	print "Failed to open the input file %s" % input_file
