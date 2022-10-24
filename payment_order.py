from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile


def collect_pay_info(file: str) -> list:
    # Парсит платёжные поручения, выгруженные из 1С.

    # Сопоставление ключей 1С и XML
    translators = {
        'Дата': 'docDate',
        'ПолучательСчет': 'recip_CheckAcc',
        'Получатель1': 'recip_Name',
        'ПолучательИНН': 'recip_INN',
        'ПолучательРасчСчет': 'recip_CheckAcc',
        'ПолучательБанк1': 'recip_BankName',
        'ПолучательБИК': 'recip_BIK',
        'ПолучательКорсчет': 'recip_CorrAcc',
        'Сумма': 'paySum',
        'Номер': 'docNum',
        }

    # Словарь форматирования ключей платежного поручения
    formaters = {
        'Дата': datetime.now().strftime('%Y-%m-%d'),
    }

    docpack = []
    curdoc = {}
    text = open(file, 'r', encoding='utf-8').read()
    for line in text.splitlines()[1:]:
        if line.startswith('КонецДокумента'):
            docpack.append(curdoc)
            curdoc = {}
            continue
        if line.startswith('КонецФайла'):
            break
        key, value = line.split('=', maxsplit=1)
        value = formaters.get(key, value)
        key = translators.get(key, None)
        if key:
            curdoc[key] = value
    return docpack


def file_name(n: int) -> str:
    # Возвращает имя файла для экспорта в требуемом формате
    code = 'TSE_0401060_D07_'   # Код платежного поручения.
    org = '123Я4567'            # Код организации (учетный номер по Сводному реестру).
    return code + org + _dm_convert(datetime.now()) + _convert36(n) + '.XML'


def _dm_convert(date) -> str:
    # Конвертирует день в формат для имени файла: 1–9, A–V, и месяц: 1–9, A–С.
    days = '0123456789ABCDEFGHIJKLMNOPQRSTUV'
    months = '0123456789ABC'
    return days[date.day] + months[date.month]


def _convert36(n) -> str:
    # Конвертирует число в 36-ричный формат, возвращая строку из 6-ти символов.
    # (соответствие требованиям именования файлов для импорта)
    base = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while n:
        n, y = divmod(n, 36)
        result = base[y] + result
    if len(result) < 6:
        result = '0' * (6 - len(result)) + result
    return result


def create_file(t_dir, m):
    # Создает XML файлы из шаблона с требуемым именем.
    # t_dir - директория, куда складываются сформированные XML файлы; перед созданием файлов директория очищается;
    # m - количество платёжных поручений в выгрузке 1С;
    files = Path(t_dir).glob('**/*')
    for file in files:
        try:
            file.unlink()
        except Exception as e:
            print(f'Failed to delete {file}. Reason: {e}')
    file_start_num = 1296  # 100 в 36-ричной системе (можно задать любой начальный номер в имени файла)
    content = read_xml_template()
    for i in range(m):
        path = t_dir + file_name(file_start_num + i)
        with open(path, 'w', encoding='utf-8') as f:
            for line in content:
                f.write(line)


def read_xml_template():
    with open('./file_examples/template.XML', 'r', encoding='utf-8') as t:
        structure = t.readlines()
    return structure


def zip_xml_files(dir_name, zip_file_name):
    # Создает архив с XML файлами
    with ZipFile(dir_name.joinpath(zip_file_name), 'w') as archive:
        files = list(Path(dir_name).glob('*.XML'))
        for file in files:
            archive.write(file, file.name)


def modify_xml(source: str, start_num: str, pay_purpose: str):
    # Модифицирует XML файлы, вставляя информацию из выгрузки 1С.
    # source - путь к файлу выгрузки 1С;
    # start_num - начальный номер платёжного поручения;
    # Начальный номер платежки может браться из выгрузки 1С (бухгалтер вводит '0') или задаваться бухгалтером.
    # pay_purpose - назначение платежа, общий для всех платёжек; вводит бухглатер;

    target_dir = './out/'  # директория, куда складываются сформированные XML файлы
    pay_order_num = int(start_num)
    print(pay_order_num, type(pay_order_num))
    pay_orders = collect_pay_info(source)
    create_file(target_dir, len(pay_orders))
    files = list(Path(target_dir).glob('*'))

    for i in range(len(files)):
        tree = ET.parse(files[i])
        root = tree.getroot()
        root.findall('TranscriptPP_PayPurpose')[0].text = pay_purpose
        if pay_order_num:
            root.findall('BasicRequisites_DocNum')[0].text = str(pay_order_num + i)
        else:
            root.findall('BasicRequisites_DocNum')[0].text = pay_orders[i]['docNum']
        root.findall('BasicRequisites_DocDate')[0].text = pay_orders[i]['docDate']
        root.findall('PayerAndRecipient_Recip_Name')[0].text = pay_orders[i]['recip_Name']
        root.findall('PayerAndRecipient_Recip_INN')[0].text = pay_orders[i]['recip_INN']
        root.findall('PayerAndRecipient_Recip_CheckAcc')[0].text = pay_orders[i]['recip_CheckAcc']
        root.findall('PayerAndRecipient_Recip_BIK')[0].text = pay_orders[i]['recip_BIK']
        root.findall('PayerAndRecipient_Recip_BankName')[0].text = pay_orders[i]['recip_BankName']
        root.findall('PayerAndRecipient_Recip_CorrAcc')[0].text = pay_orders[i]['recip_CorrAcc']
        root.findall('BasicRequisites_PaySum')[0].text = pay_orders[i]['paySum']
        root.findall('./TSE_Tab0401060/TSE_Tab0401060_ITEM/Sum')[0].text = pay_orders[i]['paySum']
        tree.write(files[i], encoding='utf-8')

    zip_xml_files(Path(target_dir), 'download.zip')


if __name__ == '__main__':
    f_1c = './upload/1C_upload.txt'
    modify_xml(f_1c, '8', 'заработная плата')
