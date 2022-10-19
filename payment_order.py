from datetime import datetime


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
    #  Конвертирует число в 36-ричный формат, возвращая строку из 6-ти символов.
    #  (соответствие требованиям именования файлов для импорта)
    base = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while n:
        n, y = divmod(n, 36)
        result = base[y] + result
    if len(result) < 6:
        result = '0' * (6 - len(result)) + result
    return result


if __name__ == '__main__':
    f = '/path/to/1C_file.txt'
    pay_orders = collect_pay_info(f)
