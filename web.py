def encrypt(value):
    data = urllib.urlencode({'txtcrypt':value})
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    the_page = response.read()
    return the_page.split('<font')[1].split('<b>')[1].split('</b>')[0]