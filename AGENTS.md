# Habits - Contexto do Projeto

## Produto

- Nome do projeto/produto: Habits.
- Comando principal: `habits`.
- Idioma da interface do usuário: português.
- Código interno, tabelas/colunas do banco e chaves de configuração: inglês.
- A CLI aceita aliases em português e inglês para subcomandos.

## Alvo

- Fedora Linux com GNOME.
- Aplicativo de terminal em Python 3 usando Rich.
- SQLite via biblioteca padrão `sqlite3` do Python.
- Execução offline, sem sudo e sem processos em segundo plano.

## Locais dos Dados

- Banco do usuário: `~/.local/share/habits/habits.db`.
- Configuração do usuário: `~/.config/habits/config.json`.
- Testes e desenvolvimento podem sobrescrever caminhos com:
  - `HABITS_DB_PATH`
  - `HABITS_CONFIG_PATH`

## Instalação/Desinstalação

- `./run.sh install` instala o app para o usuário atual.
- `./run.sh uninstall` remove o comando do usuário e pergunta se deve manter ou remover os dados.
- Reinstalar deve reutilizar os dados existentes quando eles forem mantidos.

## Escopo da v0.1

- CLI com Rich e menu interativo.
- Tela de boas-vindas.
- Menu de primeiros passos quando ainda não existe nenhum hábito.
- Menus dinâmicos para ações dependentes do estado dos dados.
- Criar, listar, arquivar, desarquivar e apagar hábitos.
- Registrar uma entrada por hábito por dia, com duração e nota opcionais.
- Cálculo de sequência atual.
- Comandos rápidos com aliases PT/EN.
- Comandos diretos por nome do hábito.
- Histórico por hábito.
- Visualizador do banco para inspeção técnica.
- Guia de comandos.
- Visualizador de caminhos dentro de Configurações e como comando direto.
- Gerenciamento básico de configuração.
- Testes básicos desde o começo.

## Escopo da v0.2

- Editar nome, ícone, cor, frequência e meta diária de um hábito pelo gerenciador interativo.
- Seletor de ícones organizado por categorias numeradas, com entrada manual de emoji ainda disponível.
- Fluxo de backup/exportação dentro de Configurações:
  - Backup completo copia banco e configuração.
  - Exportação JSON inclui configuração, hábitos e entradas.
  - Exportação CSV escreve `habits.csv` e `entries.csv`.
- Arquivos de backup/exportação vão por padrão para `~/Downloads/habits-backups/`.
- Testes e desenvolvimento podem sobrescrever o destino de backup/exportação com `HABITS_BACKUP_DIR`.

## Adiado

- Gráficos com Matplotlib.
- Interface GTK 4/libadwaita.
- Alertas avançados.
- Estatísticas avançadas.

## Decisões de Comportamento

- A semana começa na segunda-feira e termina no domingo.
- `weekdays` significa segunda a sexta.
- Sábado e domingo são válidos para hábitos diários e semanais.
- Se uma entrada já existe para hoje, o app pergunta se deve atualizá-la.
- Arquivar um hábito nunca apaga seu histórico.
- Telas do terminal devem limpar antes de renderizar novo conteúdo de menu.
- O banner do Habits deve aparecer em todas as telas interativas de menu, não apenas na tela inicial.
- O banner deve degradar bem em larguras menores de terminal.
- Labels de frequência exibidas ao usuário devem ficar em português.
- Campo vazio em prompt de ID/número de hábito deve cancelar e voltar em direção ao menu principal.
- A configuração não deve incluir opção de saudação.
- Entrada vazia ou inválida do usuário deve ser tratada com mensagens amigáveis, nunca com traceback cru.
- Prompts de pausa/retorno devem usar o mesmo estilo de input com borda das escolhas de menu.
- Telas dependentes vazias devem renderizar um aviso amigável e um prompt com borda para pressionar Enter e voltar.
- Quando o banco não tem nenhum hábito, o menu interativo deve mostrar um menu reduzido de primeiros passos apenas com ações que fazem sentido.
- Menus devem esconder ações impossíveis quando existe um motivo claro no estado dos dados, como não haver hábitos ativos ou arquivados.
- Arquivar deve ter fluxo correspondente para desarquivar.
- Apagar um hábito é definitivo, remove suas entradas e exige confirmação forte pelo nome exato do hábito mais `S`/`N`.
- Histórico por hábito é uma tela de usuário; `db` continua sendo uma visão técnica/debug.
- Histórico por hábito na UI interativa deve separar tela de seleção e tela de resultado; ao sair do resultado, volta para a seleção de histórico.
- O menu principal deve mostrar `Registrar hábito` antes de `Menu do dia`.
- Histórico de hábito deve ficar dentro de `Gerenciar hábitos`, não como opção de topo no menu principal.
- Caminhos devem aparecer diretamente em `Configurações`, não como opção selecionável ou item separado de topo no menu interativo.
- Visualizador do banco deve continuar disponível como comando técnico direto, não como item regular do menu interativo.
- Entrada de ícone deve oferecer categorias numeradas, mas ainda aceitar qualquer emoji/caractere curto que o terminal renderize.
- Comandos diretos podem aceitar argumentos por nome do hábito, por exemplo `habits check treinar` e `habits historico estudar`.
- Se uma busca direta por nome encontrar vários hábitos, o usuário deve escolher entre os resultados.
- O input do menu principal também pode aceitar comando direto, por exemplo `habits registrar Correr`, não apenas escolhas numéricas.
- Confirmações devem usar `S`/`N` em português, não `y/n`.
- Metas de frequência semanal devem ficar limitadas a 1-7, porque o modelo atual guarda no máximo uma entrada por hábito por data.
- `daily` significa uma conclusão esperada por dia de calendário, não várias ocorrências no mesmo dia.
- Entrada de cor deve ignorar maiúsculas/minúsculas.
- Mensagens de validação visíveis ao usuário devem ficar em português.
- Escolhas inválidas de menu não devem empilhar caixas de prompt; a tela deve limpar/re-renderizar em volta do aviso.
- Inputs encaixotados sequenciais devem ser transitórios: após Enter, a caixa ativa desaparece e fica uma linha simples de confirmação antes do próximo input.
- Na criação de hábito, inputs encaixotados como frequência e meta semanal também devem ser transitórios; apenas o input ativo atual mantém borda verde.
- Seleção de hábito visível ao usuário deve usar números visuais sequenciais (`Nº`) mapeados internamente para IDs estáveis do banco. IDs reais devem aparecer apenas em visões técnicas/debug.
- Editar um hábito altera apresentação e regras futuras, mas não reescreve entradas antigas.
- Editar frequência deve pedir nova meta semanal apenas quando a nova frequência for `weekly`.
- Meta diária vazia durante edição significa remover a meta diária.
- Backup/exportação pertence a Configurações, enquanto a tabela de caminhos continua visível diretamente na tela de Configurações.
