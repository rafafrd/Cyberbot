import streamlit as st
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import string
import secrets
import math
import re

# --- FUNÇÕES AUXILIARES PARA O VERIFICADOR DE SENHAS ---

def analisar_forca_senha(password):
    """Analisa a força de uma senha e estima o tempo para quebrá-la."""
    length = len(password)
    if length == 0:
        return {"score": 0, "tempo_estimado": "N/A", "feedback": "Digite uma senha para análise."}

    # Determina o conjunto de caracteres (pool)
    pool = 0
    feedback_pontos = []
    if re.search(r'[a-z]', password):
        pool += 26
        feedback_pontos.append("letras minúsculas")
    if re.search(r'[A-Z]', password):
        pool += 26
        feedback_pontos.append("letras maiúsculas")
    if re.search(r'\d', password):
        pool += 10
        feedback_pontos.append("números")
    if re.search(r'[^a-zA-Z\d]', password):
        pool += 32 # Símbolos comuns
        feedback_pontos.append("símbolos")

    if pool == 0: pool = 26 # Caso apenas caracteres não mapeados sejam usados

    # Calcula as combinações possíveis
    combinacoes = pool ** length

    # Estimativa de tempo para quebrar (considerando 1 trilhão de tentativas/segundo)
    tentativas_por_segundo = 1_000_000_000_000
    segundos_para_quebrar = combinacoes / tentativas_por_segundo

    # Converte segundos para um formato legível
    def humanize_time(seconds):
        if seconds < 1: return "instantaneamente"
        if seconds < 60: return f"{seconds:.0f} segundos"
        minutes = seconds / 60
        if minutes < 60: return f"{minutes:.1f} minutos"
        hours = minutes / 60
        if hours < 24: return f"{hours:.1f} horas"
        days = hours / 24
        if days < 365: return f"{days:.1f} dias"
        years = days / 365
        if years < 1000: return f"{years:,.0f} anos"
        if years < 1_000_000: return f"{years/1000:,.1f} mil anos"
        return f"{years/1_000_000:,.1f} milhões de anos"

    tempo_estimado = humanize_time(segundos_para_quebrar)

    # Calcula uma pontuação de 0 a 4
    score = 0
    if length >= 8: score += 1
    if length >= 12: score += 1
    if 'letras maiúsculas' in feedback_pontos and 'letras minúsculas' in feedback_pontos: score +=1
    if 'números' in feedback_pontos and 'símbolos' in feedback_pontos: score += 1

    feedback_final = ""
    if score <= 1: feedback_final = "Muito Fraca. Aumente o comprimento e adicione variedade."
    elif score == 2: feedback_final = "Fraca. Tente adicionar mais caracteres ou tipos diferentes."
    elif score == 3: feedback_final = "Boa. Considere aumentar o comprimento para maior segurança."
    else: feedback_final = "Forte. Excelente combinação de comprimento e variedade."

    return {"score": score, "tempo_estimado": tempo_estimado, "feedback": feedback_final}

def gerar_senha_segura(length, incluir_numeros, incluir_simbolos):
    """Gera uma senha segura com base nos critérios fornecidos."""
    alphabet = string.ascii_letters
    if incluir_numeros:
        alphabet += string.digits
    if incluir_simbolos:
        alphabet += string.punctuation
    
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# --- Configuração da Página e Tema ---
st.set_page_config(
    page_title="NCTECH cyberbot",
    page_icon="🛡️",
    layout="centered"
)

# --- Injeção de CSS para o Tema Azul e Preto ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    h1 { color: #58a6ff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6 { color: #58a6ff; }
    [data-testid="stChatMessage"] { border-radius: 10px; padding: 1em; margin-bottom: 1em; border: 1px solid #30363d; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; border-radius: 5px; }
    .stButton>button { background-color: #238636; color: white; border: 1px solid #2ea043; border-radius: 5px; }
    .stButton>button:hover { background-color: #2ea043; border: 1px solid #3fb950; }
    .stSelectbox>div>div { background-color: #161b22; border: 1px solid #30363d; border-radius: 5px; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #d9534f, #f0ad4e, #5cb85c, #5cb85c); }
    .st-emotion-cache-1gulkj5 {
        color: #c9d1d9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Título e Descrição ---
st.title("🛡️ NCTECH cyberbot")
st.caption("Uma ferramenta completa para cibersegurança.")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Configurações")
    gemini_api_key = st.text_input("Chave da API do Gemini", type="password")
    st.markdown("---")
    app_mode = st.selectbox(
        "Escolha a função", 
        ["Chatbot de Cibersegurança", "Verificador de Senhas", "Simulador de Phishing"]
    )
    st.markdown("---")
    st.info("Este projeto é para fins educacionais. Use com responsabilidade.")

# --- Lógica Principal ---
# O verificador de senhas funciona sem API Key
if not gemini_api_key and app_mode != "Verificador de Senhas":
    st.warning("Por favor, insira sua chave da API do Gemini para usar o Chatbot ou o Simulador.")
    st.stop()

# Configura a API apenas quando necessário
if app_mode != "Verificador de Senhas":
    try:
        genai.configure(api_key=gemini_api_key)
    except Exception as e:
        st.error(f"Erro ao configurar a API do Gemini: {e}")
        st.stop()


# --- MODO 1: CHATBOT DE CIBERSEGURANÇA ---
if app_mode == "Chatbot de Cibersegurança":
    st.header("🤖 Fale com o Especialista Virtual")

    system_instruction = """
    Você é o 'CyberBot da NCTECH', um assistente virtual especialista e focado exclusivamente em cibersegurança. Sua única função é responder a perguntas e fornecer informações dentro deste domínio.

    **REGRAS ESTRITAS:**
    1.  **SEMPRE** responda apenas a perguntas relacionadas à cibersegurança. Isso inclui: malware, phishing, engenharia social, segurança de redes, firewalls, criptografia, pentesting, vulnerabilidades, gestão de identidade, LGPD, segurança em nuvem, etc.
    2.  **NUNCA** responda a perguntas que estejam fora do tópico de cibersegurança. Se o usuário perguntar sobre o tempo, esportes, história, ou qualquer outro assunto, recuse educadamente.
    3.  **COMO RECUSAR:** Ao receber uma pergunta fora do tópico, responda: "Desculpe, como um bot da NCTECH, fui programado para responder apenas a perguntas sobre cibersegurança. Como posso ajudar dentro desse tema?".
    4.  **SEJA PRECISO E OBJETIVO:** Forneça respostas claras, precisas e, quando apropriado, sugira boas práticas.
    5.  **IDENTIFIQUE-SE:** Sempre que iniciar uma nova conversa, apresente-se como 'CyberBot da NCTECH'.
    """

    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=system_instruction
    )

    if "chat_history" not in st.session_state or st.session_state.get("app_mode") != "Chatbot de Cibersegurança":
        st.session_state.chat_history = []
        st.session_state.app_mode = "Chatbot de Cibersegurança"
    
    chat = model.start_chat(history=st.session_state.chat_history)

    for message in chat.history:
        role = "Você" if message.role == "user" else "Assistente"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    if prompt := st.chat_input("Digite sua dúvida sobre cibersegurança..."):
        with st.chat_message("Você"):
            st.markdown(prompt)
        
        with st.spinner("Analisando..."):
            try:
                response = chat.send_message(prompt)
                with st.chat_message("Assistente"):
                    st.markdown(response.text)
                st.session_state.chat_history = chat.history
                st.rerun()
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")


# --- MODO 2: VERIFICADOR DE SENHAS ---
elif app_mode == "Verificador de Senhas":
    st.header("🔐 Verificador e Gerador de Senhas")

    st.subheader("Analisador de Força de Senha")
    password_to_check = st.text_input("Digite uma senha para analisar", type="password", key="password_checker")

    if password_to_check:
        analise = analisar_forca_senha(password_to_check)
        score = analise["score"]
        
        progress_values = {0: 10, 1: 25, 2: 50, 3: 75, 4: 100}

        st.progress(progress_values.get(score, 0))
        st.metric(label="Tempo estimado para quebra", value=analise["tempo_estimado"])
        st.info(f"**Feedback:** {analise['feedback']}")
        st.caption("Cálculo baseado em um ataque de força bruta com 1 trilhão de tentativas por segundo.")


    st.markdown("---")

    st.subheader("Gerador de Senha Segura")
    
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        comprimento = st.slider("Comprimento da Senha", min_value=8, max_value=64, value=16, key="len_slider")
    with col2:
        incluir_numeros = st.checkbox("Incluir Números", value=True, key="inc_nums")
    with col3:
        incluir_simbolos = st.checkbox("Incluir Símbolos", value=True, key="inc_syms")
        
    if st.button("Gerar Nova Senha"):
        senha_gerada = gerar_senha_segura(comprimento, incluir_numeros, incluir_simbolos)
        st.session_state.generated_password = senha_gerada

    if "generated_password" in st.session_state:
        st.text_input("Senha Gerada (copie abaixo)", value=st.session_state.generated_password, disabled=False, key="generated_pwd_display")


# --- MODO 3: SIMULADOR DE PHISHING ---
elif app_mode == "Simulador de Phishing":
    st.header("🎣 Simulador de E-mail de Phishing")
    st.warning(
        "**Atenção:** Use esta ferramenta de forma ética e apenas com consentimento explícito. "
        "O objetivo é educar sobre os riscos de phishing.",
        icon="⚠️"
    )

    with st.form("phishing_form"):
        st.subheader("Configuração do E-mail do Remetente (Teste)")
        sender_email = st.text_input("Seu E-mail de Teste (Ex: Gmail)")
        sender_password = st.text_input("Sua Senha de App", type="password")
        st.markdown("---")
        st.subheader("Configuração do E-mail Alvo")
        target_email = st.text_input("E-mail do Alvo")
        subject = st.text_input("Assunto do E-mail")
        body = st.text_area("Corpo do E-mail (HTML é suportado)", height=200, 
                            placeholder="Ex: <html><body><p>Prezado(a),</p><p>Sua conta expira em 24h. Clique <a href='http://link-malicioso-simulado.com'>aqui</a> para renovar.</p></body></html>")
        
        submitted = st.form_submit_button("Enviar E-mail de Simulação")

        if submitted:
            if not all([sender_email, sender_password, target_email, subject, body]):
                st.error("Por favor, preencha todos os campos antes de enviar.")
            else:
                try:
                    msg = EmailMessage()
                    msg.set_content(body, subtype='html')
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = target_email
                    with st.spinner("Enviando e-mail..."):
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender_email, sender_password)
                            smtp.send_message(msg)
                    st.success(f"E-mail de simulação enviado com sucesso para {target_email}!")
                    st.balloons()
                except smtplib.SMTPAuthenticationError:
                    st.error("Erro de autenticação. Verifique seu e-mail e senha de app.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao enviar o e-mail: {e}")
