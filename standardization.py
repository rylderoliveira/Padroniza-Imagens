import os
import re
from PIL import Image, ImageEnhance
import argparse
import requests
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--root-path', help='Full Input Path')
parser.add_argument('-w', '--new-width', help='New image width')
args = parser.parse_args()

BASE_URL = "https://image.tmdb.org/t/p/original"
# The new width for images in the ROOT_PATH folder.
NEW_WIDTH = args.new_width or 1080
# Path to the folder you want Python to find and resize images
ROOT_PATH = args.root_path or r'C:\www\Inova\image-treatment\images'

STYLES = ['backdrop', 'logo', 'poster']

# Fatores de filtro da imagem final
FATOR_SHARP = 10
FATOR_BRILHO = 1.2
FATOR_CONTRASTE = 0.9


def delete_not_processed(root, file):
    flag = '_PROCESSED'
    if flag not in file:
        os.remove(f'{root}\{file}')
        print(f'{root}\{file} removed')


def files_loop_delete(root, files):
    for file in files:
        delete_not_processed(root, file)


def img_download():

    # Tabela de testes com URL's mockadas
    table = pd.read_excel("C:\www\Inova\image-treatment\mock.xlsx")

    for item in range(len(table)):

        # Criando repositorios caso não exista
        if not os.path.exists('./images'):
            os.makedirs('images')

        if not os.path.exists('./images/' + str(table['tmdb'][item])):
            os.makedirs('./images/' + str(table['tmdb'][item]))

        for style in STYLES:
            if str(table[style][item]) != 'nan':
                url_file = './images/' + \
                    str(table['tmdb'][item]) + '/' + style + str(item) + '.jpg'
                with open(url_file, 'wb') as imagem:
                    resposta = requests.get(
                        BASE_URL + str(table[style][item]), stream=True)

                    if not resposta.ok:
                        print("Ocorreu um erro, status:", resposta.status_code)
                    else:
                        for dado in resposta.iter_content(1024):
                            if not dado:
                                break
                            imagem.write(dado)
                    print("Imagem salva! =)")


def calc_new_height(width, height, new_width):
    return round(new_width * height / width)


def resize(root, file, new_width, new_img_name):
    original_img_path = os.path.join(root, file)
    new_img_path = os.path.join(root, new_img_name)

    try:
        new_width = int(new_width)
    except:
        raise TypeError(
            f'-w, --new-width or NEW_WIDTH must be a number. Sent "{NEW_WIDTH}".')

    pillow_img = Image.open(original_img_path)
    width, height = pillow_img.size

    new_height = calc_new_height(width, height, new_width)

    new_img = pillow_img.resize(
        (new_width, new_height), Image.Resampling.LANCZOS)

    # # Aplica um filtro de Sharp
    # enhancer = ImageEnhance.Sharpness(new_img)
    # enhancer.enhance(FATOR_SHARP).show()

    # # Aplica um efeito de Brilho
    # enhancer2 = ImageEnhance.Brightness(new_img)
    # enhancer2.enhance(FATOR_BRILHO).show()

    # # Aplica um efeito de Contraste
    # enhancer3 = ImageEnhance.Contrast(new_img)
    # enhancer3.enhance(FATOR_CONTRASTE).show()

    # Rodar em modo Debug e ver qual o melhor filtro ou a melhor combinação
    # Ao finalizar a parametrização, mudar o nome da variavel new_img para o nome da variavel da imagem final

    try:
        new_img.save(
            new_img_path,
            optimize=True,
            quality=50,
            exif=pillow_img.info.get('exif')
        )
    except:
        try:
            new_img.save(
                new_img_path,
                optimize=True,
                quality=50,
            )
        except:
            raise RuntimeError(f'Could not convert "{original_img_path}".')

    print(f'Saved at {new_img_path}')


def is_image(extension):
    extension_lowercase = extension.lower()
    return bool(re.search(r'^\.(jpe?g|png)$', extension_lowercase))


def files_checks(root, file):
    filename, extension = os.path.splitext(file)

    if not is_image(extension):
        return

    flag = '_PROCESSED'

    if flag in file:
        return

    new_img_name = filename + flag + extension

    resize(root=root, file=file, new_width=NEW_WIDTH, new_img_name=new_img_name)


def files_loop(root, files):
    for file in files:
        files_checks(root, file)


def main(root_folder):
    img_download()

    # Loop para tratar imagens
    for root, dirs, files in os.walk(root_folder):
        files_loop(root, files)

    # Loop para excluir imagens não tratadas
    for root, dirs, files in os.walk(root_folder):
        files_loop_delete(root, files)


if __name__ == '__main__':
    main(ROOT_PATH)
