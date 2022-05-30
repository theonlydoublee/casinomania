import os

from PIL import Image

resizeAmount = 4


async def cards_image(cards, userID, guildID, hide=False):
    # cards = []
    # for i in range(2):
    #     cards.append(random.choice(os.listdir('casinomania/images/cards/')))

    # print(cards)
    images = [Image.open(f'casinomania/images/cards/{x}') for x in cards]

    newImages = []

    for image in images:
        image = image.resize(((image.width/resizeAmount).__floor__(), (image.height/resizeAmount).__floor__()))
        newImages.append(image)
        # print(image.width)

    if hide:
        newImages[1] = Image.open(f'casinomania/images/cards/back.png').resize((((500/resizeAmount).__floor__(), (726/resizeAmount).__floor__())))
    widths, heights = zip(*(i.size for i in newImages))

    total_width = sum(widths) + ((len(newImages)-1)*resizeAmount)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in newImages:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]+resizeAmount
    os.makedirs(f'casinomania/images/hands/{guildID}/', exist_ok=True)

    new_im.save(f'casinomania/images/hands/{guildID}/{userID}.jpg')

    # return new_im.load()
    return f'casinomania/images/hands/{guildID}/{userID}.jpg'
