import csv
import os
from django.core.files.storage import FileSystemStorage
from ofxtools.ofxparse import OfxParser

def process_file(uploaded_file):
    # Salvar o arquivo enviado
    fs = FileSystemStorage()
    filename = fs.save(uploaded_file.name, uploaded_file)
    file_path = fs.path(filename)  # Use fs.path aqui

    # Inicializar um array para os itens
    items = []

    # Determinar a extensão do arquivo
    _, file_extension = os.path.splitext(uploaded_file.name)

    try:
        if file_extension.lower() == '.ofx':
            # Processar arquivo OFX
            with open(file_path, 'r') as file:
                ofx = OfxParser.parse(file)
                # Extrair informações específicas do OFX
                for transaction in ofx.account.statement.transactions:
                    items.append({
                        'date': transaction.date,
                        'amount': transaction.amount,
                        'description': transaction.memo,
                    })

        elif file_extension.lower() == '.csv':
            # Processar arquivo CSV
            with open(file_path, newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    items.append(row)  # Adicione a linha ao array de itens

    except Exception as e:
        # Aqui você pode lidar com erros, por exemplo:
        print(f"Error processing file: {e}")

    # Retornar o array de itens
    return items
