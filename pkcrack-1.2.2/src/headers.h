/*
 * headers.h
 *
 * This file defines some structures containing information from a typical
 * ZIP-archive. Gratefully received from a person who wishes to remain 
 * anonymous. Some changes by Peter Conrad, August 1996.
 *
 * $Id: headers.h,v 1.7 2003/01/05 14:40:37 lucifer Exp $
 *
 * $Log: headers.h,v $
 * Revision 1.7  2003/01/05 14:40:37  lucifer
 * Included RElf's modifications regarding data descriptor
 *
 *
 * Revision 1.7  2003/01/04 13:10:05  RElf
 * Added 'signature' field to struct ddesctype
 * Header types are replaced with signatures
 *
 * Revision 1.6  2002/12/28 15:56:55  lucifer
 * Integrated fix6 from RElf: added option -p to extract
 *
 * Revision 1.6  2002/12/03 23:55:32  RElf
 * Added FLG_IGNORE_PATH
 *
 * Revision 1.5  1998/04/28 21:09:23  lucifer
 * Added FLG_VERBOSE
 * Added DDESC
 *
 * Revision 1.4  1997/09/23 17:32:18  lucifer
 * Added flags
 *
 * Revision 1.3  1997/09/18 18:14:57  lucifer
 * Added _HEADERS_H
 *
 * Revision 1.2  1996/08/21 17:35:19  conrad
 * variable-prototypes for stuff in readhead.c
 *
 * Revision 1.1  1996/08/20 17:58:45  conrad
 * Initial revision
 *
 */

#ifndef _HEADERS_H
#define _HEADERS_H

/******************************************************************************/
/* Various types and constants                                                */
/******************************************************************************/

/******************************************************************************/
/* Signatures constants / Header types                                        */
/******************************************************************************/
#define SIGN_LOCAL 0x04034b50u
#define SIGN_DIR   0x02014b50u
#define SIGN_END   0x06054b50u
#define SIGN_DDESC 0x08074b50u

/******************************************************************************
 * Flags								      *
 ******************************************************************************/
#define FLG_NO_SKIP		1
#define	FLG_CASE_SENSITIVE	2
#define FLG_VERBOSE		4
#define FLG_IGNORE_PATH         8

/******************************************************************************/
/* Local header                                                               */
/******************************************************************************/
typedef struct
{
  unsigned char version[2];
  unsigned char gpb[2];
  unsigned char compr[2];
  unsigned char time[2];
  unsigned char date[2];
  unsigned long crc;
  unsigned long csize;
  unsigned long uncsize;
  unsigned short flen;
  unsigned short extralen;
} local;

/******************************************************************************/
/* Directory                                                                  */
/******************************************************************************/
typedef struct
{
  unsigned char version[2];
  unsigned char verneed[2];
  unsigned char gpb[2];
  unsigned char compr[2];
  unsigned char time[2];
  unsigned char date[2];
  unsigned long crc;
  unsigned long csize;
  unsigned long uncsize;
  unsigned short flen;
  unsigned short extralen;
  unsigned short commlen;
  unsigned short disk;
  unsigned char attr[2];
  unsigned long extattr;
  unsigned long locoffset;
} dirtype;

/******************************************************************************/
/* End of directory                                                           */
/******************************************************************************/
typedef struct
{
  unsigned short diskno;
  unsigned short centrdiskno;
  unsigned short diskentries;
  unsigned short totentries;
  unsigned long centrsize;
  unsigned long centroffset;
  unsigned short commlen;
} enddirtype;

/******************************************************************************/
/* Data descriptor                                                            */
/******************************************************************************/
typedef struct
{
  unsigned long signature;
  unsigned long crc;
  unsigned long csize;
  unsigned long uncsize;
} ddesctype;

extern local		lh;
extern dirtype		dir;
extern enddirtype	enddir;
extern ddesctype	ddesc;
extern char		*filename;

#endif /* _HEADERS_H */
