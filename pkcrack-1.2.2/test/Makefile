
all: test-pkcrack test-zipdecrypt test-makekey test-findkey test-extract

test-pkcrack: test-makekey crypt.zip plain.zip
	make -C ../src
	./test.sh crypt.zip plain.zip appnote.txt ../doc/appnote.iz.txt a
	./test.sh crypt.zip plain.zip appnote2.txt ../doc/appnote.iz.txt ar
	./test.sh crypt.zip plain.zip appnote3.txt ../doc/appnote.iz.txt arg
	./test.sh crypt.zip plain.zip ../doc/appnote.iz.txt \
		  ../doc/appnote.iz.txt argh
	./test.sh crypt.zip plain.zip appnote5.txt ../doc/appnote.iz.txt aargh
	./test.sh crypt.zip plain.zip appnote6.txt ../doc/appnote.iz.txt aarrgh
	./test.sh crypt.zip plain.zip appnote7.txt ../doc/appnote.iz.txt aarrggh
	./test.sh crypt.zip plain.zip appnote8.txt ../doc/appnote.iz.txt \
		  aarrgghh

test-zipdecrypt: crypt.zip
	make -C ../src
	../src/zipdecrypt `../src/makekey aargh` crypt.zip newplain.zip || \
		/bin/true
	unzip newplain.zip appnote5.txt
	diff appnote5.txt ../doc/appnote.iz.txt
	rm -f appnote5.txt newplain.zip

test-makekey:
	make -C ../src
	test "`../src/makekey a`" = "64799c96 b303049c a253270a"
	test "`../src/makekey ar`" = "a7035ffd 02b9fffe 0e79db15"
	test "`../src/makekey arg`" = "107d7905 0dbb8c10 1362e18d"
	test "`../src/makekey argh`" = "3313609c be926f5d bfc303f7"
	test "`../src/makekey aargh`" = "653aa040 53893167 6c0be6ca"
	test "`../src/makekey aarrgh`" = "a8a5ef0e 525157c6 342f5c26"
	test "`../src/makekey aarrggh`" = "23e17d4d 32e43a89 94c31d27"
	test "`../src/makekey aarrgghh`" = "4b27353a 9ad9b1d0 b5440c2c"

test-findkey: test-makekey
	make -C ../src
	for i in willi fritz wunshwald eon argle bargle chick whatever \
		 how many tests shall I make; do \
	    echo Testing $$i...; \
	    keys="`../src/makekey $$i`"; \
	    test `../src/findkey $$keys 2>&1 | grep -c "as a string.*'$$i'"` -gt 0; \
	done

test-extract: plain.zip
	make -C ../src
	../src/extract -p plain.zip README
	diff ../doc/README README
	rm -f README

plain.zip:
	zip $@ ../doc/appnote.iz.txt
	zip -0 $@ ../doc/README

crypt.zip: bug.zip
	cp bug.zip crypt.zip
	cp ../doc/appnote.iz.txt appnote.txt
	zip -P a $@ appnote.txt
	mv appnote.txt appnote2.txt
	zip -P ar $@ appnote2.txt
	mv appnote2.txt appnote3.txt
	zip -P arg $@ appnote3.txt
	mv appnote3.txt appnote4.txt
	zip -P argh $@ appnote4.txt
	mv appnote4.txt appnote5.txt
	zip -P aargh $@ appnote5.txt
	mv appnote5.txt appnote6.txt
	zip -P aarrgh $@ appnote6.txt
	mv appnote6.txt appnote7.txt
	zip -P aarrggh $@ appnote7.txt
	mv appnote7.txt appnote8.txt
	zip -P aarrgghh $@ appnote8.txt
	rm appnote*.txt
	cp ../doc/README .
	last=README; \
	for i in `seq 1 200`; do \
	    this=README.$$i; \
	    mv $$last $$this; \
	    zip $@ $$this; \
	    last=$$this; \
	done; \
	rm $$last

clean:
	rm -rf test.sh.out* plain.zip crypt.zip appnote* newplain.zip README*
 
