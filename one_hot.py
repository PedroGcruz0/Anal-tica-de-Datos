import pandas as pd     
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

funcionarios = pd.DataFrame({
    "Nome": ["Ana", "Luis", "Carla", "Pedro", "Sofia", "Jorge"],
    "Departamento": ["RH", "TI", "Vendas", "TI", "RH", "Vendas"],
    "Salario": [2000, 5000, 3000, 5200, 2100, 3100]
})
print(funcionarios)
print(funcionarios.groupby("Departamento")["Salario"].mean())

dept_onehot = pd.get_dummies(funcionarios["Departamento"], prefix="Dept", dtype=int)
print(dept_onehot)

tabela = pd.concat([funcionarios, dept_onehot], axis=1)
print(tabela)
print(dept_onehot.sum(axis=1))  # soma de cada linha
print(dept_onehot.sum())        # soma de cada coluna