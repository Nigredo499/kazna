from datetime import datetime


def collect_pay_info(file: str) -> list:
    # Парсит платёжного поручения, выгруженного из 1С.

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


if __name__ == '__main__':
    f = '/path/to/1C_file.txt'
    pay_oerders = collect_pay_info(f)
