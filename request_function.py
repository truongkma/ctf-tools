import urllib2, urllib
def request(url,data,cookie):
	headers = {"Cookie": cookie}
	req = urllib2.Request(url, data, headers)
	response = urllib2.urlopen(req).read()
	return response