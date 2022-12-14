import pyrebase
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

firebaseConfig = {
  'apiKey': "AIzaSyDmaICrJnzE6_mkwsFLwMGDHys-a-5cL1s",
  'authDomain': "streamlit-firebase-mapfre.firebaseapp.com",
  'projectId': "streamlit-firebase-mapfre",
  'databaseURL': "https://streamlit-firebase-mapfre-default-rtdb.firebaseio.com/",
  'storageBucket': "streamlit-firebase-mapfre.appspot.com",
  'messagingSenderId': "132852245968",
  'appId': "1:132852245968:web:231b2521c6870cbbccc5d5",
  'measurementId': "G-TWNT2X9R59"
}
          
# firebase authentication
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# database
db = firebase.database()
storage = firebase.storage()

st.set_page_config(page_title="Mapfre arquivos", page_icon="🧊")
st.image("https://upload.wikimedia.org/wikipedia/commons/b/bf/Mapfre_logo.svg", width=200)

placeholder = st.empty()

# initialize state
if 'key' not in st.session_state:
  st.session_state.key = False

user = ''
if ~st.session_state.key:
  try:
    with placeholder.form(key="my-form"):
      options = st.selectbox('Entrar/Registrar', ['Entrar', 'Registrar'])
      email = st.text_input('Informar e-mail')
      password = st.text_input('Informar password', type='password')
      
      if options:
        submit = st.form_submit_button('Enviar')
        if submit:
          st.session_state.key = True
          if(options == 'Registrar'):
            #Signup 
            user = auth.create_user_with_email_and_password(email, password)
            st.success('Usuário criado com sucesso')
            st.balloons()
          else:
            # Login
            user = auth.sign_in_with_email_and_password(email, password)
            db.child(user['localId']).child("Handle").set(email)
            db.child(user['localId']).child("ID").set(user['localId'])
  except ValueError:
    st.error('Verifique os dados: email e senha', icon="⚠️")
    user = ''
    st.session_state.key = False
    placeholder.empty()
    
# download dataframe
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep=';', encoding='latin1', header=True, decimal=',')

# editable table
def editable_df(df):
  gd = GridOptionsBuilder.from_dataframe(df)
  gd.configure_pagination(enabled=True)
  gd.configure_default_column(editable=True, groupable=True, headerCheckboxSelection=True)
  
  sel_mode = st.radio('Selecione o tipo', options=['single','multiple'])
  gd.configure_selection(selection_mode=sel_mode, use_checkbox=True)
  grid_options = gd.build()
  grid_table = AgGrid(df, theme='dark', try_to_convert_back_to_original_types=False, gridOptions=grid_options, update_mode= GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED, allow_unsafe_jscode=True, height=500 )
  sel_row = grid_table['selected_rows']
  
  df_grid = pd.DataFrame(sel_row)
  
  csv = convert_df(df)
  st.download_button(
    label="Download tabela modificada como CSV",
    data=csv,
    file_name='dados_alterados.csv',
    mime='text/csv',  
  )
  st.subheader('Linhas atualizadas: ')
  st.table(data=df_grid)
    
  
if st.session_state.key:
  placeholder.empty()
  c = st.container()
  # ---- MAINPAGE ----
  c.title("Arquivo Texto Mapfre")
  c.markdown("""---""")

  uploaded_file = c.file_uploader("Escolha o arquivo TXT/CSV", type=["txt", "csv"], on_change=None, key="my-file", accept_multiple_files=False)

  if uploaded_file:
    print('subiu arquivo')
    df = pd.read_csv(uploaded_file, sep=";", encoding='latin-1')
    editable_df(df)
    out = df.to_json(orient='records')[1:-1]
  

