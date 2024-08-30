import os
import random
import time
import webbrowser
import tkinter as tk
from threading import Thread
from datetime import datetime
from datetime import timedelta
import requests
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai


class JarvisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis")
        self.root.geometry("200x190")
        # Definindo as cores
        bg_color = "#006400"
        fg_color = "#000000"
        self.root.configure(bg=bg_color)

        self.label = tk.Label(
            root, text="Assistente de Voz - J.A.R.V.I.S.", bg=bg_color, fg=fg_color
        )
        self.label.pack(pady=10)

        # Criar o círculo brilhante neon
        self.canvas = tk.Canvas(root, width=100, height=100, bg=bg_color, highlightthickness=0)
        self.circle = self.canvas.create_oval(30, 30, 70, 70, outline="black", width=5)
        self.canvas.pack()

        self.btn_iniciar = tk.Button(
            root,
            text="Iniciar Assistente",
            command=self.iniciar_assistente,
            bg=fg_color,
            fg=bg_color,
        )
        self.btn_iniciar.pack(pady=5)

        self.thread = None
        self.running = False
        self.listening = False
        self.speaking = False

    def iniciar_assistente(self):
        if not self.running:
            self.thread = Thread(target=self.executar_assistente)
            self.thread.start()
            self.running = True
            self.label.config(text="Assistente Executando...")

    def executar_assistente(self):
        # Inicializar o engine de síntese de fala
        engine = pyttsx3.init()

        # Faz o computador falar
        def falar(texto):
            mudar_cor_circulo("#00FF00")
            self.speaking = True
            engine.say(texto)
            engine.runAndWait()
            self.speaking = False
            mudar_cor_circulo("#00FFFF")

        # Muda a cor do círculo
        def mudar_cor_circulo(cor):
            self.canvas.itemconfig(self.circle, outline=cor)

        def animar_circulo():
            if self.speaking:
                for i in range(5, 18, 5):
                    if not self.speaking:
                        break
                    self.canvas.coords(self.circle, 20 - i, 20 - i, 80 + i, 80 + i)
                    self.canvas.update()
                    time.sleep(0.05)
                for i in range(17, 4, -5):
                    if not self.speaking:
                        break
                    self.canvas.coords(self.circle, 20 - i, 20 - i, 80 + i, 80 + i)
                    self.canvas.update()
                    time.sleep(0.05)
            self.root.after(47, animar_circulo)

        def apresentacao():
            # Obtendo a hora atual
            hora_atual = datetime.now().hour
            animar_circulo()
            if 0 <= hora_atual < 12:
                saudacao = "Um ótimo dia"
            elif 12 <= hora_atual < 18:
                saudacao = "Boa tarde"
            else:
                saudacao = "Boa noite"
            falar(
                f"{saudacao} senhor Carlos. Hoje é {datetime.now().strftime("%d/%m/%Y")}, são {datetime.now().strftime("%H:%M")}, {obter_temperatura('São Paulo')}. Me chamo Jarvis."
            )
            self.label.config(text="Se precisar de mim, diga meu nome....")
            falar("Se precisar de mim, diga meu nome.")

        # Função para ouvir e reconhecer fala:
        def ouvir_microfone(primeira_vez):
            # Habilita microfone usuário
            microfone = sr.Recognizer()

            # Apresentação apenas na primeira vez
            if primeira_vez:
                apresentacao()
                primeira_vez = False

            while self.running:
                with sr.Microphone() as source:
                    # Chama um algoritmo de redução de ruídos no som
                    microfone.adjust_for_ambient_noise(source)

                    # Armazena o que foi dito numa variável
                    print("Esperando pelo comando 'Jarvis'...")
                    self.label.config(text="Esperando pelo comando 'Jarvis'...")
                    audio = microfone.listen(source)

                    try:
                        # Passa a variável para o algoritmo reconhecer os padrões
                        frase = microfone.recognize_google(audio, language="pt-BR")
                        print(f"Comando reconhecido: {frase}")

                        # Lista de respostas possíveis
                        respostas = [
                            "Como posso te ajudar?",
                            "Sim senhor Carlos?",
                            "Às suas ordens senhor?",
                            "Pois não senhor?",
                            "Estou aqui senhor?",
                            "O que posso fazer pelo senhor?",
                            "Pronto senhor?",
                        ]
                        # Verifica se a palavra "Jarvis" foi dita
                        if "Jarvis" in frase:
                            # Seleciona uma resposta aleatoriamente da lista
                            resposta = random.choice(respostas)
                            self.label.config(text=resposta)
                            falar(resposta)

                            # Escuta o próximo comando
                            with sr.Microphone() as source:
                                audio = microfone.listen(source)

                            try:
                                # Passa a variável para o algoritmo reconhecer os padrões
                                comando = microfone.recognize_google(audio, language="pt-BR")

                                if "pesquisar" in comando:
                                    pesquisa = comando.split("pesquisar", 1)[1].strip()
                                    if pesquisa:
                                        self.label.config(text="Um momento, estou pesquisando.")
                                        falar("Um momento, estou pesquisando.")
                                        resposta = pesquisar_no_google(pesquisa)
                                        falar(resposta)
                                    else:
                                        self.label.config(text="Sobre o que deseja saber?")
                                        falar("Sobre o que deseja saber?")
                                        with sr.Microphone() as source:
                                            audio = microfone.listen(source)
                                        try:
                                            pesquisa = microfone.recognize_google(audio, language="pt-BR")
                                            self.label.config(text="Só um momento, estou pesquisando.")
                                            falar("Só um momento, estou pesquisando.")
                                            resposta = pesquisar_no_google(pesquisa)
                                            falar(resposta)
                                        except sr.UnknownValueError:
                                            self.label.config(text="Não consegui entender a pesquisa.")
                                            falar("Não consegui entender a pesquisa.")
                                elif "iniciar modo conversa" in comando:
                                    falar("Sobre o que deseja conversar senhor?")
                                    modo_conversa_ativo = True
                                    self.label.config(text="Modo Conversa Ativo")
                                    while modo_conversa_ativo:
                                        with sr.Microphone() as source:
                                            audio = microfone.listen(source)
                                        try:
                                            pesquisa = microfone.recognize_google(audio, language="pt-BR")
                                            if "encerrar modo conversa" in pesquisa.lower():
                                                modo_conversa_ativo = False
                                                falar("Encerrando modo conversa.")
                                            else:
                                                resposta = pesquisar_no_google(pesquisa + "no final, sempre faça uma pergunta para manter uma conversa")
                                                falar(resposta)
                                        except sr.UnknownValueError:
                                            falar("Não entendi o que disse")
                                elif "Abrir youtube" in comando:
                                    reproduzir_musica(microfone)
                                elif "Qual a temperatura em" in comando:
                                    cidade = comando.split("Qual a temperatura em", 1)[1].strip()
                                    clima = obter_temperatura(cidade)
                                    falar(clima)
                                    print(clima)
                                elif "previsão do tempo em" in comando:
                                    cidade = (comando.split("previsão do tempo em", 1)[1].strip() if "em" in comando else None)
                                    if not cidade:
                                        falar("Por favor, diga o nome da cidade.")
                                        with sr.Microphone() as source:
                                            audio = microfone.listen(source)
                                            try:
                                                cidade = microfone.recognize_google(audio, language="pt-BR")
                                            except sr.UnknownValueError:
                                                falar("Não consegui entender o nome da cidade.")
                                                cidade = None
                                    if cidade:
                                        previsao = obter_previsao(cidade)
                                        falar(previsao)
                                        print(previsao)
                                    else:
                                        falar("Não foi possível obter a cidade para a previsão do tempo.")
                                elif "Abrir navegador" in comando:
                                    os.system("start chrome.exe")
                                    falar("Abrindo o navegador")
                                elif "Abrir calculadora" in comando:
                                    os.system("start calc.exe")
                                    falar("Abrindo a calculadora")
                                elif "Abrir Paint" in comando:
                                    os.system("start mspaint.exe")
                                    falar("Abrindo o Paint")
                                elif "Abrir bloco de notas" in comando:
                                    os.system("start notepad.exe")
                                    falar("Abrindo o bloco de notas")
                                elif "Abrir Excel" in comando:
                                    os.system("start Excel.exe")
                                    falar("Abrindo o Excel")
                                elif "Abrir Word" in comando:
                                    os.system("start winword.exe")
                                    falar("Abrindo o Word")
                                elif "Abrir CMD" in comando:
                                    os.system("start cmd.exe")
                                    falar("Abrindo o prompt de comando")
                                    self.parar_assistente()
                                elif "Concertar internet" in comando:
                                    falar("Iniciando o solucionador de problemas de rede")
                                    os.system("msdt.exe /id NetworkDiagnosticsNetworkAdapter")
                                elif "Abrir vs code" in comando:
                                    os.system("code")
                                    falar("Abrindo o Visual Studio Code")
                                elif "Que horas são" in comando:
                                    hora_atual = datetime.now().strftime("%H:%M")
                                    falar(f"Agora são {hora_atual}.")
                                elif "Que dia é hoje" in comando:
                                    data_atual = datetime.now().strftime("%d/%m/%Y")
                                    falar(f"Hoje é {data_atual}.")
                                elif "transcrever" in comando:
                                    falar("Qual mensagem você gostaria de salvar?")
                                    with sr.Microphone() as source:
                                        audio = microfone.listen(source)
                                    try:
                                        mensagem = microfone.recognize_google(audio, language="pt-BR")
                                        caminho_arquivo = (r"C:\Users\CARLOS GARCIA\Desktop\mensagens_jarvis.txt")
                                        with open(caminho_arquivo, "a") as arquivo:
                                            arquivo.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - {mensagem}\n")
                                        falar("Mensagem salva com sucesso.")
                                    except sr.UnknownValueError:
                                        falar("Não consegui entender a mensagem. Tente novamente.")
                                elif "desligar sistema" in comando:
                                    falar("Finalizando o sistema. Até logo.")
                                    self.running = False
                                    self.label.config(text="Assistente Desligado.")
                                else:
                                    falar(f"Infelizmente não entendi o comando senhor {comando}.")
                            except sr.UnknownValueError:
                                self.label.config(text="Perdão, não entendi o senhor disse.")
                                falar("Perdão, não entendi o que o sernho disse.")
                    except sr.UnknownValueError:
                        pass
            return False

        def obter_temperatura(cidade):
            api_key = "SUA_CHAVE_API"
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            complete_url = base_url + "appid=" + api_key + "&q=" + cidade

            response = requests.get(complete_url)

            if response.status_code == 200:
                data = response.json()
                main = data["main"]
                temperature = round(main["temp"] - 273.15, 2)
                return f"A temperatura em {cidade} neste mometo é de {temperature} graus celsius."
            else:
                return "Cidade não encontrada."

        def obter_previsao(cidade):
            chave_api = "SUA_CHAVE_API"
            url_base = "http://api.openweathermap.org/data/2.5/forecast?"
            url_completa = url_base + "appid=" + chave_api + "&q=" + cidade

            resposta = requests.get(url_completa)

            if resposta.status_code == 200:
                dados = resposta.json()
                # Previsão para amanhã
                amanha = (datetime.now() + timedelta(days=1)).date()
                previsao = [
                    item
                    for item in dados["list"]
                    if datetime.fromtimestamp(item["dt"]).date() == amanha
                ]
                temp = round(previsao[0]["main"]["temp"] - 273.15, 2)
                descricao = previsao[0]["weather"][0]["description"]
                previsao_texto = f"A previsão para amanhã em {cidade} é de {descricao} com temperatura de {temp} graus Celsius."
                return previsao_texto
            else:
                return "Cidade não encontrada."

        # Função para reproduzir música do YouTube
        def reproduzir_musica(microfone):
            # Solicita ao usuário o nome da música
            falar("Qual música você deseja ouvir?")
            with sr.Microphone() as source:
                audio = microfone.listen(source)
            try:
                musica = microfone.recognize_google(audio, language="pt-BR")
                # Se não foi especificado o nome da música, solicita novamente
                if not musica:
                    falar("Por favor, diga o nome da música.")
                    with sr.Microphone() as source:
                        audio = microfone.listen(source)
                    musica = microfone.recognize_google(audio, language="pt-BR")
                # Formata a música para a busca no YouTube
                musica_formatada = musica.replace(" ", "+")
                # URL de pesquisa do YouTube com a música
                url_youtube = f"https://www.youtube.com/results?search_query={musica_formatada}"
                # Abre o navegador e redireciona para o youtube
                webbrowser.open(url_youtube)
            except sr.UnknownValueError:
                falar("Desculpe, não consegui entender. Por favor, repita.")

        # Função para pesquisar no Google usando a API
        def pesquisar_no_google(pesquisa):
            regras = """
                > Responda como J.A.R.V.I.S., assistente do Homem de Ferro.
                > Respostas objetivas, diretas e informativas.
                > Limite as respostas a no máximo 20 palavras.
                > Mantenha o tom inteligente e levemente sarcástico.
            """
            # Configurando a API do Google
            google_api_key = "SUA_CHAVE_API"
            genai.configure(api_key=google_api_key)
            # Configurando a Temperatura das Respostas
            configurar_geracao = {
                "candidate_count": 1,
                "temperature": 0.9,
            }
            # Configurando os níveis de segurança das respostas (Ofensivas, Raciais, Sexuais, perigosas)
            configurar_seguranca = {
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE",
            }
            # Definindo o Modelo Usado para Pesquisa
            model = genai.GenerativeModel(
                model_name="gemini-1.0-pro",
                generation_config=configurar_geracao,
                safety_settings=configurar_seguranca,
            )
            # Configurando o Histórico de Pesquisa
            chat = model.start_chat(history=[])
            response = chat.send_message(regras + pesquisa)
            return response.text

        # Loop do Assistente Jarvis
        primeira_vez = True
        while self.running:
            if ouvir_microfone(primeira_vez):
                break
            primeira_vez = False


# Criar a Interface Gráfica
root = tk.Tk()
app = JarvisApp(root)
root.mainloop()
