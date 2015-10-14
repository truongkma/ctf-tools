/* 
 * findkey.c
 *
 * This program tries to find a PkZip-password for a given initial state
 * of key0, key1 and key2. In the current version it prints information about
 * the progress of the search to stdout every couple of minutes. You can use
 * that information for resuming the search at a later time.
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: findkey.c,v 1.6 2002/11/02 15:12:06 lucifer Exp $
 *
 * $Log: findkey.c,v $
 * Revision 1.6  2002/11/02 15:12:06  lucifer
 * Integrated RElf's changes (with small mods) from fix2.zip
 *
 * Revision 1.6  2002/10/25 17:47:08  RElf
 * Call to initStage3Tab() replaced with initMulTab()
 * 
 * Revision 1.5  1997/09/18 18:14:02  lucifer
 * Added comment
 * Fixed idiotic Cut&Paste-bug (pointed out by several people)
 *
 * Revision 1.4  1996/08/13 13:15:09  conrad
 * declared main as void to suppress warning
 *
 * Revision 1.3  1996/06/23 12:39:28  lucifer
 * Added char RCSID[]
 *
 * Revision 1.2  1996/06/23  10:34:30  lucifer
 * findkey now prints status information, which may be used to restart
 * the program at a later time.
 * key[012] values are now read from the command line instead of stdin.
 *
 * Revision 1.1  1996/06/10 17:41:53  conrad
 * Initial revision
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include "pkctypes.h"
#include "pkcrack.h"
#include "stage3.h"
#include "crc.h"
#include "mktmptbl.h"

static char RCSID[]="$Id: findkey.c,v 1.6 2002/11/02 15:12:06 lucifer Exp $";

static void usage( char *name )
{
    fprintf( stderr, "Usage: %s <key0> <key1> <key2> [<pwdlen> <initvalue>]\n", name );
    fprintf( stderr, "<key0>, <key1> and <key2> must be in hexadecimal.\n" );
    fprintf( stderr, "<pwd> and <initvalue> can be given to continue an interrupted search.\n" );
    fprintf( stderr, "<initvalue> must also be in hexadecimal.\n" );
    exit( 1 );
}

void main( int argc, char **argv )
{
uword	key0, key1, key2;
int	pwdLen=0;
uword	initBytes;

    if( argc != 4 && argc != 6 )
	usage( argv[0] );

    if( sscanf( argv[1], "%x", &key0 ) != 1 ||
	sscanf( argv[2], "%x", &key1 ) != 1 ||
	sscanf( argv[3], "%x", &key2 ) != 1 )
	usage( argv[0] );

    if( argc == 6 && (sscanf( argv[4], "%d", &pwdLen ) != 1 ||
		      sscanf( argv[5], "%x", &initBytes ) != 1) )
	usage( argv[0] );

    mkCrcTab( );
    initMulTab( );

    if( pwdLen > 0 )
	findLongPwd( key0, key1, key2, pwdLen, initBytes );
    else
	findPwd( key0, key1, key2 );
}
