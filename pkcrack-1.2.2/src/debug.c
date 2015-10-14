/* 
 * debug.c
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: debug.c,v 1.2 2002/01/30 15:25:26 lucifer Exp $
 *
 * $Log: debug.c,v $
 * Revision 1.2  2002/01/30 15:25:26  lucifer
 * Inserted #ifdefs so debugging can be turned off easily
 *
 * Revision 1.1  2002/01/21 18:50:50  lucifer
 * Some debugging functions to be called from various places
 *
 */

static char RCSID[]="$Id: debug.c,v 1.2 2002/01/30 15:25:26 lucifer Exp $";

#ifdef DEBUG

#include <stdio.h>
#include "keystuff.h"
#include "pkcrack.h"

static uword *myKey0i, *myKey1i, *myKey2i;

/* Prepare debugging: ask for initial key0, key1, key2 values, create all
 * intermediate values and store them. */
void prepareDebug(int l) {
int i;

    myKey0i = malloc(l*sizeof(uword));
    myKey1i = malloc(l*sizeof(uword));
    myKey2i = malloc(l*sizeof(uword));

    if (!myKey0i || !myKey1i || !myKey2i) {
	fprintf(stderr, "Can't allocate memory for debug arrays!\n");
	exit(1);
    }

    printf("Input initial key0 value:\n");
    scanf("%x", &key0);
    printf("Input initial key1 value:\n");
    scanf("%x", &key1);
    printf("Input initial key2 value:\n");
    scanf("%x", &key2);

    printf("Ok. Using 0x%08x, 0x%08x, 0x%08x.\n", key0, key1, key2);

    for (i = 0; i < l; i++) {
	myKey0i[i] = key0;
	myKey1i[i] = key1;
	myKey2i[i] = key2;
	cUpdateKeys(ciphertext[i]);
    }
}

/* Check if the key2 value before encryption of byte i is in the key2i array */
void checkKey2(int i) {
int j;

//    printf("CheckKey2 at %d\n", i);

    for (j = 0; j < numKey2s; j++) {
	if (myKey2i[i] == key2i[j]) {
	    return;
	}
    }

    fprintf(stderr, "Argh! Missing key2 value %08x at index %d!\n", myKey2i[i],
	    i);
    exit(1);
}

/* Set the list of remaining key2i values to the single correct value */
void setRemaining(int i) {
    key2i[0] = myKey2i[i];
    numKey2s = 1;
}

/* Check if the given array contains valid key2 values. If so, say so. */
int _checkKey2list(uword *array, int offset) {
int i;

    for (i = 1; i <= 12; i++) {
	if (array[i] != myKey2i[offset+i]) { return 0; }
    }
    printf("Key2s match.\n");
    return 1;
}

/* Check if the given array contains valid key1 values. If so, say so. */
int _checkKey1list(uword *array, int offset) {
int i;

    for (i = 3; i <= 12; i++) {
	if (array[i] != myKey1i[offset+i]) { return 0; }
    }
    printf("Key1s match.\n");
    return 1;
}

/* Check if the given array contains a valid key1 value at index i.
 * If so, say so. */
int _checkRecursion1(uword *array, int offset, int i) {
    if (array[i] != myKey1i[offset+i]) { return 0; }
    printf("Recursion1 match at %d.\n", i);
    return 1;
}

#endif /* ifdef DEBUG */

