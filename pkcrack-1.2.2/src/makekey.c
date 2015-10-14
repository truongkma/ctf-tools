/* pkcrack - makekey.c
 *
 * (C) by Mats Lofkvist <mal@aristotle.algonet.se>
 *
 * $Id: makekey.c,v 1.1 1997/02/15 09:44:44 lucifer Release1_2_1 $
 *
 * $Log: makekey.c,v $
 * Revision 1.1  1997/02/15 09:44:44  lucifer
 * Initial revision
 *
 */

#include <stdio.h>
#include <string.h>
#include "pkcrack.h"
#include "keystuff.h"
#include "crc.h"

static char RCSID[]="$Id: makekey.c,v 1.1 1997/02/15 09:44:44 lucifer Release1_2_1 $";

static void usage( char *name )
{
    fprintf( stderr, "Usage: %s <password>\n", name );
    exit( 1 );
}

void main( int argc, char **argv )
{
char *	pwd;  
int	pwdLen, i;

    if( argc != 2 )
	usage( argv[0] );

    pwd = argv[1];
    pwdLen = strlen( pwd );

    mkCrcTab( );
    initkeys( );
    for( i = 0; i < pwdLen; i++ )
	updateKeys( pwd[i] );

    printf( "%08x %08x %08x\n", key0, key1, key2 );
}

