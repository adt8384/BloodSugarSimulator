import sys
import datetime, time
from intervaltree import Interval, IntervalTree


def get_date_time_ts(dt, tm):
	d_fields = dt.split('-')
	tm_fields = tm.split(':')
	t = datetime.datetime(int(d_fields[2]), int(d_fields[0]), int(d_fields[1]),
						  int(tm_fields[0]), int(tm_fields[1]))
	return float(time.mktime(t.timetuple()))

if len(sys.argv) < 2:
	print "Usage: python compute_blood_sugar.py <file_name> duration"
	exit()

input_file = sys.argv[1]
# change ts1 to beginning of day which is 9 am
#ts1 = 1498233600.0
ts1 = get_date_time_ts(time.strftime("%m-%d-%Y"),'9:00')
# change ts2 to end of day.
ts2 = get_date_time_ts(time.strftime("%m-%d-%Y"), '18:00')
# set it to 80 to blood sugar.
blood_sugar_count = 80
# glycation
glycation = 0
# change duration. default set to 1800s or 30 minutes.
duration = 1800
count = 0
gg = dict()
try:
	fd = open(input_file, 'r')
	int_tree = IntervalTree()
	for line in fd:
		fields = line.split()
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
	print "Blood Sugar Graph:"
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
		
		if blood_sugar_count > 150:
			glycation += 1
			
		
		if ( count % 1800 == 0):
			print "%s -> %s" %(time.strftime('%m-%d-%Y %H:%M', 
							time.localtime(ts1)), blood_sugar_count) 
			gg[ts1] = glycation
		
		# reset glycation to zero after 1 day
		if (count % 86400 == 0):
			glycation = 0
			count = 0	
		
		ts1 += 60
		count += 60
	print "Glycation Graph:"
	for g in gg:
		print "%s -> %s" %(time.strftime('%m-%d-%Y %H:%M',
						time.localtime(g)),gg[g])
	
except IOError as e:
	print "Failed to open the input file %s" % input_file
