/* 
 * decrypt.c
 *
 * This file contains the main function of the zipdecrypt program.
 *
 * (C) by Peter Conrad <conrad@unix-ag.uni-kl.de>
 *
 * $Id: zdmain.c,v 1.4 2002/12/28 17:01:42 lucifer Exp $
 *
 * $Log: zdmain.c,v $
 * Revision 1.4  2002/12/28 17:01:42  lucifer
 * Integrated RElf's fix7 / fix8.zip, partially at least
 *
 * Revision 1.4  2002/12/13 02:23:43  RElf
 * Joined with zdmain.c
 *
 * Revision 1.3  1997/09/18 18:36:33  lucifer
 * Added comment and pkctypes.h
 *
 * Revision 1.2  1996/08/21 17:54:09  conrad
 * Some cleanups to suppress warnings...
 *
 * Revision 1.1  1996/08/21 17:39:28  conrad
 * Initial revision
 *
 */

static char RCSID[]="$Id: zdmain.c,v 1.4 2002/12/28 17:01:42 lucifer Exp $";

#include <stdio.h>
#include "pkctypes.h"
#include "crc.h"
#include "pkcrack.h"
#include "keystuff.h"

extern void zipdecrypt( char*infile, char*outfile, int k0, int k1, int k2 );

void main( int argc, char **argv )
{
char *c;

    mkCrcTab();

    switch( argc ) {
    case 4:
        initkeys();
        for(c=argv[1];*c;c++) updateKeys(*c);
        break;
    case 6:
        sscanf(argv[1], "%x", &key0);
        sscanf(argv[2], "%x", &key1);
        sscanf(argv[3], "%x", &key2);
        break;
    default:
        fprintf( stderr, "Usage: %s {<password> | <key0> <key1> <key2>} <cryptedzipfile> <plainzipfile>\n", argv[0] );
        return;
    }

    zipdecrypt( argv[argc-2], argv[argc-1], key0, key1, key2 );
}
