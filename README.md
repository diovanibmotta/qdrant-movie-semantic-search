# 🎬 Qdrant Movie Semantic Search

Projeto de busca semântica de filmes utilizando **Qdrant** como banco de dados vetorial e **Sentence Transformers** para geração de embeddings. O objetivo é demonstrar como diferentes estratégias de segmentação de texto (chunking) impactam a qualidade dos resultados em uma busca por similaridade.

## 🎯 Objetivo

Este projeto explora três estratégias de chunking aplicadas às sinopses de 50 filmes clássicos:

- **Fixed-size chunks** — divisão em blocos de tamanho fixo (em palavras) com sobreposição
- **Sentence chunks** — agrupamento de sentenças em blocos de até N frases
- **Paragraph chunks** — separação por parágrafos (fallback para texto completo)

Cada sinopse é processada pelas três estratégias, gerando embeddings independentes que são armazenados como **named vectors** em uma única coleção no Qdrant. Isso permite comparar lado a lado como cada abordagem responde a uma mesma consulta semântica.

## 📋 Pré-requisitos

- Python 3.10+
- Conta no [Qdrant Cloud](https://cloud.qdrant.io/) (gratuita)

## ☁️ Configurando o Qdrant Cloud

### 1. Criar uma conta

1. Acesse [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
2. Clique em **Sign Up** e crie sua conta (pode usar GitHub, Google ou e-mail)
3. Confirme seu e-mail se necessário

### 2. Criar um cluster

1. No painel do Qdrant Cloud, clique em **Clusters** → **Create Cluster**
2. Selecione o plano **Free** (1GB de armazenamento, suficiente para este projeto)
3. Escolha a região mais próxima (ex: `us-east-1` ou `eu-west-1`)
4. Dê um nome ao cluster e clique em **Create**
5. Aguarde alguns segundos até o status ficar **Active**

### 3. Obter a URL do cluster

1. Na lista de clusters, clique no cluster criado
2. Copie a **URL** exibida (formato: `https://<cluster-id>.<region>.aws.cloud.qdrant.io:6333`)

### 4. Gerar a API Key

1. No painel do cluster, vá para a aba **API Keys**
2. Clique em **Create API Key**
3. Dê um nome descritivo (ex: `movie-search-dev`)
4. Copie a chave gerada — ela não será exibida novamente

### 5. Configurar as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como modelo):

```env
QDRANT_URL=https://seu-cluster-id.regiao.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=sua-api-key-aqui
```

> ⚠️ Nunca commite o arquivo `.env` — ele já está no `.gitignore`.

## 🚀 Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/qdrant-movie-semantic-search.git
cd qdrant-movie-semantic-search
```

### 2. Criar ambiente virtual e instalar dependências

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configurar o `.env`

```bash
cp .env.example .env
# Edite o .env com sua URL e API Key do Qdrant Cloud
```

### 4. Popular o banco vetorial

```bash
python populate_movies.py
```

Este script:
- Carrega os 50 filmes do `movies.json`
- Aplica as três estratégias de chunking em cada sinopse
- Gera embeddings com o modelo `all-MiniLM-L6-v2` (384 dimensões)
- Cria a coleção `day1_semantic_search` no Qdrant com três named vectors
- Faz upload de todos os pontos

### 5. Executar buscas semânticas

```bash
python search_movies.py
```

Este script:
- Executa consultas semânticas de exemplo comparando as três estratégias
- Exibe os top 3 resultados de cada estratégia com score de similaridade
- Apresenta uma análise estatística dos chunks gerados

## 📊 Resultado esperado

### Busca comparativa

```
Query: 'a hero seeking revenge for the murder of his family'

--- FIXED CHUNKING ---
1. Gladiator
   Score: 0.742
   Chunk: Maximus Decimus Meridius, Rome's most respected and beloved general...
2. The Revenant
   Score: 0.698
   Chunk: In the unforgiving wilderness of the 1820s American frontier...
...

--- SENTENCE CHUNKING ---
...

--- PARAGRAPH CHUNKING ---
...
```

### Análise de estratégias

```
CHUNKING STRATEGY ANALYSIS
========================================

FIXED STRATEGY:
  Total chunks: 50
  Avg chunk size: 810 chars
  Size range: 746-961 chars

SENTENCE STRATEGY:
  Total chunks: 150
  Avg chunk size: 270 chars
  Size range: 80-350 chars

PARAGRAPH STRATEGY:
  Total chunks: 50
  Avg chunk size: 810 chars
  Size range: 746-961 chars
```

> Os valores exatos variam conforme o conteúdo das sinopses.

## 📁 Estrutura do projeto

```
qdrant-movie-semantic-search/
├── .env.example          # Template das variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Documentação do projeto
├── requirements.txt      # Dependências Python
├── movies.json           # Dataset com 50 filmes (título, ano, gênero, sinopse)
├── populate_movies.py    # Script de chunking, embedding e upload para Qdrant
└── search_movies.py      # Script de busca semântica e análise
```

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| [Qdrant](https://qdrant.tech/) | Banco de dados vetorial para busca por similaridade |
| [Sentence Transformers](https://www.sbert.net/) | Geração de embeddings semânticos |
| [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | Modelo de embedding (384 dimensões) |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Carregamento de variáveis de ambiente |

## 📝 Licença

MIT
