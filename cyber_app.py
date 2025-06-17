import streamlit as st
import google.generativeai as genai
import smtplib
from email.message import EmailMessage

# --- Configuração da Página ---
st.set_page_config(
    page_title="Assistente de Cibersegurança",
    page_icon="🛡️",
    layout="centered"
)

# --- Título e Descrição ---
st.title("🛡️ Assistente de Cibersegurança com Gemini")
st.caption("Uma ferramenta para tirar dúvidas sobre segurança e simular phishing para fins educacionais.")

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Configurações")
    # Campo para inserir a chave da API do Gemini
    gemini_api_key = st.text_input("Chave da API do Gemini", type="password")
    
    st.markdown("---")
    
    # Seleção de modo do aplicativo
    app_mode = st.selectbox(
        "Escolha a função",
        ["Chatbot de Cibersegurança", "Simulador de Phishing"]
    )
    st.markdown("---")
    st.info("Este projeto é para fins educacionais. Use o simulador de phishing com responsabilidade.")

# --- Lógica Principal do Aplicativo ---

# Verifica se a chave da API foi inserida
if not gemini_api_key:
    st.warning("Por favor, insira sua chave da API do Gemini na barra lateral para continuar.")
    st.stop()

# Configura a API do Gemini
try:
    genai.configure(api_key=gemini_api_key)
except Exception as e:
    st.error(f"Erro ao configurar a API do Gemini: {e}")
    st.stop()

# --- MODO 1: CHATBOT DE CIBERSEGURANÇA ---
if app_mode == "Chatbot de Cibersegurança":
    st.header("🤖 Fale com o Especialista Virtual")

    # --- INÍCIO DA MODIFICAÇÃO ---

    # 1. Definição da instrução de sistema para focar o chatbot.
    system_instruction = """
    Você é o 'CyberBot', um assistente virtual especialista e focado exclusivamente em cibersegurança. Sua única função é responder a perguntas e fornecer informações dentro deste domínio.

    **REGRAS ESTRITAS:**
    1.  **SEMPRE** responda apenas a perguntas relacionadas à cibersegurança. Isso inclui, mas não se limita a: malware, phishing, engenharia social, segurança de redes, firewalls, criptografia, pentesting, vulnerabilidades, gestão de identidade, segurança em nuvem, etc.
    2.  **NUNCA** responda a perguntas que estejam fora do tópico de cibersegurança. Se o usuário perguntar sobre o tempo, esportes, história, matemática, programação geral, ou qualquer outro assunto, você deve recusar educadamente.
    3.  **COMO RECUSAR:** Ao receber uma pergunta fora do tópico, responda de forma educada e direta, por exemplo: "Desculpe, fui programado para responder apenas a perguntas sobre cibersegurança. Como posso ajudar dentro desse tema?" ou "Meu escopo é limitado à cibersegurança. Você tem alguma dúvida sobre esse assunto?".
    4.  **SEJA PRECISO E OBJETIVO:** Forneça respostas claras, precisas e, quando apropriado, sugira boas práticas.
    5.  **NÃO OPINE:** Mantenha um tom profissional e informativo. Não dê opiniões pessoais.
    """

    # 2. Inicializa o modelo Gemini com a instrução de sistema e um nome de modelo válido.
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        system_instruction=system_instruction
    )

    # --- FIM DA MODIFICAÇÃO ---


    # Inicializa o histórico do chat na sessão
    # (Verifica se o modo mudou para limpar o histórico antigo)
    if "app_mode" not in st.session_state or st.session_state.app_mode != "Chatbot de Cibersegurança":
        st.session_state.chat_history = []
        st.session_state.app_mode = "Chatbot de Cibersegurança"
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Inicia o chat com o histórico
    chat = model.start_chat(history=st.session_state.chat_history)

    # Exibe as mensagens do histórico
    for message in chat.history:
        role = "Você" if message.role == "user" else "Assistente"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Campo de entrada para a pergunta do usuário
    if prompt := st.chat_input("Digite sua dúvida sobre cibersegurança..."):
        # Adiciona a mensagem do usuário ao chat visual
        with st.chat_message("Você"):
            st.markdown(prompt)

        # Envia a mensagem para o Gemini e obtém a resposta
        with st.spinner("Pensando..."):
            try:
                response = chat.send_message(prompt)
                # Adiciona a resposta do assistente ao chat visual
                with st.chat_message("Assistente"):
                    st.markdown(response.text)
                # Atualiza o histórico da sessão
                st.session_state.chat_history = chat.history
                st.rerun() # Adicionado para atualizar o histórico visual imediatamente
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")

# --- MODO 2: SIMULADOR DE PHISHING ---
# (Nenhuma alteração nesta seção)
elif app_mode == "Simulador de Phishing":
    st.header("🎣 Simulador de E-mail de Phishing")
    st.warning(
        "**Atenção:** Use esta ferramenta de forma ética e apenas com consentimento explícito. "
        "O objetivo é educar e conscientizar sobre os riscos de phishing.",
        icon="⚠️"
    )

    with st.form("phishing_form"):
        st.subheader("Configuração do E-mail do Remetente (Teste)")
        sender_email = st.text_input("Seu E-mail de Teste (Ex: Gmail)")
        # Use a senha de app aqui se estiver usando Gmail
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
                    # Cria a mensagem de e-mail
                    msg = EmailMessage()
                    msg.set_content(body, subtype='html')
                    msg['Subject'] = subject
                    msg['From'] = sender_email
                    msg['To'] = target_email

                    # Conecta ao servidor SMTP do Gmail e envia o e-mail
                    with st.spinner("Enviando e-mail..."):
                        # Usando o servidor SMTP do Gmail como exemplo
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(sender_email, sender_password)
                            smtp.send_message(msg)
                    
                    st.success(f"E-mail de simulação enviado com sucesso para {target_email}!")
                    st.balloons()

                except smtplib.SMTPAuthenticationError:
                    st.error("Erro de autenticação. Verifique seu e-mail e senha de app.")
                except Exception as e:
                    st.error(f"Ocorreu um erro ao enviar o e-mail: {e}")