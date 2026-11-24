import pandas as pd
import tabulate as tb
import matplotlib as plt
from sklearn.preprocessing import StandardScaler


#Parte 1

archivo = pd.read_csv("Human_Resources.csv")
archivo_max = archivo ["Age"].max()
archivo_min = archivo ["Age"].min()
archivo_mean = archivo ["Age"].mean()

print(archivo_max)
print(archivo_min)
print(archivo_mean)

#Parte 2

# Faltantes antes
filas_con_nan = archivo[archivo["MonthlyRate"].isnull()].index
print("Faltantes antes:", archivo["MonthlyRate"].isnull().sum())
print("Filas con faltantes:", list(filas_con_nan))

# Calcular la mediana
mediana_monthly_rate = archivo["MonthlyRate"].median()
print("Mediana de MonthlyRate:", mediana_monthly_rate)

# Rellenar los faltantes con la mediana
archivo["MonthlyRate"] = archivo["MonthlyRate"].fillna(mediana_monthly_rate)

# Confirmar que se realizó correctamente
print("Faltantes después:", archivo["MonthlyRate"].isnull().sum())
print(archivo.loc[filas_con_nan, ["MonthlyRate"]])

#Parte 3

hr_df_limpio = pd.read_csv("Human_Resources.csv")
print("Antes:", hr_df_limpio.shape)
hr_df_limpio = hr_df_limpio.dropna(how="any")
print("Después:", hr_df_limpio.shape)
print("Faltantes restantes:", hr_df_limpio.isnull().sum().sum())

# Categorías únicas en Education
print("Categorías únicas en Education:", hr_df_limpio["Education"].nunique())
print(hr_df_limpio["Education"].value_counts().sort_index())

# Codificación one-hot
education_encoded = pd.get_dummies(hr_df_limpio["Education"], prefix="Education", dtype=int)
print(education_encoded.head())

# Unir al DataFrame y quitar la columna original
hr_df_codificado = pd.concat([hr_df_limpio.drop(columns="Education"), education_encoded], axis=1)
print(hr_df_codificado.shape)


#Parte 4

columnas_numericas = hr_df_limpio.select_dtypes(include="number").columns
columnas_a_escalar = [c for c in columnas_numericas
                      if c != "EmployeeNumber" and hr_df_limpio[c].nunique() > 1]
print(columnas_a_escalar)

scaler = StandardScaler()
hr_df_escalado = pd.DataFrame(scaler.fit_transform(hr_df_limpio[columnas_a_escalar]),
                              columns=columnas_a_escalar, index=hr_df_limpio.index)
print(hr_df_escalado.head())

comprobacion = pd.DataFrame({
    "media": hr_df_escalado.mean().round(4) + 0.0,
    "desv_estandar": hr_df_escalado.std(ddof=0).round(4)
})
print(comprobacion)

#Parte 5

hr_df_daily_alto = archivo[archivo["DailyRate"] >= 1450]
print("Empleados con DailyRate >= 1450:", len(hr_df_daily_alto))
print(hr_df_daily_alto[["Age", "Department", "JobRole", "DailyRate"]].head())

daily_rate_combinado = hr_df_daily_alto["DailyRate"].sum()
print("DailyRate combinado:", daily_rate_combinado)

#Parte 6

archivo.hist(figsize=(22, 20), bins=30, color="steelblue", edgecolor="white")
plt.suptitle("Histogramas de todas las variables numéricas", fontsize=18)
plt.tight_layout()
plt.show()