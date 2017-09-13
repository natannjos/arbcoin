from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView
from urllib.request import urlopen
import json
import codecs

from decimal import Decimal

from .models import Exchanges, Ofertas, Oportunidade

from django.core.mail import EmailMessage

from rest_framework.views import APIView
from rest_framework.response import Response

import urllib
def monitor(request):
    # retorna a lista de exchanges e suas APIs
    exchanges = Exchanges.objects.all()
    numero_de_ofertas = Ofertas.objects.all().count()
    if numero_de_ofertas > 10000:
        Ofertas.objects.all().delete()

    # Adiciona os headers da requisição as APIs
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}

    # transforma bytecode em utf-8
    reader = codecs.getreader('utf-8')

    # percorre a lista de exchanges e salva as ultimas ofertas no banco
    for exchange in exchanges:
        try:
            req = urllib.request.Request(exchange.api_url, headers=headers)
            # requisição dos dados da API
            response = reader(urlopen(req))
            # converte os dados obtidos em json
            data = json.load(response)

            # extrai os precos de compra e venda e quantidades de Bitcoins da exchange atual
            if 'ask' in data and 'bid' in data:
                dados_de_venda = data['ask'][0]
                dados_de_compra = data['bid'][0]
            else:
                dados_de_venda = data['asks'][0]
                dados_de_compra = data['bids'][0]
            # salva a exchange e os dados da oferta
            salva_oferta(exchange, dados_de_compra, dados_de_venda)

        except:
            continue
    # compara as ultimas ordens adicionadas e busca uma possivel oportunidade de transação
    procura_arbitragem()

    # faz uma query das oportunidades dos últimos 2 minutos para adicionar no contexto da página

    return render(request, "monitor.html")


def procura_arbitragem():
    """Compara os precos das ultimas ordens salvas e busca uma
    oportunidade de arbitragem baseada na diferença de
    precos de compra e venda de cada uma delas"""

    n_exchanges = Exchanges.objects.count();
    ofertas = Ofertas.objects.order_by('-pk')[:n_exchanges]

    dados_venda = [[d.exchange, d.valor_compra] for d in ofertas]
    dados_compra = [[d.exchange, d.valor_venda] for d in ofertas]
    oportunidade = {}

    for compra in dados_compra:
        for venda in dados_venda:
            percentual_real = (1 - (compra[1] / venda[1])) * 100
            if (percentual_real >= percentual_escolhido() and percentual_real < 100):
                oportunidade['exchange_compra'] = compra[0]
                oportunidade['exchange_venda'] = venda[0]
                oportunidade['preco_compra'] = compra[1]
                oportunidade['preco_venda'] = venda[1]
                oportunidade['percentual'] = percentual_real
                salva_oportunidade(oportunidade)


def salva_oferta(exchange, compra, venda):
    oferta = Ofertas()
    oferta.exchange = exchange

    if type(compra) is dict and type(venda) is dict:
        oferta.valor_compra = compra['price']
        oferta.quant_compra = compra['quantity']
        oferta.valor_venda = venda['price']
        oferta.quant_venda = venda['quantity']
    else:
        oferta.valor_compra = compra[0]
        oferta.quant_compra = compra[1]
        oferta.valor_venda = venda[0]
        oferta.quant_venda = venda[1]
    oferta.save()


def salva_oportunidade(oportunidade):
    nova = Oportunidade()
    oportunidade['percentual'] = Decimal(str(oportunidade['percentual']))
    oportunidade['preco_compra'] = Decimal(str(oportunidade['preco_compra']))
    oportunidade['preco_venda'] = Decimal(str(oportunidade['preco_venda']))

    try:
        ultima = Oportunidade.objects.latest('time')
    except ObjectDoesNotExist:
        nova.exchange_compra = oportunidade['exchange_compra']
        nova.exchange_venda = oportunidade['exchange_venda']
        nova.preco_venda = oportunidade['preco_venda']
        nova.preco_compra = oportunidade['preco_compra']
        nova.percentual = oportunidade['percentual']
        nova.save()
        envia_email()
        return

    if (oportunidade['percentual'] != ultima.percentual and
                oportunidade['preco_compra'] != ultima.preco_compra and
                oportunidade['preco_venda'] != ultima.preco_venda):
        nova.exchange_compra = oportunidade['exchange_compra']
        nova.exchange_venda = oportunidade['exchange_venda']
        nova.preco_venda = oportunidade['preco_venda']
        nova.preco_compra = oportunidade['preco_compra']
        nova.percentual = oportunidade['percentual']
        nova.save()
        envia_email()


def envia_email():
    ultima = Oportunidade.objects.latest('time')
    titulo = 'Compre na {} e venda na {}'.format(ultima.exchange_compra, ultima.exchange_venda)
    mensagem = "Compre na {} e venda na {}. A diferença está em {}%".format(
        ultima.exchange_compra, ultima.exchange_venda, ultima.percentual
    )

    email = EmailMessage(titulo, mensagem, to=['arbcoinbot@gmail.com', 'natannjos@gmail.com'])
    email.send()


def percentual_escolhido():
    return 5


class ViewGraph(TemplateView):
    template_name = 'graph.html'


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        n_exchanges = Exchanges.objects.count();
        ofertas = Ofertas.objects.order_by('-pk')[:n_exchanges]

        data = {}

        for oferta in ofertas:
            dados_compra = [oferta.valor_compra, oferta.quant_compra]
            dados_venda = [oferta.valor_venda, oferta.quant_venda]
            exchange = oferta.exchange.name
            hora = oferta.time

            data[exchange] = {
                'asks': dados_venda,
                'bids': dados_compra
            }
        return Response(data)
