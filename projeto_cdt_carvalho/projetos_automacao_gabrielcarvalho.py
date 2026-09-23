import os
import time
import json
import threading
import flet as ft
from flet import app as ft_app
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# 1. ARQUIVOS HTML DAS PÁGINAS DO SITE
# ==========================================

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>GymFit - Sua Academia de Alta Performance</title>
    <style>
         * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #0800a2; color: #ffffff; line-height: 1.6; }
        header { background-color: #0003b3; padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #003cff; }
        .logo { font-size: 28px; font-weight: bold; color: #1e52ed; text-transform: uppercase; }
        nav a { color: #ffffff; text-decoration: none; margin-left: 20px; font-weight: 500; }
        nav a:hover, nav a.active { color: #00bbff; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background: #1e1e1e; border-radius: 8px; }
        h1 { color: #040081; text-align: center; margin-bottom: 20px; }
        .grid-aulas { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
        .aula-box { background: #121212; padding: 20px; border-radius: 8px; border: 1px solid #000b82; text-align: center; }
        .aula-box h3 { color: #090d7f; margin-bottom: 10px; }
        .btn-reservar { background: #00e5ff; color: #fff; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }
        .btn-reservar:hover { background: #0047c1; }
        #reserva-confirmada { display: none; background: #110094; color: #fff; padding: 15px; text-align: center; margin-top: 20px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="logo">GymFit</div>
        <nav>
            <a href="index.html" class="active">Início</a>
            <a href="planos.html">Planos</a>
            <a href="aulas.html">Agendar Aulas</a>
            <a href="login.html">Área do Aluno</a>
        </nav>
    </header>

    <section class="hero">
        <h1>Transforme Seu Corpo e Mente</h1>
        <p>A melhor estrutura e os melhores profissionais à sua disposição.</p>
        <a href="planos.html" class="btn-principal" id="btn-conhecer-planos">Conheça Nossos Planos</a>
    </section>

    <!-- CHATBOT FLUTUANTE INTEGRADO -->
    <div id="chatbot-container" style="position: fixed; bottom: 20px; right: 20px; width: 320px; background: #1e1e1e; border: 2px solid #ff4500; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 9999;">
        <div id="chat-header" style="background: #ff4500; color: #fff; padding: 10px 15px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
            <span>🤖 Assistente GymFit</span>
            <span id="chat-status" style="font-size: 11px; background: #28a745; padding: 2px 6px; border-radius: 4px;">Online</span>
        </div>
        <div id="chat-box" style="height: 220px; padding: 10px; overflow-y: auto; background: #141414; display: flex; flex-direction: column; gap: 8px;">
            <div class="bot-msg" style="background: #2a2a2a; color: #fff; padding: 8px 12px; border-radius: 8px; max-width: 85%; align-self: flex-start; font-size: 13px;">
                Olá! Sou o assistente virtual da GymFit. Como posso te ajudar hoje?
            </div>
        </div>
        <div style="display: flex; border-top: 1px solid #333;">
            <input type="text" id="chat-input" placeholder="Digite sua mensagem..." style="flex: 1; padding: 10px; background: #1e1e1e; border: none; color: #fff; font-size: 13px; outline: none;">
            <button id="btn-chat-enviar" style="background: #ff4500; border: none; color: #fff; padding: 10px 15px; cursor: pointer; font-weight: bold;">Enviar</button>
        </div>
    </div>

    <script>
        const chatInput = document.getElementById('chat-input');
        const btnEnviar = document.getElementById('btn-chat-enviar');
        const chatBox = document.getElementById('chat-box');

        function adicionarMensagem(texto, sender) {
            const msgDiv = document.createElement('div');
            msgDiv.style.padding = '8px 12px';
            msgDiv.style.borderRadius = '8px';
            msgDiv.style.maxWidth = '85%';
            msgDiv.style.fontSize = '13px';
            msgDiv.style.marginBottom = '5px';

            if(sender === 'user') {
                msgDiv.style.background = '#ff4500';
                msgDiv.style.color = '#fff';
                msgDiv.style.alignSelf = 'flex-end';
                msgDiv.className = 'user-msg';
            } else {
                msgDiv.style.background = '#2a2a2a';
                msgDiv.style.color = '#fff';
                msgDiv.style.alignSelf = 'flex-start';
                msgDiv.className = 'bot-msg';
            }

            msgDiv.innerText = texto;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function responderBot(msg) {
            let resposta = "Desculpe, não entendi. Você pode perguntar sobre 'horário', 'planos', 'preço' ou 'modalidades'.";
            const texto = msg.toLowerCase();

            if (texto.includes('olá') || texto.includes('oi') || texto.includes('bom dia')) {
                resposta = "Olá! Seja bem-vindo à GymFit. Em que posso ajudar?";
            } else if (texto.includes('horário') || texto.includes('funciona')) {
                resposta = "Funcionamos de segunda a sexta das 06:00 às 23:00, e sábados das 08:00 às 16:00.";
            } else if (texto.includes('plano') || texto.includes('preço') || texto.includes('valor')) {
                resposta = "Temos o Plano Mensal (R$ 99/mês) e o Plano VIP (R$ 149/mês). Veja na página de Planos!";
            } else if (texto.includes('aula') || texto.includes('agendar')) {
                resposta = "Você pode agendar aulas de Crossfit, Spinning e Pilates na aba 'Agendar Aulas'.";
            }

            setTimeout(() => {
                adicionarMensagem(resposta, 'bot');
            }, 600);
        }

        btnEnviar.addEventListener('click', () => {
            const texto = chatInput.value.trim();
            if (texto) {
                adicionarMensagem(texto, 'user');
                chatInput.value = '';
                responderBot(texto);
            }
        });

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') btnEnviar.click();
        });
    </script>

    <footer>
        <p>&copy; 2026 GymFit. Todos os direitos reservados.</p>
    </footer>
</body>
</html>
"""

PLANOS_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>GymFit - Nossos Planos</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #121212; color: #ffffff; line-height: 1.6; }
        header { background-color: #1e1e1e; padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4500; }
        .logo { font-size: 28px; font-weight: bold; color: #ff4500; text-transform: uppercase; }
        nav a { color: #ffffff; text-decoration: none; margin-left: 20px; font-weight: 500; }
        nav a:hover, nav a.active { color: #ff4500; }
        .container { padding: 50px 20px; text-align: center; }
        h1 { color: #ff4500; margin-bottom: 30px; }
        .cards { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; }
        .card { background-color: #1e1e1e; padding: 30px; border-radius: 8px; width: 300px; border: 1px solid #333; }
        .card:hover { border-color: #ff4500; transform: translateY(-5px); transition: 0.3s; }
        .preco { font-size: 32px; color: #ff4500; font-weight: bold; margin: 15px 0; }
        ul { list-style: none; margin-bottom: 20px; text-align: left; }
        ul li { margin-bottom: 8px; color: #ccc; }
        .btn-assinar { background-color: #ff4500; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; }
        .btn-assinar:hover { background-color: #e03e00; }
        .mensagem-sucesso { display: none; background: #28a745; color: #fff; padding: 15px; margin-top: 20px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="logo">GymFit</div>
        <nav>
            <a href="index.html">Início</a>
            <a href="planos.html" class="active">Planos</a>
            <a href="aulas.html">Agendar Aulas</a>
            <a href="login.html">Área do Aluno</a>
        </nav>
    </header>

    <div class="container">
        <h1>Escolha o Plano Ideal para Você</h1>
        <div class="cards">
            <div class="card" id="card-mensal">
                <h3>Plano Mensal</h3>
                <div class="preco">R$ 99/mês</div>
                <ul>
                    <li>✓ Acesso à musculação</li>
                    <li>✓ Horário livre</li>
                    <li>✓ Sem fidelidade</li>
                </ul>
                <button class="btn-assinar" id="btn-assinar-mensal" onclick="assinar('Mensal')">Assinar Mensal</button>
            </div>
            <div class="card" id="card-vip">
                <h3>Plano VIP</h3>
                <div class="preco">R$ 149/mês</div>
                <ul>
                    <li>✓ Musculação + Aulas Especiais</li>
                    <li>✓ Acesso VIP em qualquer unidade</li>
                    <li>✓ Leve 1 acompanhante por mês</li>
                </ul>
                <button class="btn-assinar" id="btn-assinar-vip" onclick="assinar('VIP')">Assinar VIP</button>
            </div>
        </div>
        <div id="status-assinatura" class="mensagem-sucesso"></div>
    </div>

    <script>
        function assinar(plano) {
            const divStatus = document.getElementById('status-assinatura');
            divStatus.style.display = 'block';
            divStatus.innerText = '✅ Plano ' + plano + ' selecionado com sucesso!';
        }
    </script>
</body>
</html>
"""

AULAS_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>GymFit - Agendamento de Aulas</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #121212; color: #ffffff; line-height: 1.6; }
        header { background-color: #1e1e1e; padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4500; }
        .logo { font-size: 28px; font-weight: bold; color: #ff4500; text-transform: uppercase; }
        nav a { color: #ffffff; text-decoration: none; margin-left: 20px; font-weight: 500; }
        nav a:hover, nav a.active { color: #ff4500; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background: #1e1e1e; border-radius: 8px; }
        h1 { color: #ff4500; text-align: center; margin-bottom: 20px; }
        .grid-aulas { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; }
        .aula-box { background: #121212; padding: 20px; border-radius: 8px; border: 1px solid #333; text-align: center; }
        .aula-box h3 { color: #ff4500; margin-bottom: 10px; }
        .btn-reservar { background: #28a745; color: #fff; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-top: 10px; }
        .btn-reservar:hover { background: #218838; }
        #reserva-confirmada { display: none; background: #ff4500; color: #fff; padding: 15px; text-align: center; margin-top: 20px; border-radius: 5px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="logo">GymFit</div>
        <nav>
            <a href="index.html">Início</a>
            <a href="planos.html">Planos</a>
            <a href="aulas.html" class="active">Agendar Aulas</a>
            <a href="login.html">Área do Aluno</a>
        </nav>
    </header>

    <div class="container">
        <h1>Grade de Aulas Coletivas</h1>
        <div class="grid-aulas">
            <div class="aula-box">
                <h3>Crossfit</h3>
                <p>🕒 Seg / Quat - 07:00</p>
                <button class="btn-reservar" id="btn-reservar-crossfit" onclick="reservar('Crossfit 07:00')">Reservar Vaga</button>
            </div>
            <div class="aula-box">
                <h3>Spinning</h3>
                <p>🕒 Ter / Quinta - 18:00</p>
                <button class="btn-reservar" id="btn-reservar-spinning" onclick="reservar('Spinning 18:00')">Reservar Vaga</button>
            </div>
            <div class="aula-box">
                <h3>Pilates</h3>
                <p>🕒 Seg / Sex - 19:30</p>
                <button class="btn-reservar" id="btn-reservar-pilates" onclick="reservar('Pilates 19:30')">Reservar Vaga</button>
            </div>
        </div>
        <div id="reserva-confirmada"></div>
    </div>

    <script>
        function reservar(aula) {
            const caixa = document.getElementById('reserva-confirmada');
            caixa.style.display = 'block';
            caixa.innerText = '🎉 Reserva realizada com sucesso para: ' + aula;
        }
    </script>
</body>
</html>
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>GymFit - Área do Aluno</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #121212; color: #ffffff; line-height: 1.6; }
        header { background-color: #1e1e1e; padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #ff4500; }
        .logo { font-size: 28px; font-weight: bold; color: #ff4500; text-transform: uppercase; }
        nav a { color: #ffffff; text-decoration: none; margin-left: 20px; font-weight: 500; }
        nav a:hover, nav a.active { color: #ff4500; }
        .form-container { max-width: 400px; margin: 60px auto; background-color: #1e1e1e; padding: 30px; border-radius: 8px; text-align: center; }
        .form-container h2 { margin-bottom: 20px; color: #ff4500; }
        .input-group { margin-bottom: 15px; text-align: left; }
        .input-group label { display: block; margin-bottom: 5px; font-size: 14px; }
        .input-group input { width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #333; background-color: #121212; color: #fff; }
        .btn-submit { width: 100%; background-color: #ff4500; color: #fff; padding: 10px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .btn-submit:hover { background-color: #e03e00; }
        #mensagem-login { display: none; margin-top: 15px; padding: 10px; border-radius: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <div class="logo">GymFit</div>
        <nav>
            <a href="index.html">Início</a>
            <a href="planos.html">Planos</a>
            <a href="aulas.html">Agendar Aulas</a>
            <a href="login.html" class="active">Área do Aluno</a>
        </nav>
    </header>

    <div class="form-container">
        <h2>Área do Aluno</h2>
        <form id="form-login" onsubmit="realizarLogin(event)">
            <div class="input-group">
                <label for="username">Usuário ou CPF</label>
                <input type="text" id="username" name="username" placeholder="Digite seu usuário" required>
            </div>
            <div class="input-group">
                <label for="password">Senha</label>
                <input type="password" id="password" name="password" placeholder="Digite sua senha" required>
            </div>
            <button type="submit" id="btn-entrar" class="btn-submit">Entrar</button>
        </form>
        <div id="mensagem-login"></div>
    </div>

    <script>
        function realizarLogin(event) {
            event.preventDefault();
            const user = document.getElementById('username').value;
            const msg = document.getElementById('mensagem-login');
            msg.style.display = 'block';
            msg.style.background = '#28a745';
            msg.style.color = '#fff';
            msg.innerText = 'Bem-vindo(a), ' + user + '! Login autenticado com sucesso.';
        }
    </script>
</body>
</html>
"""

def criar_arquivos_site():
    caminho = os.path.dirname(os.path.abspath(__file__))
    paginas = {
        "index.html": INDEX_HTML,
        "planos.html": PLANOS_HTML,
        "aulas.html": AULAS_HTML,
        "login.html": LOGIN_HTML
    }
    for nome_arq, conteudo in paginas.items():
        with open(os.path.join(caminho, nome_arq), "w", encoding="utf-8") as f:
            f.write(conteudo)

# ==========================================
# 2. MOTOR DE AUTOMAÇÕES SELENIUM
# ==========================================

class AutomacaoGymFit:
    def __init__(self):
        self.caminho_base = os.path.dirname(os.path.abspath(__file__))

    def iniciar_driver(self):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        return driver, WebDriverWait(driver, 10)

    def automacao_login(self, usuario, senha):
        driver, wait = self.iniciar_driver()
        try:
            url = f"file:///{os.path.join(self.caminho_base, 'login.html')}"
            driver.get(url)
            
            campo_user = wait.until(EC.presence_of_element_located((By.ID, "username")))
            campo_user.send_keys(usuario)
            
            campo_pwd = driver.find_element(By.ID, "password")
            campo_pwd.send_keys(senha)
            
            btn = driver.find_element(By.ID, "btn-entrar")
            btn.click()
            time.sleep(4)
        finally:
            driver.quit()

    def automacao_assinar_plano(self, tipo_plano):
        driver, wait = self.iniciar_driver()
        try:
            url = f"file:///{os.path.join(self.caminho_base, 'planos.html')}"
            driver.get(url)
            
            btn_id = "btn-assinar-vip" if tipo_plano.lower() == "vip" else "btn-assinar-mensal"
            btn = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
            btn.click()
            time.sleep(4)
        finally:
            driver.quit()

    def automacao_agendar_aula(self, modalidade):
        driver, wait = self.iniciar_driver()
        try:
            url = f"file:///{os.path.join(self.caminho_base, 'aulas.html')}"
            driver.get(url)
            
            modalidade_lower = modalidade.lower()
            if "crossfit" in modalidade_lower:
                btn_id = "btn-reservar-crossfit"
            elif "spinning" in modalidade_lower:
                btn_id = "btn-reservar-spinning"
            else:
                btn_id = "btn-reservar-pilates"
                
            btn = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
            btn.click()
            time.sleep(4)
        finally:
            driver.quit()

    def automacao_chatbot(self, mensagem_usuario):
        driver, wait = self.iniciar_driver()
        try:
            url = f"file:///{os.path.join(self.caminho_base, 'index.html')}"
            driver.get(url)
            
            input_chat = wait.until(EC.presence_of_element_located((By.ID, "chat-input")))
            input_chat.send_keys(mensagem_usuario)
            
            btn_enviar = driver.find_element(By.ID, "btn-chat-enviar")
            btn_enviar.click()
            time.sleep(4)
        finally:
            driver.quit()

# ==========================================
# 3. INTERFACE GRÁFICA FLET COMPLETA
# ==========================================

def rodar_em_thread(funcao, *args):
    t = threading.Thread(target=funcao, args=args)
    t.daemon = True
    t.start()

def main(page: ft.Page):
    criar_arquivos_site()
    bot_engine = AutomacaoGymFit()

    page.title = "Painel de Controle GymFit - Automações"
    page.window_width = 480
    page.window_height = 580
    page.bgcolor = "#121212"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20

    header_title = ft.Text(
        "⚙️ Automações GymFit", 
        size=22, 
        weight=ft.FontWeight.BOLD, 
        color="#ff4500"
    )

    # --- ABA 1: LOGIN ---
    ent_user = ft.TextField(label="Usuário", value="aluno_testador", border_color="#ff4500")
    ent_pass = ft.TextField(label="Senha", value="senha12345", password=True, can_reveal_password=True, border_color="#ff4500")
    btn_login = ft.ElevatedButton(
        "Testar Automação de Login", 
        bgcolor="#ff4500", 
        color="white",
        on_click=lambda e: rodar_em_thread(bot_engine.automacao_login, ent_user.value, ent_pass.value)
    )
    tab_login_content = ft.Column(
        [
            ent_user,
            ent_pass,
            ft.Container(height=10),
            btn_login
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- ABA 2: PLANOS ---
    radio_planos = ft.RadioGroup(
        value="VIP",
        content=ft.Column([
            ft.Radio(value="Mensal", label="Plano Mensal (R$ 99)"),
            ft.Radio(value="VIP", label="Plano VIP (R$ 149)")
        ])
    )
    btn_plano = ft.ElevatedButton(
        "Testar Assinatura", 
        bgcolor="#ff4500", 
        color="white",
        on_click=lambda e: rodar_em_thread(bot_engine.automacao_assinar_plano, radio_planos.value)
    )
    tab_planos_content = ft.Column(
        [
            ft.Text("Escolha o Plano para Testar:", size=16),
            radio_planos,
            ft.Container(height=10),
            btn_plano
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- ABA 3: AULAS ---
    drop_aulas = ft.Dropdown(
        label="Selecione a Aula Coletiva",
        value="Spinning",
        options=[
            ft.dropdown.Option("Crossfit"),
            ft.dropdown.Option("Spinning"),
            ft.dropdown.Option("Pilates"),
        ],
        border_color="#ff4500"
    )
    btn_aula = ft.ElevatedButton(
        "Testar Reserva de Aula", 
        bgcolor="#ff4500", 
        color="white",
        on_click=lambda e: rodar_em_thread(bot_engine.automacao_agendar_aula, drop_aulas.value)
    )
    tab_aulas_content = ft.Column(
        [
            drop_aulas,
            ft.Container(height=10),
            btn_aula
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- ABA 4: CHATBOT ---
    ent_chat = ft.TextField(label="Mensagem ao Chatbot", value="Qual o horário de funcionamento?", border_color="#ff4500")
    btn_chat = ft.ElevatedButton(
        "Testar Interação do Chatbot", 
        bgcolor="#ff4500", 
        color="white",
        on_click=lambda e: rodar_em_thread(bot_engine.automacao_chatbot, ent_chat.value)
    )
    tab_chat_content = ft.Column(
        [
            ent_chat,
            ft.Container(height=10),
            btn_chat
        ],
        spacing=15,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    conteudos = [tab_login_content, tab_planos_content, tab_aulas_content, tab_chat_content]
    conteudo_container = ft.Container(content=conteudos[0], padding=20)

    def trocar_aba(e):
        conteudo_container.content = conteudos[e.control.selected_index]
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color="#ff4500",
        label_color="#ff4500",
        unselected_label_color="white",
        on_change=trocar_aba,
        tabs=[
            ft.Tab(text="🔑 Login"),
            ft.Tab(text="💳 Planos"),
            ft.Tab(text="🏋️ Aulas"),
            ft.Tab(text="💬 Chatbot"),
        ]
    )

    page.add(
        ft.Column(
            [
                header_title,
                tabs,
                conteudo_container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )

if __name__ == "__main__":
    ft.app(target=main)

    'pull request'