from django.contrib import admin
from .models import Exchanges, Ofertas, Oportunidade

# Register your models here.
class ExchangesAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_url']
    search_fields = ['name']

class OfertasAdmin(admin.ModelAdmin):
    list_display = ['exchange', 'time', 'valor_compra', 'valor_venda']
    search_fields = ['exchange__name', 'time']
    list_filter = ['exchange', 'time']
    readonly_fields = (
        'exchange',
        'time',
        'valor_compra',
        'valor_venda',
        'quant_compra',
        'quant_venda')

class OportunidadeAdmin(admin.ModelAdmin):
    list_filter= ['time']
    list_display = ['__str__', 'time', 'preco_compra', 'preco_venda', 'percentual']
    readonly_fields = (
        'exchange_compra',
        'time',
        'exchange_venda',
        'preco_compra',
        'preco_venda',
        'percentual')
    
admin.site.register(Exchanges, ExchangesAdmin)
admin.site.register(Ofertas, OfertasAdmin)
admin.site.register(Oportunidade, OportunidadeAdmin)