from tradera.job import Job
from queue import SimpleQueue

class TestRequestHandler:
	def test_corectness(self):
		data = {}
		Job.get().request_handler(data)
		assert Job.get().notifications.empty()


	def test_with_four_notifications(self):
		data = [
			{'p': "10"},
			{'p': "15"}, 
			{'p': "20"}, 
			{'p': "30"}, 
			{'p': "20"},           #notification
			{'p': "130"}, 
			{'p': "30000"}, 
			{'p': "29999"},
			{'p': "29900"},        #notification
			{'p': "0"},            #notification
			{'p': "11.1111"}       #notification
		]

		expected_results = SimpleQueue()
		expected_results.put("20")
		expected_results.put("29900")
		expected_results.put("0")
		expected_results.put("11.1111")

		for d in data:
			Job.get().request_handler(d)

		while True:
			if Job.get().notifications.empty() or expected_results.empty():
				break
			assert Job.get().notifications.get()["decreased_price"] == expected_results.get()

		assert expected_results.empty()
		assert Job.get().notifications.empty()