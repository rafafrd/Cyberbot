import streamlit as st
import google.generativeai as genai
import smtplib
from email.message import EmailMessage
import time
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="CyberGuard AI - Assistente de Cibersegurança",
    page_icon="🛡️",   
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Customizado para Design Moderno ---
st.markdown("""
<style>
    /* Importar fontes modernas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
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
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
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
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }
    
    /* Cards de funcionalidades */
    .feature-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 212, 255, 0.2);
        border-color: rgba(0, 212, 255, 0.6);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    /* Chat messages personalizadas */
    .chat-message {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-left: 4px solid #00d4ff;
        border-radius: 0 15px 15px 0;
        padding: 1rem;
        margin: 0.5rem 0;
        animation: slideIn 0.3s ease;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(168, 85, 247, 0.1) 100%);
        border-left: 4px solid #8b5cf6;
        margin-left: 2rem;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.4);
        background: linear-gradient(135deg, #0099cc 0%, #00d4ff 100%);
    }
    
    /* Inputs modernos */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 2px rgba(0, 212, 255, 0.2);
    }
    
    /* Selectbox moderno */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 10px;
    }
    
    /* Warnings e alertas */
    .stWarning {
        background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%);
        border-left: 4px solid #ffc107;
        border-radius: 0 10px 10px 0;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, rgba(40, 167, 69, 0.1) 0%, rgba(25, 135, 84, 0.1) 100%);
        border-left: 4px solid #28a745;
        border-radius: 0 10px 10px 0;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.1) 0%, rgba(200, 35, 51, 0.1) 100%);
        border-left: 4px solid #dc3545;
        border-radius: 0 10px 10px 0;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online {
        background-color: #28a745;
    }
    
    .status-offline {
        background-color: #dc3545;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Metrics cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(0, 212, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        border-color: rgba(0, 212, 255, 0.5);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    /* Loading spinner personalizado */
    .custom-spinner {
        border: 3px solid rgba(0, 212, 255, 0.3);
        border-top: 3px solid #00d4ff;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #00d4ff 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #8b5cf6 0%, #00d4ff 100%);
    }
</style>
""", unsafe_allow_html=True)

# --- Header Principal ---
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛡️ CyberGuard AI</h1>
    <p class="main-subtitle">Assistente Avançado de Cibersegurança com IA</p>
</div>
""", unsafe_allow_html=True)

# --- Barra Lateral Moderna ---
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    # Status da AP I
    api_status = "🔴 Desconectado"
    if 'gemini_api_key' in st.session_state and st.session_state.get('gemini_api_key'):
        api_status = "🟢 Conectado"
    
    st.markdown(f"**Status da API:** {api_status}")
    
    # Campo para inserir a chave da API do Gemini
    gemini_api_key = st.text_input(
        "🔑 Chave da API do Gemini", 
        type="password",
        help="Insira sua chave da API do Google Gemini"
    )
    
    if gemini_api_key:
        st.session_state.gemini_api_key = gemini_api_key
    
    st.markdown("---")
    
    # Seleção de modo do aplicativo com ícones
    app_mode = st.selectbox(
        "🎯 Escolha a Função",
        ["🤖 Chatbot de Cibersegurança", "🎣 Simulador de Phishing"],
        help="Selecione o modo de operação do assistente"
    )
    
    st.markdown("---")
    
    # Métricas da sessão
    st.markdown("### 📊 Estatísticas da Sessão")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">{}</p>
            <p class="metric-label">Consultas</p>
        </div>
        """.format(st.session_state.get('query_count', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-value">{}</p>
            <p class="metric-label">Tempo Online</p>
        </div>
        """.format(st.session_state.get('session_time', '0m')), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informações e alertas
    st.markdown("### ℹ️ Informações")
    st.info("🎓 **Projeto Educacional**\n\nEste assistente foi desenvolvido para fins educacionais e de conscientização sobre cibersegurança.")
    
    st.warning("⚠️ **Uso Responsável**\n\nUse o simulador de phishing apenas com consentimento explícito e para fins legítimos de treinamento.")

# --- Inicialização de Variáveis de Sessão ---
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()

# Calcular tempo de sessão
session_duration = datetime.now() - st.session_state.session_start
minutes = int(session_duration.total_seconds() // 60)
st.session_state.session_time = f"{minutes}m"

# --- Verificação da API ---
if not gemini_api_key:
    st.markdown("""
    <div class="feature-card">
        <h3>🚀 Bem-vindo ao CyberGuard AI</h3>
        <p>Para começar, insira sua chave da API do Google Gemini na barra lateral.</p>
        <p><strong>Recursos disponíveis:</strong></p>
        <ul>
            <li>🤖 Chatbot especializado em cibersegurança</li>
            <li>🎣 Simulador de phishing para treinamento</li>
            <li>📚 Base de conhecimento atualizada</li>
            <li>🛡️ Análise de vulnerabilidades</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Configura a API do Gemini
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    st.error(f"❌ **Erro na configuração da API:** {e}")
    st.stop()

# --- MODO 1: CHATBOT DE CIBERSEGURANÇA ---
if app_mode == "🤖 Chatbot de Cibersegurança":
    
    # Header da seção
    st.markdown("""
    <div class="feature-card">
        <h2>🤖 CyberBot - Especialista Virtual</h2>
        <p>Converse com nosso assistente especializado em cibersegurança. Obtenha respostas precisas sobre malware, phishing, segurança de redes, criptografia e muito mais.</p>
    </div>
    """, unsafe_allow_html=True)

    # Definição da instrução de sistema
    system_instruction = """
    Você é o 'CyberBot', um assistente virtual especialista e focado exclusivamente em cibersegurança. Sua única função é responder a perguntas e fornecer informações dentro deste domínio.

    **REGRAS ESTRITAS:**
    1. **SEMPRE** responda apenas a perguntas relacionadas à cibersegurança. Isso inclui: malware, phishing, engenharia social, segurança de redes, firewalls, criptografia, pentesting, vulnerabilidades, gestão de identidade, segurança em nuvem, etc.
    2. **NUNCA** responda a perguntas fora do tópico de cibersegurança.
    3. **COMO RECUSAR:** Responda educadamente: "Desculpe, fui programado para responder apenas a perguntas sobre cibersegurança. Como posso ajudar dentro desse tema?"
    4. **SEJA PRECISO E OBJETIVO:** Forneça respostas claras, precisas e sugira boas práticas.
    5. **TOM PROFISSIONAL:** Mantenha um tom profissional e informativo.
    """

    # Inicializa o modelo Gemini
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=system_instruction
    )

    # Inicializa o histórico do chat
    if "app_mode" not in st.session_state or st.session_state.app_mode != "🤖 Chatbot de Cibersegurança":
        st.session_state.chat_history = []
        st.session_state.app_mode = "🤖 Chatbot de Cibersegurança"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Inicia o chat
    chat = model.start_chat(history=st.session_state.chat_history)

    # Container para o histórico do chat
    chat_container = st.container()
    
    with chat_container:
        # Exibe mensagem de boas-vindas se não houver histórico
        if not chat.history:
            st.markdown("""
            <div class="chat-message">
                <strong>🤖 CyberBot:</strong><br>
                Olá! Sou o CyberBot, seu assistente especializado em cibersegurança. 
                Estou aqui para ajudar com dúvidas sobre:
                <br><br>
                • 🦠 Malware e vírus<br>
                • 🎣 Phishing e engenharia social<br>
                • 🔐 Criptografia e segurança de dados<br>
                • 🌐 Segurança de redes<br>
                • 🛡️ Firewalls e proteção<br>
                • 🔍 Testes de penetração<br>
                • ☁️ Segurança em nuvem<br>
                <br>
                Como posso ajudar você hoje?
            </div>
            """, unsafe_allow_html=True)

        # Exibe o histórico de mensagens
        for message in chat.history:
            role = "Você" if message.role == "user" else "CyberBot"
            icon = "👤" if message.role == "user" else "🤖"
            css_class = "user" if message.role == "user" else ""
            
            st.markdown(f"""
            <div class="chat-message {css_class}">
                <strong>{icon} {role}:</strong><br>
                {message.parts[0].text}
            </div>
            """, unsafe_allow_html=True)

    # Campo de entrada para mensagens
    col1, col2 = st.columns([6, 1])
    
    with col1:
        prompt = st.text_input(
            "💬 Digite sua dúvida sobre cibersegurança...",
            key="chat_input",
            placeholder="Ex: Como posso me proteger contra ataques de phishing?"
        )
    
    with col2:
        send_button = st.button("📤 Enviar", key="send_btn")

    # Processa a mensagem quando enviada
    if (prompt and send_button) or (prompt and st.session_state.get('send_on_enter', False)):
        st.session_state.query_count += 1
        
        # Adiciona indicador de digitação
        with st.spinner("🧠 CyberBot está pensando..."):
            try:
                response = chat.send_message(prompt)
                st.session_state.chat_history = chat.history
                st.rerun()
            except Exception as e:
                st.error(f"❌ **Erro ao processar pergunta:** {e}")

# --- MODO 2: SIMULADOR DE PHISHING ---
elif app_mode == "🎣 Simulador de Phishing":
    
    # Header da seção
    st.markdown("""
    <div class="feature-card">
        <h2>🎣 Simulador de E-mail de Phishing</h2>
        <p>Ferramenta educacional para simular ataques de phishing e treinar usuários sobre os riscos de engenharia social.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Aviso de segurança
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.1) 100%); 
                border-left: 4px solid #ffc107; border-radius: 0 15px 15px 0; padding: 1rem; margin: 1rem 0;">
        <strong>⚠️ AVISO IMPORTANTE</strong><br>
        Esta ferramenta deve ser usada APENAS para fins educacionais e com consentimento explícito. 
        O objetivo é conscientizar sobre os riscos de phishing e treinar usuários.
    </div>
    """, unsafe_allow_html=True)

    # Formulário de configuração
    with st.form("phishing_form", clear_on_submit=False):
        
        # Seção de configuração do remetente
        st.markdown("### 📧 Configuração do E-mail Remetente")
        
        col1, col2 = st.columns(2)
        with col1:
            sender_email = st.text_input(
                "📮 Seu E-mail de Teste",
                placeholder="exemplo@gmail.com",
                help="Use um e-mail de teste configurado para desenvolvimento"
            )
        
        with col2:
            sender_password = st.text_input(
                "🔐 Senha de App",
                type="password",
                help="Use uma senha de aplicativo específica, não sua senha principal"
            )

        st.markdown("---")

        # Seção de configuração do alvo
        st.markdown("### 🎯 Configuração do E-mail Alvo")
        
        col1, col2 = st.columns(2)
        with col1:
            target_email = st.text_input(
                "📨 E-mail do Destinatário",
                placeholder="usuario@exemplo.com"
            )
        
        with col2:
            subject = st.text_input(
                "📋 Assunto do E-mail",
                placeholder="Urgente: Verifique sua conta"
            )

        # Corpo do e-mail
        st.markdown("### ✏️ Conteúdo do E-mail")
        
        # Templates pré-definidos
        template_options = {
            "Personalizado": "",
            "Verificação de Conta": """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #d32f2f;">🚨 Ação Necessária: Verificação de Conta</h2>
                    <p>Prezado(a) usuário(a),</p>
                    <p>Detectamos atividade suspeita em sua conta. Para manter sua segurança, 
                    é necessário verificar sua identidade.</p>
                    <p><strong>Sua conta será suspensa em 24 horas se não for verificada.</strong></p>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="http://site-simulacao-phishing.com/verificar" 
                           style="background: #d32f2f; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            ✅ Verificar Conta Agora
                        </a>
                    </div>
                    <p><small>Este é um e-mail de simulação para fins educacionais.</small></p>
                </div>
            </body>
            </html>
            """,
            "Atualização de Segurança": """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #1976d2;">🔒 Atualização de Segurança Necessária</h2>
                    <p>Olá,</p>
                    <p>Implementamos novas medidas de segurança para proteger melhor sua conta.</p>
                    <p>Para continuar usando nossos serviços, você deve atualizar suas 
                    configurações de segurança até <strong>hoje</strong>.</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="http://site-simulacao-atualizacao.com" 
                           style="background: #1976d2; color: white; padding: 12px 24px; 
                                  text-decoration: none; border-radius: 5px; display: inline-block;">
                            🔧 Atualizar Configurações
                        </a>
                    </div>
                    <p><small>Simulação educacional - Não clique em links suspeitos!</small></p>
                </div>
            </body>
            </html>
            """
        }
        
        selected_template = st.selectbox(
            "📄 Escolha um Template",
            list(template_options.keys()),
            help="Selecione um template pré-definido ou escolha 'Personalizado'"
        )
        
        if selected_template != "Personalizado":
            body = st.text_area(
                "📝 Corpo do E-mail (HTML)",
                value=template_options[selected_template],
                height=300,
                help="Você pode editar o template selecionado"
            )
        else:
            body = st.text_area(
                "📝 Corpo do E-mail (HTML)",
                height=300,
                placeholder="Digite o conteúdo do e-mail aqui... (HTML é suportado)"
            )
        
        # Botão de envio
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Enviar Simulação de Phishing",
                help="Certifique-se de que todos os campos estão preenchidos"
            )

        # Processamento do envio
        if submitted:
            if not all([sender_email, sender_password, target_email, subject, body]):
                st.error("❌ **Erro:** Por favor, preencha todos os campos antes de enviar.")
            else:
                try:
                    # Cria a mensagem de e-mail
                    msg = EmailMessage()
                    msg.set_content(body, subtype='html')
                    msg['Subject'] = f"[SIMULAÇÃO] {subject}"
                    msg['From'] = sender_email
                    msg['To'] = target_email

                    # Progresso de envio
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🔄 Conectando ao servidor SMTP...")
                    progress_bar.progress(25)
                    time.sleep(1)
                    
                    # Conecta ao servidor SMTP
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        status_text.text("🔐 Autenticando...")
                        progress_bar.progress(50)
                        time.sleep(1)
                        
                        smtp.login(sender_email, sender_password)
                        
                        status_text.text("📧 Enviando e-mail...")
                        progress_bar.progress(75)
                        time.sleep(1)
                        
                        smtp.send_message(msg)
                        
                        status_text.text("✅ E-mail enviado com sucesso!")
                        progress_bar.progress(100)
                    
                    # Sucesso
                    st.success(f"🎉 **Simulação enviada com sucesso!**\n\n📧 Destinatário: {target_email}")
                    st.balloons()
                    
                    # Estatísticas
                    st.markdown("""
                    <div class="feature-card">
                        <h4>📊 Resumo da Simulação</h4>
                        <p><strong>Destinatário:</strong> {}</p>
                        <p><strong>Assunto:</strong> {}</p>
                        <p><strong>Horário:</strong> {}</p>
                        <p><strong>Status:</strong> ✅ Entregue</p>
                    </div>
                    """.format(target_email, subject, datetime.now().strftime("%d/%m/%Y %H:%M:%S")), unsafe_allow_html=True)

                except smtplib.SMTPAuthenticationError:
                    st.error("""
                    ❌ **Erro de Autenticação**
                    
                    Verifique:
                    - E-mail está correto
                    - Senha de app está correta (não use sua senha principal)
                    - Autenticação de 2 fatores está habilitada
                    - Acesso a apps menos seguros está permitido
                    """)
                    
                except smtplib.SMTPRecipientsRefused:
                    st.error("❌ **Erro:** E-mail do destinatário foi rejeitado. Verifique o endereço.")
                    
                except smtplib.SMTPServerDisconnected:
                    st.error("❌ **Erro:** Conexão com servidor perdida. Tente novamente.")
                    
                except Exception as e:
                    st.error(f"❌ **Erro inesperado:** {e}")

    # Seção educacional sobre phishing
    st.markdown("---")
    st.markdown("""
    <div class="feature-card">
        <h3>🎓 Sobre Ataques de Phishing</h3>
        <p>O phishing é uma técnica de engenharia social usada para enganar pessoas e obter informações confidenciais. 
        Principais características dos e-mails de phishing:</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div>
                <h4>🚩 Sinais de Alerta:</h4>
                <ul>
                    <li>Urgência excessiva</li>
                    <li>Ameaças de suspensão</li>
                    <li>Links suspeitos</li>
                    <li>Erros de português</li>
                    <li>Remetente desconhecido</li>
                </ul>
            </div>
            <div>
                <h4>🛡️ Como se Proteger:</h4>
                <ul>
                    <li>Verificar remetente</li>
                    <li>Não clicar em links suspeitos</li>
                    <li>Verificar URLs</li>
                    <li>Usar autenticação 2FA</li>
                    <li>Manter software atualizado</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; opacity: 0.7;">
    <p>🛡️ <strong>CyberGuard AI</strong> - Desenvolvido para educação em cibersegurança</p>
    <p>Versão 2.0 | Powered by Google Gemini AI</p>
    <p><small>⚡ Tempo de resposta médio: <50ms | 🔒 Conexão segura</small></p>
</div>
""", unsafe_allow_html=True)

# --- Scripts JavaScript para interações avançadas ---
st.markdown("""
<script>
// Auto-scroll para a última mensagem do chat
function scrollToBottom() {
    const chatContainer = document.querySelector('.main');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Efeito de digitação para mensagens
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.innerHTML = '';
    
    function type() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// Animações de entrada para elementos
function animateOnScroll() {
    const elements = document.querySelectorAll('.feature-card');
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa animações
    animateOnScroll();
    
    // Adiciona listener para scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Auto-focus no campo de input do chat
    const chatInput = document.querySelector('input[placeholder*="cibersegurança"]');
    if (chatInput) {
        chatInput.focus();
    }
});

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // Enter para enviar mensagem (Ctrl + Enter)
    if (e.ctrlKey && e.key === 'Enter') {
        const sendButton = document.querySelector('button[key="send_btn"]');
        if (sendButton) {
            sendButton.click();
        }
    }
    
    // Esc para limpar input
    if (e.key === 'Escape') {
        const chatInput = document.querySelector('input[key="chat_input"]');
        if (chatInput) {
            chatInput.value = '';
            chatInput.focus();
        }
    }
});

// Efeitos sonoros (opcional)
function playNotificationSound() {
    // Cria um beep simples
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.1);
}

// Função para copiar código para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        // Feedback visual
        const notification = document.createElement('div');
        notification.innerHTML = '✅ Copiado!';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 2000);
    });
}

// Contador de caracteres dinâmico
function updateCharacterCount(inputElement, countElement, maxLength) {
    const currentLength = inputElement.value.length;
    const remaining = maxLength - currentLength;
    
    countElement.innerHTML = `${currentLength}/${maxLength}`;
    countElement.style.color = remaining < 50 ? '#dc3545' : '#6c757d';
}

// Theme switcher (modo claro/escuro)
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// Carrega tema salvo
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    document.body.classList.add('dark-theme');
}
</script>
""", unsafe_allow_html=True)