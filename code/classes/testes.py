from calendar import isleap

ano = int(input('Digite o ano: '))

if isleap(ano):
    print('É bissexto')
else:
    print('Não é bissexto')