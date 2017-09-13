from django.db import models

# Create your models here.

class Ofertas(models.Model):
    exchange = models.ForeignKey(to='Exchanges', related_name='Exchange')
    valor_compra = models.DecimalField('Valor Compra', max_digits=19, decimal_places=4)
    quant_compra = models.DecimalField('Quantidade Compra', max_digits=19, decimal_places=10)
    valor_venda = models.DecimalField('Valor Venda', max_digits=19, decimal_places=4)
    quant_venda = models.DecimalField('Quantidade Venda', max_digits=19, decimal_places=10)
    time = models.DateTimeField('Data', auto_now_add=True)

    def __str__(self):
        return "{} | {}".format(self.exchange, self.time)

    class Meta:
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        ordering = ['-time']

class Exchanges(models.Model):
    name = models.CharField('Nome', max_length=500, null=False)
    api_url = models.CharField('API', max_length=500, blank=False)

    class Meta:
        verbose_name = 'Exchange'
        verbose_name_plural = 'Exchanges'

    def __str__(self):
        return self.name

class Oportunidade(models.Model):

    time = models.DateTimeField('Data|Hora', auto_now_add=True)
    exchange_compra = models.ForeignKey(to='Exchanges', related_name='Exchange_Comprar')
    exchange_venda = models.ForeignKey(to='Exchanges', related_name='Exchange_Vender')
    preco_compra = models.DecimalField('Preço da compra', max_digits=19, decimal_places=4, null=True, blank=True)
    preco_venda = models.DecimalField('Preço da venda', max_digits=19, decimal_places=4, null=True, blank=True)
    percentual = models.DecimalField('Diferença (%)',max_digits=19, decimal_places=2, null=True, blank=True)
    class Meta:
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'
        ordering = ['-time']
    

    def __str__(self):
        return '{} -> {}'.format(self.exchange_compra.name, self.exchange_venda.name)