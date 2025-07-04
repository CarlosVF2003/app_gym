import pandas as pd
import streamlit as st
import altair as alt

USUARIOS_CSV = 'data/Usuarios.csv'
PROGRESO_CSV = 'data/Progreso.csv'
CATALOGO_CSV = 'data/Grupo_muscular.csv'


def load_dfs():
    try:
        progreso = pd.read_csv(PROGRESO_CSV)
    except FileNotFoundError:
        progreso = pd.DataFrame(columns=['Dia', 'Id_Usuario', 'Ejercicio', 'Peso', 'Sets', 'Repeticiones'])
    try:
        catalogo = pd.read_csv(CATALOGO_CSV)
    except FileNotFoundError:
        catalogo = pd.DataFrame(columns=['Grupo_Muscular', 'Ejercicio'])
    try:
        usuarios = pd.read_csv(USUARIOS_CSV)
    except FileNotFoundError:
        usuarios = pd.DataFrame(columns=['Id_Usuario', 'Nombre', 'Color', 'Username', 'Password'])
    return progreso, catalogo, usuarios


def save_df(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)


progreso_df, grupo_muscular_df, usuario_df = load_dfs()


# ------ Autenticación ------
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None


def login_form():
    st.header('Iniciar sesión')
    user = st.text_input('Usuario')
    pwd = st.text_input('Contraseña', type='password')
    if st.button('Ingresar'):
        row = usuario_df[(usuario_df['Username'] == user) & (usuario_df['Password'] == pwd)]
        if not row.empty:
            st.session_state['authenticated'] = True
            st.session_state['user_id'] = row.iloc[0]['Id_Usuario']
            st.experimental_rerun()
        else:
            st.error('Credenciales inválidas')


def register_form():
    st.header('Registro')
    name = st.text_input('Nombre para mostrar')
    user = st.text_input('Usuario', key='reg_user')
    pwd = st.text_input('Contraseña', type='password', key='reg_pwd')
    if st.button('Registrar'):
        if user in usuario_df['Username'].values:
            st.error('El usuario ya existe')
        else:
            new_id = f'U{len(usuario_df) + 1}'
            new_row = {'Id_Usuario': new_id, 'Nombre': name, 'Color': 'gray', 'Username': user, 'Password': pwd}
            usuario_df.loc[len(usuario_df)] = new_row
            save_df(usuario_df, USUARIOS_CSV)
            st.success('Usuario registrado, ahora puede iniciar sesión')


def logout():
    st.session_state['authenticated'] = False
    st.session_state['user_id'] = None
    st.experimental_rerun()


if not st.session_state['authenticated']:
    login_form()
    st.divider()
    register_form()
    st.stop()


usuario_actual = usuario_df[usuario_df['Id_Usuario'] == st.session_state['user_id']].iloc[0]
st.sidebar.write(f"Usuario: {usuario_actual['Nombre']}")
st.sidebar.button('Cerrar sesión', on_click=logout)

st.title('🏋️‍♂️ Registro de Entrenamiento')

# ------ Catálogo de Ejercicios ------
with st.expander('📚 Catálogo de Ejercicios'):
    st.dataframe(grupo_muscular_df)
    with st.form('add_exercise'):
        grupo = st.text_input('Grupo Muscular')
        ejercicio = st.text_input('Ejercicio')
        submitted = st.form_submit_button('Agregar')
        if submitted and grupo and ejercicio:
            grupo_muscular_df.loc[len(grupo_muscular_df)] = [grupo, ejercicio]
            save_df(grupo_muscular_df, CATALOGO_CSV)
            st.experimental_rerun()
    if not grupo_muscular_df.empty:
        borrar = st.selectbox('Eliminar ejercicio', grupo_muscular_df['Ejercicio'].unique())
        if st.button('Eliminar'):
            grupo_muscular_df = grupo_muscular_df[grupo_muscular_df['Ejercicio'] != borrar]
            save_df(grupo_muscular_df, CATALOGO_CSV)
            st.experimental_rerun()

# ------ Registro de entrenamiento ------
with st.expander('📝 Registrar Entrenamiento'):
    dia = st.text_input('Día')
    ejercicio = st.selectbox('Ejercicio', grupo_muscular_df['Ejercicio'].unique())
    sets = st.number_input('Sets', min_value=1, max_value=10, step=1, value=4)
    peso = st.number_input('Peso', min_value=0.0, step=0.1)
    reps = st.number_input('Repeticiones', min_value=1, step=1, value=10)
    if st.button('Guardar') and dia:
        nuevo = pd.DataFrame({'Dia': [dia], 'Id_Usuario': [st.session_state['user_id']],
                             'Ejercicio': [ejercicio], 'Peso': [peso], 'Sets': [sets],
                             'Repeticiones': [reps]})
        progreso_df = pd.concat([progreso_df, nuevo], ignore_index=True)
        save_df(progreso_df, PROGRESO_CSV)
        st.success('Entrenamiento guardado')

# ------ Panel de progreso ------
with st.expander('📊 Progreso'):
    usuario_datos = progreso_df[progreso_df['Id_Usuario'] == st.session_state['user_id']]
    if usuario_datos.empty:
        st.info('Aún no hay datos registrados')
    else:
        usuario_datos['Volumen'] = usuario_datos['Peso'] * usuario_datos['Repeticiones'] * usuario_datos['Sets']
        total_volumen = usuario_datos['Volumen'].sum()
        dias = usuario_datos['Dia'].nunique()
        st.metric('Volumen total', f"{total_volumen:.2f}")
        st.metric('Días registrados', dias)
        pr = usuario_datos.groupby('Ejercicio')['Peso'].max().reset_index(name='PR')
        st.subheader('Récords personales')
        st.dataframe(pr)
        grafica = alt.Chart(usuario_datos).mark_line().encode(
            x='Dia:T', y='Peso', color='Ejercicio'
        )
        st.altair_chart(grafica, use_container_width=True)

