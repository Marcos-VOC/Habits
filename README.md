# Habits

Habits é um gerenciador pessoal de hábitos para terminal, feito para Linux Fedora com Python, Rich e SQLite.

A interface do usuário é em português, já o código interno, as tabelas/colunas do banco e as chaves de configuração usam nomes em inglês, visando estudo da linguagem e aprendizado da norma padrão e boas práticas.

## Funcionalidades

- Menu interativo no terminal com Rich.
- Menu de primeiros passos quando ainda não existe nenhum hábito.
- Menus dinâmicos que escondem ações impossíveis no estado atual dos dados.
- Criar, editar, listar, arquivar, desarquivar e apagar hábitos.
- Seletor de ícones por categoria, ainda permitindo qualquer emoji suportado pelo terminal.
- Registro de uma entrada por hábito por dia, com duração e nota opcionais.
- Cálculo de sequências atuais para hábitos diários, de segunda a sexta e semanais.
- Histórico por hábito.
- Backup/exportação em Configurações, com backup completo, exportação JSON e exportação CSV.
- Comandos rápidos com aliases em português e inglês.
- Comandos diretos por nome do hábito, como `habits check treinar`.
- Visualização técnica do SQLite por `habits db` ou `habits banco`.
- Guia de comandos por `habits guia`.
- Caminhos exibidos diretamente no menu de configurações e por `habits paths`.
- Instalação/desinstalação local do usuário por `run.sh`.

## Regras Importantes

- `Todos os dias` significa uma conclusão esperada por dia de calendário.
- `Segunda a sexta` ignora sábado e domingo no cálculo de sequência.
- `X vezes por semana` aceita uma meta semanal de 1 a 7.
- Habits guarda no máximo uma entrada por hábito por data.
- Confirmações usam `S`/`N`.
- Apagar um hábito é permanente e também remove seu histórico.
- As listas visuais usam números sequenciais; os IDs reais do SQLite continuam estáveis internamente para evitar bugs.
- Entrada de cor não diferencia maiúsculas/minúsculas, então `azul`, `Azul` e `AZUL` resolvem para a mesma cor (tal feature ainda não foi 100% polida e implementada, aguardando interface visual).

## Instalação

```bash
./run.sh install
```

Isso instala o comando `habits` para o usuário atual em:

```text
~/.local/bin/habits
```

A desinstalação pergunta se deve manter ou remover os dados do usuário:

```bash
./run.sh uninstall
```

## Execução

Durante o desenvolvimento, é possível rodar sem instalar:

```bash
./run.sh
./run.sh hoje
```

Depois de instalar:

```bash
habits
habits hoje
habits today
habits check
habits registrar
habits check treinar
habits streak
habits sequencia
habits history
habits historico
habits historico estudar
habits guia
habits comandos
habits paths
habits caminhos
habits db
habits banco
```

## Dados

Habits guarda os dados do usuário em diretórios padrão do Linux:

```text
~/.local/share/habits/habits.db
~/.config/habits/config.json
```

Testes e desenvolvimento podem sobrescrever esses caminhos:

```bash
HABITS_DB_PATH=/tmp/habits-test.db HABITS_CONFIG_PATH=/tmp/habits-config.json ./run.sh
```

Backups e exportações são salvos por padrão em:

```text
~/Downloads/habits-backups/
```

Testes e desenvolvimento podem sobrescrever esse diretório:

```bash
HABITS_BACKUP_DIR=/tmp/habits-backups ./run.sh
```

## Desenvolvimento

Dependência de execução:

```text
rich
```

Dependência de desenvolvimento/testes:

```text
pytest
```

Rodar testes:

```bash
./run.sh test
```

Os testes usam caminhos temporários e não tocam nos seus dados reais do Habits, uma vez que um banco de dados exclusivo é criado na máquina após instalação.

## Estrutura do Projeto

```text
src/habits/
  main.py          roteamento da CLI
  db.py            conexão e schema do SQLite
  models.py        CRUD e acesso aos dados
  stats.py         cálculo de sequências
  backup.py        auxiliares de backup e exportação
  config.py        configuração do usuário
  palette.py       paleta de cores
  paths.py         caminhos de dados/configuração
  ui/              interface de terminal com Rich
tests/             suíte pytest
```

## Roadmap

- Adicionar estatísticas avançadas.
- Adicionar alertas avançados.
- Adicionar gráficos.
- Adicionar interface GTK/libadwaita no futuro.
