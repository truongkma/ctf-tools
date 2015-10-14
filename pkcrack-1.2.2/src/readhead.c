/*
 * readhead.c
 *
 * This file contains functions for reading parts of a ZIP-archive.
 * Gratefully received from a person who wishes to remain anonymous.
 *
 * $Id: readhead.c,v 1.13 2003/01/05 14:40:37 lucifer Exp $
 *
 * $Log: readhead.c,v $
 * Revision 1.13  2003/01/05 14:40:37  lucifer
 * Included RElf's modifications regarding data descriptor
 *
 * Revision 1.13  2003/01/04 13:54:33  RElf
 * Support for 'signature' field in struct ddesctype
 * Symbolic signatures used
 *
 * Revision 1.12  2002/12/29 15:51:32  lucifer
 * Integrated changes regarding data descriptor, inspired by AGL
 *
 * Revision 1.11  2002/12/28 15:56:55  lucifer
 * Integrated fix6 from RElf: added option -p to extract
 *
 * Revision 1.10 2002/12/04 00:27:33  RElf
 * Added support for FLG_IGNORE_PATH
 *
 * Revision 1.9  2002/11/02 11:38:32  RElf
 * Fixed conditions for using stricmp 
 *
 * Revision 1.8  2002/09/26 18:38:15  RElf
 * Fixed support for Data Descriptor
 *
 * Revision 1.7  1999/01/20 20:21:44  lucifer
 * some special stuff for windoze compiler
 *
 * Revision 1.6  1998/04/28 21:08:53  lucifer
 * Added support for Data Descriptor
 * Added flag FLG_VERBOSE
 *
 * Revision 1.5  1997/09/23 17:35:28  lucifer
 * Added FLG_CASE_SENSITIVE in read_local
 * Changed handling of flags in other funcs
 *
 * Revision 1.4  1997/09/18 18:23:05  lucifer
 * Fixed a few problems with lh.flen and dir.flen
 *
 * Revision 1.3  1996/08/21 18:09:30  conrad
 * Some cleanups to suppress some warnings...
 *
 * Revision 1.2  1996/08/21 17:38:14  conrad
 * Added noskip parameter to read_{local,dir,end}
 *
 */

/******************************************************************************/
/* Functions to read signature and headers                                    */
/******************************************************************************/
#include <stdio.h>
#include <malloc.h>
#include <string.h>

#ifndef _WIN32
#include <unistd.h>
#endif

#if defined(__EMX__) || defined(__WATCOMC__) || defined(_WIN32)
#define strcasecmp    stricmp
#endif

#include "headers.h"

static char RCSID[]="$Id: readhead.c,v 1.13 2003/01/05 14:40:37 lucifer Exp $";

local lh;
dirtype dir;
enddirtype enddir;
ddesctype ddesc;
char		*filename=NULL;
static int	fnlen;

/******************************************************************************/
/* READ Integer                                                               */
/******************************************************************************/
static int read2int( FILE *fp, unsigned short *dest )
{
unsigned char	dummy[2];

    if( fread( dummy, 2, 1, fp ) != 1 )
	return 0;

    *dest = (((unsigned short)dummy[1])<<8)+dummy[0];

    return 1;
}

static int read4int( FILE *fp, unsigned long *dest )
{
unsigned short	d1, d2;

    if( !read2int( fp, &d1 ) || !read2int( fp, &d2 ) )
	return 0;

    *dest = (((unsigned int)d2)<<16) + d1;

    return 1;
}

/******************************************************************************/
/* READ SIGNATURE                                                             */
/******************************************************************************/
int read_sig(FILE *fp)
{
unsigned long sig;
int ret;

  ret = read4int( fp, &sig );
  if(ret != 1)
  {
    fprintf( stderr, "Error in signature reading\n" );
    return(-1);
  }
  else;

  switch(sig)
  {
    case SIGN_LOCAL:
    case SIGN_DIR:
    case SIGN_END:
    case SIGN_DDESC:		
      return sig;
      break;
  }
  fprintf( stderr, "Read unknown signature: 0x%08lx\n", sig );

  return -1;
}

/******************************************************************************
 * READ DDESC		                                                      *
 * Allowed flags:                                                             *
 *  FLG_VERBOSE	- be verbose						      *
 ******************************************************************************/
int read_ddesc(FILE *fp, int flags)
{
int ret;
unsigned long sig;

    ret = read4int( fp, &sig );
    if( ret == 1 ) {
	/* This is a workaround for the discrepancy between PkWare's spec
	 * and InfoZIP's spec. This is not perfect, of course - think of a
	 * file with a CRC equal to SIGN_DDESC, but according to InfoZIP
	 * PkWare's utilities never use the data descriptor, anyway.
	 */
        if( sig != SIGN_DDESC ) {
            ddesc.signature = 0;
            ddesc.crc = sig;
        } else {
            ddesc.signature = sig;
            ret = read4int( fp, &ddesc.crc );
        }
    }
    if( ret == 1 ) {
        ret = read4int( fp, &ddesc.csize );
    }
    if( ret == 1 ) {
        ret = read4int( fp, &ddesc.uncsize );
    }
    if(ret != 1) {
        perror("Error reading data descriptor");
        return(-1);
    }
    if( flags&FLG_VERBOSE ) {
        fprintf( stderr, "CRC           = %08lx\n", ddesc.crc);
        fprintf( stderr, "Compr. size   = %lu\n", ddesc.csize);
        fprintf( stderr, "Uncomp. size  = %lu\n", ddesc.uncsize);
    }
    return 0;
}


/******************************************************************************
 * READ FILE HEADER                                                           *
 * Allowed flags:							      *
 *  FLG_CASE_SENSITIVE	- do case sensitive filename matching		      *
 *  FLG_NO_SKIP		- don't skip ZIP comments			      *
 *  FLG_VERBOSE		- be verbose					      *
 *  FLG_IGNORE_PATH    	- ignore path while matching filenames					      *
 *									      *
 * Returns: -1 generic error                                                  *
 *           1 found                                                          *
 *           0 skipped                                                        *
 ******************************************************************************/
int read_local(FILE *fp,char *name, int flags)
{
int ret;
char *fname;

  ret = fread( lh.version, 2, 1, fp );
  if( ret == 1 )
	ret = fread( lh.gpb, 2, 1, fp );
  if( ret == 1 )
	ret = fread( lh.compr, 2, 1, fp );
  if( ret == 1 )
	ret = fread( lh.time, 2, 1, fp );
  if( ret == 1 )
	ret = fread( lh.date, 2, 1, fp );
  if( ret == 1 )
	ret = read4int( fp, &lh.crc );
  if( ret == 1 )
	ret = read4int( fp, &lh.csize );
  if( ret == 1 )
	ret = read4int( fp, &lh.uncsize );
  if( ret == 1 )
	ret = read2int( fp, &lh.flen );
  if( ret == 1 )
	ret = read2int( fp, &lh.extralen );
  if(ret != 1)
  {
    fprintf( stderr, "Error in local header\n");
    return(-1);
  }
  else;

  if( flags&FLG_VERBOSE ) {
    fprintf( stderr, "Version       = %02x %02x\n",lh.version[0],lh.version[1]);
    fprintf( stderr, "General purp. = %02x %02x\n", lh.gpb[0], lh.gpb[1]);
    fprintf( stderr, "Compression   = %02x %02x\n", lh.compr[0], lh.compr[1]);
    fprintf( stderr, "Time          = %02x %02x\n", lh.time[0], lh.time[1]);
    fprintf( stderr, "Date          = %02x %02x\n", lh.date[0], lh.date[1]);
    fprintf( stderr, "CRC           = %08lx\n", lh.crc);
    fprintf( stderr, "Compr. size   = %lu\n", lh.csize);
    fprintf( stderr, "Uncomp. size  = %lu\n", lh.uncsize);
    fprintf( stderr, "Filename len. = %d\n", lh.flen);
    fprintf( stderr, "Extra field   = %d\n", lh.extralen);
  }

  if( !filename )
  {
    fnlen = 2*lh.flen;
    filename = malloc( fnlen+1 );
  }
  else if( lh.flen > fnlen )
  {
    fnlen = 2*lh.flen;
    filename = realloc( filename, fnlen+1 );
  }
  memset(filename, '\0', fnlen+1);
  ret = fread(filename, lh.flen, 1, fp);
  if(ret != 1)
  {
    fprintf( stderr, "Error in reading filename\n");
    return(-1);
  }

  if( flags&FLG_VERBOSE ) {
    fprintf( stderr, "Filename = %s\n", filename);
  }

  if( flags&FLG_IGNORE_PATH ) {
      char *lastslash,
           *temp = filename - 1;
      /* first try to locate last '/' */
      do {
          lastslash = temp;
          temp = strchr(temp+1,'/');
      } while(temp);
      if( lastslash == filename-1 ) {
          /* no luck with '/', let's try '\' */
          temp = filename-1;
          do {
              lastslash = temp;
              temp = strchr(temp+1,'\\');
          } while(temp);
      }
      fname = lastslash + 1;
  } else {
      fname = filename;
  }

  if( lh.extralen != 0 && !(flags&FLG_NO_SKIP) )
  {
    if( flags&FLG_VERBOSE ) {
      fprintf( stderr, "Skipping extra data...\n" );
    }
    ret = fseek(fp, lh.extralen, SEEK_CUR);
    if(ret != 0)
    {
      perror("Error seeking file");
      return(-1);
    }
  }

  /**************************************************************************/
  /* If the file is the one we are searching, returns                       */
  /**************************************************************************/
  if((!(flags&FLG_CASE_SENSITIVE) && !strcasecmp(name, fname)) ||
     ((flags&FLG_CASE_SENSITIVE) && !strcmp(name, fname)) )
  {
    return(1);
  }
  else if( !(flags&FLG_NO_SKIP) )
  {
    /************************************************************************/
    /* This is to skip the file data                                        */
    /************************************************************************/
    if( flags&FLG_VERBOSE ) {
      fprintf( stderr, "Skipping file data...\n" );
    }
    ret = fseek(fp, lh.csize, SEEK_CUR);
    if(ret != 0)
    {
      perror("Error seeking file");
      return(-1);
    }
  
    if((lh.gpb[0] & 0x08) == 0x08)
    {
      unsigned long sig;

      if( flags&FLG_VERBOSE ) {
        fprintf( stderr, "File contains data descriptor\n");
      }
      ret = read_ddesc( fp, flags );
    }
  }
  return(ret);
}

/******************************************************************************
 * READ DIRECTORY ENTRY                                                       *
 * Allowed flags:							      *
 *  FLG_NO_SKIP - don't skip extra ZIP-header data			      *
 *  FLG_VERBOSE - be verbose						      *
 ******************************************************************************/
int read_dir(FILE *fp, int flags)
{
int ret;

  ret = fread( dir.version, 2, 1, fp );
  if( ret == 1 )
	ret = fread( dir.verneed, 2, 1, fp );
  if( ret == 1 )
	ret = fread( dir.gpb, 2, 1, fp );
  if( ret == 1 )
	ret = fread( dir.compr, 2, 1, fp );
  if( ret == 1 )
	ret = fread( dir.time, 2, 1, fp );
  if( ret == 1 )
	ret = fread( dir.date, 2, 1, fp );
  if( ret == 1 )
	ret = read4int( fp, &dir.crc );
  if( ret == 1 )
	ret = read4int( fp, &dir.csize );
  if( ret == 1 )
	ret = read4int( fp, &dir.uncsize );
  if( ret == 1 )
	ret = read2int( fp, &dir.flen );
  if( ret == 1 )
	ret = read2int( fp, &dir.extralen );
  if( ret == 1 )
	ret = read2int( fp, &dir.commlen );
  if( ret == 1 )
	ret = read2int( fp, &dir.disk );
  if( ret == 1 )
	ret = fread( dir.attr, 2, 1, fp );
  if( ret == 1 )
	ret = read4int( fp, &dir.extattr );
  if( ret == 1 )
	ret = read4int( fp, &dir.locoffset );
  if(ret != 1)
  {
    fprintf( stderr, "Error in dir header\n");
    return(-1);
  }
  else;

  if( flags&FLG_VERBOSE ) {
    fprintf(stderr,"Version       = %02x %02x\n",dir.version[0],dir.version[1]);
    fprintf(stderr,"Version need  = %02x %02x\n",dir.verneed[0],dir.verneed[1]);
    fprintf( stderr, "General purp. = %02x %02x\n", dir.gpb[0], dir.gpb[1]);
    fprintf( stderr, "Compression   = %02x %02x\n", dir.compr[0], dir.compr[1]);
    fprintf( stderr, "Time          = %02x %02x\n", dir.time[0], dir.time[1]);
    fprintf( stderr, "Date          = %02x %02x\n", dir.date[0], dir.date[1]);
    fprintf( stderr, "CRC           = %08lx\n", dir.crc);
    fprintf( stderr, "Compr. size   = %lu\n", dir.csize);
    fprintf( stderr, "Uncomp. size  = %lu\n", dir.uncsize);
    fprintf( stderr, "Filename len. = %d\n", dir.flen);
    fprintf( stderr, "Extra field   = %d\n", dir.extralen);
    fprintf( stderr, "Comment len   = %d\n", dir.commlen);
    fprintf( stderr, "Disk          = %d\n", dir.disk);
    fprintf( stderr, "Attributes    = %02x %02x\n", dir.attr[0], dir.attr[1]);
    fprintf( stderr, "Ext. attr.    = %08lx\n", dir.extattr);
    fprintf( stderr, "Offset of loc = %lu\n", dir.locoffset);
  }

  if( !filename )
  {
    fnlen = 2*dir.flen;
    filename = malloc( fnlen+1 );
  }
  else if( dir.flen > fnlen )
  {
    fnlen = 2*dir.flen;
    filename = realloc( filename, fnlen+1 );
  }
  memset(filename, '\0', fnlen+1);
  ret = fread(filename, dir.flen, 1, fp);
  if(ret != 1)
  {
    fprintf( stderr, "Error in reading filename\n");
    return(-1);
  }

  if( flags&FLG_VERBOSE ) {
    fprintf( stderr, "Filename = %s\n", filename);
  }

  if(dir.extralen != 0 && !(flags&FLG_NO_SKIP))
  {
    if( flags&FLG_VERBOSE ) {
      fprintf( stderr, "File contains extra data (skipped)\n");
    }
    ret = fseek(fp, dir.extralen, SEEK_CUR);
  }

  if(dir.commlen != 0 && !(flags&FLG_NO_SKIP))
  {
    if( flags&FLG_VERBOSE ) {
      fprintf( stderr, "File contains comment data (skipped)\n");
    }
    ret = fseek(fp, dir.commlen, SEEK_CUR);
  }
  else;

  return 0;
}

/******************************************************************************
 * READ END OF DIRECTORY                                                      *
 * Allowed flag:							      *
 *  FLG_NO_SKIP - don't skip extra info in ZIP dir-entry		      *
 *  FLG_VERBOSE - be verbose						      *
 ******************************************************************************/
int read_end(FILE *fp, int flags)
{
int ret;

  ret = read2int( fp, &enddir.diskno );
  if( ret == 1 )
	ret = read2int( fp, &enddir.centrdiskno );
  if( ret == 1 )
	ret = read2int( fp, &enddir.diskentries );
  if( ret == 1 )
	ret = read2int( fp, &enddir.totentries );
  if( ret == 1 )
	ret = read4int( fp, &enddir.centrsize );
  if( ret == 1 )
	ret = read4int( fp, &enddir.centroffset );
  if( ret == 1 )
	ret = read2int( fp, &enddir.commlen );
  if(ret != 1)
  {
    fprintf( stderr, "Error in end of dir\n");
    return(-1);
  }
  else;

  if( flags&FLG_VERBOSE ) {
    fprintf( stderr, "Disk          = %d\n", enddir.diskno);
    fprintf( stderr, "Central disk  = %d\n", enddir.centrdiskno);
    fprintf( stderr, "Disk entries  = %d\n", enddir.diskentries);
    fprintf( stderr, "Total  entr.  = %d\n", enddir.totentries);
    fprintf( stderr, "Central size  = %lu\n", enddir.centrsize);
    fprintf( stderr, "Central offset= %lu\n", enddir.centroffset);
    fprintf( stderr, "Comment len   = %d\n", enddir.commlen);
  }

  if(enddir.commlen != 0 && !(flags&FLG_NO_SKIP))
  {
    if( flags&FLG_VERBOSE ) {
      fprintf( stderr, "Directory contains comment data (skipped)\n" );
    }
    ret = fseek(fp, enddir.commlen, SEEK_CUR);
  }
  else;

  return 0;
}

