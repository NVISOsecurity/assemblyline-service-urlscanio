from time import sleep
from urlscan import *

from assemblyline_v4_service.common.base import ServiceBase
from assemblyline_v4_service.common.result import Result, ResultSection, BODY_FORMAT

class UrlScanIo(ServiceBase):
	def __init__(self, config=None):
		super(UrlScanIo, self).__init__(config)

	def start(self):
		self.log.debug("Urlscan.io service started")

	def stop(self):
		self.log.debug("Urlscan.io service ended")

	def wait_processing(self, u):
		completed = 0

		# Checks if there's a result on the API page
		while not completed:
			try:
				response = u.checkStatus()
				completed = 1
			except requests.exceptions.HTTPError:
				completed = 0

		# If there's a result but this one is still being processed we wait
		while "notdone" in response.json().values():
			sleep(1)
			response = u.checkStatus()

		return response

	def execute(self, request):
		result = Result()
		url = request.task.metadata.get('submitted_url')
		api_key = request.get_param("api_key")
		public = request.get_param("public")

		u = UrlScan(apikey=api_key, url=url, public=public)
		u.submit()

		# We need to wait for the API to process our request
		response = self.wait_processing(u)

		# We get the response parts that we want and merge them all together
		report = {
			**response.json()["verdicts"]["overall"],
			**response.json()["lists"],
			**response.json()["page"]
		}

		# We convert the "certicates" section from a list of dictionnaries to a dictionnary of lists
		certificates = report.pop("certificates")
		certificates = {k: [dic[k] for dic in certificates] for k in certificates[0]}

		# We add the converted section to the report
		report = {**report, **certificates}

		# We create the KEY_VALUE section to add the report to the result page
		kv_section = ResultSection("Urlscan.io report", body_format=BODY_FORMAT.KEY_VALUE, body=json.dumps(report))

		for domain in report["domains"]:
			kv_section.add_tag("network.static.domain", domain.strip())

		result.add_section(kv_section)

		# We get the preview of the website
		screenshot = u.getScreenshot()
		with open(self.working_directory + "/preview.png", "wb") as ofile:
			ofile.write(screenshot)

		# Adding the preview on the result page
		url_section = ResultSection('Urlscan.io website screenshot', body_format=BODY_FORMAT.URL, body=json.dumps({"name": "The preview is also available here !", "url": response.json()["task"]["screenshotURL"]}))
		result.add_section(url_section)
		request.add_extracted(self.working_directory + "/preview.png", "preview.png", "Here\'s the preview of the site")

		request.result = result
