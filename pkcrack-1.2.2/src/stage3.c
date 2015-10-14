/* 
 * stage3.c
 *
 * This file implements stage 3 of the cracking process, namely finding
 * a PkZip-password for a given internal state of key0, key1 and key2.
 * It re-uses some code from stage2.c
 * See section 3.6 of the paper.
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: stage3.c,v 1.10 2002/12/30 18:27:25 lucifer Exp $
 *
 * $Log: stage3.c,v $
 * Revision 1.10  2002/12/30 18:27:25  lucifer
 * Fixed problem in recursion1 - see RElf's fix in stage2.c
 *
 * Revision 1.9  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.9  2002/10/25 14:28:44  RElf
 * Common constants and definitions moved to pkcrack.h and mktmptbl.h
 * CRC inverse routines are simplified
 * initStage3Tab() removed
 *
 * Revision 1.8  1997/02/15 09:48:44  lucifer
 * Patch by Mats Lofkvist <mal@aristotle.algonet.se>:
 * Test for passwords of length 1,2 or 3 chars
 *
 * Revision 1.7  1996/08/15 10:24:43  conrad
 * findlongpwd() rewritten, because of a small bug in the progress output.
 * overall, it should be clearer now.
 *
 * Revision 1.6  1996/08/13 13:25:46  conrad
 * minor changes...
 *
 * Revision 1.5  1996/06/23 10:40:24  lucifer
 * Support for restarting the search at a specific point added
 *
 * Revision 1.4  1996/06/12 09:47:27  conrad
 * Release version
 *
 * Revision 1.3  1996/06/11 20:15:30  conrad
 * Several speedups using more table lookup and less function calls.
 *
 * Revision 1.2  1996/06/11 10:26:56  conrad
 * fixed small bug when printing passwords
 * inserted fflush(stdout) to keep track of progress
 *
 */

static char RCSID[]="$Id: stage3.c,v 1.10 2002/12/30 18:27:25 lucifer Exp $";

#include <stdio.h>
#include "pkctypes.h"
#include "stage3.h"
#include "pkcrack.h"
#include "crc.h"
#include "keystuff.h"
#include "mktmptbl.h"

#define	BYTES_BEFORE_INIT	4

static byte	pwd[15];
static int	pwdLen;

static uword	l0, l1, l2, m0, m1, m2;
static uword	key1list[7], key0list[7];

#ifndef	SLOW
#define updateKeys(x) fast_updateKeys(x)
static void fast_updateKeys( byte plainbyte )
/* we don't need temp and key3... */
{
    key0 = CRC32( key0, plainbyte );
    key1 = (key1 + (key0&0xff))*CONST + 1;
    key2 = CRC32( key2, MSB(key1) );
}
#endif

static int recursion1( int i, int (*foundFunc)() )
/* given a value for key1_i, compute all possible values of key1_{i-1} that
 * fit the MSB of key1_{i-2}. See also recursion in stage2.c. */
{
int	k, res=0, t;
uword	MSBiminus1, MSBiminus2, lsbkey0, rhs, test, temp2;
byte	diff;

    MSBiminus1 = key1list[i-1] & MSBMASK;
    MSBiminus2 = key1list[i-2] & MSBMASK;
    rhs = MULT(key1list[i]-1);
    temp2 = MULT(rhs-1);
    diff = MSB( temp2 - MSBiminus2 );
    for (t = 2; t; t--, diff--) for( k = 0; k < mTab2Counter[diff]; k++ ) {
	lsbkey0 = mTab2[diff][k];
	test = temp2 - mulTab[lsbkey0] - MSBiminus2;
	if( test <= MAXDELTA && (((rhs-lsbkey0)&MSBMASK)==MSBiminus1) ) {
	    key1list[i-1] = rhs - lsbkey0;
	    key0list[i]   = lsbkey0;
	    if( i > 4 )
		res |= recursion1( i-1, foundFunc );
	    else
		res |= foundFunc();
	}
    }

    return res;
}

static int testPwd( )
{
int	i, res=0;
uword	k0, k1, k2;

    k0 = key0;
    k1 = key1;
    k2 = key2;
#ifdef SLOW
    initkeys();
#else
    key0 = KEY0INIT;
    key1 = KEY1INIT;
    key2 = KEY2INIT;
#endif
    for( i = 0; i < pwdLen; i++ )
	updateKeys( pwd[i] );
    if( key0 == l0 && key1 == l1 && key2 == l2 )
	res = 1;

    key0 = k0;
    key1 = k1;
    key2 = k2;

    return res;
}

static int printPwd( )
{
int	i;

    if( testPwd() )
    {
	printf( "Key:" );
	for( i = 0; i < pwdLen; i++ )
	    printf( " %02x", pwd[i] );
	printf( "\nOr as a string: '" );
	for( i = 0; i < pwdLen; i++ )
	    printf( "%c", pwd[i] );
	printf( "' (without the enclosing single quotes)\n" );
	fflush( stdout );
	return 1;
    }

    return 0;
}

static int print4Bytes( byte b1, byte b2, byte b3, byte b4 )
{
    pwd[0] = b1;
    pwd[1] = b2;
    pwd[2] = b3;
    pwd[3] = b4;
    pwdLen = 4;
    return printPwd();
}

/* Find 4 bytes with crc(crc(crc(crc(init,b1),b2),b3),b4) == result */
static int find4Bytes( uword init, uword result, int (*foundFunc)( byte b1, byte b2, byte b3, byte b4 ) )
{
    int	i;
    uword temp;

    temp = result;
    for( i=0; i<4; i++ ) temp = INVCRC32(temp,0);
    temp ^= init;

    return foundFunc( temp&0xFF, (temp>>8)&0xFF, (temp>>16)&0xFF, (temp>>24)&0xFF);
}

static int find5c( byte b1, byte b2, byte b3, byte b4 )
{
int	res;

    pwd[pwdLen++] = b1;
    pwd[pwdLen++] = b2;
    pwd[pwdLen++] = b3;
    pwd[pwdLen++] = b4;
    pwdLen++;

    res = printPwd( );

    pwdLen -= 5;

    return res;
}

static int find5b( )
{
int	i, res=0;
uword	key00;

    for( i = 0; i < 256; i++ )
    {
	key00 = INVCRC32(l0,i);
	if( (key00&0xff) == (key0list[5]&0xff) )
	{
	    pwd[pwdLen+4] = i;
	    res |= find4Bytes( key0, key00, find5c );
	}
    }

    return res;
}

static int find5a( byte b1, byte b2, byte b3, byte b4 )
{
    key1list[2] = b1<<24;
    key1list[3] = b2<<24;
    key1list[4] = b3<<24;
    key1list[5] = b4<<24;
    return recursion1( 6, find5b );
}

static int find5Bytes( )
{
uword	key20;

    initkeys();

    key20 = INVCRC32( l2, MSB(l1) );
    key1list[6] = l1;

    return find4Bytes( KEY2INIT, key20, find5a );
}

static int find6c( byte b1, byte b2, byte b3, byte b4 )
{
int	res;

#ifdef SLOW
uword	k0, k1, k2;

    k0 = key0;
    k1 = key1;
    k2 = key2;
    key0 = m0;
    key1 = m1;
    key2 = m2;

    updateKeys( b1 );
    updateKeys( b2 );
    updateKeys( b3 );
    updateKeys( b4 );
    updateKeys( pwd[pwdLen+4] );
    updateKeys( pwd[pwdLen+5] );

    if( key0 == l0 && key1 == l1 && key2 == l2 )
    {
#endif

    pwd[pwdLen++] = b1;
    pwd[pwdLen++] = b2;
    pwd[pwdLen++] = b3;
    pwd[pwdLen++] = b4;
    pwdLen += 2;

    res = printPwd( );

    pwdLen -= 6;

#ifdef SLOW
    }
    else
	res = 0;

    key0 = k0;
    key1 = k1;
    key2 = k2;
#endif

    return res;
}

static int find6b( )
{
uword	i, j;
uword	key00, key0minus1;

    i = (key0list[6]^crcinvtab[MSB(l0)])&0xff;
    key00 = INVCRC32(l0,i);
    j = (key0list[5]^crcinvtab[MSB(key00)])&0xff;
    key0minus1 = INVCRC32(key00,j);
    pwd[pwdLen+4] = j;
    pwd[pwdLen+5] = i;
    return find4Bytes( key0, key0minus1, find6c );
}

static int find6a( byte b1, byte b2, byte b3, byte b4 )
{
    key1list[2] = b1<<24;
    key1list[3] = b2<<24;
    key1list[4] = b3<<24;
    key1list[5] = b4<<24;
    return recursion1( 6, find6b );
}

static int find6Bytes( )
{
uword	key10, key20, key2minus1;

#ifdef SLOW
int	i;

    initkeys();
    for( i = 0; i < pwdLen; i++ )
	updateKeys( pwd[i] );
#else
    key0 = m0;
    key1 = m1;
    key2 = m2;
#endif

    key20 = INVCRC32( l2, MSB(l1) );
    key10 = (l1-1)*INVCONST-(l0&0xff);
    key2minus1 = INVCRC32( key20, MSB(key10) );

    key1list[6] = key10;
    return find4Bytes( key2, key2minus1, find6a );
}

void findLongPwd( uword key0, uword key1, uword key2, int initLength, uword initBytes )
{
int	i, j;
uword	key0list[20], key1list[20], key2list[20];

    l0 = key0;
    l1 = key1;
    l2 = key2;

/* initLength is the length of the first pwd to be tested. the last 6
 * bytes of the pwd are found using find6Bytes(), so we are left with
 * initLength-6 bytes for the trial-and-error-part. */
    pwdLen = initLength-6;

/* pwd[] is arranged as follows:
 *
 * index:   0 ... a ... a+3 ... pwdLen
 * content: 0 0 0 k l m n   0 0 0
 *
 * where a+3 = pwdLen-BYTES_BEFORE_INIT+1, and (klmn) = initbytes (MSB first).
 */
    for( i = pwdLen-1; i >= 0; i-- )
    {
	if( pwdLen-i < BYTES_BEFORE_INIT )
	    pwd[i] = 1;
	else if( pwdLen-i < BYTES_BEFORE_INIT+4 )
	    pwd[i] = (initBytes>>((pwdLen-i-BYTES_BEFORE_INIT)*8))&0xff;
	else
	    pwd[i] = 1; /* not exactly useful. */
    }
    key0list[0] = KEY0INIT;
    key1list[0] = KEY1INIT;
    key2list[0] = KEY2INIT;
    for( i = 1; i < pwdLen; i++ )
    {
	key0list[i] = CRC32( key0list[i-1], pwd[i-1] );
	key1list[i] = (key1list[i-1] + (key0list[i]&0xff))*CONST + 1;
	key2list[i] = CRC32( key2list[i-1], MSB(key1list[i]) );
    }
    m0 = CRC32( key0list[pwdLen-1], pwd[pwdLen-1] );
    m1 = (key1list[pwdLen-1] + (m0&0xff))*CONST + 1;
    m2 = CRC32( key2list[pwdLen-1], MSB(m1) );

    while( !find6Bytes( ) ){
	for( i = pwdLen-1; i >= 0 && !(++pwd[i]); i-- );
	for( j = i+1; j < pwdLen; j++ )
	    pwd[j] = 1;
	if( i < 0 )
	{
	    pwd[pwdLen++] = 1;
	    i = 0;
	}
	if( pwdLen-i >= BYTES_BEFORE_INIT )
	{
	    initBytes = 0;
	    for( j = pwdLen-BYTES_BEFORE_INIT; j > pwdLen-BYTES_BEFORE_INIT-4 && j >= 0; j-- )
		initBytes |= (((uword)pwd[j])<<((pwdLen-BYTES_BEFORE_INIT-j)*8));
	    printf( "%2d: %8x\r", pwdLen+6, initBytes );
	    fflush( stdout );
	}
	for( ; i < pwdLen-1; i++ )
	{
	    key0list[i+1] = CRC32( key0list[i], pwd[i] );
	    key1list[i+1] = (key1list[i] + (key0list[i+1]&0xff))*CONST + 1;
	    key2list[i+1] = CRC32( key2list[i], MSB(key1list[i+1]) );
	}
	m0 = CRC32( key0list[pwdLen-1], pwd[pwdLen-1] );
	m1 = (key1list[pwdLen-1] + (m0&0xff))*CONST + 1;
	m2 = CRC32( key2list[pwdLen-1], MSB(m1) );
    }
}

static int findShortPwd( uword key0, uword key1, uword key2 )          /* of length <= 3 */
{
    if ( key0 == KEY0INIT && key1 == KEY1INIT && key2 == KEY2INIT )
    {
	printf ( "Null (i.e. zero length) key!!!\n" );
	return 1;
    }
    else
    {
        int i, j;
        uword temp, temp2;

        temp = key0;
        for( i=1; i<4; i++ ) {
            temp = INVCRC32(temp,0);
            temp2 = temp^KEY0INIT;

            if( (temp2>>(8*i)) == 0 ) {
                for( j=0; j<i; j++ ) pwd[j] = (temp2>>(8*j)) & 0xFF;
                pwdLen = i;
                if( printPwd() ) return 1;
            }
        }
        return 0;
    }
}

void findPwd( uword key0, uword key1, uword key2 )
{
    l0 = key0;
    l1 = key1;
    l2 = key2;

    if( !findShortPwd( key0, key1, key2 ) )
    {
        if( !find4Bytes( KEY0INIT, key0, print4Bytes ) )
	{
	    pwdLen = 0;
	    m0 = KEY0INIT;
	    m1 = KEY1INIT;
	    m2 = KEY2INIT;
	    if( !find5Bytes( ) && !find6Bytes( ) )
	        findLongPwd( key0, key1, key2, 7, 0 );
	}
    }
}
