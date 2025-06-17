import streamlit as st
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import string
import secrets
import re
import time
from datetime import datetime

# --- FUNÇÕES AUXILIARES PARA O VERIFICADOR DE SENHAS ---

def analisar_forca_senha(password):
    """Analisa a força de uma senha e estima o tempo para quebrá-la."""
    length = len(password)
    if length == 0:
        return {"score": 0, "tempo_estimado": "N/A", "feedback": "Digite uma senha para análise."}
    pool = 0
    feedback_pontos = []
    if re.search(r'[a-z]', password): pool += 26; feedback_pontos.append("letras minúsculas")
    if re.search(r'[A-Z]', password): pool += 26; feedback_pontos.append("letras maiúsculas")
    if re.search(r'\d', password): pool += 10; feedback_pontos.append("números")
    if re.search(r'[^a-zA-Z\d]', password): pool += 32; feedback_pontos.append("símbolos")
    if pool == 0: pool = 26
    combinacoes = pool ** length
    tentativas_por_segundo = 1_000_000_000_000
    segundos_para_quebrar = combinacoes / tentativas_por_segundo

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
    
    score = 0
    if length >= 8: score += 1
    if length >= 12: score += 1
    if 'letras maiúsculas' in feedback_pontos and 'letras minúsculas' in feedback_pontos: score +=1
    if 'números' in feedback_pontos and 'símbolos' in feedback_pontos: score += 1

    if score <= 1: feedback_final = "Muito Fraca. Aumente o comprimento e adicione variedade."
    elif score == 2: feedback_final = "Fraca. Tente adicionar mais caracteres ou tipos diferentes."
    elif score == 3: feedback_final = "Boa. Considere aumentar o comprimento para maior segurança."
    else: feedback_final = "Forte. Excelente combinação de comprimento e variedade."
    
    return {"score": score, "tempo_estimado": tempo_estimado, "feedback": feedback_final}

def gerar_senha_segura(length, incluir_numeros, incluir_simbolos):
    """Gera uma senha segura com base nos critérios fornecidos."""
    alphabet = string.ascii_letters
    if incluir_numeros: alphabet += string.digits
    if incluir_simbolos: alphabet += string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# --- Configuração da Página ---
st.set_page_config(
    page_title="CyberGuard AI - Assistente de Cibersegurança",
    page_icon="🛡️",   
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS e JS Customizado para Design Moderno ---
st.markdown("""
<style>
    /* Importar fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .main, body, .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    div[data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }
    .stApp > header {
        background-color: transparent;
    }
    
    /* Header principal com gradiente animado */
    .main-header {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 25%, #0066ff 50%, #8b5cf6 75%, #a855f7 100%);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 212, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .main-title {
        font-size: 3rem; font-weight: 700; margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative; z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;
        font-weight: 300; position: relative; z-index: 1;
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Cards de funcionalidades */
    .feature-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px; padding: 1.5rem; margin: 1rem 0;
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 212, 255, 0.2);
        border-color: rgba(0, 212, 255, 0.6);
    }
    
    /* Chat messages personalizadas */
    .chat-message {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-left: 4px solid #00d4ff;
        border-radius: 0 15px 15px 0;
        padding: 1rem; margin: 0.5rem 0;
        animation: slideIn 0.3s ease-out;
    }
    .chat-message.user {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        border-left: 4px solid #8b5cf6;
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white; border: none; border-radius: 10px;
        padding: 0.75rem 2rem; font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        width: 100%; /* Para o botão de envio do chat ocupar a coluna */
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
        background: linear-gradient(135deg, #0099cc 0%, #00d4ff 100%);
    }
    
    /* Inputs e Selectbox modernos */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px; color: white;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
    }
    
    /* Alertas */
    .stWarning, .stSuccess, .stError, .stInfo {
        border-left-width: 4px;
        border-radius: 0 10px 10px 0;
    }
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
        border-radius: 15px; padding: 1rem; text-align: center;
        border: 1px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease; margin-bottom: 10px;
    }
    .metric-card:hover {
        transform: scale(1.05); border-color: rgba(0, 212, 255, 0.5);
    }
    .metric-value {
        font-size: 1.5rem; font-weight: 700; color: #00d4ff; margin: 0;
    }
    .metric-label {
        font-size: 0.8rem; opacity: 0.8; margin-top: 0.5rem; text-transform: uppercase;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Principal ---
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛡️ NCTech Cyberbot</h1>
    <p class="main-subtitle">Assistente Avançado de Cibersegurança com IA</p>
</div>
""", unsafe_allow_html=True)

# --- Inicialização de Variáveis de Sessão ---
if 'query_count' not in st.session_state: st.session_state.query_count = 0
if 'session_start' not in st.session_state: st.session_state.session_start = datetime.now()
if 'gemini_api_key' not in st.session_state: st.session_state.gemini_api_key = ""

# --- Barra Lateral Moderna ---
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    api_status = "🔴 Desconectado"
    if st.session_state.gemini_api_key:
        api_status = "🟢 Conectado"
    st.markdown(f"**Status da API:** {api_status}")
    
    user_api_key = st.text_input(
        "🔑 Chave da API do Gemini", type="password",
        help="Insira sua chave da API do Google Gemini",
        value=st.session_state.gemini_api_key
    )
    if user_api_key: st.session_state.gemini_api_key = user_api_key
        
    st.markdown("---")
    
    app_mode = st.radio(
        "🎯 Escolha a Função",
        ["🤖 Chatbot", "🔐 Verificador de Senhas", "🎣 Simulador de Phishing"],
        help="Selecione o modo de operação do assistente"
    )
    
    st.markdown("---")
    
    session_duration = datetime.now() - st.session_state.session_start
    minutes = int(session_duration.total_seconds() // 60)
    
    st.markdown("### 📊 Estatísticas da Sessão")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{st.session_state.query_count}</p>
            <p class="metric-label">Consultas</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{minutes}m</p>
            <p class="metric-label">Tempo</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.info("🎓 Projeto Educacional para conscientização em cibersegurança.")
    st.warning("⚠️ Use o simulador de phishing com responsabilidade e consentimento.")

# --- Verificação da API ---
if not st.session_state.gemini_api_key:
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Bem-vindo ao NCTech Cyberbot</h3>
        <p>Para começar, insira sua chave da API do Google Gemini na barra lateral para ativar as funcionalidades de IA.</p>
        <p><strong>A função 'Verificador de Senhas' está disponível offline.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    if app_mode != "🔐 Verificador de Senhas":
        st.stop()

if st.session_state.gemini_api_key:
    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
    except Exception as e:
        st.error(f"❌ **Erro na configuração da API:** {e}")
        st.stop()

# --- MODO: CHATBOT ---
if app_mode == "🤖 Chatbot":
    st.markdown('<div class="feature-card"><h2>🤖 CyberBot - Especialista Virtual</h2><p>Converse com nosso assistente. Obtenha respostas sobre malware, phishing, segurança de redes, etc.</p></div>', unsafe_allow_html=True)
    system_instruction = "Você é o 'CyberBot', um assistente virtual especialista e focado exclusivamente em cibersegurança..." # Prompt omitido
    model = genai.GenerativeModel('gemini-2.0-flash', system_instruction=system_instruction)
    if "chat_history" not in st.session_state or st.session_state.get("app_mode") != "🤖 Chatbot":
        st.session_state.chat_history = []; st.session_state.app_mode = "🤖 Chatbot"
    chat = model.start_chat(history=st.session_state.chat_history)
    for msg in chat.history:
        role = "Você" if msg.role == "user" else "CyberBot"; icon = "👤" if role == "Você" else "🤖"; css_class = "user" if role == "Você" else ""
        st.markdown(f'<div class="chat-message {css_class}"><strong>{icon} {role}:</strong><br>{msg.parts[0].text}</div>', unsafe_allow_html=True)
    
    prompt = st.chat_input("Digite sua dúvida sobre cibersegurança...")
    if prompt:
        st.session_state.query_count += 1
        st.markdown(f'<div class="chat-message user"><strong>👤 Você:</strong><br>{prompt}</div>', unsafe_allow_html=True)
        with st.spinner("🧠 CyberBot está pensando..."):
            response = chat.send_message(prompt)
            st.markdown(f'<div class="chat-message"><strong>🤖 CyberBot:</strong><br>{response.text}</div>', unsafe_allow_html=True)
            st.session_state.chat_history = chat.history
            time.sleep(0.1); st.rerun()

# --- MODO: VERIFICADOR DE SENHAS ---
elif app_mode == "🔐 Verificador de Senhas":
    st.markdown('<div class="feature-card"><h2>🔐 Verificador e Gerador de Senhas</h2><p>Analise a força de suas senhas e gere novas senhas seguras e aleatórias.</p></div>', unsafe_allow_html=True)
    st.subheader("Analisador de Força de Senha")
    password_to_check = st.text_input("Digite uma senha para analisar", type="password", key="password_checker")
    if password_to_check:
        analise = analisar_forca_senha(password_to_check)
        st.metric(label="Tempo estimado para quebra", value=analise["tempo_estimado"])
        st.info(f"**Feedback:** {analise['feedback']}")
    st.markdown("---"); st.subheader("Gerador de Senha Segura")
    col1, col2, col3 = st.columns([2,1,1])
    with col1: comprimento = st.slider("Comprimento da Senha", 8, 64, 16)
    with col2: incluir_numeros = st.checkbox("Números", True)
    with col3: incluir_simbolos = st.checkbox("Símbolos", True)
    if st.button("Gerar Nova Senha"):
        st.session_state.generated_password = gerar_senha_segura(comprimento, incluir_numeros, incluir_simbolos)
    if "generated_password" in st.session_state:
        st.text_input("Senha Gerada", value=st.session_state.generated_password, key="pwd_display")

# --- MODO: SIMULADOR DE PHISHING ---
elif app_mode == "🎣 Simulador de Phishing":
    st.markdown('<div class="feature-card"><h2>🎣 Simulador de E-mail de Phishing</h2><p>Ferramenta educacional para simular ataques e treinar usuários.</p></div>', unsafe_allow_html=True)
    with st.form("phishing_form"):
        st.markdown("### 📧 Configuração do Remetente")
        col1, col2 = st.columns(2)
        with col1: sender_email = st.text_input("Seu E-mail de Teste")
        with col2: sender_password = st.text_input("Sua Senha de App", type="password")
        st.markdown("---"); st.markdown("### 🎯 Configuração do Alvo")
        col1, col2 = st.columns(2)
        with col1: target_email = st.text_input("E-mail do Destinatário")
        with col2: subject = st.text_input("Assunto do E-mail")
        st.markdown("### ✏️ Conteúdo do E-mail")
        body = st.text_area("Corpo do E-mail (HTML é suportado)", height=200)
        if st.form_submit_button("🚀 Enviar Simulação"):
            if not all([sender_email, sender_password, target_email, subject, body]):
                st.error("❌ Por favor, preencha todos os campos.")
            else:
                msg = EmailMessage(); msg.set_content(body, subtype='html'); msg['Subject'] = f"[SIMULAÇÃO] {subject}"
                msg['From'] = sender_email; msg['To'] = target_email
                with st.spinner("Enviando e-mail..."):
                    try:
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender_email, sender_password); smtp.send_message(msg)
                        st.success(f"🎉 Simulação enviada com sucesso para {target_email}!"); st.balloons()
                    except Exception as e: st.error(f"❌ Erro ao enviar: {e}")

# --- Footer ---
st.markdown("---")
st.markdown('<div style="text-align: center; padding: 2rem; opacity: 0.7;"><p>🛡️ <strong>CyberGuard AI</strong> - Powered by Google Gemini</p></div>', unsafe_allow_html=True)
