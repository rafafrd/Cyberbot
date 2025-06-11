import streamlit as st
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import time

# --- Configuração da Página ---
st.set_page_config(
    page_title="Assistente de Cibersegurança",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado ---
st.markdown("""
<style>
    /* Importar Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Animações CSS */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes glow {
        0% { box-shadow: 0 0 5px #00ff88; }
        50% { box-shadow: 0 0 20px #00ff88, 0 0 30px #00ff88; }
        100% { box-shadow: 0 0 5px #00ff88; }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Estilo do título principal */
    .main-title {
        font-family: 'Orbitron', monospace;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(45deg, #00ff88, #00ccff, #ff0080);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInUp 1s ease-out;
    }
    
    /* Subtítulo */
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #888;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1.2s ease-out;
    }
    
    /* Headers das seções */
    .section-header {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00ff88, #00ccff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 1rem 0;
        animation: slideInLeft 0.8s ease-out;
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(45deg, #00ff88, #00ccff);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 255, 136, 0.5);
        animation: pulse 1s infinite;
    }
    
    /* Card containers */
    .info-card {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 204, 255, 0.1));
        border: 1px solid rgba(0, 255, 136, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: fadeInUp 1s ease-out;
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(255, 0, 128, 0.1), rgba(255, 100, 0, 0.1));
        border: 1px solid rgba(255, 0, 128, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        animation: fadeInUp 1.2s ease-out;
    }
    
    /* Sidebar personalizada */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(0, 255, 136, 0.05), rgba(0, 204, 255, 0.05));
    }
    
    /* Inputs personalizados */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        border-radius: 10px;
        border: 2px solid rgba(0, 255, 136, 0.3);
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #00ff88;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        animation: glow 2s infinite;
    }
    
    /* Chat messages */
    .stChatMessage {
        animation: fadeInUp 0.5s ease-out;
    }
    
    /* Loading spinner personalizado */
    .stSpinner > div {
        border-top-color: #00ff88 !important;
    }
    
    /* Efeito de digitação */
    .typing-effect {
        font-family: 'Inter', sans-serif;
        overflow: hidden;
        border-right: 2px solid #00ff88;
        white-space: nowrap;
        animation: typing 3s steps(40, end), blink-caret 0.75s step-end infinite;
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #00ff88; }
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 255, 136, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #00ff88, #00ccff);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #00ccff, #ff0080);
    }
</style>
""", unsafe_allow_html=True)

# --- Função para criar efeito de digitação ---
def typewriter_effect(text, delay=0.05):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(f'<div class="typing-effect">{displayed_text}</div>', unsafe_allow_html=True)
        time.sleep(delay)
    return placeholder

# --- Título Principal com Animação ---
st.markdown('<h1 class="main-title">🛡️ ASSISTENTE DE CIBERSEGURANÇA</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle"> 🚀 Powered by Gemini AI | Proteção Inteligente & Educação em Segurança Digital</p>', unsafe_allow_html=True)

# --- Barra Lateral Melhorada ---
with st.sidebar:
    st.markdown('<h2 class="section-header">⚙️ Centro de Controle</h2>', unsafe_allow_html=True)
    
    # Card de configuração
    with st.container():
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### Configuração da API")
        gemini_api_key = st.text_input("Chave da API do Gemini", type="password", placeholder="Cole sua API key aqui...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Seleção de modo com estilo
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### Selecione o Modo")
    app_mode = st.selectbox(
        "Escolha sua missão",
        ["🤖 Chatbot de Cibersegurança", "🎣 Simulador de Phishing"],
        format_func=lambda x: x
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Card de informações
    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
    st.markdown("### Aviso Importante")
    st.markdown("""
    **🎓 Fins Educacionais**
    
    Esta ferramenta foi desenvolvida para:
    - ✅ Educação em cibersegurança
    - ✅ Treinamento de conscientização
    - ✅ Testes éticos autorizados
    
    **Use com responsabilidade!**
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Verificação da API ---
if not gemini_api_key:
    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
    st.warning("**Configuração Necessária:** Insira sua chave da API do Gemini na barra lateral para ativar o sistema.", icon="⚠️")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Configuração da API com tratamento de erro melhorado
try:
    genai.configure(api_key=gemini_api_key)
    st.sidebar.success("API Gemini conectada com sucesso!")
except Exception as e:
    st.error(f"❌ Erro na configuração da API: {e}")
    st.stop()

# --- MODO 1: CHATBOT DE CIBERSEGURANÇA ---
if app_mode == "Chatbot de Cibersegurança":
    st.markdown('<h2 class="section-header">Especialista Virtual em Segurança</h2>', unsafe_allow_html=True)
    
    # Card de introdução
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("""
    ### **Como posso ajudar você hoje?**
    
    💡 **Exemplos de perguntas:**
    - 🔒 Como criar senhas seguras?
    - 🌐 O que é phishing e como me proteger?
    - 🛡️ Quais as melhores práticas de segurança digital?
    - 🦠 Como detectar malware?
    - 📱 Segurança em dispositivos móveis
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Inicializa o modelo Gemini
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Inicializa o histórico do chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Inicia o chat com histórico
    chat = model.start_chat(history=st.session_state.chat_history)

    # Container para o chat
    chat_container = st.container()
    
    with chat_container:
        # Exibe mensagens do histórico com animação
        for message in chat.history:
            role = "Você" if message.role == "user" else "🤖 Especialista"
            avatar = "🧑‍💻" if message.role == "user" else "🛡️"
            
            with st.chat_message(role, avatar=avatar):
                st.markdown(message.parts[0].text)

    # Campo de entrada estilizado
    if prompt := st.chat_input("💬 Digite sua dúvida sobre cibersegurança..."):
        # Adiciona mensagem do usuário
        with st.chat_message("Você", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Processa resposta com spinner personalizado
        with st.chat_message("Especialista", avatar="🛡️"):
            with st.spinner("Analisando sua pergunta..."):
                try:
                    response = chat.send_message(prompt)
                    
                    # Efeito de digitação para a resposta
                    response_placeholder = st.empty()
                    displayed_text = ""
                    
                    for char in response.text:
                        displayed_text += char
                        response_placeholder.markdown(displayed_text)
                        time.sleep(0.01)  # Velocidade da digitação
                    
                    # Atualiza histórico
                    st.session_state.chat_history = chat.history
                    
                    # Feedback positivo
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"❌ Ops! Ocorreu um erro: {e}")

# --- MODO 2: SIMULADOR DE PHISHING ---
elif app_mode == "🎣 Simulador de Phishing":
    st.markdown('<h2 class="section-header">🎣 Simulador de E-mail de Phishing</h2>', unsafe_allow_html=True)
    
    # Aviso importante com estilo
    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
    st.markdown("""
    ### ⚠️ **ATENÇÃO - USO ÉTICO OBRIGATÓRIO**
    
    🛡️ **Esta ferramenta deve ser usada apenas para:**
    - ✅ Treinamentos de conscientização autorizados
    - ✅ Testes de segurança com consentimento explícito
    - ✅ Fins educacionais em ambiente controlado
    
    ❌ **NUNCA use para:**
    - Ataques reais ou maliciosos
    - Teste sem autorização
    - Qualquer atividade ilegal
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Formulário estilizado
    with st.form("phishing_form", clear_on_submit=False):
        # Seção do remetente
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### **Configuração do E-mail Remetente**")
        
        col1, col2 = st.columns(2)
        with col1:
            sender_email = st.text_input("Seu E-mail de Teste", placeholder="exemplo@gmail.com")
        with col2:
            sender_password = st.text_input("Senha de App", type="password", placeholder="Senha de aplicativo")
        
        st.info("💡 **Dica:** Use uma senha de aplicativo para Gmail, não sua senha principal!")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Seção do alvo
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### **Configuração do E-mail Alvo**")
        
        target_email = st.text_input("E-mail do Destinatário", placeholder="destinatario@exemplo.com")
        subject = st.text_input("📋 Assunto do E-mail", placeholder="Urgente: Verificação de Segurança Necessária")
        
        st.markdown("### **Conteúdo do E-mail**")
        body = st.text_area(
            "Corpo do E-mail (HTML suportado)", 
            height=200,
            placeholder="""<html>
<body>
    <h2>🔔 Alerta de Segurança</h2>
    <p>Prezado(a) usuário(a),</p>
    <p>Detectamos atividade suspeita em sua conta. Para sua segurança, é necessário verificar suas informações.</p>
    <p><a href="http://link-educacional-simulado.com" style="background-color: #ff4444; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">🔒 Verificar Conta Agora</a></p>
    <p><small>Este é um e-mail de simulação para fins educacionais.</small></p>
</body>
</html>"""
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botão de envio estilizado
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 **Executar Simulação**", use_container_width=True)

        if submitted:
            if not all([sender_email, sender_password, target_email, subject, body]):
                st.error("❌ **Campos obrigatórios:** Preencha todos os campos antes de prosseguir.")
            else:
                # Progress bar para o envio
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Simulação de progresso
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        if i < 30:
                            status_text.text("🔧 Configurando servidor SMTP...")
                        elif i < 60:
                            status_text.text("📝 Preparando mensagem...")
                        elif i < 90:
                            status_text.text("📤 Enviando e-mail...")
                        else:
                            status_text.text("✅ Finalizando...")
                        time.sleep(0.02)
                    
                    # Cria e envia o e-mail
                    msg = EmailMessage()
                    msg.set_content(body, subtype='html')
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = target_email

                    # Conecta ao servidor SMTP
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(sender_email, sender_password)
                        smtp.send_message(msg)
                    
                    # Remove progress bar
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Sucesso com efeitos
                    st.success(f"✅ **Missão Cumprida!** E-mail de simulação enviado para **{target_email}**")
                    st.balloons()
                    
                    # Estatísticas do envio
                    st.markdown('<div class="info-card">', unsafe_allow_html=True)
                    st.markdown(f"""
                    ### 📊 **Relatório da Simulação**
                    - 📧 **Destinatário:** {target_email}
                    - 📋 **Assunto:** {subject}
                    - 📅 **Data/Hora:** {time.strftime("%d/%m/%Y às %H:%M:%S")}
                    - ✅ **Status:** Enviado com sucesso
                    """)
                    st.markdown('</div>', unsafe_allow_html=True)

                except smtplib.SMTPAuthenticationError:
                    st.error("❌ **Erro de Autenticação:** Verifique seu e-mail e senha de aplicativo.")
                except Exception as e:
                    st.error(f"❌ **Erro no Envio:** {e}")
                finally:
                    progress_bar.empty()
                    status_text.empty()

# --- Footer ---
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.8rem;">'
    '🛡️ Assistente de Cibersegurança | Desenvolvido para Educação e Conscientização em Segurança Digital'
    '</div>', 
    unsafe_allow_html=True
)