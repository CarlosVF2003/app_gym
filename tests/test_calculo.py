import pandas as pd
from main import calcular_promedio


def test_calcular_promedio_columns():
    progreso = pd.read_csv('data/Progreso.csv')
    grupo = pd.read_csv('data/Grupo_muscular.csv')
    usuarios = pd.read_csv('data/Usuarios.csv')
    df = progreso.merge(grupo, on='Maquina').merge(usuarios, on='Id_Usuario')
    df['Peso'] = df.apply(lambda r: r['Peso'] * 0.453592 if str(r.get('Medida', '')).lower() == 'lb' else r['Peso'], axis=1)
    df['Medida'] = 'kg'
    df['Dia_ordenado'] = pd.to_numeric(df['Dia'], errors='coerce')

    result = calcular_promedio(df)
    assert {'Id_Usuario', 'Dia', 'Suma_Repeticiones', 'Promedio_Ponderado'} <= set(result.columns)
