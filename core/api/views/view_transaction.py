import base64
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Transaction
from core.serializers import *
import datetime  # Importar o módulo completo para evitar conflito
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # Para adicionar meses e anos

from rest_framework.permissions import IsAuthenticated

#?  -----------------------
#?  -------- Transaction ---------
#?  -----------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_transaction(request):
    if request.method == 'GET':
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Ensure start_date and end_date are provided and valid
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return Response({"error": "Invalid date format, use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

        # transactions = Transaction.objects.all()
        
        transactions = Transaction.objects.filter(
            expiry_date__gte=start_date,
            expiry_date__lte=end_date,
            created_by=request.user
        ).order_by('expiry_date')
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_transaction_by_id(request):
   
    if "id" not in request.GET:
        return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try: 
       transaction = Transaction.objects.get(id=request.GET["id"])
    except:
        return Response({"error": "transaction not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TransactionSerializer(transaction)
    return Response(serializer.data, status=status.HTTP_200_OK)
        
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    if request.method == 'POST':
        user = request.user
        
        # Obter os dados da requisição
        data = request.data.copy()
        installments = int(data.get('installments', 1))  # Garantir que é um inteiro
        recurrence = data.get('recurrence', 'SINGLE')  # Obter a recorrência
        
        # Atribuir o ID do usuário autenticado aos campos 'created_by' e 'updated_by'
        data['created_by'] = user.id  # Atribui o ID do usuário
        data['updated_by'] = user.id  # Atribui o ID do usuário
        
        # Calcular o valor de cada parcela
        total_value = float(data.get('value', 0))
        
        if recurrence == 'INSTALLMENTS' and installments > 0:
            value_installment = total_value / installments  # Divide o valor total pelo número de parcelas
        else:
            value_installment = total_value  # Para outros tipos de recorrência, mantém o valor total
        
        data['value_installment'] = value_installment  
        
        # Criar a transação principal
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            # Salva a transação única inicial
            transaction = serializer.save(installments=installments, related_transaction=None)  
            base_expiry_date = transaction.expiry_date  # Salvar a data de vencimento base
            transaction_group = transaction.pk  # Usa o ID da transação principal como grupo

            # Se houver parcelas, criar as transações adicionais
            for i in range(1, installments):
                # Calcular a nova data de vencimento com base na recorrência
                if transaction.recurrence == 'INSTALLMENTS':
                    new_expiry_date = base_expiry_date + relativedelta(months=i)
                elif transaction.recurrence == 'WEEKLY':
                    new_expiry_date = base_expiry_date + timedelta(weeks=i)
                elif transaction.recurrence == 'MONTHLY':
                    new_expiry_date = base_expiry_date + relativedelta(months=i)
                elif transaction.recurrence == 'ANNUAL':
                    new_expiry_date = base_expiry_date + relativedelta(years=i)
                else:
                    new_expiry_date = base_expiry_date  # Para SINGLE ou outros tipos, usar a mesma data

                # Criar a nova transação com a nova data de vencimento
                Transaction.objects.create(
                    value=transaction.value,  # O valor da parcela
                    value_installment=value_installment,  # O valor da parcela
                    description=transaction.description,
                    account=transaction.account,
                    category=transaction.category,
                    expiry_date=new_expiry_date,
                    is_paid=False,  # Inicialmente não paga
                    date_payment=None,
                    receipt=None,
                    current_installment=i+1,
                    installments=installments,  # Cada transação de parcela é única
                    related_transaction=transaction,  # Associa a transação original
                    type=transaction.type,  # Copia o tipo de transação
                    recurrence=transaction.recurrence,  # Copia a recorrência da transação
                    created_by=user,  # Atribuindo a instância do usuário
                    updated_by=user   # Atribuindo a instância do usuário
                )

            return Response({"transaction_group": str(transaction_group)}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    if request.method == 'PATCH':
        try:
            # Buscar a transação principal
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        # Obter os dados da requisição
        data = request.data.copy()
        installments = int(data.get('installments', transaction.installments))  # Garantir que é um inteiro
        recurrence = data.get('recurrence', 'SINGLE')  # Obter a recorrência
        
        # Calcular o valor de cada parcela
        total_value = float(data.get('value', 0))
        
        if recurrence == 'INSTALLMENTS' and installments > 0:
            value_installment = total_value / installments  # Divide o valor total pelo número de parcelas
        else:
            value_installment = total_value  # Para outros tipos de recorrência, mantém o valor total
        
        data['value_installment'] = value_installment  
        
        # Atualizar a transação principal
        serializer = TransactionSerializer(transaction, data=data, partial=True)  # Use partial=True para permitir atualizações parciais
        if serializer.is_valid():
            updated_transaction = serializer.save()  # Salva a transação atualizada
            
            # Checar se o parâmetro edit_all está definido como True
            edit_all = data.get('edit_all', False)
            print(edit_all)
            
            # Se edit_all for verdadeiro, atualizar todas as transações relacionadas
            print(transaction.related_transaction)
            
            if edit_all:
                related_transactions = Transaction.objects.filter(related_transaction=updated_transaction)

                for rel_transaction in related_transactions:
                    rel_transaction.value_installment = updated_transaction.value / installments if installments > 0 else updated_transaction.value
                    rel_transaction.value = updated_transaction.value
                    rel_transaction.description = updated_transaction.description

                    if 'account' in data:
                        rel_transaction.account_id = data['account']  # Certifique-se de que é um ID válido
                    if 'category' in data:
                        rel_transaction.category_id = data['category']  # Certifique-se de que é um ID válido

                    rel_transaction.save()  # Salva cada transação individualmente

            return Response({"message": "Transaction updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_transaction(request, id):
    try:
        transaction = Transaction.objects.get(id=int(id))
        
        # Verifica se deve excluir todas as transações relacionadas
        all_transaction = request.query_params.get('all_transaction', 'false').lower() == 'true'
        
        print(all_transaction)
        
        if all_transaction:
            print(transaction.related_transaction)
            
            if transaction.related_transaction is None:
                # Se a transação não tem um related_transaction, significa que é a principal
                Transaction.objects.filter(related_transaction=transaction).delete()
            else:
                # Excluir todas as transações do mesmo grupo, incluindo a principal
                Transaction.objects.filter(
                    related_transaction=transaction.related_transaction
                ).delete()
                transaction.related_transaction.delete()
        
        # Se não for para deletar todas, apenas a transação selecionada é excluída
        transaction.delete()

    except Transaction.DoesNotExist:
        return Response({'detail': 'Transaction not found'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'worked': True}, status=status.HTTP_200_OK)


      
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def pay_transaction(request):
    transaction_id = request.data.get('transaction_id')
    receipt_image_base64 = request.data.get('receipt_image', None)

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID e marcar como paga
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
        transaction.is_paid = True
        transaction.date_payment = datetime.datetime.today()

        # Verificar se uma imagem foi enviada
        if receipt_image_base64:
            # Decodificar a imagem base64 e salvar no campo 'receipt'
            format, imgstr = receipt_image_base64.split(';base64,')
            ext = format.split('/')[-1]
            receipt_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{transaction_id}.{ext}')
            transaction.receipt = receipt_image

        transaction.save()
        return Response({"message": "Transaction marked as paid and image saved successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_pay_transaction(request):
    transaction_id = request.data.get('transaction_id')

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID e marcar como não paga
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)
        transaction.is_paid = False
        transaction.save()

        return Response({"message": "Transaction payment canceled successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def upload_transaction_image(request):
    transaction_id = request.data.get('transaction_id')
    receipt_image_base64 = request.data.get('receipt_image', None)

    if not transaction_id:
        return Response({"error": "Transaction ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not receipt_image_base64:
        return Response({"error": "Receipt image is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Localizar a transação pelo ID
        transaction = Transaction.objects.get(id=transaction_id, created_by=request.user)

        # Decodificar a imagem base64 e salvar no campo 'receipt'
        format, imgstr = receipt_image_base64.split(';base64,')
        ext = format.split('/')[-1]
        receipt_image = ContentFile(base64.b64decode(imgstr), name=f'receipt_{transaction_id}.{ext}')
        transaction.receipt = receipt_image
        transaction.save()

        return Response({"message": "Transaction image uploaded successfully."}, status=status.HTTP_200_OK)

    except Transaction.DoesNotExist:
        return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

