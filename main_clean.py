from PIL import Image
import pytesseract
import pyperclip
import time
import os

# configuring this for windows it easy, change screenshot_path (more details in config.txt) and next change is os.system('cls') instead of 'clear'

language = 'eng'
delete_after = True
screenshot_path = '/home/pc/Pictures'


files = []
for i in os.listdir(screenshot_path):
    if i.lower().endswith('.png'):
        files.append(i)
files = files


before_files = files

os.system('clear')
print('running')



question_text=''
def process_image(image_path):
    global question_text
    im = Image.open(image_path, mode='r', formats=['png'])
    text = pytesseract.image_to_string(im, lang=language).strip(' \n')

    text = text.strip('\n\t')

    pyperclip.copy(text)

    name = os.path.split(image_path)[1]
    print_text  = name+'\n'
    print_text = '-'*len(name)+'\n'
    print_text += text+'\n'
    print_text += '-'*(len(name))

    print('\n'+print_text)



while True:
    time.sleep(0.4)

    files_before = files
    files = []
    for i in os.listdir(screenshot_path):
        if i.lower().endswith('.png'):
            files.append(i)

    if (len(files) > len(before_files)):
        pyperclip.copy('')
        os.system('clear')
        image_path = os.path.join(screenshot_path, files[-1])
        process_image(image_path)
        if delete_after:
            os.remove(image_path)
        else:
            before_files=files
