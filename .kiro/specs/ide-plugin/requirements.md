# Requirements Document - IDE Plugin for Bsmart-ALM

## Introduction

Plugin para IDEs (VS Code, Kiro, Cursor, etc.) que permite desenvolvedores se autenticarem no Bsmart-ALM, visualizarem seus work items atribuídos, selecionarem tarefas e exportarem o contexto para ferramentas de coding assistido por IA (Copilot, Kiro, Continue, etc.).

O plugin atua como ponte entre o sistema de gerenciamento (Bsmart-ALM) e o ambiente de desenvolvimento, trazendo as tarefas diretamente para onde o código é escrito.

---

## Requirements

### Requirement 1: Autenticação no Bsmart-ALM

**User Story:** Como desenvolvedor, quero me autenticar no Bsmart-ALM através do plugin da IDE, para acessar minhas tarefas sem sair do ambiente de desenvolvimento.

#### Acceptance Criteria

1. WHEN o desenvolvedor abre o plugin THEN o sistema SHALL exibir tela de login
2. WHEN o desenvolvedor insere credenciais válidas THEN o sistema SHALL armazenar token JWT de forma segura
3. WHEN o token expira THEN o sistema SHALL solicitar nova autenticação
4. IF o desenvolvedor já está autenticado THEN o sistema SHALL carregar automaticamente os dados
5. WHEN o desenvolvedor faz logout THEN o sistema SHALL limpar todas as credenciais armazenadas

---

### Requirement 2: Seleção de Projeto e Tenant

**User Story:** Como desenvolvedor, quero selecionar o projeto em que estou trabalhando, para visualizar apenas as tarefas relevantes.

#### Acceptance Criteria

1. WHEN o desenvolvedor está autenticado THEN o sistema SHALL listar todos os projetos do seu tenant
2. WHEN o desenvolvedor seleciona um projeto THEN o sistema SHALL armazenar a seleção
3. WHEN o desenvolvedor troca de projeto THEN o sistema SHALL atualizar a lista de work items
4. IF o desenvolvedor pertence a múltiplos projetos THEN o sistema SHALL permitir troca rápida entre eles
5. WHEN o desenvolvedor reabre a IDE THEN o sistema SHALL lembrar o último projeto selecionado

---

### Requirement 3: Visualização de Work Items

**User Story:** Como desenvolvedor, quero visualizar meus work items atribuídos, para saber quais tarefas preciso executar.

#### Acceptance Criteria

1. WHEN o desenvolvedor seleciona um projeto THEN o sistema SHALL listar work items atribuídos a ele
2. WHEN a lista é exibida THEN o sistema SHALL mostrar título, status, prioridade e descrição
3. WHEN o desenvolvedor clica em um work item THEN o sistema SHALL exibir detalhes completos
4. IF há novos work items THEN o sistema SHALL notificar o desenvolvedor
5. WHEN o desenvolvedor filtra por status THEN o sistema SHALL mostrar apenas work items correspondentes

---

### Requirement 4: Exportação de Contexto para AI Coding Tools

**User Story:** Como desenvolvedor, quero exportar o contexto de um work item para ferramentas de IA, para que o assistente entenda o que preciso implementar.

#### Acceptance Criteria

1. WHEN o desenvolvedor seleciona um work item THEN o sistema SHALL exibir botão "Export to AI"
2. WHEN o desenvolvedor clica em "Export to AI" THEN o sistema SHALL gerar contexto formatado
3. WHEN o contexto é gerado THEN o sistema SHALL incluir título, descrição, acceptance criteria e arquivos relacionados
4. IF o work item tem especificações THEN o sistema SHALL incluir no contexto
5. WHEN o contexto é exportado THEN o sistema SHALL copiar para clipboard OU enviar direto para ferramenta de IA

---

### Requirement 5: Integração com Ferramentas de IA

**User Story:** Como desenvolvedor, quero enviar work items diretamente para Copilot/Kiro/Continue, para começar a codificar imediatamente.

#### Acceptance Criteria

1. WHEN o desenvolvedor exporta contexto THEN o sistema SHALL detectar ferramentas de IA disponíveis
2. WHEN Copilot está ativo THEN o sistema SHALL enviar contexto via API do Copilot
3. WHEN Continue está instalado THEN o sistema SHALL enviar contexto via API do Continue
4. WHEN Kiro está ativo THEN o sistema SHALL enviar contexto via API do Kiro
5. IF nenhuma ferramenta está disponível THEN o sistema SHALL copiar para clipboard

---

### Requirement 6: Atualização de Status do Work Item

**User Story:** Como desenvolvedor, quero atualizar o status do work item diretamente do plugin, para manter o projeto sincronizado.

#### Acceptance Criteria

1. WHEN o desenvolvedor inicia trabalho em um work item THEN o sistema SHALL permitir marcar como "In Progress"
2. WHEN o desenvolvedor completa o trabalho THEN o sistema SHALL permitir marcar como "Done"
3. WHEN o status é atualizado THEN o sistema SHALL sincronizar com Bsmart-ALM via API
4. IF há erro na sincronização THEN o sistema SHALL notificar o desenvolvedor
5. WHEN o desenvolvedor adiciona comentário THEN o sistema SHALL enviar para o work item

---

### Requirement 7: Sincronização com Git

**User Story:** Como desenvolvedor, quero que o plugin detecte quando faço commit/push, para atualizar automaticamente o work item.

#### Acceptance Criteria

1. WHEN o desenvolvedor faz commit THEN o sistema SHALL detectar via Git hooks
2. WHEN o commit menciona work item ID THEN o sistema SHALL associar commit ao work item
3. WHEN o desenvolvedor faz push THEN o sistema SHALL atualizar status do work item
4. IF o push é para branch principal THEN o sistema SHALL marcar work item como "Done"
5. WHEN há conflitos THEN o sistema SHALL notificar no work item

---

### Requirement 8: Visualização de Arquivos Relacionados

**User Story:** Como desenvolvedor, quero ver quais arquivos estão relacionados ao work item, para saber onde fazer mudanças.

#### Acceptance Criteria

1. WHEN o work item tem arquivos relacionados THEN o sistema SHALL listar os arquivos
2. WHEN o desenvolvedor clica em um arquivo THEN o sistema SHALL abrir no editor
3. WHEN o desenvolvedor adiciona arquivo THEN o sistema SHALL associar ao work item
4. IF há documentação técnica THEN o sistema SHALL exibir link
5. WHEN há dependências THEN o sistema SHALL listar work items relacionados

---

### Requirement 9: Modo Offline

**User Story:** Como desenvolvedor, quero trabalhar offline, para continuar codificando mesmo sem conexão com Bsmart-ALM.

#### Acceptance Criteria

1. WHEN a conexão cai THEN o sistema SHALL entrar em modo offline
2. WHEN em modo offline THEN o sistema SHALL permitir visualizar work items em cache
3. WHEN o desenvolvedor faz mudanças offline THEN o sistema SHALL armazenar localmente
4. WHEN a conexão retorna THEN o sistema SHALL sincronizar mudanças automaticamente
5. IF há conflitos THEN o sistema SHALL solicitar resolução manual

---

### Requirement 10: Configurações e Preferências

**User Story:** Como desenvolvedor, quero configurar o plugin, para personalizar minha experiência.

#### Acceptance Criteria

1. WHEN o desenvolvedor abre configurações THEN o sistema SHALL exibir opções disponíveis
2. WHEN o desenvolvedor configura URL do servidor THEN o sistema SHALL validar conexão
3. WHEN o desenvolvedor escolhe ferramenta de IA padrão THEN o sistema SHALL salvar preferência
4. IF o desenvolvedor quer notificações THEN o sistema SHALL permitir configurar
5. WHEN o desenvolvedor exporta configurações THEN o sistema SHALL gerar arquivo de config
