import os
import customtkinter as ctk
import time
from tkinter import messagebox
from api_backend.database import Database
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import threading
import undetected_chromedriver as uc
from tkinter import filedialog
import string
import datetime
import re
import json
import uuid
from selenium_stealth import stealth
import faker as fk
import unicodedata
import random
import requests
from urllib.parse import urlparse

# Configurações da aparência
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class LoginApp(ctk.CTk):
    """Aplicação Principal de Login."""
    def __init__(self, db):
        super().__init__()
        self.db = db
        try:
            ping_resp = requests.get("https://moneymaker-g0pn.onrender.com/ping", timeout=5)
        except requests.exceptions.Timeout:
            # Timeout ocorreu, continuar normalmente
            pass
        except requests.exceptions.RequestException:
            # Outros erros de conexão, continuar normalmente também
            pass
        self.title("MONEY MAKER")
        self.geometry("400x350")

        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(pady=20, padx=40, fill="both", expand=True)

        label = ctk.CTkLabel(main_frame, text="Login", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20, padx=10)

        self.user_entry = ctk.CTkEntry(main_frame, placeholder_text="Usuário", width=200)
        self.user_entry.pack(pady=12, padx=10)

        self.pass_entry = ctk.CTkEntry(main_frame, placeholder_text="Senha", show="*", width=200, )
        self.pass_entry.pack(pady=12, padx=10)
        
        self.pass_entry.bind("<Return>", lambda event: self.login_user())

        login_button = ctk.CTkButton(main_frame, text="Entrar", command=self.login_user, width=200)
        login_button.pack(pady=12, padx=10)
        
        Disclaimer = ctk.CTkLabel(main_frame, text="O Arquivo de configuração de conta é de responsabilidade do usuário", font=ctk.CTkFont(size=9))
        Disclaimer.pack(pady=12, padx=10)

    def login_user(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        try:
            # Altere para sua URL real do Render
            resp = requests.post("https://moneymaker-g0pn.onrender.com/login", json={"username": username, "password": password}, timeout=10)
            if resp.status_code == 200:
                self.withdraw()
                self.open_main_app_window(username)
            else:
                messagebox.showerror("Falha no Login", "Usuário ou senha inválidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao conectar com o servidor:\n{e}")
    

    def open_main_app_window(self, username):
        CAMINHO_ARQUIVO_USUARIO = f"{username}.txt"
        CAMINHO_CONTAS_JSON = f"Contas{username}.json"
        desabilitarEnvelopes = False
        proxyAtivada = False
        driversAtivos = []
# Função para carregar ou criar o arquivo de nome de usuário
        def carregar_usuario(username):
            if os.path.exists(CAMINHO_ARQUIVO_USUARIO):
                with open(CAMINHO_ARQUIVO_USUARIO, 'r') as f:
                    if f:
                        return f
            with open(CAMINHO_ARQUIVO_USUARIO, 'w') as f:
                f.write("### LISTA DE PROXIES SALVAS ### \n")
                f.write("### LISTA DE CHAVES PIX SALVAS ### \n")
                
            return username
        carregar_usuario(username)
        main_app_win = ctk.CTkToplevel(self)
        main_app_win.title("MONEY MAKER - Aplicação Principal")
        main_app_win.geometry("1200x600")
        
        # Função para fechar a aplicação inteira ao fechar a janela principal
        def on_closing():
            self.destroy()
        
        
        
        
        
        
        main_app_win.protocol("WM_DELETE_WINDOW", on_closing)
        
        #region FRAME TOP
        #frameTop = ctk.CTkFrame(main_app_win)
        #frameTop.grid(row = 0, column = 0, padx = 10, pady = 10,sticky="nsew")
        #frameTop.grid_rowconfigure(0, weight=1)
        #frameTop.grid_columnconfigure(0, weight=0)
        #endregion
        
        #region FRAME GERAL
        frameGeral = ctk.CTkFrame(main_app_win)
        frameGeral.grid(row = 1, column = 1, padx = 10, pady = 10,sticky="nsew")
        frameGeral.grid_rowconfigure(1, weight=1)
        frameGeral.grid_columnconfigure(1, weight=1)
        #endregion
        
        #region FRAME LATERAL
        frameLateral = ctk.CTkFrame(main_app_win, width= 100)
        frameLateral.grid(row=1, column=0, pady=10, sticky="nEWs")
        frameLateral.grid_columnconfigure(0, weight=1)
        frameLateral.grid_rowconfigure(1, weight=0)
        #endregion
        
        #region FRAME CRIAR CONTA
        frameCriarConta = ctk.CTkFrame(frameGeral)
        frameCriarConta.grid(row = 0, column = 0, padx = 10, pady = 10,sticky="nE")
        frameCriarConta.grid_columnconfigure(0, weight=0)
        frameCriarConta.grid_rowconfigure(0, weight=0)
        #endregion
        
        main_app_win.grid_columnconfigure(0, weight=0)  # lateral com peso 0 (fixo)
        main_app_win.grid_columnconfigure(1, weight=1)  # geral com peso 1 (flexível)
        main_app_win.grid_rowconfigure(1, weight=1)
        
        def remover_de_txt(caminho_arquivo, tipo, dado_para_remover):
            # Leitura do conteúdo do arquivo
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
            except FileNotFoundError:
                print("Arquivo não encontrado.")
                return

            # Define qual seção procurar
            if tipo.lower() == "proxy":
                cabecalho = "### LISTA DE PROXIES SALVAS ###\n"
            elif tipo.lower() == "pix":
                cabecalho = "### LISTA DE CHAVES PIX SALVAS ###\n"
            else:
                raise ValueError("Tipo deve ser 'proxy' ou 'pix'")

            try:
                indice = linhas.index(cabecalho)
            except ValueError:
                print("Cabeçalho não encontrado no arquivo.")
                return

            # Encontra o fim da seção
            fim_secao = len(linhas)
            for i in range(indice + 1, len(linhas)):
                if linhas[i].startswith("###"):
                    fim_secao = i
                    break

            # Se o dado a remover for exatamente o tipo, remove toda a seção
            if dado_para_remover.lower() == tipo.lower():
                del linhas[indice:fim_secao]
            else:
                # Remove todas as ocorrências da linha que começa com o dado informado
                novas_linhas = []
                dado_encontrado = False
                for i in range(indice + 1, fim_secao):
                    if linhas[i].strip().startswith(dado_para_remover):
                        dado_encontrado = True
                        continue  # pula essa linha
                    novas_linhas.append(linhas[i])

                if not dado_encontrado:
                    return

                # Substitui a parte da seção pelas novas linhas filtradas
                linhas[indice + 1:fim_secao] = novas_linhas

            # Reescreve o arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.writelines(linhas)

    
        def inserir_em_txt(caminho_arquivo, tipo, novo_dado):
            # Leitura do conteúdo do arquivo
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
            except FileNotFoundError:
                linhas = []

            # Define o cabeçalho da seção com base no tipo
            if tipo.lower() == "proxy":
                cabecalho = "### LISTA DE PROXIES SALVAS ###\n"
            elif tipo.lower() == "pix":
                cabecalho = "### LISTA DE CHAVES PIX SALVAS ###\n"
            else:
                raise ValueError("Tipo deve ser 'proxy' ou 'pix'")

            # Garante que o cabeçalho exista
            if cabecalho not in linhas:
                if not linhas or not linhas[-1].endswith("\n"):
                    linhas.append("\n")
                linhas.append(cabecalho)

            # Verifica duplicata
            if f"{novo_dado}\n" in linhas:
                return

            try:
                indice = linhas.index(cabecalho)
            except ValueError:
                print("Cabeçalho não encontrado no arquivo.")
                return

            # Encontra o fim da seção atual
            fim_secao = len(linhas)
            for i in range(indice + 1, len(linhas)):
                if linhas[i].startswith("###"):
                    fim_secao = i
                    break

            # Insere o novo dado antes do próximo cabeçalho ou do fim
            linhas.insert(fim_secao, f"{novo_dado}\n")

            # Salva de volta no arquivo
            with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                f.writelines(linhas)      
  
        def inserir_em_json(caminho_arquivo, novo_dado):
            # Cria o arquivo se não existir
            if not os.path.exists(caminho_arquivo):
                with open(caminho_arquivo, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)

            # Carrega os dados existentes
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            # Evita duplicatas com base no Username (para contas)
            if isinstance(novo_dado, dict) and "Username" in novo_dado:
                if any(conta["Username"] == novo_dado["Username"] for conta in dados):
                    return

            dados.append(novo_dado)

            # Salva de volta
            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)  
  
        def remover_de_json(caminho_arquivo, campo, valor):
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            novos_dados = [item for item in dados if item.get(campo) != valor]

            with open(caminho_arquivo, "w", encoding="utf-8") as f:
                json.dump(novos_dados, f, ensure_ascii=False, indent=2)  
  
        def carregar_inicio():
            for widget in frameGeral.winfo_children():
                widget.destroy()

            # Frame principal
            frameCriarConta = ctk.CTkFrame(frameGeral)
            frameCriarConta.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            frameCriarConta.grid_columnconfigure((0, 1, 2), weight=1)
            
            entradas_digitos = []
            
            modo_var = ctk.StringVar(value="Modo Mobile (Android, iOS)")

            modo_dropdown = ctk.CTkOptionMenu(
                frameCriarConta,  # substitua pelo frame onde você está colocando os elementos
                values=[
                    "Modo Computador",
                    "Modo  Mobile (Android, iOS)",
                    "Modo App"
                ],
                variable=modo_var,
                width=250,  # ajuste o tamanho se necessário
                height=35,  # pode deixar mais alto para parecer botão
                corner_radius=5
            )
            modo_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            
            chrome_undetect = ctk.CTkLabel(frameCriarConta, text="Configurações de navegação")
            chrome_undetect.grid(row=0, column=0, padx=5, pady=5, sticky="ew", columnspan=10)

            # Linha 2 - Adicionar extensão e senhas
            add_ext = ctk.CTkButton(frameCriarConta, text="Adicionar Extensão")
            add_ext.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

            senhas_salvas = {
                "cadastro": "",
                "saques": []}       

            def abrir_tela_senhas():
                janela_senhas = ctk.CTkToplevel()
                janela_senhas.title("Digite suas senhas")
                janela_senhas.geometry("400x300")
                janela_senhas.grab_set()

                entradas_digitos = []

                label_info = ctk.CTkLabel(janela_senhas, text="deixe o campo desejado em branco para senha aleatória", text_color="#6060ff")
                label_info.pack(pady=(10, 5))

                label_cadastro = ctk.CTkLabel(janela_senhas, text="Senha de cadastro:")
                label_cadastro.pack(anchor="w", padx=20)
                entrada_cadastro = ctk.CTkEntry(janela_senhas, show="*")
                entrada_cadastro.pack(padx=20, pady=(0, 5), fill="x")

                help_cadastro = ctk.CTkLabel(janela_senhas, text="6-16 caracteres, inclua letras/números/símbolos", text_color="gray", font=ctk.CTkFont(size=10))
                help_cadastro.pack(anchor="w", padx=20, pady=(0, 10))

                label_saques = ctk.CTkLabel(janela_senhas, text="Senha de saques:")
                label_saques.pack(anchor="w", padx=20)

                frame_digitos = ctk.CTkFrame(janela_senhas, fg_color="transparent")
                frame_digitos.pack(pady=5)

                def limitar_e_avancar(event, idx):
                    entry = entradas_digitos[idx]
                    texto = entry.get()

                    # Permitir apenas um dígito numérico
                    if not texto.isdigit() or len(texto) > 1:
                        entry.delete(0, ctk.END)
                        if texto and texto[0].isdigit():
                            entry.insert(0, texto[0])
                    elif len(texto) == 1 and idx < len(entradas_digitos) - 1:
                        entradas_digitos[idx + 1].focus()

                for i in range(6):
                    entrada = ctk.CTkEntry(frame_digitos, width=30, justify="center")
                    entrada.pack(side="left", padx=2)
                    entrada.bind("<KeyRelease>", lambda e, idx=i: limitar_e_avancar(e, idx))
                    entradas_digitos.append(entrada)

                help_saques = ctk.CTkLabel(janela_senhas, text="não pode ser 6 números sequenciais ou iguais", text_color="gray", font=ctk.CTkFont(size=10))
                help_saques.pack(anchor="w", padx=20)

                def confirmar_senhas():
                    senha_cadastro = entrada_cadastro.get().strip()
                    senha_saques = []

                    for entrada in entradas_digitos:
                        valor = entrada.get()
                        if valor.isdigit():
                            senha_saques.append(int(valor))

                    # Salvar nas variáveis globais
                    senhas_salvas["cadastro"] = senha_cadastro
                    senhas_salvas["saques"] = senha_saques

                    print("Senha de cadastro:", senhas_salvas["cadastro"])
                    print("Senha de saques:", senhas_salvas["saques"])  # Exemplo: [1, 2, 3, 4, 5, 6]

                    janela_senhas.destroy()

                btn_confirmar = ctk.CTkButton(janela_senhas, text="Confirmar", command=confirmar_senhas)
                btn_confirmar.pack(pady=15)

            # Botão na tela principal
            senha_btn = ctk.CTkButton(frameCriarConta, text="Senhas", command=abrir_tela_senhas)
            senha_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

            # Botão na tela principal
            senha_btn = ctk.CTkButton(frameCriarConta, text="Senhas", command=abrir_tela_senhas)
            senha_btn.grid(row=1, column=2, padx=5, pady=5, sticky="ew")



            # Linha 3 - Quantidade de contas
            qtd_label = ctk.CTkLabel(frameCriarConta, text="Quantidade de Contas:")
            qtd_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            
            qtd_entry = ctk.CTkEntry(frameCriarConta )
            qtd_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            qtd_entry.insert(0, "1")

            # Linha 4 - Valores depósito
            val_label = ctk.CTkLabel(frameCriarConta, text="Valores Para Depósito:")
            val_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
            
            val_min = ctk.CTkEntry(frameCriarConta, placeholder_text="MIN")
            val_min.grid(row=3, column=1, padx=2, pady=5, sticky="ew")
            
            val_max = ctk.CTkEntry(frameCriarConta, placeholder_text="MÁX")
            val_max.grid(row=3, column=2, padx=2, pady=5, sticky="ew")

            # Linha 5 - Funcionalidades
            funcionalidades_frame = ctk.CTkFrame(frameCriarConta)
            funcionalidades_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky="ew")

            for i, text in enumerate(["Proxy Ativado", "Múltiplos Links", "Captcha Automático", "Remover Envelopes-Bônus"]):
                chk = ctk.CTkCheckBox(funcionalidades_frame, text=text)
                chk.grid(row=0, column=i, padx=5, pady=5, sticky="w")
                if text == "Remover Envelopes-Bônus":
                    desabilitarEnvelope = True
                    chk.select()
                if text == "Proxy Ativado":
                    proxyAtivada = True
                    chk.select()
                    
            # Linha 6 - Botões de Ação
            def AbrirRelatorio():
                for driver in driversAtivos:
                    def extrair_raiz(driver):
                        url = driver.current_url
                         
                        partes = urlparse(url)
                        raiz = f"{partes.scheme}://{partes.netloc}"
                        raiz = f'{raiz}/'
                        return raiz
                    link = extrair_raiz(driver["driver"])
                    driver["driver"].get(f"{link}home/report?reportCurrent=1") 
              
            def registrarChavesPixNoSite():
                def encontrarChaves():
                    chaves_pix = []
                    lendo_chaves = False

                    with open(CAMINHO_ARQUIVO_USUARIO, 'r', encoding='utf-8') as f:
                        for linha in f:
                            linha = linha.strip()

                            # Ativa a leitura quando encontrar o cabeçalho
                            if linha == "### LISTA DE CHAVES PIX SALVAS ###":
                                lendo_chaves = True
                                continue

                            # Para de ler se encontrar outro cabeçalho ou seção
                            if lendo_chaves and linha.startswith("###"):
                                break

                            # Se estiver lendo a seção de chaves e a linha contiver um tipo:valor
                            if lendo_chaves and ':' in linha:
                                tipo, valor = linha.split(':', 1)
                                chaves_pix.append((tipo.strip().upper(), valor.strip()))

                    return chaves_pix
                chavesParaCadastrar = encontrarChaves()
                for driver in driversAtivos:
                    try:
                        def extrair_raiz(driver):
                            url = driver.current_url
                             
                            partes = urlparse(url)
                            raiz = f"{partes.scheme}://{partes.netloc}"
                            raiz = f'{raiz}/'
                            return raiz
                        link = extrair_raiz(driver["driver"])
                        driver["driver"].get(f"{link}home/mine") 
                        wait = WebDriverWait(driver["driver"], 1000, poll_frequency=0.5)
                        nomeConta = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/section/div/section/div[2]/div[1]/div[2]/div[2]/p/div/span[2]')))
                        with open(CAMINHO_CONTAS_JSON, "r", encoding="utf-8") as f:
                            contas = json.load(f)

                        # Procurar a conta com username igual ao nomeDaConta

                        conta_encontrada = next((conta for conta in contas if conta.get("Username") == nomeConta.text), None)

                        entradas_digitos = conta_encontrada.get("SenhaSaque")
                        botaoSaques = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/div/section/div[2]/div[2]/div[1]/i')))
                        botaoSaques.click()

                        botaoComecarDigitacao = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/div/div[1]/div[2]/div/div[1]/div/ul/li[1]')))
                        botaoComecarDigitacao.click()
                        time.sleep(random.uniform(0.8, 1.5))
                        teclados = driver["driver"].find_elements(By.CLASS_NAME, 'ui-number-keyboard')

                        for teclado in teclados:
                            # Verifica se o teclado está visível
                            if teclado.value_of_css_property('display') != 'none':
                                # Dentro do teclado visível, insere os dígitos
                                for digito in entradas_digitos:
                                    xpath_botao = f".//div[@role='button' and contains(@class, 'ui-number-keyboard-key') and text()='{digito}']"
                                    botao = teclado.find_element(By.XPATH, xpath_botao)
                                    botao.click()
                                break 
                        time.sleep(random.uniform(0.8, 1.5))
                        for teclado in teclados:
                            # Verifica se o teclado está visível
                            if teclado.value_of_css_property('display') != 'none':
                                # Dentro do teclado visível, insere os dígitos
                                for digito in entradas_digitos:
                                    xpath_botao = f".//div[@role='button' and contains(@class, 'ui-number-keyboard-key') and text()='{digito}']"
                                    botao = teclado.find_element(By.XPATH, xpath_botao)
                                    botao.click()
                                break 
                        confirmarButton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/div/div[2]/div/button')))
                        confirmarButton.click()
                        try:
                            elemento = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div/div/div/div[1]/div/div[2]/span/div')))
                            elemento.click()
                            confirmacao = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div[1]/div[3]/button')))
                            confirmacao.click()
                        except TimeoutException:
                            pass
                        time.sleep(random.uniform(0.8, 1.5))
                        contaParaRecebimentoButton = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-8"]/div/div/section/div/div[2]/form/div[1]/div/div/div/div')))
                        contaParaRecebimentoButton.click()
                        time.sleep(random.uniform(0.8, 1.5))
                        buttonAdd = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="addAccountClick"]')))
                        buttonAdd.click()
                        teclados2 = driver["driver"].find_elements(By.CLASS_NAME, 'ui-number-keyboard')
                        for teclado in teclados2:
                            # Verifica se o teclado está visível
                            if teclado.value_of_css_property('display') != 'none':
                                # Dentro do teclado visível, insere os dígitos
                                for digito in entradas_digitos:
                                    xpath_botao = f".//div[@role='button' and contains(@class, 'ui-number-keyboard-key') and text()='{digito}']"
                                    time.sleep(random.uniform(0.8, 1.5))
                                    botao = teclado.find_element(By.XPATH, xpath_botao)
                                    botao.click()
                                break 
                        time.sleep(random.uniform(0.8, 1.5))
                        botaoProximo = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div[1]/div[2]/form/button')))
                        botaoProximo.click()
                        time.sleep(random.uniform(0.8, 1.5))
                        campoCpf = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Insira o número de 11 dígitos do CPF']")))
                        campoCpf.click()
                        if chavesParaCadastrar:
                            for chave in chavesParaCadastrar:
                                campoCpf.send_keys(chave[1])
                                botaoFinalziarCadastro = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="bindWithdrawAccountNextClick"]')))
                                botaoFinalziarCadastro.click()
                                break             
                    except Exception as e:
                        print(f"[ERRO] Erro ao registrar no driver: {e}")
                        continue  # Continua para o próximo driver
              
              
            def paginaPrincipal():
                
                for driver in driversAtivos:
                    url = driver["driver"].current_url
                    partes = urlparse(url)
                    raiz = f"{partes.scheme}://{partes.netloc}/"
                    return raiz              
              
            def paginaPromocoes():
                
                for driver in driversAtivos:
                    url = driver["driver"].current_url
                    partes = urlparse(url)
                    raiz = f"{partes.scheme}://{partes.netloc}/"
                    linkCompleto = f"{raiz}home/event?eventCurrent=1"
                    driver["driver"].get(linkCompleto)
                    
            def coletarMissoes():
                for driver in driversAtivos:
                    url = driver["driver"].current_url
                    partes = urlparse(url)
                    raiz = f"{partes.scheme}://{partes.netloc}/home/"
                    linkCompleto = f"{raiz}task?eventCurrent=1&curTask=101"
                    driver["driver"].get(linkCompleto)
                    wait = WebDriverWait(driver["driver"], 1000)
                    botaoReceber = wait.until(EC.element_to_be_clickable((By.ID, "taskReceiveClick")))
                    botaoReceber.click()
                    BotaoLembrete = driver["driver"].find_element(By.XPATH, "//*[contains(text(), 'Lembrete importante')]")
                    if BotaoLembrete:
                        try:
                            messagebox.showinfo("Atenção", "Não é possivel receber as missoes pois ainda não foi cadastrado nenhum chave PIX na conta.")
                        except Exception as e:
                            continue  # Continua para o próximo driver
            
            def abrirDepositar():
                for driver in driversAtivos:
                    def extrair_raiz(driver):
                        url = driver.current_url
                         
                        partes = urlparse(url)
                        raiz = f"{partes.scheme}://{partes.netloc}"
                        raiz = f'{raiz}/'
                        return raiz
                    link = extrair_raiz(driver["driver"])
                    driver["driver"].get(link)
                    wait = WebDriverWait(driver["driver"], 10)
                    depositElement = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Depósito']")))  
                    depositElement.click()
                    botaoDeposito = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/div/section/div[2]/div[2]/div[2]/div/i')))
                    botaoDeposito.click()
                    if val_min.get() not in [None, ''] and val_max.get() not in [None, '']:
                        random_number = round(random.uniform(int(val_min.get()), int(val_max.get())), 2)
                        campoDeposito = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-25"]/div/form/div/div[3]/div/div/div/div[1]/div/input')))
                        campoDeposito.click()
                        campoDeposito.send_keys(random_number)
                        btnConfirmarDeposito = wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'ui-button__text') and normalize-space()='Deposite agora']"))
                        )
                        btnConfirmarDeposito.click()
                
            botoes = [
                "Preencher Dados", "Coletar Missões", "Cadastrar Pix", "Preencher Saques",
                "Página Promoções", "Depositar", "Página Inicial", "Relatório de Apostas", "Ativar touch"
            ]
            # Linha 9 - URL e play
            url_entry = ctk.CTkEntry(frameCriarConta, placeholder_text="URL")
            url_entry.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

            for i, nome in enumerate(botoes):
                btn = ctk.CTkButton(frameCriarConta, text=nome)
                btn.grid(row=5 + i // 3, column=i % 3, padx=5, pady=4, sticky="ew")
                if nome == "Relatório de Apostas":
                    btn.configure(command=lambda: threading.Thread(target=lambda: AbrirRelatorio(), daemon=True).start())
                elif nome == "Cadastrar Pix":
                    btn.configure(command=lambda: threading.Thread(target=lambda: registrarChavesPixNoSite(), daemon=True).start())
                elif nome == "Página Inicial":
                    btn.configure(command=lambda: threading.Thread(target=lambda: paginaPrincipal(), daemon=True).start())
                elif nome == "Página Promoções":
                    btn.configure(command=lambda: threading.Thread(target=lambda: paginaPromocoes(), daemon=True).start())
                elif nome == "Depositar":
                    btn.configure(command=lambda: threading.Thread(target=lambda: abrirDepositar(), daemon=True).start())
                elif nome == "Coletar Missões":
                    btn.configure(command=lambda: threading.Thread(target=lambda: coletarMissoes(), daemon=True).start())


            
            play_btn = ctk.CTkButton(frameCriarConta, text="Play", command=lambda: iniciar_thread_cadastro(int(qtd_entry.get())))
            play_btn.grid(row=8, column=2, padx=5, pady=5, sticky="ew")
            
            def iniciar_thread_cadastro(quantidade):
                i=0
                while i < quantidade:
                    thread = threading.Thread(target=abrir_google_mobile_com_uuid, args=(f'{url_entry.get()}',))
                    thread.daemon = True  # Encerra com a aplicação
                    thread.start()
                    i += 1
            def iniciar_thread_cadastrarPix():
                    threadPix = threading.Thread(target=registrarChavesPixNoSite(url_entry.get()))
                    threadPix.daemon = True  # Encerra com a aplicação
                    threadPix.start()

            # Linha 10 - Campo de texto e botões inferiores
            search_entry = ctk.CTkEntry(frameCriarConta, placeholder_text="Buscar jogo (ex: double fortune)")
            search_entry.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

            buscar_btn = ctk.CTkButton(frameCriarConta, text="Buscar")
            buscar_btn.grid(row=9, column=2, padx=5, pady=5, sticky="ew")

            atualizar_btn = ctk.CTkButton(frameCriarConta, text="Atualizar páginas")
            atualizar_btn.grid(row=10, column=0, columnspan=3, padx=5, pady=10, sticky="ew") 
            def abrir_google_mobile_com_uuid(link):
                try:
                    options = uc.ChromeOptions()
                    options.add_argument(
                        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
                    )
                    options.add_argument("--disable-blink-features=AutomationControlled")  # Ajuda a esconder automação
                    options.add_argument("--enable-unsafe-webgpu")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--window-size=375,667")  # iPhone X tamanho aproximado
                    options.add_argument("--disable-infobars")
                    UuidMobile = str(uuid.uuid4())

                    if proxyAtivada:
                        with open(CAMINHO_ARQUIVO_USUARIO, 'r', encoding='utf-8') as f:
                            linhas = f.readlines()
    
                        # Localiza proxies
                        try:
                            indice_proxies = linhas.index("### LISTA DE PROXIES SALVAS ###\n")
                        except ValueError:
                            raise ValueError("Seção de proxies não encontrada no arquivo.")
    
                        proxy_linha_valida = None
                        for linha in linhas[indice_proxies + 1:]:
                            if linha.startswith("###"):
                                break
                            if not linha.strip():
                                continue
                            partes_virgula = linha.strip().split(",")
                            partes_colon = partes_virgula[0].split(":")
                            if len(partes_colon) != 4:
                                continue
                            ip, port = partes_colon[0], partes_colon[1]
                            ip_valido = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip)
                            port_valida = port.isdigit() and 0 < int(port) <= 65535
                            if ip_valido and port_valida:
                                proxy_linha_valida = linha.strip()
                                break
                        if not proxy_linha_valida:
                            raise ValueError("Nenhum proxy válido encontrado na seção.")
    
                        partes_virgula = proxy_linha_valida.split(",")
                        partes_colon = partes_virgula[0].split(":")
                        Proxy = {
                            "host": partes_colon[0].strip(),
                            "port": partes_colon[1].strip(),
                            "login": partes_colon[2].strip(),
                            "password": partes_colon[3].strip(),
                            "type": partes_virgula[-1].strip(),
                        }
                        print(f'Proxy detectada: {Proxy["host"]}:{Proxy["port"]} com usuário {Proxy["login"]}')
    
                        proxy_options = {
                            'proxy': {
                                'http': f'http://{Proxy["login"]}:{Proxy["password"]}@{Proxy["host"]}:{Proxy["port"]}',
                                'https': f'https://{Proxy["login"]}:{Proxy["password"]}@{Proxy["host"]}:{Proxy["port"]}',
                                'no_proxy': 'localhost,127.0.0.1'
                            }
                        }

                        driver = uc.Chrome(options=options, seleniumwire_options=proxy_options)
                        if proxyAtivada and proxy_linha_valida:
                            remover_de_txt(CAMINHO_ARQUIVO_USUARIO, "proxy", proxy_linha_valida.split(":")[0])
                    else:
                        driver = uc.Chrome(options=options)
                    # Script anti-fingerprint avançado
                    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                        "source": """
                            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                            window.navigator.chrome = { runtime: {} };
                            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']});
                            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});

                            // Fake WebGL Vendor/Renderer
                            const getParameter = WebGLRenderingContext.prototype.getParameter;
                            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                                if (parameter === 37445) return 'NVIDIA Corporation'; // UNMASKED_VENDOR_WEBGL
                                if (parameter === 37446) return 'NVIDIA GeForce RTX 3060'; // UNMASKED_RENDERER_WEBGL
                                return getParameter(parameter);
                            };

                            // Fake time zone
                            Intl.DateTimeFormat = function() {
                                return {
                                    resolvedOptions: () => ({ timeZone: 'America/Sao_Paulo' })
                                };
                            };

                            // Fake screen dimensions
                            Object.defineProperty(screen, 'width', { get: () => 375 });
                            Object.defineProperty(screen, 'height', { get: () => 667 });

                            // Disable WebRTC
                            Object.defineProperty(window, 'RTCPeerConnection', { get: () => undefined });
                            Object.defineProperty(window, 'webkitRTCPeerConnection', { get: () => undefined });
                        """
                    })
                    wait = WebDriverWait(driver, 1000)
                    # Stealth para disfarçar mais ainda
                    stealth(
                        driver,
                        languages=["pt-BR", "pt", "en-US"],
                        vendor="Google Inc.",
                        platform="iPhone",
                        webgl_vendor="NVIDIA Corporation",
                        renderer="NVIDIA GeForce RTX 3060",
                        fix_hairline=True,
                    )

                    # Abertura da página com delay humano e scroll
                    driver.get(link)

                    # Scroll suave simulando leitura
                    def scroll_suave(driver, passos=8, altura_total=1000):
                        passo = altura_total // passos
                        for i in range(passos):
                            driver.execute_script(f"window.scrollBy(0, {passo});")
                            time.sleep(random.uniform(0.3, 0.8))

                    scroll_suave(driver)


                    def criarContaCadastro(link):
                        username = ""
                        senha = ""
                        cpf = ""
                        def extrair_raiz(url):
                            
                            partes = urlparse(url)
                            raiz = f"{partes.scheme}://{partes.netloc}/"
                            return raiz

                        link = extrair_raiz(link)

                        fake = fk.Faker('pt_BR')
                        nomes = fake.first_name()
                        sobrenomes = fake.last_name()
                        sobrenome2 = fake.last_name()
                        senhaSaque = senhas_salvas["saques"]
                        if not senhaSaque:
                            senhaSaque = [f'{random.randint(0, 9)}' for _ in range(6)]

                        cpf = random.randint(10000000000, 99999999999)
                        nomeReal = f"{nomes} {sobrenomes} {sobrenome2}"
                        username = f"{nomes[:8].lower()}{sobrenomes[:3].lower()}{random.randint(1, 999)}"
                        username = username.replace(" ", "")

                        def remover_acentos(texto):
                            return ''.join(
                                c for c in unicodedata.normalize('NFD', texto)
                                if unicodedata.category(c) != 'Mn'
                            )

                        username = remover_acentos(username)
                        caracteres = string.ascii_letters + string.digits + string.punctuation
                        senha = ''.join(random.choice(caracteres) for _ in range(14))
                        dataHoraCadastro = datetime.datetime.now().strftime("%d/%m/%Y - %Hh%M")

                        contaGerada = {
                            "Username": username,
                            "Senha": senha,
                            "SenhaSaque": senhaSaque,
                            "Uuid Mobile": UuidMobile,
                            "Nome": nomeReal,
                            "Casa": link,
                            "Data e Hora do Cadastro": dataHoraCadastro,
                            "Proxy": Proxy
                        }

                        return contaGerada

                    dadosParaCadastro = criarContaCadastro(link)
                    driversAtivos.append({
                        "driver": driver,
                        "username": dadosParaCadastro["Username"]
                    })

                    # Monitoramento individual por driver
                    if desabilitarEnvelope:
                        def monitorar_elemento(driver_para_monitorar):
                            wait = WebDriverWait(driver_para_monitorar, 10, poll_frequency=0.2)
                            
                            while True:
                                try:
                                    elemento = driver_para_monitorar.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[1]/div/div[2]/span')
                                    if elemento.is_displayed():
                                        print(f"[Monitor-{id(driver_para_monitorar)}] Elemento visível. Clicando...")
                                        try:
                                            elemento.click()
                                            confirmacao = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[7]/div/div[1]/div[3]/button/div')))
                                            confirmacao.click()
                                        except ElementClickInterceptedException:
                                            driver_para_monitorar.execute_script("arguments[0].click();", elemento)
                                        time.sleep(0.2)
                                except NoSuchElementException:
                                    try:
                                        botao_fechar = driver_para_monitorar.find_element(By.XPATH, "//i[contains(@class, 'ui-dialog-close-box__icon')]")
                                        
                                        lembrete_encontrado = False
                                        
                                        # Verifica "Lembrete importante"
                                        try:
                                            driver_para_monitorar.find_element(By.XPATH, "//*[contains(text(), 'Lembrete importante')]")
                                            lembrete_encontrado = True
                                            print(f"[Monitor-{id(driver_para_monitorar)}] Lembrete importante detectado, não vai fechar.")
                                        except NoSuchElementException:
                                            pass

                                        # Verifica "Inserir PIN"
                                        try:
                                            driver_para_monitorar.find_element(By.XPATH, "//*[contains(text(), 'Inserir PIN')]")
                                            lembrete_encontrado = True
                                            print(f"[Monitor-{id(driver_para_monitorar)}] Inserir PIN detectado, não vai fechar.")
                                        except NoSuchElementException:
                                            pass

                                        # Se nenhum dos dois foi encontrado, fecha
                                        if not lembrete_encontrado:
                                            if botao_fechar.is_displayed():
                                                driver_para_monitorar.execute_script("arguments[0].click();", botao_fechar)
                                                print(f"[Monitor-{id(driver_para_monitorar)}] Clicou no botão de fechar (forçado com JS).")
                                    except NoSuchElementException:
                                        try:
                                            botao_cancelar = driver_para_monitorar.find_element(By.XPATH, "//button[.//span[text()='Cancelar']]")
                                            if botao_cancelar.is_displayed():
                                                botao_cancelar.click()
                                                print(f"[Monitor-{id(driver_para_monitorar)}] Clicou em Cancelar.")
                                        except Exception:
                                            pass
                                        print(f"[Monitor-{id(driver_para_monitorar)}] Botão de fechar não encontrado no momento.")
                                    except Exception:
                                        try:
                                            botao_cancelar = driver_para_monitorar.find_element(By.XPATH, "//button[.//span[text()='Cancelar']]")
                                            if botao_cancelar.is_displayed():
                                                botao_cancelar.click()
                                                print(f"[Monitor-{id(driver_para_monitorar)}] Clicou em Cancelar.")
                                        except Exception:
                                            pass
                                except Exception as e:
                                    print(f"[Monitor-{id(driver_para_monitorar)}] Erro inesperado: {e}")
                                    break

                                time.sleep(0.2)

                        thread = threading.Thread(target=monitorar_elemento, args=(driver,), daemon=True)
                        thread.start()
                    def move_mouse_like_human(driver, element):
                        try:
                            actions = ActionChains(driver)
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                            location = element.location_once_scrolled_into_view
                            size = element.size

                            # Garantir que o elemento está visível e com tamanho válido
                            if size['width'] == 0 or size['height'] == 0:
                                print("Elemento invisível ou tamanho inválido.")
                                return

                            x = location['x'] + random.randint(3, max(size['width'] - 6, 3))
                            y = location['y'] + random.randint(3, max(size['height'] - 6, 3))

                            # Mover suavemente
                            actions.move_by_offset(x, y).perform()
                            time.sleep(random.uniform(0.4, 1.0))
                        except Exception as e:
                            print(f"[move_mouse_like_human] Erro ao mover mouse: {e}")
                        
                    def type_like_human(element, text):
                        for char in text:
                            element.send_keys(char)
                            time.sleep(random.uniform(0.07, 0.25))
                        time.sleep(random.uniform(0.5, 1.2))  # pequena pausa

                    campoUser = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-2"]/div/form/div[2]/div/div[1]/span/div/div/div[1]/div/input')))
                    type_like_human(campoUser, dadosParaCadastro["Username"])
                    

                    
                    campoSenha = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-2"]/div/form/div[4]/div/div/div/div[1]/div/input')))
                    type_like_human(campoSenha, dadosParaCadastro["Senha"])
                    
                    campoSenha2 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-2"]/div/form/div[6]/div/div[1]/div/div[1]/div/input')))
                    type_like_human(campoSenha2, dadosParaCadastro["Senha"]) 
                       
                    campoNome = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-2"]/div/form/div[7]/div/div[1]/div/div[1]/div/input')))
                    type_like_human(campoNome, dadosParaCadastro["Nome"])
                    
                    
                    time.sleep(random.uniform(0.8, 1.5))
                    botaoRegistro = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="insideRegisterSubmitClick"]')))
                    move_mouse_like_human(driver, botaoRegistro) 
                    botaoRegistro.click()
                    time.sleep(2)
                    
                    while True:
                        try:
                            element = driver.find_element(By.CLASS_NAME, "geetest_box")
                            # Checar se o elemento está visível (não tem display: none)
                            is_displayed = driver.execute_script(
                                "return window.getComputedStyle(arguments[0]).display !== 'none';",
                                element
                            )
                            if is_displayed:
                                print("CAPTCHA visível. Aguardando...")
                                time.sleep(1)  # Espera 1 segundo antes de verificar novamente
                            else:
                                print("CAPTCHA invisível. Continuando...")
                                break
                        except: 
                            # Se o elemento não for encontrado, considera que sumiu
                            print("CAPTCHA não encontrado. Continuando...")
                            break

                    inserir_em_json(CAMINHO_CONTAS_JSON, dadosParaCadastro)
                    time.sleep(3)
                    botaoPerfil = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Perfil']")))
                    botaoPerfil.click()
                    botaoDeposito = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/section/div/section/div[2]/div[2]/div[2]/div/i')))
                    botaoDeposito.click()
                    print(val_max.get(), val_min.get())
                    if val_min.get() not in [None, ''] and val_max.get() not in [None, '']:
                        random_number = round(random.uniform(int(val_min.get()), int(val_max.get())), 2)
                        campoDeposito = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ui-tab-25"]/div/form/div/div[3]/div/div/div/div[1]/div/input')))
                        campoDeposito.click()
                        campoDeposito.send_keys(random_number)
                        btnConfirmarDeposito = wait.until(
                            EC.element_to_be_clickable((By.XPATH, "//*[contains(@class, 'ui-button__text') and normalize-space()='Deposite agora']"))
                        )
                        btnConfirmarDeposito.click()
                except Exception as e:
                    print(f"Erro: {e}")
                    
                    

            #endregion

        def chavesPIX():
            pagina_atual = 0
            chaves_por_pagina = 9
            dados_pix = []

            def salvar_dados_pix():
                arquivo_origem = filedialog.askopenfilename(
                    title="Selecione o arquivo com as chaves PIX",
                    filetypes=[("Arquivos de texto", "*.txt")]
                )
                if not arquivo_origem:
                    return

                # Função auxiliar fora do loop
                def identificar_tipo_pix(chave: str) -> str:
                    chave = chave.strip()
                    if re.fullmatch(r'\d{3}\.\d{3}\.\d{3}-\d{2}', chave):
                        return "CPF"
                    if re.fullmatch(r'(\+?\d{2,3})?[\s\-\.]?\(?\d{2}\)?[\s\-\.]?\d{4,5}[\s\-\.]?\d{4}', chave) or re.fullmatch(r'\d{11}', chave):
                        return "TELEFONE"
                    if "@" in chave and re.fullmatch(r"[^@]+@[^@]+\.[^@]+", chave):
                        return "EMAIL"
                    return "DESCONHECIDO"

                novas_chaves = []

                with open(arquivo_origem, 'r', encoding='utf-8') as origem:
                    for linha in origem:
                        linha = linha.strip()
                        if not linha:
                            continue
                        tipo_pix = identificar_tipo_pix(linha)
                        if tipo_pix != "DESCONHECIDO":
                            nova_linha = f"{tipo_pix}:{linha}"
                            novas_chaves.append(nova_linha)

                # Lê o destino atual
                try:
                    with open(CAMINHO_ARQUIVO_USUARIO, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()
                except FileNotFoundError:
                    linhas = []

                # Procura ou cria a seção ### LISTA DE CHAVES PIX SALVAS ###
                SECAO_PIX = "### LISTA DE CHAVES PIX SALVAS ###\n"
                try:
                    idx_pix = linhas.index(SECAO_PIX)
                except ValueError:
                    linhas.append("\n" + SECAO_PIX)
                    idx_pix = len(linhas) - 1

                # Coletar todas as chaves já registradas após a seção
                chaves_existentes = set()
                for linha in linhas[idx_pix + 1:]:
                    if linha.startswith("###"):
                        break
                    chaves_existentes.add(linha.strip())

                # Adicionar novas chaves, evitando duplicatas
                novas_linhas = []
                for chave in novas_chaves:
                    if chave not in chaves_existentes:
                        novas_linhas.append(chave + "\n")

                # Inserir novas linhas logo após a seção
                linhas[idx_pix + 1:idx_pix + 1] = novas_linhas

                with open(CAMINHO_ARQUIVO_USUARIO, 'w', encoding='utf-8') as f:
                    f.writelines(linhas)

                carregar_chaves_pix()
                exibir_chaves_na_pagina()

            def carregar_chaves_pix():
                nonlocal titulo_label
                dados_pix.clear()
                try:
                    with open(CAMINHO_ARQUIVO_USUARIO, 'r', encoding='utf-8') as f:
                        linhas = f.readlines()

                    try:
                        indice_chaves = linhas.index("### LISTA DE CHAVES PIX SALVAS ###\n")
                    except ValueError:
                        titulo_label.configure(text="Nenhuma seção de chaves PIX encontrada.")
                        return

                    for linha in linhas[indice_chaves + 1:]:
                        if linha.startswith("### LISTA DE CHAVES PIX SALVAS ###"):
                            break
                        if not linha.strip():
                            titulo_label.configure(text="Nenhuma chave PIX cadastrada.")
                            continue
                        if linha.startswith("###"):
                            titulo_label.configure(text="Nenhuma chave PIX cadastrada.")
                            break
                        if ":" in linha:
                            tipo, chave = linha.strip().split(":", 1)
                            dados_pix.append([tipo, chave])
                except FileNotFoundError:
                    pass

                titulo_label.configure(text=f"Chaves Pix Disponíveis: {len(dados_pix)}")

            def exibir_chaves_na_pagina():
                for widget in framePix.winfo_children():
                    info = str(widget)
                    if "ctklabel" in info.lower() or "ctkbutton" in info.lower():
                        grid_info = widget.grid_info()
                        if int(grid_info.get("row", 0)) >= 2:
                            widget.destroy()

                inicio = pagina_atual * chaves_por_pagina
                fim = inicio + chaves_por_pagina
                chaves_visiveis = dados_pix[inicio:fim]
                

                def excluir_chave(tipo, chave):
                    linha = f"{tipo}:{chave}"
                    dados_pix.remove([tipo, chave])
                    remover_de_txt(CAMINHO_ARQUIVO_USUARIO, "pix", linha)
                    carregar_chaves_pix()
                    exibir_chaves_na_pagina()
                  
                if chaves_visiveis:  
                    for idx, (tipo, chave) in enumerate(chaves_visiveis):
                        lbl_chave = ctk.CTkLabel(framePix, text=chave)
                        lbl_chave.grid(row=2 + idx, column=0, padx=10, pady=2, sticky="wN")

                        lbl_tipo = ctk.CTkLabel(framePix, text=tipo)
                        lbl_tipo.grid(row=2 + idx, column=1, padx=10, pady=2, sticky="wN")

                        btn_excluir = ctk.CTkButton(
                            framePix,
                            text="Excluir",
                            command=lambda t=tipo, c=chave: excluir_chave(t, c),
                            fg_color="#c47600",
                            width=70
                        )
                        btn_excluir.grid(row=2 + idx, column=2, padx=5)
                else:
                    lbl_chave = ctk.CTkLabel(framePix, text="Nenhuma chave pix cadastrada")
                    lbl_chave.grid(row=2, column=0, padx=10, pady=2, sticky="wNe", columnspan=3)


            def pagina_anterior():
                nonlocal pagina_atual
                if pagina_atual > 0:
                    pagina_atual -= 1
                    exibir_chaves_na_pagina()

            def proxima_pagina():
                nonlocal pagina_atual
                total_paginas = (len(dados_pix) - 1) // chaves_por_pagina
                if pagina_atual < total_paginas:
                    pagina_atual += 1
                    exibir_chaves_na_pagina()

            def excluir_todas_chaves():
                for tipo, chave in dados_pix[:]:
                    remover_de_txt(CAMINHO_ARQUIVO_USUARIO, "pix", f"{tipo}:{chave}")
                dados_pix.clear()
                carregar_chaves_pix()
                exibir_chaves_na_pagina()

            for widget in frameGeral.winfo_children():
                widget.destroy()

            framePix = ctk.CTkFrame(frameGeral)
            framePix.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            framePix.grid_columnconfigure((0, 1, 2), weight=1)
            framePix.grid_rowconfigure(1, weight=0)

            titulo_label = ctk.CTkLabel(framePix, text="Chaves Pix Disponíveis: 0", font=ctk.CTkFont(size=16, weight="bold"), text_color="blue")
            titulo_label.grid(row=0, column=0, columnspan=3, pady=(10, 5))

            # Cabeçalhos
            ctk.CTkLabel(framePix, text="Chave", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, sticky="n")
            ctk.CTkLabel(framePix, text="Tipo", font=ctk.CTkFont(weight="bold")).grid(row=1, column=1, padx=10, sticky="n")
            ctk.CTkButton(framePix, text="Excluir Tudo", fg_color="#3b3bbf", command=excluir_todas_chaves).grid(row=1, column=2, sticky="Ne", padx=10)

            # Rodapé
            rodape = ctk.CTkFrame(framePix)
            rodape.grid(row=20, column=0, columnspan=3, pady=10, sticky="eSw")
            rodape.grid_columnconfigure( 1, weight=1)

            ctk.CTkButton(rodape, text="Anterior", fg_color="orange", text_color="black", width=100, command=pagina_anterior).grid(row=0, column=0, padx=10)
            ctk.CTkButton(rodape, text="Importar Chaves PIX", fg_color="#3b3bbf", width=180, command=salvar_dados_pix).grid(row=0, column=1, padx=10)
            ctk.CTkButton(rodape, text="Próxima", fg_color="orange", text_color="black", width=100, command=proxima_pagina).grid(row=0, column=2, padx=10)

            carregar_chaves_pix()
            exibir_chaves_na_pagina()

        def telaContas():
            pagina_atual = 0
            contas_por_pagina = 9
            dados_contas = []

            CAMINHO_CONTAS_JSON = f"Contas{username}.json"
            for widget in frameGeral.winfo_children():
                widget.destroy()

            frameContas = ctk.CTkFrame(frameGeral)
            frameContas.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            frameContas.grid_rowconfigure(0, weight=1)
            frameContas.grid_columnconfigure(0, weight=1)

            def carregar_contas():
                carregar_dados_contas()
                exibir_contas_na_pagina()

            def carregar_dados_contas():
                nonlocal titulo_label
                dados_contas.clear()

                if not os.path.exists(CAMINHO_CONTAS_JSON):
                    titulo_label.configure(text="Arquivo de contas não encontrado.")
                    return

                try:
                    with open(CAMINHO_CONTAS_JSON, 'r', encoding='utf-8') as f:
                        contas_json = json.load(f)

                    for conta in contas_json:
                        user = conta.get("Username", "")
                        senha = conta.get("Senha", "")
                        senha_saque = conta.get("SenhaSaque", "")
                        casa = conta.get("Casa", "")
                        data = conta.get("Data e Hora do Cadastro", "")
                        dados_contas.append([user, senha, senha_saque, casa, data])

                    titulo_label.configure(text=f"Contas totais: {len(dados_contas)}")

                except json.JSONDecodeError:
                    titulo_label.configure(text="Erro ao carregar o JSON.")

            def exibir_contas_na_pagina():
                nonlocal frameContas
                for widget in frameContas.winfo_children():
                    info = str(widget)
                    if "ctklabel" in info.lower() or "ctkbutton" in info.lower():
                        grid_info = widget.grid_info()
                        if int(grid_info.get("row", 0)) >= 3:
                            widget.destroy()

                inicio = pagina_atual * contas_por_pagina
                fim = inicio + contas_por_pagina
                contas_visiveis = dados_contas[inicio:fim]

                def excluirConta(user):
                    if not os.path.exists(CAMINHO_CONTAS_JSON):
                        return

                    try:
                        with open(CAMINHO_CONTAS_JSON, 'r', encoding='utf-8') as f:
                            contas = json.load(f)

                        contas_filtradas = [conta for conta in contas if conta.get("Username") != user]

                        with open(CAMINHO_CONTAS_JSON, 'w', encoding='utf-8') as f:
                            json.dump(contas_filtradas, f, ensure_ascii=False, indent=2)

                        carregar_dados_contas()
                        exibir_contas_na_pagina()

                    except Exception as e:
                        print(f"Erro ao excluir conta: {e}")

                for idx, linha in enumerate(contas_visiveis):
                    user, senha, senha_saque, casa, data = linha
                    dados_formatados = [user, senha, senha_saque, casa, data]

                    for col, dado in enumerate(dados_formatados):
                        lbl = ctk.CTkLabel(frameContas, text=dado)
                        lbl.grid(row=3 + idx, column=col, padx=5, pady=2)

                    btn_excluir = ctk.CTkButton(
                        frameContas,
                        text="Excluir",
                        command=lambda u=user: excluirConta(u),
                        fg_color="#c47600",
                        width=70
                    )
                    btn_excluir.grid(row=3 + idx, column=len(dados_formatados), padx=5)

            def pagina_anterior():
                nonlocal pagina_atual
                if pagina_atual > 0:
                    pagina_atual -= 1
                    exibir_contas_na_pagina()

            def proxima_pagina():
                nonlocal pagina_atual
                total_paginas = (len(dados_contas) - 1) // contas_por_pagina
                if pagina_atual < total_paginas:
                    pagina_atual += 1
                    exibir_contas_na_pagina()

            for widget in frameGeral.winfo_children():
                widget.destroy()

            frameGeral.grid_rowconfigure(1, weight=1)
            frameGeral.grid_columnconfigure(1, weight=1)

            frameContas = ctk.CTkFrame(frameGeral)
            frameContas.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

            for i in range(12):
                frameContas.grid_rowconfigure(i, weight=1)

            titulo_label = ctk.CTkLabel(frameContas, text="Contas totais: 0", font=ctk.CTkFont(size=16, weight="bold"))
            titulo_label.grid(row=0, column=1, padx=10, pady=10, sticky="n")

            colunas = ["User", "Senha", "Senha Saque", "Casa", "Data", "Ações"]
            for i, nome in enumerate(colunas):
                header = ctk.CTkLabel(frameContas, text=nome, font=ctk.CTkFont(weight="bold"))
                header.grid(row=2, column=i, padx=5, pady=5)
                frameContas.grid_columnconfigure(i, weight=1)

            frame_rodape = ctk.CTkFrame(frameContas)
            frame_rodape.grid(row=12, column=0, columnspan=6, pady=10, sticky="ew")

            btn_anterior = ctk.CTkButton(frame_rodape, text="Anterior", fg_color="#c47600", width=80, command=pagina_anterior)
            btn_anterior.pack(side="left", padx=5)

            btn_proxima = ctk.CTkButton(frame_rodape, text="Próxima", fg_color="#c47600", width=80, command=proxima_pagina)
            btn_proxima.pack(side="right", padx=5)

            carregar_dados_contas()
            exibir_contas_na_pagina()
                

        def telaProxy():
                    # Variáveis de controle
            pagina_atual = 0
            proxies_por_pagina = 9
            dados_proxies = []

            def salvar_dados_proxies():
                arquivo_destino = CAMINHO_ARQUIVO_USUARIO
                arquivo_origem = filedialog.askopenfilename(
                    title="Selecione o arquivo com os dados de proxy",
                    filetypes=[("Arquivos de texto", "*.txt")]
                )
                if not arquivo_origem:
                    return
                with open(arquivo_origem, 'r') as origem:
                    linhas = origem.readlines()

                for linha in linhas:
                    novo_dado = f"{linha.strip()},disponivel,HTTP"
                    inserir_em_txt(CAMINHO_ARQUIVO_USUARIO, "proxy", novo_dado)

                carregar_dados_proxies()
                exibir_proxies_na_pagina()

            def carregar_dados_proxies():
                nonlocal titulo_label
                dados_proxies.clear()

                try:
                    with open(CAMINHO_ARQUIVO_USUARIO, 'r', encoding='utf-8') as origem:
                        linhas = origem.readlines()

                    # Localiza o índice da seção de proxies
                    try:
                        indice_proxies = linhas.index("### LISTA DE PROXIES SALVAS ###\n")
                    except ValueError:
                        titulo_label.configure(text="Nenhuma seção de proxies encontrada.")
                        return

                    # Coleta linhas de proxy até o próximo cabeçalho ou fim
                    for linha in linhas[indice_proxies + 1:]:
                        if linha.startswith("###"):  # outra seção
                            break
                        if not linha.strip():
                            continue

                        partes = linha.strip().split(",")
                        if len(partes) < 2:
                            continue

                        try:
                            ip_port_login_senha = partes[0].split(":")
                            if len(ip_port_login_senha) != 4:
                                continue

                            ip, port = ip_port_login_senha[0], ip_port_login_senha[1]
                            ip_valido = re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip)
                            port_valida = port.isdigit() and 0 < int(port) <= 65535

                            if not ip_valido or not port_valida:
                                continue

                            # Junta tudo para a exibição
                            dados_str = partes[0]
                            status = partes[1]
                            dados_proxies.append([dados_str, status.strip()])

                        except Exception:
                            continue

                except FileNotFoundError:
                    pass

                titulo_label.configure(text=f"Proxies totais: {len(dados_proxies)}")

            def exibir_proxies_na_pagina():
                nonlocal frameProxy
                for widget in frameProxy.winfo_children():
                    info = str(widget)
                    if "ctklabel" in info.lower() or "ctkbutton" in info.lower():
                        grid_info = widget.grid_info()
                        if int(grid_info.get("row", 0)) >= 3:
                            widget.destroy()

                inicio = pagina_atual * proxies_por_pagina
                fim = inicio + proxies_por_pagina
                proxies_visiveis = dados_proxies[inicio:fim]
                
                def excluirProxies(host, port, user, password, status):
                    linha = f"{host}:{port}:{user}:{password},{status}"
                    linha_original = [f"{host}:{port}:{user}:{password}", status]
                    linhaParaComparacao = [linha]
                    dadosParaComapracao = [[f"{proxy[0]},{proxy[1]}"] for proxy in dados_proxies]

                    if linhaParaComparacao in dadosParaComapracao:
                        remover_de_txt(CAMINHO_ARQUIVO_USUARIO, "proxy", linha)
                        dados_proxies.remove(linha_original)
                        carregar_dados_proxies()
                        exibir_proxies_na_pagina()
                                    
                for idx, linha in enumerate(proxies_visiveis):
                    try:
                        dados_str, status = linha
                        host, port, user, password = dados_str.split(":")
                    except ValueError:
                        continue  # pula se o formato estiver errado

                    dados_formatados = [host, port, user, password, status]

                    for col, dado in enumerate(dados_formatados):
                        lbl = ctk.CTkLabel(frameProxy, text=dado)
                        lbl.grid(row=3 + idx, column=col, padx=5, pady=2)
                    btn_excluir = ctk.CTkButton(
                        frameProxy,
                        text="Excluir",
                        command=lambda h=host, p=port, u=user, pw=password, s=status: excluirProxies(h, p, u, pw, s),
                        fg_color="#c47600",
                        width=70
                    )
                    btn_excluir.grid(row=3 + idx, column=len(dados_formatados), padx=5)

            def pagina_anterior():
                nonlocal pagina_atual
                if pagina_atual > 0:
                    pagina_atual -= 1
                    exibir_proxies_na_pagina()

            def proxima_pagina():
                nonlocal pagina_atual
                total_paginas = (len(dados_proxies) - 1) // proxies_por_pagina
                if pagina_atual < total_paginas:
                    pagina_atual += 1
                    exibir_proxies_na_pagina()

            for widget in frameGeral.winfo_children():
                widget.destroy()
                
            frameGeral.grid_rowconfigure(1, weight=1)
            frameGeral.grid_columnconfigure(1, weight=1)

            frameProxy = ctk.CTkFrame(frameGeral)
            frameProxy.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            frameProxy.grid_rowconfigure(0, weight=0)
            frameProxy.grid_columnconfigure(0, weight=0)
            for i in range(12):  # até linha 11
                frameProxy.grid_rowconfigure(i, weight=1)

            # Método de conexão
            metodo_label = ctk.CTkLabel(frameProxy, text="Método de Conexão")
            metodo_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 5), sticky="w")

            metodo_var = ctk.StringVar(value="HTTP")
            metodo_menu = ctk.CTkOptionMenu(frameProxy, variable=metodo_var, values=["HTTP", "SOCKS5"])
            metodo_menu.grid(row=1, column=0, padx=(10, 5), sticky="w")

            # Título (contagem de proxies)
            titulo_label = ctk.CTkLabel(frameProxy, text="Proxies totais: 0", font=ctk.CTkFont(size=16, weight="bold"))
            titulo_label.grid(row=0, column=1, padx=10, pady=10, sticky="n")
            
            def excluirTodosProxies():
                remover_de_txt(CAMINHO_ARQUIVO_USUARIO, "proxy", "proxy")
                carregar_dados_proxies()
                exibir_proxies_na_pagina()
            
            buttonExcluirTudo = ctk.CTkButton(frameProxy, text="Excluir todos", fg_color="#c47600", width=100, command=excluirTodosProxies)
            buttonExcluirTudo.grid(row=0, column=2, padx=10, pady=10, sticky="n")

            # Cabeçalhos da tabela
            colunas = ["Host", "Porta", "Usuário", "Senha", "Status", "Ações"]
            for i, nome in enumerate(colunas):
                header = ctk.CTkLabel(frameProxy, text=nome, font=ctk.CTkFont(weight="bold"))
                header.grid(row=2, column=i, padx=5, pady=5)

            # Botões e funcionalidades fixos
            frame_rodape = ctk.CTkFrame(frameProxy)
            frame_rodape.grid(row=12, column=0, columnspan=6, pady=10, sticky="ew")

            btn_anterior = ctk.CTkButton(frame_rodape, text="Anterior", fg_color="#c47600", width=80, command=pagina_anterior)
            btn_anterior.pack(side="left", padx=5)

            btn_proxima = ctk.CTkButton(frame_rodape, text="Próxima", fg_color="#c47600", width=80, command=proxima_pagina)
            btn_proxima.pack(side="right", padx=5)

            btn_importar = ctk.CTkButton(frame_rodape, text="Importar Proxies", fg_color="#3b3bbf", command=salvar_dados_proxies, width=150)
            btn_importar.pack(side="top", pady=5)

            # Carrega e exibe os proxies da primeira página
            carregar_dados_proxies()
            exibir_proxies_na_pagina()


        def gestaoDeTelas():
            from screeninfo import get_monitors

            for widget in frameGeral.winfo_children():
                widget.destroy()

            frameTelas = ctk.CTkFrame(frameGeral)
            frameTelas.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
            frameTelas.grid_rowconfigure(0, weight=1)
            frameTelas.grid_columnconfigure(0, weight=1)

            linhas_var = ctk.IntVar(value=2)
            colunas_var = ctk.IntVar(value=5)

            monitores_detectados = get_monitors()
            opcoes_monitores = [f"Monitor {i+1} ({m.width}x{m.height})" for i, m in enumerate(monitores_detectados)]

            # Scrollable Layout com peso
            scrollLayout = ctk.CTkScrollableFrame(frameTelas, fg_color="#2e2e2e")
            scrollLayout.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            scrollLayout.grid_columnconfigure(0, weight=1)

            # Frame de controle
            frameInferior = ctk.CTkFrame(frameTelas)
            frameInferior.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
            frameInferior.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=0)
            frameInferior.grid_columnconfigure(6, weight=1)

            ctk.CTkLabel(frameInferior, text="Linhas:").grid(row=0, column=0, padx=5)
            ctk.CTkEntry(frameInferior, textvariable=linhas_var, width=40).grid(row=0, column=1, padx=5)

            ctk.CTkLabel(frameInferior, text="Colunas:").grid(row=0, column=2, padx=5)
            ctk.CTkEntry(frameInferior, textvariable=colunas_var, width=40).grid(row=0, column=3, padx=5)

            combo_monitor = ctk.CTkComboBox(frameInferior, values=opcoes_monitores, width=180)
            combo_monitor.grid(row=0, column=5, padx=10)
            combo_monitor.set(opcoes_monitores[0])

            def atualizar_layout():
                for widget in scrollLayout.winfo_children():
                    widget.destroy()

                linhas = linhas_var.get()
                colunas = colunas_var.get()

                monitor_index = combo_monitor.cget("values").index(combo_monitor.get())
                monitor_info = monitores_detectados[monitor_index]
                mon_width = monitor_info.width
                mon_height = monitor_info.height

                proporcao_monitor = mon_width / mon_height

                # Container para layout real com grid
                container = ctk.CTkFrame(scrollLayout, fg_color="transparent")
                container.grid(row=0, column=0, sticky="nsew")
                container.grid_columnconfigure(tuple(range(colunas)), weight=1)
                container.grid_rowconfigure(tuple(range(linhas)), weight=1)

                for i in range(linhas):
                    for j in range(colunas):
                        slot = ctk.CTkFrame(container, fg_color="#d3d3d3", corner_radius=5)
                        slot.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")

            ctk.CTkButton(frameInferior, text="Atualizar/Resetar Layout", command=atualizar_layout, fg_color="orange").grid(row=0, column=4, padx=10)
            ctk.CTkButton(frameInferior, text="Salvar Posições Personalizadas", fg_color="#3b6efb").grid(row=0, column=6, padx=10, sticky="e")

            atualizar_layout()
        

        botaoInicio = ctk.CTkButton(frameLateral, text="INICIO", command=carregar_inicio)
        botaoInicio.grid(row = 1, column = 0, padx = 10, pady = 10,sticky="nsew")
        botaoChavesPix = ctk.CTkButton(frameLateral, text="CHAVES PIX", command=chavesPIX)
        botaoChavesPix.grid(row = 2, column = 0, padx = 10, pady = 10,sticky="nSew")
        botaoContas = ctk.CTkButton(frameLateral, text="CONTAS", command=telaContas)
        botaoContas.grid(row = 3, column = 0, padx = 10, pady = 10,sticky="nSew")
        botaoProxies = ctk.CTkButton(frameLateral, text="PROXIES", command=telaProxy)
        botaoProxies.grid(row = 4, column = 0, padx = 10, pady = 10,sticky="nSew")
        botaoTelas = ctk.CTkButton(frameLateral, text="TELAS", command=gestaoDeTelas)
        botaoTelas.grid(row = 5, column = 0, padx = 10, pady = 10,sticky="nsew")
        botaoJogar = ctk.CTkButton(frameLateral, text="JOGAR")
        botaoJogar.grid(row = 6, column = 0, padx = 10, pady = 10,sticky="nsew")
        carregar_inicio()
        
        
        
    


if __name__ == "__main__":
    db_manager = Database()  # Cria a instância do banco de dados
    app = LoginApp(db_manager)
    
    # Garante que a conexão com o DB seja fechada ao fechar a janela
    def on_app_closing():
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_app_closing)
    app.mainloop()