import smtplib
import ssl

# --- PREENCHA COM SEUS DADOS AQUI ---
# Coloque seu e-mail de teste.
seu_email = "rafafrd9@gmail.com"
# Coloque a senha de app de 16 caracteres, sem espaços.
senha_app = "ywjekonqpbcipigb"
# ------------------------------------

# Detalhes do servidor do Gmail
smtp_server = "smtp.gmail.com"
port = 465  # Para SSL

print("--- INICIANDO TESTE ---")
print(f"Tentando conectar ao servidor {smtp_server} na porta {port}...")

# Cria um contexto SSL seguro
context = ssl.create_default_context()

try:
    # Usando 'with' para garantir que a conexão seja fechada
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        print("Conexão bem-sucedida!")
        print("Tentando fazer login...")

        # O comando de login
        server.login(seu_email, senha_app)

        print(">>> SUCESSO! Login realizado com êxito! <<<")
        print("Isso confirma que sua conta, sua senha e sua rede estão funcionando.")

except smtplib.SMTPAuthenticationError:
    print(">>> FALHA! Erro de autenticação. <<<")
    print("O servidor do Google rejeitou a combinação de e-mail/senha.")
    print("Isso ainda aponta para um problema com a Senha de App ou as configurações de segurança da conta.")

except Exception as e:
    print(f">>> FALHA! Ocorreu um erro inesperado: {e} <<<")

print("--- TESTE CONCLUÍDO ---")