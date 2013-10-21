import analyzer

class EWMAAnalyzer(analyzer.Analyzer):
	
	def __init__(self, mainid, subid, field):
		self.mainid = mainid 
		self.subid = subid
		self.field = field
		self.last_value = None

		values = csv_configurator.readDictionary("AnalyzerConfig.csv")[self.__class__.__name__]
		self.st = values['st']
		self.p_st = values['p_st']
		self.ewmv = values['ewmv']
		self.p_ewmv = values['p_ewmv']
		self.L = values['L'] 
	
	def passDataSet(self, data):
		mainid = self.mainid
		subid = self.subid
		field = self.field
		value = data[mainid][subid][field]
	 	timestamp = data[mainid][subid]["timestamp"]
	
		if self.last_value is None:
			self.last_value = data[mainid][subid][field]
			return

		t = value - self.last_value
		self.st = self.p_st * t + (1 - self.p_st) * self.st
		self.ewmv = self.p_ewmv * (t - self.st)**2 + (1 - self.p_ewmv) * self.ewmv

		lower_bound = self.st - self.L * math.sqrt(self.ewmv * self.p_st / (2 - self.p_st))
		upper_bound = self.st + self.L * math.sqrt(self.ewmv * self.p_st / (2 - self.p_st))

		parameterdump = OrderedDict([
			("mainid", self.mainid),
			("subid", self.subid),
			("last_value", self.last_value),
			("L", self.L),
			("st", self.st),
			("p_st", self.p_st),
			("ewmv", self.ewmv),
			("p_ewmv", self.p_ewmv),
			("value", value),
			("t", t),
			("lower_bound", lower_bound),
			("upper_bound", upper_bound)
		])

		self.last_value = data[mainid][subid][field]
			
		# print >> sys.stderr, parameterdump		

		if lower_bound - t > 6e-14:
			return (self.__class__.__name__, mainid, subid, "LowValue", timestamp, timestamp, "%s < %s" % (t, lower_bound), str(parameterdump))
		if upper_bound - t < -6e-14:
			return (self.__class__.__name__, mainid, subid, "HighValue", timestamp, timestamp, "%s > %s" % (t, upper_bound), str(parameterdump))
