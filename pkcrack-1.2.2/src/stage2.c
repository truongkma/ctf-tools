/* pkcrack - stage2.c
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: stage2.c,v 1.16 2003/01/03 15:18:18 lucifer Exp $
 *
 * $Log: stage2.c,v $
 * Revision 1.16  2003/01/03 15:18:18  lucifer
 * Fixed general purpose bit 3
 * Improved comment in stage2.c
 *
 * Revision 1.15  2002/12/28 15:56:26  lucifer
 * Small cleanup from RElf (fix6.zip)
 *
 * Revision 1.13  2002/10/25 17:39:57  RElf
 * Common constants and definitions moved to pkcrack.h and mktmptbl.h
 * 
 * Revision 1.12  2002/01/31 16:27:08  lucifer
 * Integrated "RElf"'s changes with (improved) invTempTable stuff
 *
 * Revision 1.7.2.1  2002/01/22 21:51:39  lucifer
 * Changes by RElf:
 * !!! Bugfixed key1 list handling !!!
 * A number of various simplifications & improvements
 *
 * Revision 1.7  1996/08/21 18:06:16  conrad
 * Some cleanups to suppress some warnings...
 *
 * Revision 1.6  1996/08/15 10:22:44  conrad
 * changed meaning of i in buildkey0list() a little
 * reduced chances for double hits in buildkey1list() and recursion1()
 *
 * Revision 1.5  1996/08/13 13:22:18  conrad
 * Removed call to findPwd
 * More plaintext used to determine correctness of key (after receiving reports
 * of false hits).
 * Some changes to support offset (-o)
 * Changed one line because of a bug in VisualC++ optimizer.
 *
 * Revision 1.4  1996/06/23 10:38:32  lucifer
 * stage2 can now be called with key2i values for any i in the plaintext.
 * This is for improved efficiency (see main.c)
 *
 * Revision 1.3  1996/06/12  09:47:24  conrad
 * Release version
 *
 * Revision 1.2  1996/06/11 10:28:53  conrad
 * moved fflush() a couple of lines to the front, so key[012] values
 * get printed as soon as they are found.
 *
 * Revision 1.1  1996/06/10 18:04:36  conrad
 * Initial revision
 *
 */

static char RCSID[]="$Id: stage2.c,v 1.16 2003/01/03 15:18:18 lucifer Exp $";

#include <stdio.h>
#include "pkcrack.h"
#include "crc.h"
#include "mktmptbl.h"
#include "keystuff.h"

static int   numTestBytes, minimalOffset;

uword	loesung0=0, loesung1=0, loesung2=0, got_keys=0;
static uword key2list[13], key1list[13], key0list[13];

static void buildkey0list( )
/* From 4 consecutive LSBs of key0 build a complete key0 value.
 * See section 3.4 of the Biham/Kocher paper.
 */
{
int	i;
uword	temp;

    temp = key0 = key0list[4];
    updateKeys( plaintext[4+bestOffset-12] );
    temp ^= ((key0^key0list[5])&0xff)<<8;
    key0 = temp;
    updateKeys( plaintext[4+bestOffset-12] );

    temp = key0;
    updateKeys( plaintext[5+bestOffset-12] );
    temp ^= ((key0^key0list[6])&0xff)<<8;
    key0 = temp;
    updateKeys( plaintext[5+bestOffset-12] );

    temp = key0;
    updateKeys( plaintext[6+bestOffset-12] );
    temp ^= ((key0^key0list[7])&0xff)<<8;
    key0 = temp;
    updateKeys( plaintext[6+bestOffset-12] );

    temp = key0;
    updateKeys( plaintext[7+bestOffset-12] );
    temp ^= ((key0^key0list[8])&0xff)<<8;
    key0 = temp;

    /* Now we have the full value of key0_7 */
    /* Check if it is valid by computing key0_{[8..12]} and comparing to
     * the known LSBs */
    i = 7;
    key1 = key1list[i];
    key2 = key2list[i];
    do{
	updateKeys( plaintext[i+bestOffset-12] );
	i++;
    } while( i < 13 && (key0&0xff) == (key0list[i]&0xff) );

    i -= 12;
    /* Do some more checking if we have more testbytes available. */
    while( i < numTestBytes && 
	   (ciphertext[i+bestOffset]^key3) == plaintext[i+bestOffset] )
    {
	updateKeys( plaintext[i+bestOffset] );
	i++;
    }

    if( i == numTestBytes )
    { /* Got it! Now calculate backwards 'til key0_0... */
	i += bestOffset;
	do{
	    key2 = INVCRC32(key2,MSB(key1));
	    temp = (key2 & 0xffff)|3;
	    key3 = ((temp*(temp^1))>>8)&0xff;
	    if( i <= minimalOffset )
		plaintext[i-1] = ciphertext[i-1]^key3;
	    key1 = MULT(key1-1)-(key0&0xff);
	    key0 = INVCRC32(key0,plaintext[i-1]);
	    /*printf( "%2d %8x %8x %8x\n", i-1, key0, key1, key2 );*/
	    i--;
	}while( i > 0 && plaintext[i] == (ciphertext[i]^key3) );

	if( i == 0 )
	{
            got_keys = 1;
	    loesung0 = key0;
	    loesung1 = key1;
	    loesung2 = key2;
	    printf( "Ta-daaaaa! key0=%8x, key1=%8x, key2=%8x\007\n", key0, key1, key2 );
	    printf( "Probabilistic test succeeded for %d bytes.\n", numTestBytes+12-8 );
	    fflush( stdout );
	}
    }
    else if( i >= 1 )
    {
	fprintf( stderr, "Strange... had a false hit.\n" );
	fflush( stderr );
    }
}

static void recursion1( int n )
/* given a value for key1_n, compute all possible values of key1_{n-1} that
 * fit the MSB of key1_{n-2} */
{
int	k, t;
uword	MSBnminus1, MSBnminus2, rhs, temp2;
byte	diff;

    if( n == 3 )
    {
	buildkey0list( );
	return;
    }

    MSBnminus1 = key1list[n-1] & MSBMASK;
    MSBnminus2 = key1list[n-2] & MSBMASK;

    /* right hand side of formula from section 3.3 */
    rhs = MULT(key1list[n]-1);
    temp2 = MULT(rhs - 1);
    diff = MSB( temp2 - MSBnminus2 ); /* almost = MSB(temp2)-MSB(MSBnminus2) */
    /* Note that MSB(a) - MSB(b) = MSB(a-b) or MSB(a) - MSB(b) = MSB(a-b) + 1 */

    /* The equation from section 3.3 is used twice here:
     * (1) key1_{n-1} + LSB(key0_n) = rhs = (key1_n - 1) * INVCONST
     * and
     * (2) key1_{n-2} + LSB(key0_{n-1}) = (key1_{n-1} - 1) * INVCONST
     *
     * At this point we know key1_n, MSB(key1_{n-1}) and MSB(key1_{n-2}).
     *
     * From (2) follows
     * MSB(key1_{n-2}) = MSB((key1_{n-1} - 1) * INVCONST - LSB(key0_{n-1}))
     * Inserting (1) yields
     * MSB(key1_{n-2}) = MSB((rhs - 1)*INVCONST -
     *                       LSB(key0_n)*INVCONST - LSB(key0_{n-1}))
     * which means that either
     * (a) MSB(key1_{n-2}) = MSB((rhs - 1)*INVCONST) -
     *                       MSB(LSB(key0_n)*INVCONST - LSB(key0_{n-1}))
     * or
     * (b) MSB(key1_{n-2}) = MSB((rhs - 1)*INVCONST) -
     *                       MSB(LSB(key0_n)*INVCONST - LSB(key0_{n-1})) - 1
     *
     * It can easily be verified that for any two bytes b1, b2:
     * MSB( b1*INVCONST + b2 ) = MSB( b1*INVCONST )
     * (simple exhaustive test on 2^16 combinations)
     *
     * We have computed diff = MSB((rhs - 1)*INVCONST) - MSB(key1_{n-2}).
     * Now all we have to do is find values for key0_n so that
     * (following from (1))
     * MSB(key1_{n-1}) = MSB(rhs-LSB(key0_n))
     * and (following from (a) and (b)) either
     * diff = MSB(LSB(key0_n)*INVCONST)
     * or
     * diff = MSB(LSB(key0_n)*INVCONST) + 1
     *
     * Candidate values are selected using the precomputed lookup table mTab2.
     */
    for( t=2; t; t--, diff-- ) for( k = 0; k < mTab2Counter[diff]; k++ )
    {
        uword lsbkey0 = mTab2[diff][k],
                 test = temp2 - mulTab[lsbkey0] - MSBnminus2;
	if( (test <= MAXDELTA) && (((rhs-lsbkey0)&MSBMASK)==MSBnminus1) )
	{
	    key1list[n-1] = rhs - lsbkey0;
	    key0list[n]   = lsbkey0;
            recursion1( n-1 );
	}
    }
}

static void buildkey1list( )
/* Find all values for key1_12 that produce the correct MSB for key_11
 * See section 3.3 of the Biham-Kocher paper. */
{
uword	i, j, k, t;
uword	test, MSBi, MSBiminus1, temp, temp2;
byte	diff;

    MSBi       = key1list[12] & MSBMASK;
    MSBiminus1 = key1list[11] & MSBMASK;

    /* There's 2^24 possible values for key1_12, given its MSB.
     * We check them all, substitution multiplications by table-lookup and add
     * to save time */
    temp = (mulTab[MSB(MSBi)]<<24) - INVCONST;       /* = MULT(MSBi-1) */
    for( i = 0; i < 256; i++ )
	for( j = 0; j < 256; j++ )
	{
	    temp2 = temp + (mulTab[i]<<16) + (mulTab[j]<<8);

	    /* See the explanation in recursion1 how this works... */
	    diff = MSB(MSBiminus1 - (temp2&MSBMASK));
	    for( t=2; t; t--, diff-- ) for( k = 0; k < mTab2Counter[diff]; k++ )
	    {
		test = temp2 + mulTab[mTab2[diff][k]] - MSBiminus1;
		if( test <= MAXDELTA )
		{
		    key1list[12] = MSBi + (i<<16) + (j<<8) + mTab2[diff][k];
                    recursion1( 12 );
		}
	    }
	}
}

static void recursion2( int i )
/* Calculate key2_{i-1} from key2_i, key3_{i-1} and key3_{i-2},
 * calculate MSB of key1_i */
{
int	k, l;
byte	key3iminus1, key3iminus2, hadIt=0;
uword	key2j, key2iminus1, key2iminus2, newKey, oldValue;

    if( i == 1 )
    {
	buildkey1list( );
	return;
    }

    key3iminus1 = KEY3(i+bestOffset-12-1);
    key3iminus2 = KEY3(i+bestOffset-12-2);
    /* This works exactly like reduceKey2s in stage 1 */
    key2j = key2list[i];
    key2iminus1 = INVCRC32(key2j,0) & 0xffffff00;
    for( k = 0; k < invEntries[key3iminus1][(key2iminus1&0xfc00)>>10]; k++ )
	if( (tempTable[key3iminus1]
		      [invTempTable[key3iminus1][(key2iminus1&0xfc00)>>10]
				   [k]]&0xff00) == (key2iminus1&0xff00) )
	{
	    newKey = key2iminus1 |
		     tempTable[key3iminus1]
			      [invTempTable[key3iminus1]
					   [(key2iminus1&0xfc00)>>10][k]]; /* b) */
	    key2iminus2 = INVCRC32(newKey,0)&0xfc00;
	    key2iminus2 >>= 10;
	    for( l = 0; l < invEntries[key3iminus2][key2iminus2]; l++ ) {
	        newKey = key2iminus1 |
		         (((tempTable[key3iminus2]
				     [invTempTable[key3iminus2]
					          [key2iminus2][l]] ^
			    crcinvtab[MSB(key2iminus1)])>>8)&0xff); /* c) (and b) */
	        if( !hadIt || oldValue != newKey )
	        {
		    key2list[i-1] = newKey;
/* The following line was changed because VisualC++ has a bug in its
 * Optimizer...
 *		    key1list[i] = (((key2j<<8)^crcinvtab[(key2j>>24)&0xff]^newKey)&0xff)<<24;*/
		    key1list[i] = (crcinvtab[MSB(key2j)]^newKey)<<24;
		    recursion2( i-1 );
		    oldValue = newKey;
		    hadIt = 1;
	        }
	    }
	}
}

void buildKey2Lists( uword aKey2_13, int testBytes, int minOffset )
{
    numTestBytes = testBytes;
    minimalOffset = minOffset;
    key2list[12] = aKey2_13;
    recursion2( 12 );
}

