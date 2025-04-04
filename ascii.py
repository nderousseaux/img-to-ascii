from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import sys
import random

# === Constantes pour la configuration ===
IMAGE_PATH = "./in.png"          # Chemin vers l'image source
OUTPUT_PATH = "./out.png"       # Chemin de sauvegarde de l'image ASCII
ASCII_CHARS = " ·-+#"				    	 # Caractères à utiliser pour la conversion
OUTPUT_WIDTH_CHARS = 40            # Largeur de l'image ASCII en caractères
OUTPUT_WIDTH_SIZE = 2080					 # Largeur de l'image ASCII en pixels
RELATIVE_SIZE_OF_ASCII_CHAR = 1.3    # Taille de l'ascii dans son pixel (1 = 100%)
FONT = "./font.ttf"                # Chemin vers la police de caractères

CONTRAST = 0			                 # Contraste
LUMINOSITY = 0			               # Luminosité
SHARPNESS = 0			               		# Netteté
SHARPEN = 0			               # Activer le filtre de netteté
DETAIL = 0			               # Activer le filtre de détails

# === Chargement de l'image d'origine ===
orig_image = Image.open(IMAGE_PATH)
orig_width, orig_height = orig_image.size

# === Calcul de la taille de l'image de sortie ===
output_width = OUTPUT_WIDTH_CHARS
output_height = int(OUTPUT_WIDTH_CHARS * orig_height / orig_width)
output_height_size = OUTPUT_WIDTH_SIZE * orig_height // orig_width
print(f"Taille de l'image à convertir: {orig_width}x{orig_height}")
print(f"Taille de nombre de caractères ASCII: {output_width}x{output_height}")
print(f"Taille de l'image de sortie: {OUTPUT_WIDTH_SIZE}x{output_height_size}")

if OUTPUT_WIDTH_SIZE % OUTPUT_WIDTH_CHARS != 0 or output_height_size % output_height != 0:
	print("Le nombre de caractères ASCII n'est pas un multiple de la taille de l'image de sortie.")
	sys.exit(1)
ascii_pixel_width = OUTPUT_WIDTH_SIZE // OUTPUT_WIDTH_CHARS
ascii_pixel_height = output_height_size // output_height

# === Conversion de l'image pour l'analyse ===
image = orig_image.convert("L")
image = image.filter(ImageFilter.EDGE_ENHANCE_MORE) if DETAIL else image
image = image.filter(ImageFilter.SHARPEN) if SHARPEN else image
image = ImageEnhance.Contrast(image).enhance(1 + CONTRAST)
image = ImageEnhance.Brightness(image).enhance(1 + LUMINOSITY)
image = ImageEnhance.Sharpness(image).enhance(1 + SHARPNESS)
# image = image.filter(ImageFilter.DETAIL) if DETAIL else image

# image = ImageEnhance.
image.save("debug.png") # Enregistrement de l'image convertie pour debug

image = image.resize((output_width, output_height))

# === Création du tableau de charactères ASCII ===
output_np = np.zeros((OUTPUT_WIDTH_CHARS, int(OUTPUT_WIDTH_CHARS * orig_height / orig_width)), dtype=str)
for y in range(output_height):
		for x in range(output_width):
				output_np[x, y] = ASCII_CHARS[image.getpixel((x, y)) * len(ASCII_CHARS) // 256]
		
# === Output du string ASCII ===
output_str = ""
for y in range(output_height):
		for x in range(output_width):
				output_str += output_np[x, y]
		output_str += "\n"
# print(output_str)

# === Creation de l'image de sortie ===
output = Image.new("RGB", (OUTPUT_WIDTH_SIZE, OUTPUT_WIDTH_SIZE * orig_height // orig_width), (255, 255, 255))

# === Calcul de la carte de pixels ASCII ===
ascii_pixels = np.zeros((OUTPUT_WIDTH_CHARS, int(OUTPUT_WIDTH_CHARS * orig_height / orig_width)), dtype=object)
for y in range(int(OUTPUT_WIDTH_CHARS * orig_height / orig_width)):
		for x in range(OUTPUT_WIDTH_CHARS):
				x0 = x * ascii_pixel_width
				y0 = y * ascii_pixel_height
				x1 = x0 + ascii_pixel_width
				y1 = y0 + ascii_pixel_height
				ascii_pixels[x, y] = (x0, y0, x1, y1)

# === Dessin de l'image de sortie ===
draw = ImageDraw.Draw(output)
font = ImageFont.truetype(FONT, int(ascii_pixel_height * RELATIVE_SIZE_OF_ASCII_CHAR))
draw.rectangle([0, 0, OUTPUT_WIDTH_SIZE, OUTPUT_WIDTH_SIZE * orig_height // orig_width], fill=(0, 0, 0))

# On dessine le caractère ASCII au centre du pixel
def size(char):
	bbox = font.getbbox(char)
	x, y = bbox[2] - bbox[0], bbox[3]
	return (x, y)

# pour chaque pixel ASCII
for y in range(ascii_pixels.shape[1]):
	for x in range(ascii_pixels.shape[0]):
		x0, y0, x1, y1 = ascii_pixels[x, y]
		char = output_np[x, y]
		char_size = size(char)
		# On dessine le caractère ASCII au centre du pixel
		draw.text((x0 + (ascii_pixel_width - char_size[0]) // 2, y0 + (ascii_pixel_height - char_size[1]) // 2), char, font=font, fill=(255, 255, 255))


		# Contour, pour le debug
		# draw.rectangle([x0, y0, x1, y1], outline=(255, 0, 0))
		


# === Sauvegarde de l'image finale ===
output.save(OUTPUT_PATH)