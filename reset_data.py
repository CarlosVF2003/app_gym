import pandas as pd

USERS_CSV = 'data/Usuarios.csv'

COLUMNS = ['Id_Usuario', 'Nombre', 'Color', 'Username', 'Password']

def reset_users():
    pd.DataFrame(columns=COLUMNS).to_csv(USERS_CSV, index=False)

if __name__ == '__main__':
    reset_users()
    print('Datos de usuarios reiniciados')
