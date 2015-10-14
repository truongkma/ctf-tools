#include <SDL2/SDL.h>
Uint32 getpixel(SDL_Surface *surface, int x, int y) {
    int bpp = surface->format->BytesPerPixel;
    Uint8 *p = (Uint8 *)surface->pixels + y * surface->pitch + x * bpp;

    switch(bpp) {
    case 1:
        return *p;

    case 2:
        return *(Uint16 *)p;

    case 3:
        if(SDL_BYTEORDER == SDL_BIG_ENDIAN)
            return p[0] << 16 | p[1] << 8 | p[2];
        else
            return p[0] | p[1] << 8 | p[2] << 16;
    case 4:
        return *(Uint32 *)p;

    default:
        return 0;
    }
}

void putpixel(SDL_Surface *surface, int x, int y, Uint32 pixel) {
    int bpp = surface->format->BytesPerPixel;
    Uint8 *p = (Uint8 *)surface->pixels + y * surface->pitch + x * bpp;

    switch(bpp) {
    case 1:
        *p = pixel;
        break;

    case 2:
        *(Uint16 *)p = pixel;
        break;

    case 3:
        if(SDL_BYTEORDER == SDL_BIG_ENDIAN) {
            p[0] = (pixel >> 16) & 0xff;
            p[1] = (pixel >> 8) & 0xff;
            p[2] = pixel & 0xff;
        } else {
            p[0] = pixel & 0xff;
            p[1] = (pixel >> 8) & 0xff;
            p[2] = (pixel >> 16) & 0xff;
        }
        break;

    case 4:
        *(Uint32 *)p = pixel;
        break;
    }
}

int main() {
  SDL_Init(SDL_INIT_VIDEO);
  SDL_Surface* s = SDL_LoadBMP("qr.bmp");

  for (int y = 0; y < s->h; y+=8) {
    for (int x = 0; x < s->w; x+=8) {
      Uint32 p = getpixel(s, x, y);
      Uint8 r, g, b;
      SDL_GetRGB(p, s->format, &r, &g, &b);
      int v = (r + g + b) / 2;
      if (v > 200)
        printf("_");
      else if (v > 50)
        printf("?");
      else
        printf("X");
    }
    puts("");
  }
}
