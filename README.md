# Folder_Hider
# Ocultador de Pasta v2

Este script Python fornece uma interface gráfica (GUI) e teclas de atalho para ocultar e mostrar uma pasta específica no sistema de arquivos do Windows. Ele salva a configuração da pasta alvo e as teclas de atalho em um arquivo JSON para persistência entre as sessões.

## Funcionalidades

*   **Interface Gráfica (GUI):** Interface amigável construída com Tkinter para selecionar a pasta, ocultá-la, mostrá-la e sair da aplicação.
*   **Teclas de Atalho Globais:**
    *   Ocultar pasta (Padrão: `Ctrl+Alt+A`)
    *   Mostrar pasta (Padrão: `Ctrl+Alt+Q`)
    *   Sair da aplicação (Padrão: `Ctrl+Alt+S`)
*   **Persistência de Configuração:** Salva o caminho da pasta alvo e as combinações de teclas de atalho em um arquivo `config_ocultador.json`.
*   **Verificação e Criação de Pasta:** Se a pasta alvo não existir, o script pode criá-la.
*   **Atualização da Área de Trabalho (Windows):** Tenta atualizar a visualização do Explorer após ocultar/mostrar a pasta para que as alterações sejam refletidas imediatamente.
*   **Verificação de Dependências:** Verifica a presença da biblioteca `keyboard` e do `attrib.exe` no Windows.
*   **Aviso de Permissão (Windows):** Avisa se o script não estiver sendo executado com privilégios de administrador, o que pode ser necessário para algumas operações.

## Requisitos

*   **Python 3.x**
*   **Biblioteca `tkinter`:** Geralmente incluída na instalação padrão do Python.
*   **Biblioteca `keyboard`:** Para escutar as teclas de atalho globais.
*   **Sistema Operacional:**
    *   **Windows:** Funcionalidade completa (ocultar/mostrar pasta usando `attrib.exe`).
    *   **Outros SOs (Linux, macOS):** A interface gráfica pode iniciar e as teclas de atalho podem ser detectadas (se a biblioteca `keyboard` tiver as permissões necessárias), mas as funções de **ocultar/mostrar pasta não são implementadas** para esses sistemas no estado atual do código.

## Instalação

1.  **Instale o Python 3:** Se ainda não o tiver, baixe e instale a partir de [python.org](https://www.python.org/).
2.  **Clone ou baixe este repositório/script.**
3.  **Instale a biblioteca `keyboard`:**
    Abra um terminal ou prompt de comando e execute:
    ```bash
    pip install keyboard
    ```
    *Nota para usuários Linux:* A biblioteca `keyboard` pode exigir acesso `root` ou que o usuário esteja no grupo `input` para monitorar eventos de teclado globalmente.
    *Nota para usuários macOS:* Pode ser necessário conceder permissões de acessibilidade ao terminal/IDE que executa o script.

## Como Executar

1.  Salve o código como um arquivo Python (por exemplo, `ocultador_pasta.py`).
2.  Navegue até o diretório onde salvou o arquivo usando o terminal ou prompt de comando.
3.  Execute o script com:
    ```bash
    python ocultador_pasta.py
    ```
    No Windows, pode ser necessário executar o script como administrador para garantir que `attrib.exe` possa modificar os atributos de todas as pastas e para que `ctypes.windll.shell32.IsUserAnAdmin()` funcione corretamente.

## Como Usar

### Interface Gráfica (GUI)

Ao executar o script, uma janela será aberta:

1.  **Caminho da Pasta:**
    *   Digite o caminho completo da pasta que deseja ocultar/mostrar.
    *   Ou clique em **"Procurar..."** para selecionar a pasta através de uma caixa de diálogo.
2.  **Definir e Verificar Pasta:**
    *   Após inserir ou selecionar um caminho, clique neste botão.
    *   O script verificará se o caminho é válido. Se a pasta não existir, perguntará se deseja criá-la (no estado atual, ele a cria automaticamente se não existir).
    *   O caminho definido será salvo na configuração.
3.  **Botões de Ação:**
    *   **Ocultar Pasta:** Torna a pasta alvo invisível no explorador de arquivos (no Windows, define o atributo "+h"). Este botão só fica ativo após uma pasta ser definida.
    *   **Mostrar Pasta:** Torna a pasta alvo visível novamente (no Windows, remove o atributo "-h"). Este botão só fica ativo após uma pasta ser definida.
    *   **Sair:** Fecha a aplicação.
4.  **Status:** Uma mensagem na parte inferior da janela indicará o status da operação atual (ex: "Pasta ocultada.", "Erro ao definir caminho.", etc.).
5.  **Teclas de Atalho Listadas:** As teclas de atalho atualmente configuradas são exibidas na parte inferior da GUI.

### Teclas de Atalho (Hotkeys)

Mesmo com a janela da aplicação minimizada ou sem foco, você pode usar as seguintes teclas de atalho (combinações padrão):

*   `Ctrl + Alt + A`: Oculta a pasta alvo.
*   `Ctrl + Alt + Q`: Mostra a pasta alvo.
*   `Ctrl + Alt + S`: Fecha a aplicação.

As teclas de atalho são carregadas do arquivo `config_ocultador.json`. Se o arquivo não existir ou uma tecla não estiver definida, os valores padrão serão usados.

## Configuração

O script cria e utiliza um arquivo chamado `config_ocultador.json` no mesmo diretório onde é executado. Este arquivo armazena:

*   `caminho_pasta`: O último caminho de pasta alvo definido pelo usuário.
*   `tecla_ocultar`: A combinação de teclas para ocultar a pasta.
*   `tecla_mostrar`: A combinação de teclas para mostrar a pasta.
*   `tecla_sair`: A combinação de teclas para sair da aplicação.

Exemplo de `config_ocultador.json`:

```json
{
    "caminho_pasta": "C:\\Caminho\\Para\\MinhaPastaSecreta",
    "tecla_ocultar": "ctrl+alt+a",
    "tecla_mostrar": "ctrl+alt+q",
    "tecla_sair": "ctrl+alt+s"
}
```

Você pode editar este arquivo manualmente para alterar as teclas de atalho, mas **faça isso com a aplicação fechada**. O script carrega a configuração ao iniciar e salva automaticamente ao definir um novo caminho de pasta ou ao fechar a aplicação.

## Estrutura do Código

*   **Importações:** Bibliotecas necessárias.
*   **Configuração Inicial e Constantes:** Define o nome do arquivo de configuração e as teclas de atalho padrão.
*   **Variáveis Globais:** Armazenam o estado atual da aplicação (caminho da pasta, teclas, etc.).
*   **Funções de Carregar/Salvar Configuração:** `carregar_configuracao()` e `salvar_configuracao()` lidam com o arquivo JSON.
*   **Funções _core:**
    *   `atualizar_variaveis_caminho()`: Processa o caminho da pasta.
    *   `refresh_desktop_windows()`: Atualiza o Explorer no Windows.
    *   `verificar_e_criar_pasta_core()`: Verifica e/ou cria a pasta alvo.
    *   `ocultar_pasta_core()`: Lógica para ocultar a pasta (Windows: `attrib +h`).
    *   `mostrar_pasta_core()`: Lógica para mostrar a pasta (Windows: `attrib -h`).
*   **Classe `FolderHiderApp`:** Define a interface gráfica com Tkinter, seus widgets e os métodos para interagir com as funções _core e gerenciar eventos.
*   **Bloco Principal (`if __name__ == "__main__":`)**:
    *   Verificações iniciais de dependências (ex: `attrib.exe` no Windows).
    *   Aviso de permissão de administrador (Windows).
    *   Inicializa e executa a aplicação Tkinter.
    *   Limpeza ao fechar (remove os ganchos de teclado).

## Limitações e Observações

*   **Foco no Windows:** A funcionalidade principal de ocultar/mostrar pastas é implementada apenas para Windows usando o comando `attrib.exe`. Em outros sistemas, essas ações não funcionarão.
*   **`attrib.exe`:** A presença e o funcionamento correto do `attrib.exe` (localizado por padrão em `C:\Windows\System32\attrib.exe`) são cruciais no Windows.
*   **Permissões:**
    *   Para modificar atributos de algumas pastas no Windows, podem ser necessários privilégios de administrador.
    *   A biblioteca `keyboard` pode exigir permissões especiais para monitorar teclas globalmente em alguns sistemas (principalmente Linux e macOS).
*   **Segurança:** Ocultar uma pasta desta forma não é um método de segurança robusto. Usuários com conhecimento técnico podem facilmente encontrar pastas ocultas. Não use esta ferramenta para proteger dados sensíveis de forma crítica.

## Possíveis Melhorias Futuras

*   Implementar funcionalidade de ocultar/mostrar para Linux e macOS (ex: renomear para `.nome_da_pasta`).
*   Interface gráfica para configurar as teclas de atalho diretamente na aplicação.
*   Opção para minimizar para a bandeja do sistema (system tray).
*   Adicionar criptografia básica ou proteção por senha (aumentaria a complexidade significativamente).
```
