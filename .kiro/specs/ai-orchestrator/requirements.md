# Requirements Document - AI Coding Orchestrator

## Introduction

Orquestrador autônomo que consome work items do Bsmart-ALM, distribui tarefas para agentes de coding AI (Aider, OpenHands), executa validações com ferramentas de qualidade (Continue, AI Checks), e atualiza o status das tarefas automaticamente ao fazer commit/push no Git.

O orquestrador atua como um "desenvolvedor virtual" que pega tarefas da fila, implementa usando IA, valida a qualidade, e entrega o código pronto.

---

## Requirements

### Requirement 1: Consumo de Work Items do Bsmart-ALM

**User Story:** Como orquestrador, quero consumir work items da fila do Bsmart-ALM, para processar tarefas automaticamente.

#### Acceptance Criteria

1. WHEN o orquestrador inicia THEN o sistema SHALL conectar na API do Bsmart-ALM
2. WHEN há work items com status "Ready" THEN o sistema SHALL buscar próximo da fila
3. WHEN um work item é selecionado THEN o sistema SHALL marcar como "In Progress"
4. IF o work item tem prioridade alta THEN o sistema SHALL processar primeiro
5. WHEN o work item é processado THEN o sistema SHALL atualizar status via API

---

### Requirement 2: Seleção de Agente de Coding AI

**User Story:** Como orquestrador, quero selecionar o agente de IA mais adequado para cada tarefa, para otimizar qualidade e custo.

#### Acceptance Criteria

1. WHEN um work item é selecionado THEN o sistema SHALL analisar complexidade
2. WHEN a tarefa é simples THEN o sistema SHALL usar Aider com Ollama (local/gratuito)
3. WHEN a tarefa é complexa THEN o sistema SHALL usar Aider com Grok ou Gemini
4. IF a tarefa requer múltiplos arquivos THEN o sistema SHALL usar OpenHands
5. WHEN o agente é selecionado THEN o sistema SHALL registrar no log

---

### Requirement 3: Integração com Aider

**User Story:** Como orquestrador, quero executar Aider para implementar tarefas, para gerar código automaticamente.

#### Acceptance Criteria

1. WHEN Aider é selecionado THEN o sistema SHALL preparar contexto do work item
2. WHEN o contexto está pronto THEN o sistema SHALL executar Aider via CLI
3. WHEN Aider com Ollama THEN o sistema SHALL usar modelo local (codellama, deepseek-coder)
4. WHEN Aider com API THEN o sistema SHALL usar Grok ou Gemini
5. WHEN Aider completa THEN o sistema SHALL capturar arquivos modificados

---

### Requirement 4: Integração com OpenHands

**User Story:** Como orquestrador, quero executar OpenHands para tarefas complexas, para ter agente autônomo completo.

#### Acceptance Criteria

1. WHEN OpenHands é selecionado THEN o sistema SHALL iniciar ambiente Docker
2. WHEN o ambiente está pronto THEN o sistema SHALL enviar work item via API
3. WHEN OpenHands executa THEN o sistema SHALL monitorar progresso
4. IF OpenHands falha THEN o sistema SHALL tentar com Aider
5. WHEN OpenHands completa THEN o sistema SHALL extrair mudanças do container

---

### Requirement 5: Validação com Continue

**User Story:** Como orquestrador, quero validar código gerado com Continue, para garantir qualidade antes do commit.

#### Acceptance Criteria

1. WHEN código é gerado THEN o sistema SHALL executar Continue para review
2. WHEN Continue analisa THEN o sistema SHALL verificar padrões de código
3. WHEN há problemas THEN o sistema SHALL solicitar correção ao agente
4. IF Continue aprova THEN o sistema SHALL prosseguir para testes
5. WHEN validação falha 3 vezes THEN o sistema SHALL marcar work item como "Blocked"

---

### Requirement 6: Execução de AI Checks

**User Story:** Como orquestrador, quero executar verificações automáticas de IA, para validar segurança e qualidade.

#### Acceptance Criteria

1. WHEN código é gerado THEN o sistema SHALL executar AI Checks
2. WHEN AI Checks executa THEN o sistema SHALL verificar vulnerabilidades
3. WHEN há vulnerabilidades THEN o sistema SHALL solicitar correção
4. IF há problemas de performance THEN o sistema SHALL notificar
5. WHEN todos os checks passam THEN o sistema SHALL aprovar para commit

---

### Requirement 7: Execução de Testes Automatizados

**User Story:** Como orquestrador, quero executar testes automatizados, para garantir que código funciona.

#### Acceptance Criteria

1. WHEN código é validado THEN o sistema SHALL executar testes unitários
2. WHEN testes unitários passam THEN o sistema SHALL executar testes de integração
3. WHEN testes falham THEN o sistema SHALL enviar erro para agente corrigir
4. IF testes passam após 3 tentativas THEN o sistema SHALL aprovar
5. WHEN todos os testes passam THEN o sistema SHALL prosseguir para commit

---

### Requirement 8: Commit e Push Automático

**User Story:** Como orquestrador, quero fazer commit e push automaticamente, para entregar código no repositório.

#### Acceptance Criteria

1. WHEN código é aprovado THEN o sistema SHALL criar branch com nome do work item
2. WHEN branch é criada THEN o sistema SHALL fazer commit com mensagem descritiva
3. WHEN commit é feito THEN o sistema SHALL incluir ID do work item na mensagem
4. WHEN push é executado THEN o sistema SHALL enviar para repositório remoto
5. IF há conflitos THEN o sistema SHALL tentar resolver automaticamente

---

### Requirement 9: Criação de Pull Request

**User Story:** Como orquestrador, quero criar pull request automaticamente, para facilitar code review humano.

#### Acceptance Criteria

1. WHEN push é concluído THEN o sistema SHALL criar PR via API do GitHub/GitLab
2. WHEN PR é criado THEN o sistema SHALL incluir descrição do work item
3. WHEN PR é criado THEN o sistema SHALL adicionar labels apropriados
4. IF há reviewers configurados THEN o sistema SHALL solicitar review
5. WHEN PR é criado THEN o sistema SHALL adicionar link no work item

---

### Requirement 10: Atualização de Status no Bsmart-ALM

**User Story:** Como orquestrador, quero atualizar status do work item automaticamente, para manter projeto sincronizado.

#### Acceptance Criteria

1. WHEN PR é criado THEN o sistema SHALL marcar work item como "In Review"
2. WHEN PR é aprovado THEN o sistema SHALL marcar work item como "Done"
3. WHEN há erro THEN o sistema SHALL marcar work item como "Blocked"
4. IF tarefa falha THEN o sistema SHALL adicionar comentário com erro
5. WHEN work item é concluído THEN o sistema SHALL notificar assignee

---

### Requirement 11: Monitoramento e Logs

**User Story:** Como administrador, quero monitorar execução do orquestrador, para identificar problemas.

#### Acceptance Criteria

1. WHEN orquestrador executa THEN o sistema SHALL registrar logs detalhados
2. WHEN há erro THEN o sistema SHALL registrar stack trace completo
3. WHEN tarefa completa THEN o sistema SHALL registrar tempo de execução
4. IF há falhas recorrentes THEN o sistema SHALL alertar administrador
5. WHEN solicitado THEN o sistema SHALL gerar relatório de execuções

---

### Requirement 12: Configuração de Modelos de IA

**User Story:** Como administrador, quero configurar quais modelos de IA usar, para controlar custo e qualidade.

#### Acceptance Criteria

1. WHEN administrador configura THEN o sistema SHALL permitir escolher modelos
2. WHEN Ollama é configurado THEN o sistema SHALL listar modelos locais disponíveis
3. WHEN API externa é configurada THEN o sistema SHALL validar chave de API
4. IF há limite de custo THEN o sistema SHALL respeitar orçamento
5. WHEN modelo não está disponível THEN o sistema SHALL usar fallback

---

### Requirement 13: Fila de Processamento

**User Story:** Como orquestrador, quero processar múltiplos work items em paralelo, para aumentar throughput.

#### Acceptance Criteria

1. WHEN há múltiplos work items THEN o sistema SHALL processar em paralelo
2. WHEN há limite de workers THEN o sistema SHALL respeitar máximo configurado
3. WHEN worker está ocupado THEN o sistema SHALL enfileirar próximo work item
4. IF há dependências THEN o sistema SHALL respeitar ordem
5. WHEN worker completa THEN o sistema SHALL pegar próximo da fila

---

### Requirement 14: Retry e Error Handling

**User Story:** Como orquestrador, quero tentar novamente quando há falhas, para aumentar taxa de sucesso.

#### Acceptance Criteria

1. WHEN há erro temporário THEN o sistema SHALL tentar novamente
2. WHEN falha 3 vezes THEN o sistema SHALL marcar como "Blocked"
3. WHEN há timeout THEN o sistema SHALL cancelar e tentar com outro agente
4. IF há erro de API THEN o sistema SHALL aguardar e tentar novamente
5. WHEN erro é permanente THEN o sistema SHALL notificar e parar

---

### Requirement 15: Dashboard de Monitoramento

**User Story:** Como administrador, quero visualizar dashboard do orquestrador, para acompanhar execuções.

#### Acceptance Criteria

1. WHEN administrador acessa dashboard THEN o sistema SHALL mostrar work items em processamento
2. WHEN há estatísticas THEN o sistema SHALL exibir taxa de sucesso
3. WHEN há custos THEN o sistema SHALL mostrar gasto com APIs
4. IF há erros THEN o sistema SHALL destacar em vermelho
5. WHEN solicitado THEN o sistema SHALL exportar métricas
