import streamlit as st
import pandas as pd
from pathlib import Path
import hashlib

USERS_FILE = Path(__file__).parent / 'data' / 'Usuarios.csv'


def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> pd.DataFrame:
    if USERS_FILE.exists():
        return pd.read_csv(USERS_FILE)
    return pd.DataFrame(columns=['Id_Usuario', 'Nombre', 'Color', 'Password'])


def save_users(df: pd.DataFrame) -> None:
    df.to_csv(USERS_FILE, index=False)


def signup_form():
    st.subheader('Registro')
    nombre = st.text_input('Nombre de usuario')
    password = st.text_input('Contraseña', type='password')
    if st.button('Crear Cuenta'):
        if not nombre or not password:
            st.error('Debes completar todos los campos')
            return
        df = load_users()
        if nombre in df['Nombre'].values:
            st.error('El nombre ya está registrado')
            return
        nuevo_id = f"U{len(df) + 1}"
        nuevo_usuario = {'Id_Usuario': nuevo_id, 'Nombre': nombre, 'Color': 'black', 'Password': _hash(password)}
        df = pd.concat([df, pd.DataFrame([nuevo_usuario])], ignore_index=True)
        save_users(df)
        st.success('Usuario creado. Inicia sesión para continuar.')


def login_form():
    st.subheader('Inicio de Sesión')
    nombre = st.text_input('Usuario')
    password = st.text_input('Contraseña', type='password')
    if st.button('Iniciar Sesión'):
        df = load_users()
        usuario = df[df['Nombre'] == nombre]
        if not usuario.empty and usuario.iloc[0]['Password'] == _hash(password):
            st.session_state['usuario'] = usuario.iloc[0]['Nombre']
            st.session_state['id_usuario'] = usuario.iloc[0]['Id_Usuario']
            st.session_state['logged_in'] = True
            st.success('Sesión iniciada')
        else:
            st.error('Credenciales inválidas')

