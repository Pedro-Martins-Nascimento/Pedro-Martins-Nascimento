"""
Preps a photo for ASCII conversion:
  1. Remove the background with rembg so the subject is isolated.
  2. Boost local contrast with OpenCV's CLAHE — gives a flat face real
     highlights and shadows.
  3. Composite onto pure white so the background maps to the blank end
     of the ASCII ramp (white -> spaces).
Output: source-prepped.png (grayscale), next to the input photo.

Usage: python scripts/prep_photo.py source-photo.jpg [--crop top,right,bottom,left]

--crop trims raw pixels off each edge BEFORE background removal. Handy when
something busy behind you (a screen, a poster, another person) confuses the
segmentation — e.g. --crop 60,0,0,0 trims 60px off the top.
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def parse_crop(args):
    if "--crop" not in args:
        return (0, 0, 0, 0)
    idx = args.index("--crop")
    top, right, bottom, left = (int(x) for x in args[idx + 1].split(","))
    return (top, right, bottom, left)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <photo.jpg> [--crop top,right,bottom,left]", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    out_path = "source-prepped.png"
    top, right, bottom, left = parse_crop(sys.argv)

    # 1. Remove background
    im = Image.open(src_path).convert("RGBA")
    if any((top, right, bottom, left)):
        w, h = im.size
        im = im.crop((left, top, w - right, h - bottom))
    no_bg = remove(im)  # RGBA, transparent background

    # 2. Composite onto pure white (so background -> white -> maps to space glyph)
    white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, no_bg).convert("RGB")

    # 3. Grayscale + CLAHE contrast boost
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    boosted = clahe.apply(gray)

    # Re-flatten the background to pure white: CLAHE can drag flat white
    # regions slightly off-white, which would print faint noise glyphs.
    # Anything that was near-white before CLAHE snaps back to 255.
    orig_gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    mask = orig_gray > 245
    boosted[mask] = 255

    Image.fromarray(boosted).save(out_path)
    print(f"Wrote {out_path} ({boosted.shape[1]}x{boosted.shape[0]})")


if __name__ == "__main__":
    main()
