/*
 * extract.c
 *
 * This file contains the main() function of a program for extracting
 * compressed data from a ZIP-archive. Gratefully received from a person who
 * wishes to remain anonymous.
 * Slightly modified by Peter Conrad, Aug '96
 *
 */
/******************************************************************************/
/*                                                                            */
/* FUNCTION       Extracts a file from a ZIP archive                          */
/*                                                                            */
/* INPUT          zipfilename                                                 */
/*                file to extract                                             */
/******************************************************************************/

/*
 * $Id: extract.c,v 1.12 2002/12/28 16:09:59 lucifer Exp $
 *
 * $Log: extract.c,v $
 * Revision 1.12  2002/12/28 16:09:59  lucifer
 * Integrated fix7.zip from RElf: added optional output filename argument
 *
 * Revision 1.11  2002/12/28 15:56:55  lucifer
 * Integrated fix6 from RElf: added option -p to extract
 *
 * Revision 1.11 2002/12/04 00:27:33  RElf
 * Added option -p
 *
 * Revision 1.10  2002/10/26 18:14:22 RElf
 * Added option -s <size>
 *
 * Revision 1.9  2002/01/30 14:22:37  lucifer
 * Fixed typo in Usage string
 *
 * Revision 1.8  1999/01/20 20:21:44  lucifer
 * string.h included
 *
 * Revision 1.7  1998/04/28 21:10:01  lucifer
 * Added flag -v => FLG_VERBOSE
 *
 * Revision 1.6  1997/09/23 20:07:31  lucifer
 * Removed declaration of strdup
 *
 * Revision 1.5  1997/09/23 17:31:39  lucifer
 * Added option -i
 *
 * Revision 1.4  1997/02/15  09:47:24  lucifer
 * Patch by Mats Lofkvist <mal@aristotle.algonet.se>:
 * Added compile option to *not* convert filenames to uppercase
 *
 * Revision 1.3  1996/08/21 17:52:24  conrad
 * Some more cleanups to suppress warnings
 *
 * Revision 1.2  1996/08/21 17:34:42  conrad
 * cleaned some things up...
 *
 */

#include <stdio.h>
#include <stdlib.h>

#ifndef _WIN32
#include <unistd.h>
#else
#include <io.h>
#endif

#include <fcntl.h>
#include <malloc.h>
#include <string.h>

#include "headers.h"

static char RCSID[]="$Id: extract.c,v 1.12 2002/12/28 16:09:59 lucifer Exp $";

extern char *extract( char *, char *, int caseflg );

#ifndef O_BINARY
#define	O_BINARY	0
#endif

static void usage( char *prg )
{
    fprintf( stderr, "Usage: %s [-i] [-p] [-v] [-s <size>] <zipfile> <file> [<outputfile>]\n", prg );
    fprintf( stderr, " -i\t\tswitch off case insensitive filename matching\n" );
    fprintf( stderr, " -p\t\tignore filepaths in archive\n" );
    fprintf( stderr, " -v\t\tbe verbose in parsing ZIP structure\n" );
    fprintf( stderr, " -s <size>\textract only specified number of bytes\n" );
}

void main(int argc, char *argv[])
{
char	*ret, *outname;
int	outfile, err=0, i, caseflg=0, size=0;

    for( i = 1; i < argc; i++ ) {
    	if( !strcmp( "-i", argv[i] ) ) {
	    caseflg |= FLG_CASE_SENSITIVE;
	} else if( !strcmp( "-v", argv[i] ) ) {
	    caseflg |= FLG_VERBOSE;
	} else if( !strcmp( "-p", argv[i] ) ) {
	    caseflg |= FLG_IGNORE_PATH;
        } else if( !strcmp( "-s", argv[i] ) ) {
            if (sscanf(argv[++i],"%d",&size) !=1 ) {
                fprintf(stderr,"Invalid <size>\n");
                exit(1);
            }
        } else {
	    break;
	}
    }

    if( i+2 == argc ) {
	outname = argv[i+1];
    } else if( i+3 == argc ) {
	outname = argv[i+2];
    } else {
        usage( argv[0] );
        exit(1);
    }

  /****************************************************************************/
  /* search file and write it to disk                                         */
  /****************************************************************************/
  err = !(ret = extract(argv[i], argv[i+1], caseflg ));

  if( !err )
  {
    outfile = open( outname, O_CREAT|O_WRONLY|O_BINARY, 0644 );
    if( outfile < 0 )
    {
	fprintf( stderr, "Couldn't create %s!\n", outname );
	err = 1;
    }
    else
    {
        if(size<=0) size = lh.csize;
        if(size>lh.csize) {
            fprintf(stderr,"<size> is too large, ignored\n");
            size = lh.csize;
        }
        if( write( outfile, ret, size ) != size )
	{
	    fprintf( stderr, "Couldn't write to %s!\n", outname );
	    err = 1;
	}
	close( outfile );
    }
    free( ret );
  }
  exit(err);
}
