import requests, json

class UrlScan():
	def __init__(self, apikey="", url="", public=False):
		assert len(apikey) > 0, "API key must be defined"
		assert len(url) > 0, "Url must be defined"
		assert type(public) == type(True), "Public must be a boolean"
		self.apikey = apikey
		self.url = url
		self.public = public
		self.scanid = None

	def submit(self):
		header = {'API-Key': self.apikey}
		req = {"url": self.url}

		if self.public:
			req['public'] = "on"

		s = requests.post("https://urlscan.io/api/v1/scan/", data=req, headers=header)

		if s.status_code == 200:
			self.scanid = json.loads(s.text)['uuid']
		else:
			s.raise_for_status()

	def checkStatus(self):
		header = {'API-Key': self.apikey}

		r = requests.get("https://urlscan.io/api/v1/result/%s/" % self.scanid, headers=header)

		if r.status_code == 404:
			r.raise_for_status()

		return r

	def getScreenshot(self):
		self.checkStatus()
		header = {'API-Key': self.apikey}

		screen = requests.get("https://urlscan.io/screenshots/%s.png" % self.scanid, headers=header)

		if screen.status_code == 200:
			return screen.content
		else:
			screen.raise_for_status()
