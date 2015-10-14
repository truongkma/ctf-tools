CC=gcc
CFLAGS=-O6 -Wall
#CFLAGS=-g

RM=rm -f
ifdef DJGPP
    CMD=cmd.exe /C
    RM=$(CMD) del /F /Q
    SUFF=.exe
endif

SRCS =	crc.c mktmptbl.c main.c stage1.c keystuff.c stage2.c stage3.c exfunc.c\
	readhead.c writehead.c zipdecrypt.c debug.c

OBJS =	crc.o mktmptbl.o main.o stage1.o keystuff.o stage2.o stage3.o exfunc.o\
	readhead.o writehead.o zipdecrypt.o debug.o

all: pkcrack$(SUFF) zipdecrypt$(SUFF) findkey$(SUFF) extract$(SUFF) makekey$(SUFF)

pkcrack$(SUFF): $(OBJS)
	$(CC) -o pkcrack $(CFLAGS) $(OBJS)

findkey$(SUFF): findkey.o crc.o stage3.o keystuff.o
	$(CC) -o findkey $(CFLAGS) findkey.o crc.o stage3.o keystuff.o mktmptbl.o 

zipdecrypt$(SUFF): zdmain.o zipdecrypt.o crc.o keystuff.o writehead.o readhead.o
	$(CC) -o zipdecrypt $(CFLAGS) zdmain.o zipdecrypt.o crc.o keystuff.o writehead.o readhead.o

extract$(SUFF): extract.o exfunc.o readhead.o
	$(CC) -o extract $(CFLAGS) extract.o exfunc.o readhead.o

makekey$(SUFF): makekey.o crc.o keystuff.o
	$(CC) -o makekey $(CFLAGS) makekey.o crc.o keystuff.o

clean:
	$(RM) pkcrack
	$(RM) *.o
	$(RM) findkey
	$(RM) zipdec~1
	$(RM) extract
	$(RM) makekey
	$(RM) *.exe
	$(RM) core

depend:
	makedepend -f- $(SRCS) findkey.c zdmain.c makekey.c | sed 's= /[^ ]*\.h= =g' | grep -v '^.*: *$$' >> Makefile

# DO NOT DELETE

crc.o: crc.h
mktmptbl.o: mktmptbl.h pkctypes.h 
mktmptbl.o:  pkcrack.h
main.o: pkctypes.h crc.h mktmptbl.h pkcrack.h stage1.h stage2.h stage3.h
main.o: headers.h
stage1.o:  stage1.h crc.h mktmptbl.h pkctypes.h
stage1.o:   pkcrack.h
keystuff.o: pkctypes.h  
keystuff.o:  keystuff.h pkcrack.h crc.h
stage2.o: pkcrack.h pkctypes.h  
stage2.o: crc.h mktmptbl.h keystuff.h
stage3.o: pkctypes.h   stage3.h
stage3.o: pkcrack.h crc.h keystuff.h mktmptbl.h
exfunc.o:   headers.h
readhead.o: headers.h
writehead.o: headers.h
zipdecrypt.o: pkctypes.h crc.h pkcrack.h keystuff.h headers.h
findkey.o:  pkctypes.h 
findkey.o:  pkcrack.h stage3.h crc.h mktmptbl.h
zdmain.o: pkctypes.h   crc.h
zdmain.o: pkcrack.h keystuff.h
makekey.o:  pkcrack.h pkctypes.h
makekey.o:   keystuff.h crc.h
