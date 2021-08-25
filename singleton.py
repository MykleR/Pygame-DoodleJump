class Singleton:
	"""
		Singleton pattern.
		Overload only class that must have one instance.
		Stores the instance in a static variable: Class.instance
	"""
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(Singleton, cls).__new__(cls)
		return cls.instance
