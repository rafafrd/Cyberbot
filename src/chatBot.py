import streamlit as st
from email.message import EmailMessage
import smtplib
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
# Usando um layout mais amplo para a nova estrutura sem sidebar.
st.set_page_config(
    page_title="CyberBot - NCTECH",
    page_icon="🛡️",
    layout="wide"
)

# --- 2. CSS CUSTOMIZADO PARA UM DESIGN INOVADOR ---
# Este CSS remove a sidebar, cria um tema escuro profissional e estiliza os novos componentes.
st.markdown("""
<style>
    /* Esconde o menu hamburger e o header padrão do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Remove o padding padrão do bloco principal do Streamlit */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Fundo da aplicação com gradiente sutil */
    .main {
        background: linear-gradient(180deg, #0E1117 0%, #171b26 100%);
        color: #FAFAFA;
    }

    /* Estilo do container do cabeçalho */
    .header-container {
        background-color: #1A1D24; /* Um pouco mais claro que o fundo */
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid #2c313a;
    }

    /* Estilização das abas (tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px; /* Espaçamento entre as abas */
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        border: 1px solid #4F4F4F;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #007BFF; /* Cor de destaque para a aba ativa */
        border: 1px solid #007BFF;
        color: white;
        font-weight: bold;
    }

    /* Estilo dos "cartões" para o conteúdo principal */
    .content-card {
        background-color: #1A1D24;
        border-radius: 15px;
        padding: 25px;
        border: 1px solid #2c313a;
        margin-top: 1rem;
    }
    
    /* Estilo geral dos botões */
    div.stButton > button:first-child {
        background-color: #007BFF;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 12px 24px;
        width: 100%; /* Botão ocupa a largura toda do formulário */
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }
    
    /* Estilo do chat */
    .st-emotion-cache-1c7y2kd { /* Container da mensagem do chat */
        background-color: rgba(0, 123, 255, 0.1); /* Fundo levemente azulado para mensagens */
        border-radius: 10px;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO DA APLICAÇÃO ---
# Layout em colunas para a logo, título e configurações.

# Usando HTML para controle mais fino do layout do cabeçalho
st.markdown("""
<div class="header-container">
    <div style="flex-basis: 20%;">
        </div>
    <div style="flex-basis: 60%; text-align: center;">
        <h1 style="color: #FAFAFA; margin: 0; font-size: 2.5rem;">CyberBot - NCTECH 🛡️</h1>
    </div>
    <div style="flex-basis: 20%;"></div>
</div>
""", unsafe_allow_html=True)

# A logo é inserida aqui para que o Streamlit possa gerenciá-la corretamente
# O container do cabeçalho é dividido em 3 colunas para alinhar tudo
c1, c2, c3 = st.columns([1, 3, 1])

with c1:
    # --- AQUI VOCÊ COLOCA O CAMINHO PARA A SUA LOGO ---
    # Pode ser uma URL ("https://...") ou um caminho local ("./logo.png")
    st.image("https://i.imgur.com/k1v8dhR.png", width=500) # Usei a imagem de exemplo do seu código original

with c3:
    # As configurações ficam em um expander para não poluir a interface
    with st.expander("⚙️ Configurações Essenciais"):
        gemini_api_key = st.text_input("🔑 Chave da API do Gemini", type="password", label_visibility="collapsed", placeholder="Insira a Chave da API do Gemini")


# --- 4. ESTRUTURA PRINCIPAL COM ABAS ---
# Verificação da API Key antes de carregar as abas
if not gemini_api_key:
    st.warning("👈 Por favor, insira sua chave da API do Gemini nas 'Configurações Essenciais' no canto superior direito para começar.")
    st.stop()

# Configuração do GenAI (após verificar a existência da chave)
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    st.error(f"❌ Erro ao configurar a API do Gemini: Verifique se a chave é válida.")
    st.stop()


# Cria as duas abas principais para navegação
tab1, tab2 = st.tabs(["**🤖 Chatbot de Cibersegurança**", "**🎣 Simulador de Phishing**"])

# --- ABA 1: CHATBOT DE CIBERSEGURANÇA ---
with tab1:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Converse com nosso especialista em segurança")
    st.markdown("Tire suas dúvidas sobre malwares, phishing, firewalls, proteção de dados e muito mais.")
    st.markdown("---")

    model = genai.GenerativeModel('gemini-2.0-flash') # Modelo atualizado para performance

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat = model.start_chat(history=st.session_state.chat_history)

    # Exibe o histórico do chat
    for message in chat.history:
        role = "Você" if message.role == "user" else "Assistente"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Input do usuário
    if prompt := st.chat_input("Digite sua dúvida aqui..."):
        with st.chat_message("Você"):
            st.markdown(prompt)
        
        with st.spinner("O assistente está digitando..."):
            try:
                response = chat.send_message(prompt)
                with st.chat_message("Assistente"):
                    st.markdown(response.text)
                # Atualiza o histórico
                st.session_state.chat_history = chat.history
            except Exception as e:
                st.error(f"Ocorreu um erro ao contatar a IA: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# --- ABA 2: SIMULADOR DE PHISHING ---
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.subheader("Crie e envie simulações de phishing para treinamento")
    st.warning("⚠️ **Uso Ético:** Envie e-mails apenas para contas que você controla ou com consentimento explícito.", icon="🚨")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        with st.form("phishing_form"):
            st.markdown("<h5>✉️ Passo 1: Detalhes do E-mail de Simulação</h5>", unsafe_allow_html=True)
            target_email = st.text_input("Destinatário (Alvo)", placeholder="email.alvo@exemplo.com")
            subject = st.text_input("Assunto do E-mail", placeholder="Aviso Urgente de Segurança da Sua Conta")
            body = st.text_area("Corpo do E-mail (HTML é suportado)", height=250,
                                placeholder="<html><body><p>Prezado(a),</p><p>Detectamos uma atividade suspeita na sua conta. Por favor, verifique sua identidade clicando <a href='http://link-falso-para-treinamento.com'>aqui</a> imediatamente.</p></body></html>")
            
            st.markdown("<h5>🔑 Passo 2: Configuração do Remetente</h5>", unsafe_allow_html=True)
            sender_email = st.text_input("Seu E-mail do Hotmail/Outlook", placeholder="seu.email.de.teste@hotmail.com")
            sender_password = st.text_input("Sua Senha de Aplicativo (16 caracteres)", type="password", help="Use uma 'Senha de Aplicativo' gerada na sua conta Microsoft, não sua senha normal.")

            submitted = st.form_submit_button("🚀 Enviar Simulação")

            if submitted:
                if not all([sender_email, sender_password, target_email, subject, body]):
                    st.error("Por favor, preencha todos os campos do formulário.")
                else:
                    try:
                        msg = EmailMessage()
                        msg.set_content(body, subtype='html')
                        msg['Subject'] = subject
                        msg['From'] = sender_email
                        msg['To'] = target_email

                        with st.spinner("Conectando ao servidor e enviando a simulação..."):
                            # Servidor SMTP para Hotmail/Outlook
                            server = smtplib.SMTP('smtp.office365.com', 587)
                            server.starttls()
                            server.login(sender_email, sender_password)
                            server.send_message(msg)
                            server.quit()
                        
                        st.success(f"E-mail de simulação enviado com sucesso para {target_email}!")
                        st.balloons()
                    except smtplib.SMTPAuthenticationError:
                        st.error("Erro de autenticação. Verifique seu e-mail e sua Senha de Aplicativo. Lembre-se que é necessário usar uma senha de aplicativo da Microsoft, não a senha comum.")
                    except Exception as e:
                        st.error(f"Ocorreu um erro inesperado ao enviar o e-mail: {e}")
    
    with col2:
        st.markdown("<h5>💡 Dicas para uma Simulação Eficaz</h5>", unsafe_allow_html=True)
        st.info(
            """
            - **Senso de Urgência:** Use frases como "Ação necessária urgente" ou "Sua conta será suspensa".
            - **Remetente Convincente:** Use um nome de remetente que pareça legítimo, como `suporte@empresa-conhecida.com`.
            - **Erros Sutis:** Inclua pequenos erros de gramática ou design que são comuns em e-mails de phishing reais.
            - **Links Suspeitos:** O texto do link (`<a>`) deve parecer confiável, mas o `href` deve apontar para um domínio de treinamento que você controla.
            """
        )

    st.markdown('</div>', unsafe_allow_html=True)