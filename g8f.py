from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFile
import os, sys
import re
from common import parse_arguments, pretty_print

# DAZ3D Skin Fixer for Genesis 8 / 8.1 Female (G8F / G8.1F) (and Male (G8M / G8.1M) later)
# by Bang Systems

def areola_mask(size:int, feather:int = 50) -> Image.Image:
	inner = Image.new('L', (size*2, size*2), 0)
	inner_draw = ImageDraw.Draw(inner)
	inner_draw.circle((size, size), size/4, fill=255, outline=255)
	inner = inner.filter(ImageFilter.GaussianBlur(feather))
	outer = Image.new('L', (size*2, size*2), 0)
	outer_draw = ImageDraw.Draw(outer)
	outer_draw.circle((size, size), size/2, fill=255)
	outer = outer.filter(ImageFilter.GaussianBlur(feather / 1.5))
	return ImageChops.add(outer, inner)

def process_resize_aerola(image:ImageFile.ImageFile, position:tuple, mask:Image.Image, scale:float) -> ImageFile.ImageFile:
	region = image.crop((
		position[0] - mask.size[0] // 2,
		position[1] - mask.size[1] // 2,
		position[0] + mask.size[0] // 2,
		position[1] + mask.size[1] // 2
	))
	region.putalpha(mask)
	region = region.resize((
		int(region.size[0] * scale),
		int(region.size[1] * scale)
	))
	if region.mode != 'RGBA':
		region = region.convert('RGBA')
	image.paste(region, (
		position[0] - region.size[0] // 2,
		position[1] - region.size[1] // 2
	), region)
	return image

def process_resize_aerolas(image:ImageFile.ImageFile, scale) -> ImageFile.ImageFile:
	width, height = image.size
	right_aerola = (int(0.427 * width), int(0.47975 * height))
	print("  Right aerola:", right_aerola)
	left_aerola = (int(0.573 * width), int(0.47975 * height))
	print("   Left aerola:", left_aerola)
	mask = areola_mask(int(width / 8), feather=100)
	image = process_resize_aerola(image, left_aerola, mask, scale)
	image = process_resize_aerola(image, right_aerola, mask, scale)
	return image


def navel_mask(size:int, feather:int = 50) -> Image.Image:
	inner = Image.new('L', (size*2, size*2), 0)
	inner_draw = ImageDraw.Draw(inner)
	inner_draw.circle((size, size), size/8, fill=255, outline=255)
	inner = inner.filter(ImageFilter.GaussianBlur(feather))
	outer = Image.new('L', (size*2, size*2), 0)
	outer_draw = ImageDraw.Draw(outer)
	outer_draw.circle((size, size), size/4, fill=255)
	outer = outer.filter(ImageFilter.GaussianBlur(feather / 1.5))
	return ImageChops.add(outer, inner)

def process_remove_navel(image:ImageFile.ImageFile) -> ImageFile.ImageFile:
	width, height = image.size
	mask = navel_mask(int(width / 6), feather=100)
	navel = (int(0.5 * width), int(0.69 * height))
	skin = (int(0.5 * width), int(0.60 * height))
	print("         Navel:", navel)
	print("          Skin:", skin)
	region  = image.crop((
		skin[0] - mask.size[0] // 2,
		skin[1] - mask.size[1] // 2,
		skin[0] + mask.size[0] // 2,
		skin[1] + mask.size[1] // 2
	))
	region.putalpha(mask)
	image.paste(region, (
		navel[0] - region.size[0] // 2,
		navel[1] - region.size[1] // 2
	), region)
	return image


def genital_mask(size:int, feather:int = 50) -> Image.Image:
	inner = Image.new('L', (size*2, size*2), 0)
	inner_draw = ImageDraw.Draw(inner)
	inner_draw.ellipse((
		1.5 * size // 2,
		size // 2,
		5 * size // 4,
		6 * size // 4
	), fill=255)
	inner = inner.filter(ImageFilter.GaussianBlur(feather / 2))
	outer = Image.new('L', (size*2, size*2), 0)
	outer_draw = ImageDraw.Draw(outer)
	outer_draw.polygon((
		(size - size // 2, size // 2),
		(size + size // 2, size // 2),
		(size, size + size // 1.5)
	), fill=255)
	outer = outer.filter(ImageFilter.GaussianBlur(feather))
	return ImageChops.add(outer, inner)

def process_remove_genitals(image:ImageFile.ImageFile) -> ImageFile.ImageFile:
	width, height = image.size
	mask = genital_mask(int(width / 8), feather=100)
	genital = (int(0.5 * width), int(0.903 * height))
	skin = (int(0.5 * width), int(0.79 * height))
	print("       Genital:", genital)
	print("          Skin:", skin)
	region  = image.crop((
		skin[0] - mask.size[0] // 2,
		skin[1] - mask.size[1] // 2,
		skin[0] + mask.size[0] // 2,
		skin[1] + mask.size[1] // 2
	))
	region.putalpha(mask)
	image.paste(region, (
		genital[0] - region.size[0] // 2,
		genital[1] - region.size[1] // 2
	), region)
	return image


def brow_mask(size: int, feather: int = 50, angle:int = 7) -> Image.Image:
	brow = Image.new('L', (size * 2, size * 2), 0)
	brow_draw = ImageDraw.Draw(brow)
	brow_draw.ellipse((
		size // 4,
		size // 2,
		7 * size // 4,
		size + size // 2
	), fill=255)
	brow_draw.ellipse((
		size // 10,
		size // 2 + size // 4,
		19 * size // 10,
		size + size // 2 + size // 8
	), fill=0)
	brow = brow.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
	brow_faded = brow.filter(ImageFilter.GaussianBlur(feather))
	brow = brow.filter(ImageFilter.GaussianBlur(feather / 2))
	brow = ImageChops.add(brow, brow_faded)
	return brow


def process_remove_brows(image:ImageFile.ImageFile) -> ImageFile.ImageFile:
	width, height = image.size
	left_mask = brow_mask(int(width / 6), feather=100, angle=7)
	left_brow = (int(0.38 * width), int(0.55 * height))
	left_skin = (int(0.38 * width), int(0.4885 * height))
	print("    Left brow:", left_brow)
	print("    Left skin:", left_skin)
	region  = image.crop((
		left_skin[0] - left_mask.size[0] // 2,
		left_skin[1] - left_mask.size[1] // 2,
		left_skin[0] + left_mask.size[0] // 2,
		left_skin[1] + left_mask.size[1] // 2
	))
	region.putalpha(left_mask)
	image.paste(region, (
		left_brow[0] - region.size[0] // 2,
		left_brow[1] - region.size[1] // 2
	), region)
	right_mask = brow_mask(int(width / 6), feather=100, angle=-7)
	right_brow = (int(0.62 * width), int(0.55 * height))
	right_skin = (int(0.62 * width), int(0.4885 * height))
	print("   Right brow:", right_brow)
	print("   Right skin:", right_skin)
	region  = image.crop((
		right_skin[0] - right_mask.size[0] // 2,
		right_skin[1] - right_mask.size[1] // 2,
		right_skin[0] + right_mask.size[0] // 2,
		right_skin[1] + right_mask.size[1] // 2
	))
	region.putalpha(right_mask)
	image.paste(region, (
		right_brow[0] - region.size[0] // 2,
		right_brow[1] - region.size[1] // 2
	), region)
	return image

def help():
	script = os.path.basename(sys.argv[0])
	print(f"Usage: python {script} <file> --action --parameter")
	print()
	print("[Actions]")
	print("resize:aerolas")
	print("remove:brows,gens")
	print("grayscale:0.5 #UnderDevelopment")
	print("sss:0.5 #UnderDevelopment")
	print()
	print("[Parameters]")
	print("scale:0.5")
	print("force")
	print()
	print("[Examples]")
	print(f"python {script} \"path\\filename.png\" --resize:aerolas --scale:0.5")
	print(f"python {script} \"path\\filename.png\" --remove:brows")
	print(f"python {script} \"path\\filename.png\" --grayscale:0.5")
	print(f"python {script} \"path\\filename.png\" --sss:0.8")
	print(f"python {script} \"path\\filename.png\" --remove:navel,genital --resize:nipples --scale:0.5")
	print(f"python {script} \"path\\filename.png\" --remove:navel+genital --resize:nipples --scale:0.5")

if __name__ == "__main__":
	args = parse_arguments(sys.argv)
	if '@parameters' not in args:
		help()
		sys.exit(1)
	if not isinstance(args['@parameters'], list) or len(args['@parameters']) == 0:
		help()
		sys.exit(1)
	#pretty_print(args)
	filename = args["@parameters"][0] if len(args["@parameters"]) > 0 else None
	if filename is None:
		help()
		sys.exit(1)
	if not os.path.exists(filename):
		print(f"File not found: {filename}")
		sys.exit(1)
	print("    Processing:", filename)
	image = Image.open(filename)
	print("    Image size:", image.size)
	changed = False
	force = False
	if 'force' in args:
		force = True

	if 'remove' in args:
		print(f"[Removing] {args['remove']}")
		if isinstance(args['remove'], str):
			args['remove'] = args['remove'].split(',')
		if isinstance(args['remove'], list):
			for remove in args['remove']:
				if remove in ['brows', 'brow']:
					image = process_remove_brows(image)
					changed = True
				if remove in ['navel', 'nav']:
					print("Removing navel...")
					image = process_remove_navel(image)
					changed = True
				if remove in ['genitals', 'genital', 'gens', 'gen']:
					print("Removing genitals...")
					image = process_remove_genitals(image)
					changed = True
				elif remove in ['butt', 'crack', 'buttcrack', 'ass']:
					print("Not implemented yet")
					#image = process_remove_buttcrack(image)
					#changed = True

	if 'resize' in args:
		print(f"[Resizing] {args['resize']}")
		if args['resize'] in ['aerola', 'aerolas', 'nipple', 'nipples']:
			scale = 0.5
			if 'scale' in args:
				scale = float(args['scale']) if 'scale' in args else 0.0 # type: ignore
			if scale < 0.4 and force == False:
				print("Scale value is dangerously low, consider doing the scaledown twice, or use --force")
				sys.exit(1)
			print(f"Resizing nipples to {scale}...")
			image = process_resize_aerolas(image, scale)
			changed = True

	if 'sss' in args:
		print("SSS is not implemented yet")

	if 'grayscape' in args:
		print("Grayscape is not implemented yet")

	if changed:
		file_ext = os.path.splitext(filename)[1]
		new_filename = filename.replace(file_ext, '-f.png')
		image.save(
			new_filename
		)
		print("          Done:", new_filename)
