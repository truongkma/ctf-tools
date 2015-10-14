/*
 * exfunc.c
 *
 * This file contains a function extracting compressed data from a ZIP-archive.
 * Gratefully received from a person who wishes to remain anonymous.
 * Slightly modified by Peter Conrad, Aug '96
 *
 * $Id: exfunc.c,v 1.9 2003/01/05 14:40:37 lucifer Exp $
 *
 * $Log: exfunc.c,v $
 * Revision 1.9  2003/01/05 14:40:37  lucifer
 * Included RElf's modifications regarding data descriptor
 *
 * Revision 1.9  2003/01/04 13:43:18  RElf
 * SIGN_* constants used
 *
 * Revision 1.8  2002/01/30 15:26:14  lucifer
 * Added extern int read_ddesc
 *
 * Revision 1.7  1998/04/28 21:10:31  lucifer
 * Added support for data descriptor
 *
 * Revision 1.6  1997/09/23 20:07:31  lucifer
 * Removed declaration of strdup
 *
 * Revision 1.5  1997/09/23 17:31:17  lucifer
 * Added caseflg to extract()
 *
 * Revision 1.4  1997/02/15 09:46:47  lucifer
 * Small DEBUG-bug patched by Mats Lofkvist <mal@aristotle.algonet.se>
 *
 * Revision 1.3  1996/08/21 18:17:57  conrad
 * Some cleanups to suppress some warnings...
 *
 * Revision 1.2  1996/08/21 17:33:00  conrad
 * some cleaning up with regard to variables
 * moved strupr() here (from extract.c)
 * changed parameters of read_{local,dir,end}()
 *
 */

#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include <ctype.h>
#include "headers.h"

static char RCSID[]="$Id: exfunc.c,v 1.9 2003/01/05 14:40:37 lucifer Exp $";

extern int      read_sig( FILE *fp );
extern int      read_local( FILE *fp, char *fname, int flags );
extern int      read_dir( FILE *fp, int flags );
extern int      read_end( FILE *fp, int flags );
extern int	read_ddesc(FILE *fp, int flags);

#define	TRUE	1
#define	FALSE	0

char *extract(char *zipname, char *decfile, int caseflg )
{
int end;
int error;
int found;
int ret;
int rc;
char	*data;
FILE	*fp;               /* ZIP file pointer */

  fp = fopen(zipname, "rb");
  if(fp==NULL)
  {
    perror("Error opening the ZIP file");
    return(0);
  }

  /****************************************************************************/
  /* Search the given file in the ZIP archive                                 */
  /****************************************************************************/
  found = FALSE;
  error = FALSE;
  end = FALSE;
  do
  {
    ret = read_sig(fp);
    switch(ret)
    {
      case SIGN_LOCAL:
        {
#ifdef DEBUG
	  printf("\nFile signature found\n");
#endif
	  rc = read_local(fp,decfile,caseflg);
	  switch(rc)
	  {
	    case 1:
	      {
	        found = TRUE;
	        end = TRUE;
	      }
	      break;
	    case 0:
	      break;
	    case -1:
	      {
	        printf("Error reading ZIP file\n");
	        end = TRUE;
	        error = TRUE;
	      }
	      break;
	  }
	}
	break;

      case SIGN_DIR:
          read_dir(fp,0);
	break;

      case SIGN_END:
	  read_end(fp,0);
	  end = TRUE;
	break;

      case SIGN_DDESC:
          read_ddesc(fp,0);
	break;

      default:
        printf("Error: unknown signature (ZIP file may be corrupt)\n");
	end = TRUE;
	error = TRUE;
	break;
    }
  } while (end == FALSE);

  if(error == TRUE)
  {
    fclose( fp );
    return(0);
  }
  else;

  if(found == FALSE)
  {
    fclose( fp );
    printf("File %s not found in ZIP file\n", decfile);
    return(0);
  }
  else;

  data = malloc( lh.csize );

  if(!data)
  {
    fclose( fp );
    printf("Error allocating memory\n");
    return(0);
  }
  else;

  end = FALSE;
  error = FALSE;
  ret = fread(data, (size_t) lh.csize, 1, fp);
  if(ret != 1)
  {
    perror("Error reading ZIP file");
    end = TRUE;
    error = TRUE;
    free(data);
  }

  fclose(fp);

#ifdef DEBUG
  printf("File closed\n");
#endif

  if( !error )
    return(data);
  else
    return 0;
}
