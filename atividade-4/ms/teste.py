import pandas as pd
import re

# Carregar o arquivo Excel
df = pd.read_excel('cruise_data.xlsx')

# Função para converter nomes de colunas para snake_case
def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    name = name.replace(" ", "_").replace("-", "_").lower()
    name = re.sub('_+', '_', name)  # Remove underscores duplicados
    return name

# Renomear as colunas
df.columns = [to_snake_case(col) for col in df.columns]

# Salvar o resultado em um novo arquivo Excel
df.to_excel('cruise_data.xlsx', index=False)