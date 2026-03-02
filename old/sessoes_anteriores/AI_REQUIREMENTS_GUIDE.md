# 🤖 Guia de Geração de Requisitos com IA

## ✨ Nova Funcionalidade Implementada!

Agora você pode gerar requisitos automaticamente usando IA (Ollama + llama3.2)!

## 🎯 O que foi implementado

### Backend
- ✅ Cliente Ollama para comunicação com a IA
- ✅ Prompts otimizados para geração de requisitos
- ✅ Endpoint `/api/v1/requirements/generate` - Gera requisitos
- ✅ Endpoint `/api/v1/requirements/approve` - Aprova e cria work items
- ✅ Formato EARS (Easy Approach to Requirements Syntax)

### Frontend
- ✅ Página de detalhes do projeto renovada
- ✅ Interface para descrever o projeto
- ✅ Visualização dos requisitos gerados
- ✅ Aprovação e criação automática de work items

## 🚀 Como Usar

### 1. Certifique-se que o Ollama está rodando

```bash
# Verificar se Ollama está rodando
curl http://localhost:11434/api/tags

# Se não estiver, iniciar Ollama
ollama serve
```

### 2. Reiniciar o Backend

```bash
# Parar o backend atual
kill -9 $(lsof -t -i:8086)

# Reiniciar
make dev
```

### 3. Usar no Frontend

1. **Acessar**: http://localhost:3000
2. **Login**: admin@test.com / admin123456
3. **Ir para Projects**
4. **Clicar em um projeto** (ou criar um novo)
5. **Descrever o projeto** na caixa de texto
6. **Clicar em "Generate Requirements"**
7. **Aguardar** a IA gerar os requisitos (15-30 segundos)
8. **Revisar** os requisitos gerados
9. **Remover** requisitos indesejados (botão X)
10. **Aprovar** clicando em "Approve & Create Work Items"

## 📝 Exemplo de Descrição

```
Preciso de um sistema de gerenciamento de biblioteca online.

Funcionalidades principais:
- Usuários podem buscar livros por título, autor ou categoria
- Sistema de empréstimo com controle de datas
- Notificações automáticas de devolução
- Área administrativa para gerenciar o catálogo
- Relatórios de livros mais emprestados
- Sistema de reservas para livros emprestados

Requisitos técnicos:
- Interface web responsiva
- Suporte para 1000 usuários simultâneos
- Backup diário automático
- Integração com sistema de pagamento para multas
```

## 🎨 O que a IA Gera

Para cada requisito, a IA gera:

1. **Título**: Nome descritivo do requisito
2. **User Story**: No formato "As a [role], I want [feature], so that [benefit]"
3. **Acceptance Criteria**: Critérios testáveis no formato EARS:
   - WHEN [event] THEN [system] SHALL [response]
   - IF [condition] THEN [system] SHALL [response]
4. **Priority**: high, medium ou low
5. **Type**: requirement

## ✅ Resultado

Após aprovar, o sistema:
- ✅ Cria work items automaticamente
- ✅ Cada requisito vira um work item em status "draft"
- ✅ Mantém a descrição com user story e acceptance criteria
- ✅ Vincula ao projeto correto

## 🔧 Configuração do Ollama

### Verificar modelo instalado
```bash
ollama list
```

Deve mostrar:
```
NAME                    ID              SIZE      MODIFIED
llama3.2:latest         a80c4f17acd5    2.0 GB    8 months ago
```

### Se precisar instalar
```bash
ollama pull llama3.2:latest
```

### Testar Ollama
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:latest",
  "prompt": "Hello, how are you?",
  "stream": false
}'
```

## 🐛 Troubleshooting

### Erro: "Failed to generate requirements"

**Causa**: Ollama não está rodando ou não responde

**Solução**:
```bash
# Verificar se Ollama está rodando
ps aux | grep ollama

# Iniciar Ollama
ollama serve

# Em outro terminal, testar
curl http://localhost:11434/api/tags
```

### Erro: "Connection refused"

**Causa**: Ollama não está na porta 11434

**Solução**: Verificar em qual porta o Ollama está rodando e atualizar `services/requirements/ollama_client.py`

### Geração muito lenta

**Causa**: Modelo grande ou hardware limitado

**Solução**: 
- Aguardar (primeira geração pode demorar mais)
- Usar modelo menor: `ollama pull llama3.2:1b`
- Atualizar `ollama_client.py` para usar o modelo menor

### Requisitos em inglês

**Causa**: Prompt em inglês

**Solução**: Descrever o projeto em português. A IA vai responder no mesmo idioma.

## 📊 Endpoints da API

### Gerar Requisitos
```bash
POST /api/v1/requirements/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "project_id": "uuid-do-projeto",
  "description": "Descrição do projeto..."
}
```

**Resposta**:
```json
{
  "requirements": [
    {
      "title": "Busca de livros",
      "user_story": "As a library user, I want to search for books...",
      "acceptance_criteria": [
        "WHEN user enters search term THEN system SHALL display matching books",
        "IF no books found THEN system SHALL display helpful message"
      ],
      "type": "requirement",
      "priority": "high"
    }
  ],
  "project_id": "uuid-do-projeto"
}
```

### Aprovar Requisitos
```bash
POST /api/v1/requirements/approve
Content-Type: application/json
Authorization: Bearer <token>

{
  "project_id": "uuid-do-projeto",
  "requirements": [...]
}
```

**Resposta**:
```json
{
  "message": "Created 5 work items",
  "work_items": [
    {
      "id": "uuid",
      "title": "Busca de livros",
      "type": "requirement"
    }
  ]
}
```

## 🎉 Próximos Passos

Agora você pode:

1. **Gerar requisitos** para seus projetos
2. **Revisar e editar** os requisitos gerados
3. **Aprovar** e criar work items automaticamente
4. **Gerenciar** os work items criados na página de Work Items

## 💡 Dicas

- Seja específico na descrição do projeto
- Mencione funcionalidades principais
- Inclua requisitos não-funcionais (performance, segurança)
- Revise sempre os requisitos gerados antes de aprovar
- Remova requisitos duplicados ou irrelevantes

---

**Funcionalidade de IA implementada com sucesso!** 🎊
