from threading import Thread
import subprocess as sp
from PIL import Image
import pytesseract
import pyperclip
import time
import sys
import os


def nice_str(value, lenght, align='left', fill='0'):
    if align == 'left':
        return (fill*(lenght)+str(value))[-lenght:]
    if align == 'right':
        return (str(value)+fill*(lenght))[:lenght]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# reading config
username = os.getlogin()
if 'config.txt' in os.listdir('.'):
    with open('config.txt', 'r', encoding='utf8') as f:
        data = f.read().replace('USERNAME', username)
    
    configured = [False]*3
    for i in data.split('\n'):
        i = i.split('#')[0].strip(' ')
        if i == '':
            continue
        if '=' in i:
            value = i.split('=')[1].strip(' "{}'.format("'").replace('/', '\\'))

            if i.startswith('tesseract_path'):
                configured[0] = True
                pytesseract.pytesseract.tesseract_cmd = value#.encode()
            elif i.startswith('screenshot_path'):
                configured[1] = True
                screenshot_path = value
            elif i.startswith('language_path'):
                configured[2] = True
                language_path = value
else:
    print('config.txt does not exist in your current path')
    print('your current path (where you run it) is :{}'.format(os.getcwd()))
    exit()
#---------------

# config control
for i in range(3):
    if (i==0) and (configured[i]==False):
        print('tesseract_path is not configured')
    if (i==1) and (configured[i]==False):
        print('screenshot_path is not configured')
    if (i==2) and (configured[i]==False):
        print('language_path is not configured')

if not all(configured):
    print('abort')
    exit()
#---------------

# creating text_history.txt if it's not exists
if not 'text_history.txt' in os.listdir('.'):
    with open('text_history.txt', 'w', encoding='utf8') as f:
        f.write('')
#----------------------------------------------

# creating quick_run.bat if it's not exists
py_exe_path = sys.executable
py_path = os.path.join(os.getcwd(), 'main.py')
if not 'quick_run.bat' in os.listdir('.'):
    with open('quick_run.bat', 'w', encoding='utf8') as f:
        f.write('"{}" "{}"\npause\n'.format(py_exe_path, py_path))
#----------------------------------------------



# setting language
files = os.listdir(language_path)
languages = []
for filename in files:
    if filename.endswith('.traineddata'):
        languages.append(str(filename[:-len('.traineddata')]))
languages = sorted(languages)

clear()
lenght_of_languages = len(languages)

    
terminal_size = list(os.get_terminal_size())
terminal_size[1] = 10

end_of_line_marigin = 2+1+int(-0.001+len('for more languages, download .traineddata files and put it in "{}" folder'.format(language_path))/terminal_size[0])

while True:
    max_word_lenght = max([len(i) for i in languages])
    words_per_line = lenght_of_languages//(terminal_size[1]-end_of_line_marigin)
    words_per_line_remainer = lenght_of_languages%(terminal_size[1]-end_of_line_marigin)
    lines = round((lenght_of_languages-words_per_line_remainer)/words_per_line)

    #print(words_per_line, words_per_line_remainer, lines)

    print_out = []
    for line_no in range(lines):
        out = ''
        line_lenght = words_per_line+1*(line_no<words_per_line_remainer)
        for word_no in range(line_lenght):
            if word_no == line_lenght-1:
                pass
                no=word_no*lines+line_no
                out += nice_str(no+1, len(str(lenght_of_languages+1)), fill=' ') + ')' + languages[no]
            else:
                no=word_no*lines+line_no
                out += nice_str(no+1, len(str(lenght_of_languages+1)), fill=' ') + ')' + nice_str(languages[no], max_word_lenght, fill=' ', align='right') + ' '
        print_out.append(out)

    max_out_lenght = max([len(i) for i in print_out])
    if max_out_lenght < terminal_size[0]:
        break
    else:
        terminal_size[1] = terminal_size[1]+1
clear()
print('\n'.join(print_out))
print('')


print('for more languages, download .traineddata files and put it in "{}" folder'.format(language_path))
sel3 = input('your selection? :')
assert int(sel3) == float(sel3)
sel3 = int(sel3)
assert 0<sel3
if not sel3<len(languages)+1:
    print('wrong input')
    exit()

language = languages[sel3-1]

clear()
print('language set to "{}"\nListening...\n\n'.format(language))
# ----------------





# detection and proccessing
files = os.listdir(screenshot_path)
files_png = []
for i in files:
    if i.lower().endswith('.png'):
        files_png.append(i)
files = set(files_png)


quene_images = []

living_signal = time.time()
killed = False

def ocr_thread():
    global quene_images, killed
    while True:
        if abs(time.time()-living_signal)>2:
            killed = True
            print('thread killed due to the "kill_signal"')
            break

        if len(quene_images) > 0:
            name = quene_images[0]
            quene_images.pop(0)

            full_image_path = os.path.join(screenshot_path, name)
            
            im = Image.open(full_image_path, mode='r', formats=['png'])
            if im.size == (364, 180):
                # print('Fake image :', name) # fake image is i think for the notification image
                continue

            text = pytesseract.image_to_string(im, lang=language).strip(' \n')

            pyperclip.copy(text)

            if len(name)>60:
                name = name[:60-4]+'...'
            print_text = '>' + name + '\n'
            print_text += '-'*60 + '\n'
            print_text += text + '\n'
            print_text += '-'*60+'\n'
            

            print(print_text)
            with open('text_history.txt', 'r', encoding='utf8') as f:
                full_text = f.read() + text
            
            while '\n\n\n' in full_text:
                full_text = full_text.replace('\n\n\n', '\n\n')
            
            with open('text_history.txt', 'w', encoding='utf8') as f:
                f.write(full_text+'\n'+'-'*20+'\n')

        time.sleep(.1)

Thread(target=ocr_thread).start()

before_files = files
while True:
    time.sleep(1)

    living_signal = time.time()
    if killed:
        print('threading problem, thread killed unexpectedly...')
        exit(1)

    files = os.listdir(screenshot_path)
    files_png = []
    for i in files:
        if i.lower().endswith('.png'):
            files_png.append(i)
    files = set(files_png)

    added_files = files-before_files
    if (len(added_files)>0):
        before_files = files
        # print(added_files)
        for name in added_files:
            quene_images.append(name)
#--------------------------

