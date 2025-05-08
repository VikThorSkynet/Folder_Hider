import os
import subprocess
import platform
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import json # Para salvar/carregar configuração de forma mais estruturada

try:
    import keyboard
except ImportError:
    messagebox.showerror("Erro de Importação", "A biblioteca 'keyboard' não está instalada.\nPor favor, instale-a com: pip install keyboard")
    sys.exit()

if platform.system() == "Windows":
    try:
        import ctypes
    except ImportError:
        ctypes = None
        print("AVISO: ctypes não disponível, a atualização automática da área de trabalho pode não funcionar.")
else:
    ctypes = None

# --- Configuração Inicial e Nome do Arquivo de Configuração ---
CONFIG_FILE = "config_ocultador.json"
DEFAULT_TECLA_OCULTAR = "ctrl+alt+a"
DEFAULT_TECLA_MOSTRAR = "ctrl+alt+q"
DEFAULT_TECLA_SAIR = "ctrl+alt+s"
DEFAULT_ATTRIB_EXE_PATH = r"C:\Windows\System32\attrib.exe"

# --- Variáveis Globais que serão configuradas ---
CAMINHO_COMPLETO_DA_PASTA_ALVO = "" # Será carregado ou definido pelo usuário
NOME_BASE_PASTA = ""
PASTA_PAI = ""
PASTA_ALVO_OCULTA_UNIX = ""
TECLA_OCULTAR = DEFAULT_TECLA_OCULTAR
TECLA_MOSTRAR = DEFAULT_TECLA_MOSTRAR
TECLA_SAIR = DEFAULT_TECLA_SAIR
ATTRIB_EXE_PATH = DEFAULT_ATTRIB_EXE_PATH

rodando_listener = True

# --- Funções para Carregar/Salvar Configuração ---
def carregar_configuracao():
    global CAMINHO_COMPLETO_DA_PASTA_ALVO, TECLA_OCULTAR, TECLA_MOSTRAR, TECLA_SAIR, ATTRIB_EXE_PATH
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                CAMINHO_COMPLETO_DA_PASTA_ALVO = config.get("caminho_pasta", "")
                TECLA_OCULTAR = config.get("tecla_ocultar", DEFAULT_TECLA_OCULTAR)
                TECLA_MOSTRAR = config.get("tecla_mostrar", DEFAULT_TECLA_MOSTRAR)
                TECLA_SAIR = config.get("tecla_sair", DEFAULT_TECLA_SAIR)
                # ATTRIB_EXE_PATH = config.get("attrib_path", DEFAULT_ATTRIB_EXE_PATH) # Descomente se quiser tornar configurável
                print("Configuração carregada.")
                return True
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}. Usando padrões.")
    return False

def salvar_configuracao():
    global CAMINHO_COMPLETO_DA_PASTA_ALVO, TECLA_OCULTAR, TECLA_MOSTRAR, TECLA_SAIR, ATTRIB_EXE_PATH
    config = {
        "caminho_pasta": CAMINHO_COMPLETO_DA_PASTA_ALVO,
        "tecla_ocultar": TECLA_OCULTAR,
        "tecla_mostrar": TECLA_MOSTRAR,
        "tecla_sair": TECLA_SAIR,
        # "attrib_path": ATTRIB_EXE_PATH, # Descomente se quiser tornar configurável
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuração salva em {CONFIG_FILE}")
    except Exception as e:
        print(f"Erro ao salvar configuração: {e}")


# --- Lógica do Core (Funções _core como antes, mas usando variáveis globais configuradas) ---
# (As funções refresh_desktop_windows, verificar_e_criar_pasta_core, ocultar_pasta_core, mostrar_pasta_core
# permanecem as mesmas, mas agora usarão as variáveis globais CAMINHO_COMPLETO_DA_PASTA_ALVO, etc.)

def atualizar_variaveis_caminho(caminho_completo):
    """Atualiza NOME_BASE_PASTA, PASTA_PAI, etc., baseado no caminho completo."""
    global CAMINHO_COMPLETO_DA_PASTA_ALVO, NOME_BASE_PASTA, PASTA_PAI, PASTA_ALVO_OCULTA_UNIX
    CAMINHO_COMPLETO_DA_PASTA_ALVO = caminho_completo
    if CAMINHO_COMPLETO_DA_PASTA_ALVO and os.path.isabs(CAMINHO_COMPLETO_DA_PASTA_ALVO):
        NOME_BASE_PASTA = os.path.basename(CAMINHO_COMPLETO_DA_PASTA_ALVO)
        PASTA_PAI = os.path.dirname(CAMINHO_COMPLETO_DA_PASTA_ALVO)
        PASTA_ALVO_OCULTA_UNIX = os.path.join(PASTA_PAI, "." + NOME_BASE_PASTA)
        return True
    NOME_BASE_PASTA = ""
    PASTA_PAI = ""
    PASTA_ALVO_OCULTA_UNIX = ""
    return False


# --- Funções _core (sem mudanças internas, apenas dependem das globais atualizadas) ---
def refresh_desktop_windows():
    if platform.system() == "Windows" and ctypes:
        SHCNE_ASSOCCHANGED = 0x08000000; SHCNF_IDLIST = 0x0000
        try:
            ctypes.windll.shell32.SHChangeNotify(SHCNE_ASSOCCHANGED, SHCNF_IDLIST, None, None)
            return True
        except Exception as e: print(f"Erro SHChangeNotify: {e}")
    return False

def verificar_e_criar_pasta_core():
    if not NOME_BASE_PASTA: return False, "Caminho da pasta não definido."
    if not os.path.exists(PASTA_PAI): return False, f"Diretório pai '{PASTA_PAI}' não existe."
    existe_normal = os.path.exists(CAMINHO_COMPLETO_DA_PASTA_ALVO)
    existe_oculta_unix = (platform.system() != "Windows" and os.path.exists(PASTA_ALVO_OCULTA_UNIX))
    if not existe_normal and not existe_oculta_unix:
        msg = f"'{NOME_BASE_PASTA}' não encontrada em '{PASTA_PAI}'.\nCriando..."
        try:
            os.makedirs(CAMINHO_COMPLETO_DA_PASTA_ALVO);
            if platform.system() == "Windows": refresh_desktop_windows()
            return True, f"{msg} Criada."
        except OSError as e: return False, f"{msg} Erro: {e}"
    return True, f"Pasta '{NOME_BASE_PASTA}' pronta."

def ocultar_pasta_core():
    if not NOME_BASE_PASTA: return False, "Caminho da pasta não definido."
    if platform.system() == "Windows":
        if not os.path.exists(CAMINHO_COMPLETO_DA_PASTA_ALVO): return False, f"'{NOME_BASE_PASTA}' não encontrada."
        try:
            subprocess.run([ATTRIB_EXE_PATH, '-r', CAMINHO_COMPLETO_DA_PASTA_ALVO], check=False, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run([ATTRIB_EXE_PATH, '+h', CAMINHO_COMPLETO_DA_PASTA_ALVO], check=True, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            refresh_desktop_windows(); return True, f"'{NOME_BASE_PASTA}' ocultada."
        except Exception as e: return False, f"Erro ao ocultar: {e}"
    return False, "Não implementado para este OS."

def mostrar_pasta_core():
    if not NOME_BASE_PASTA: return False, "Caminho da pasta não definido."
    if platform.system() == "Windows":
        try:
            subprocess.run([ATTRIB_EXE_PATH, '-h', CAMINHO_COMPLETO_DA_PASTA_ALVO], check=True, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            refresh_desktop_windows()
            if os.path.exists(CAMINHO_COMPLETO_DA_PASTA_ALVO): return True, f"'{NOME_BASE_PASTA}' visível."
            else: return False, f"'{NOME_BASE_PASTA}' não encontrada após comando."
        except Exception as e: return False, f"Erro ao mostrar: {e}"
    return False, "Não implementado para este OS."

# --- Classe da Aplicação GUI ---
class FolderHiderApp:
    def __init__(self, root_tk):
        self.root = root_tk
        self.root.title("Ocultador de Pasta v2")
        self.root.geometry("455x250") # Ajustar tamanho
        # self.root.resizable(False, False) # Permitir redimensionar pode ser útil

        # --- Frame para o Caminho da Pasta ---
        path_frame = tk.Frame(root_tk)
        path_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(path_frame, text="Caminho da Pasta:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar()
        self.path_entry = tk.Entry(path_frame, textvariable=self.path_var, width=40)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5,0))

        self.browse_button = tk.Button(path_frame, text="Procurar...", command=self.procurar_pasta)
        self.browse_button.pack(side=tk.LEFT, padx=(5,0))

        self.define_path_button = tk.Button(root_tk, text="Definir e Verificar Pasta", command=self.definir_e_verificar_pasta_atual)
        self.define_path_button.pack(pady=(0,10))


        # --- Label de Status ---
        self.status_var = tk.StringVar()
        self.status_label_widget = tk.Label(root_tk, textvariable=self.status_var, fg="blue", wraplength=380, height=2)
        self.status_label_widget.pack(pady=5)

        # --- Frame de Botões de Ação ---
        action_button_frame = tk.Frame(root_tk)
        action_button_frame.pack(pady=10)

        self.ocultar_button = tk.Button(action_button_frame, text="Ocultar Pasta", command=self.run_ocultar_pasta_threaded, state=tk.DISABLED)
        self.ocultar_button.pack(side=tk.LEFT, padx=5)
        self.mostrar_button = tk.Button(action_button_frame, text="Mostrar Pasta", command=self.run_mostrar_pasta_threaded, state=tk.DISABLED)
        self.mostrar_button.pack(side=tk.LEFT, padx=5)
        tk.Button(action_button_frame, text="Sair", command=self.sair_app).pack(side=tk.LEFT, padx=5)

        # --- Label de Hotkeys ---
        self.hotkey_label_var = tk.StringVar()
        tk.Label(root_tk, textvariable=self.hotkey_label_var, justify=tk.LEFT).pack(pady=5)


        # --- Inicialização e Configuração ---
        if carregar_configuracao():
            self.path_var.set(CAMINHO_COMPLETO_DA_PASTA_ALVO)
            self.definir_e_verificar_pasta_atual(silencioso=True) # Tenta validar o caminho carregado
        else:
            self.update_status_display("Digite ou procure o caminho da pasta.", is_error=False)


        self.atualizar_label_hotkeys()
        self.setup_hotkeys() # Configura os hotkeys após as variáveis serem carregadas/definidas
        self.root.protocol("WM_DELETE_WINDOW", self.sair_app)
        self.root.bind("<Destroy>", self.on_destroy) # Para salvar config ao fechar

    def on_destroy(self, event):
        """Chamado quando a janela está sendo destruída."""
        if event.widget == self.root: # Certifica-se que é o evento da janela principal
            salvar_configuracao()

    def procurar_pasta(self):
        caminho_selecionado = filedialog.askdirectory()
        if caminho_selecionado:
            self.path_var.set(caminho_selecionado)
            self.definir_e_verificar_pasta_atual()

    def definir_e_verificar_pasta_atual(self, silencioso=False):
        novo_caminho = self.path_var.get().strip()
        if not novo_caminho:
            if not silencioso:
                self.update_status_display("Caminho da pasta não pode ser vazio.", is_error=True)
            self.ocultar_button.config(state=tk.DISABLED)
            self.mostrar_button.config(state=tk.DISABLED)
            return

        if not os.path.isabs(novo_caminho):
            if not silencioso:
                self.update_status_display("Forneça um caminho absoluto para a pasta.", is_error=True)
            self.ocultar_button.config(state=tk.DISABLED)
            self.mostrar_button.config(state=tk.DISABLED)
            return

        if atualizar_variaveis_caminho(novo_caminho):
            salvar_configuracao() # Salva o novo caminho válido
            self.run_threaded_action(verificar_e_criar_pasta_core)
            self.ocultar_button.config(state=tk.NORMAL)
            self.mostrar_button.config(state=tk.NORMAL)
            if not silencioso:
                self.update_status_display(f"Pasta alvo definida: {NOME_BASE_PASTA}", is_error=False)
        else:
            if not silencioso:
                self.update_status_display("Caminho da pasta inválido.", is_error=True)
            self.ocultar_button.config(state=tk.DISABLED)
            self.mostrar_button.config(state=tk.DISABLED)


    def atualizar_label_hotkeys(self):
        self.hotkey_label_var.set(f"Hotkeys:\nOcultar: {TECLA_OCULTAR}\nMostrar: {TECLA_MOSTRAR}\nSair: {TECLA_SAIR}")


    def update_status_display(self, message, is_error=False):
        self.status_var.set(message)
        cor = "red" if is_error else ("green" if any(s in message.lower() for s in ["sucesso", "ocultada", "visível", "pronta", "criada", "definida"]) else "blue")
        self.status_label_widget.config(fg=cor)

    def run_threaded_action(self, action_func, *args):
        if not CAMINHO_COMPLETO_DA_PASTA_ALVO and action_func != verificar_e_criar_pasta_core:
            self.update_status_display("Defina um caminho de pasta primeiro.", is_error=True)
            return

        def wrapper():
            self.root.after(0, lambda: self.update_status_display("Processando...", is_error=False))
            sucesso, mensagem = action_func(*args)
            print(f"Ação {action_func.__name__}: Sucesso={sucesso}, Mensagem='{mensagem}'")
            self.root.after(0, lambda: self.update_status_display(mensagem, is_error=not sucesso))
        thread = threading.Thread(target=wrapper, daemon=True); thread.start()


    def run_ocultar_pasta_threaded(self): self.run_threaded_action(ocultar_pasta_core)
    def run_mostrar_pasta_threaded(self): self.run_threaded_action(mostrar_pasta_core)

    def setup_hotkeys(self):
        keyboard.unhook_all() # Limpa hotkeys antigos antes de registrar novos
        try:
            keyboard.add_hotkey(TECLA_OCULTAR, self.run_ocultar_pasta_threaded, suppress=False)
            keyboard.add_hotkey(TECLA_MOSTRAR, self.run_mostrar_pasta_threaded, suppress=False)
            keyboard.add_hotkey(TECLA_SAIR, self.sair_app_from_hotkey, suppress=True)
            print("Hotkeys registrados/atualizados.")
        except Exception as e:
            msg_erro = f"Erro ao registrar hotkeys: {e}"
            print(msg_erro)
            if hasattr(self, 'status_label_widget'): self.update_status_display(msg_erro, is_error=True)
            else: messagebox.showerror("Erro de Hotkey", msg_erro)

    def sair_app(self):
        global rodando_listener
        print("Saindo da aplicação...")
        rodando_listener = False
        # salvar_configuracao() # Já é salvo em on_destroy ou ao definir novo caminho
        keyboard.unhook_all()
        if self.root and self.root.winfo_exists(): self.root.destroy()

    def sair_app_from_hotkey(self):
        if self.root and self.root.winfo_exists(): self.root.after(0, self.sair_app)


# --- Bloco Principal ---
if __name__ == "__main__":
    # Validações iniciais de dependências do sistema (ex: attrib.exe)
    if platform.system() == "Windows" and not os.path.exists(ATTRIB_EXE_PATH): # ATTRIB_EXE_PATH agora é global
        messagebox.showerror("Erro Crítico", f"'{ATTRIB_EXE_PATH}' não encontrado.")
        sys.exit()

    # Aviso de permissão
    if platform.system() == "Windows":
        is_admin = False
        try: is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception: print("Não foi possível verificar privilégios de admin via ctypes.")
        if not is_admin:
            messagebox.showwarning("Aviso de Permissão", "Pode ser necessário executar como Administrador.")

    root = tk.Tk()
    app = FolderHiderApp(root)
    root.mainloop()

    print("GUI fechada. Limpando...")
    rodando_listener = False
    keyboard.unhook_all()
    print("Script finalizado.")