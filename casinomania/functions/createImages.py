import sys
import random, os
from PIL import Image


async def cards_image(cards, userID, hide=False):
    # cards = []
    # for i in range(2):
    #     cards.append(random.choice(os.listdir('casinomania/images/cards/')))

    # print(cards)
    images = [Image.open(f'casinomania/images/cards/{x}') for x in cards]
    if hide:
        images[1] = Image.open(f'casinomania/images/cards/back.png')
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths) + ((len(images)-1)*5)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]+5

    new_im.save(f'casinomania/images/hands/{userID}.jpg')

    # return new_im.load()
    return f'casinomania/images/hands/{userID}.jpg'
