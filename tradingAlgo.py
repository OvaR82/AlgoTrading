# -*- coding: utf-8 -*-
"""
ALGORITMO PARA PLANEAR ESTRATEGIA DE INVERSIÓN.
"""

import requests
import pandas as pd 
import math
import xlsxwriter

# LLamar a cualquier API de inversión. En este caso se utiliza una de prueba.
simbolo = "AMZN"
API_TOKEN_TEST = "..." # Token de acceso a la API.
api_url = f"https://sandbox.iexapis.com/stable/stock/{simbolo}/quote?token={API_TOKEN_TEST}"
# Convertir los datos obtenidos en un archivo JSON.
data = requests.get(api_url).json()

# Covertir los datos obtenidos en un dataframe.
pagina = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
tabla_stocks = pagina[0]
columnas_stocks = ["Ticker", "Precio", "Capitalización de Mercado", "Acciones a comprar"]
stocks_dataframe = pd.DataFrame(columns = columnas_stocks)

# Acceder a los símbolos de los stocks. 
for simbolo in tabla_stocks["Symbol"]:
  api_url = f"https://sandbox.iexapis.com/stable/stock/{simbolo}/quote?token={API_TOKEN_TEST}"
  data = requests.get(api_url).json()
  stocks_dataframe = stocks_dataframe.append(pd.Series([simbolo, data["latestPrice"], data["marketCap"], "N/A"], index = columnas_stocks), ignore_index = True)

# Definir una función para mejorar la el desempeño del algoritmo.
def dividir_lista(list, numero_por_grupo):
  for index in range(0, len(list), numero_por_grupo):
    yield list[index:index + numero_por_grupo]

grupos_simbolos_stock = list(dividir_lista(tabla_stocks["Symbol"], 100))

# Agrupar los símbolos en una lista.
cadena_simbolos_stock = []
for index in range(0, len(grupos_simbolos_stock)):
  cadena_simbolos_stock.append(",".join(grupos_simbolos_stock[index]))
  print(cadena_simbolos_stock[index])

# Llamar a los stocks por lotes.
lote_stocks_dataframe = pd.DataFrame(columns = columnas_stocks)
for str_simbolo in cadena_simbolos_stock:
  batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={str_simbolo}&token={API_TOKEN_TEST}"
  data = requests.get(batch_api_call_url).json()
  for simbolo in str_simbolo.split(","):
    lote_stocks_dataframe = lote_stocks_dataframe.append(pd.Series([simbolo, data[simbolo]["quote"]["latestPrice"], data[simbolo]["quote"]["marketCap"], "N/A"], index = columnas_stocks), ignore_index = True)

# Calcular las acciones a comprar en base a la valuación del portfolio y el desempeño de los stocks.
valor_portfolio = input("Ingrese valor de su portfolio: ")

try:
  valor_portfolio_float = float(valor_portfolio)
except ValueError:
  print("Error! Ingrese un número.")
  valor_portfolio = input("Ingrese valor de su portfolio: ")

tamaño_posicion = float(valor_portfolio) / len(lote_stocks_dataframe.index)
for index in range(0, len(lote_stocks_dataframe["Ticker"])-1):
  lote_stocks_dataframe.loc[index, "Acciones a comprar"] = math.floor(tamaño_posicion / lote_stocks_dataframe["Precio"][index])

print(lote_stocks_dataframe)

# Guardar la información obtenida a Excel.
excel_file = pd.ExcelWriter("Stocks.xlsx", engine="xlsxwriter")
lote_stocks_dataframe.to_excel(excel_file, sheet_name="S&P 500 Stocks", index = False)

excel_file.save()