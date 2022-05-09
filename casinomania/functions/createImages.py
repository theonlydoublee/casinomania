import sys
from PIL import Image


async def cards_image(cards):
    images = [Image.open(f'casinomania/images/{x}') for x in cards]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths) + ((len(images)-1)*5)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]+5

    new_im.save('test.jpg')

    # return new_im
