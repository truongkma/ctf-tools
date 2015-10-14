# Written By H4rryp0tt3r
import commands
import re
passlist = open("new.txt", "r").read().split("\n")[0:-1]
print "[+] Bruteforcing With 5 Length English Words."
for passwd in passlist:
    # This Below Line Will Skip All The Passwords with Special Characters in
    # it Because We don't need Special Charactes in out password.
    if(re.findall("[.'$-@#!%^&*()+=]", passwd)):
        continue
    res = commands.getstatusoutput("unrar x steg.rar -inul -p" + passwd)
    if(res[0] == 0):
        print "[+] Extracted Succesfully!"
        break
