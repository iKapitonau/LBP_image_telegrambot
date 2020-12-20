import logging
import os
import traceback
import skimage as sk
from skimage import io
from telegram import Bot, Update
from telegram.ext import Updater, MessageHandler, Filters
import skimage.io as skio
import numpy as np
from skimage.feature import local_binary_pattern as lbp


TG_TOKEN = '1374700679:AAHfE0m5qMBUc_QZ1Oikh7yiG7afFCpk_x8'
DATA_DIR = 'tmp_data'


def message_handler(update, context):
    bot = context.bot
    try:
        user = update.effective_user
        name = user.first_name if user else 'Anonymous'

        chat_id = update.effective_message.chat_id
        out_text, local_file_path = get_image_from_message(bot, update)

        if out_text:
            bot.send_message(chat_id=chat_id, text=out_text)

        if not local_file_path:
            reply_text = f'Hi, {name}\n'
            reply_text += 'I can only send your image back for now :(. ' + \
                          'Please send me an image.'
            bot.send_message(chat_id=chat_id, text=reply_text)
        else:
            bot.send_message(chat_id=chat_id, text='Processing...')

            input_img = skio.imread(local_file_path)
            P, R, method = 8, 1, 'uniform'
            img = lbp(sk.color.rgb2gray(input_img), P, R, method)

            processed_filename = 'processed.jpg'
            skio.imsave(processed_filename, img)

            out_text = f'Here is your image:'
            bot.send_message(chat_id=chat_id, text=out_text)
            bot.send_photo(chat_id=chat_id, photo=open(processed_filename, 'rb'))
    except:
        chat_id = update.effective_message.chat_id
        err_txt = traceback.format_exc()
        reply_text = 'An error occurred -.-\n\n' + err_txt
        bot.send_message(chat_id=chat_id, text=reply_text)


def get_image_from_message(bot, update):
    document = update.effective_message.document
    photo = update.effective_message.photo
    out_text, file_id = None, None

    if document:
        if not document.__class__ == list:
            document = [document]

        document = [doc for doc in document if doc.mime_type.startswith('image')]

        if document:
            out_text = 'Found image as document'
            file_id = document[0].file_id

    if photo:
        if not photo.__class__ == list:
            photo = [photo]

        num_pix_photo = [(p.height * p.width, p) for p in photo]
        ph = sorted(num_pix_photo, reverse=True)[0][1]
        w, h = ph.width, ph.height

        out_text = f'Found image as photo of resolution {w}x{h}'
        file_id = ph.file_id

    if file_id:
        file = bot.getFile(file_id)
        _, ext = os.path.splitext(file.file_path)
        local_file_path = os.path.join(DATA_DIR, 'input' + ext)
        os.makedirs(DATA_DIR, exist_ok=True)
        file.download(custom_path=local_file_path)

        return out_text, local_file_path

    return None, None


def main():
    bot = Bot(token=TG_TOKEN)
    updater = Updater(bot=bot)

    handler = MessageHandler(Filters.all, message_handler)
    updater.dispatcher.add_handler(handler)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                         level=logging.DEBUG)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
