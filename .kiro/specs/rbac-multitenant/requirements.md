# Requirements Document - RBAC e Multi-Tenant

## Introduction

Este documento especifica os requisitos para implementação de um sistema completo de controle de acesso baseado em perfis (RBAC) e isolamento multi-tenant real no Bsmart-ALM. O objetivo é permitir que múltiplas empresas usem o sistema de forma isolada, com controle granular de permissões por perfil de usuário.

---

## Requirements

### Requirement 1: Filtro de Work Items por Projeto

**User Story:** Como um usuário do sistema, eu quero filtrar work items por projeto, para que eu possa visualizar apenas os items relevantes ao projeto que estou trabalhando.

#### Acceptance Criteria

1. WHEN o usuário acessa a página de Work Items THEN o sistema SHALL exibir um dropdown de seleção de projeto
2. WHEN o usuário seleciona um projeto no dropdown THEN o sistema SHALL filtrar e exibir apenas os work items daquele projeto
3. WHEN o usuário seleciona "Todos os Projetos" THEN o sistema SHALL exibir todos os work items que o usuário tem permissão para ver
4. WHEN o usuário seleciona um projeto THEN o sistema SHALL salvar a seleção no localStorage
5. WHEN o usuário retorna à página de Work Items THEN o sistema SHALL restaurar a última seleção de projeto
6. WHEN não há projetos disponíveis THEN o sistema SHALL exibir mensagem informativa

---

### Requirement 2: Hierarquia de Empresas (Tenants)

**User Story:** Como um Super Admin, eu quero cadastrar empresas no sistema, para que cada empresa tenha seus próprios dados isolados.

#### Acceptance Criteria

1. WHEN o Super Admin acessa a tela de empresas THEN o sistema SHALL exibir lista de todas as empresas cadastradas
2. WHEN o Super Admin cria uma nova empresa THEN o sistema SHALL solicitar: nome, slug, plano de assinatura
3. WHEN uma empresa é criada THEN o sistema SHALL gerar um tenant_id único
4. WHEN uma empresa é criada THEN o sistema SHALL permitir cadastro de um administrador da empresa
5. WHEN o slug já existe THEN o sistema SHALL rejeitar o cadastro com mensagem de erro
6. WHEN uma empresa é desativada THEN o sistema SHALL impedir login de todos os usuários daquela empresa

---

### Requirement 3: Perfil Super Admin

**User Story:** Como um Super Admin, eu quero ter acesso total ao sistema, para que eu possa gerenciar todas as empresas e seus administradores.

#### Acceptance Criteria

1. WHEN o Super Admin faz login THEN o sistema SHALL permitir acesso a todas as funcionalidades
2. WHEN o Super Admin acessa o sistema THEN o sistema SHALL exibir menu de gerenciamento de empresas
3. WHEN o Super Admin cria uma empresa THEN o sistema SHALL permitir cadastro do Company Admin
4. WHEN o Super Admin visualiza empresas THEN o sistema SHALL exibir métricas de uso de cada empresa
5. WHEN o Super Admin desativa uma empresa THEN o sistema SHALL bloquear acesso de todos os usuários

---

### Requirement 4: Perfil Company Admin

**User Story:** Como um Company Admin, eu quero gerenciar usuários da minha empresa, para que eu possa controlar quem tem acesso e quais permissões cada um possui.

#### Acceptance Criteria

1. WHEN o Company Admin faz login THEN o sistema SHALL exibir apenas dados da sua empresa
2. WHEN o Company Admin acessa usuários THEN o sistema SHALL exibir apenas usuários da sua empresa
3. WHEN o Company Admin cria um usuário THEN o sistema SHALL vincular automaticamente à sua empresa
4. WHEN o Company Admin atribui perfis THEN o sistema SHALL permitir múltiplos perfis por usuário
5. WHEN o Company Admin cria projeto THEN o sistema SHALL vincular automaticamente à sua empresa
6. WHEN o Company Admin tenta acessar dados de outra empresa THEN o sistema SHALL negar acesso

---

### Requirement 5: Perfil Project Manager

**User Story:** Como um Project Manager, eu quero criar e gerenciar projetos, para que eu possa organizar o trabalho da equipe.

#### Acceptance Criteria

1. WHEN o Project Manager cria um projeto THEN o sistema SHALL vincular à sua empresa
2. WHEN o Project Manager adiciona membros ao projeto THEN o sistema SHALL permitir apenas usuários da mesma empresa
3. WHEN o Project Manager atribui perfis no projeto THEN o sistema SHALL permitir: PO, Architect, Developer, QA
4. WHEN o Project Manager cria work items THEN o sistema SHALL vincular ao projeto
5. WHEN o Project Manager atribui work items THEN o sistema SHALL permitir apenas membros do projeto
6. WHEN o Project Manager tenta acessar projeto de outro PM THEN o sistema SHALL verificar se é membro

---

### Requirement 6: Perfil PO / Requirements Analyst

**User Story:** Como um PO/Analista de Requisitos, eu quero fazer upload de documentos e gerar especificações, para que eu possa documentar os requisitos do projeto.

#### Acceptance Criteria

1. WHEN o PO acessa um projeto THEN o sistema SHALL permitir upload de documentos
2. WHEN o PO faz upload de documento THEN o sistema SHALL processar e extrair requisitos
3. WHEN o PO gera especificação THEN o sistema SHALL criar documento de especificação
4. WHEN o PO aprova requisitos THEN o sistema SHALL mudar status para "approved"
5. WHEN o PO tenta gerar arquitetura THEN o sistema SHALL negar acesso
6. WHEN o PO visualiza work items THEN o sistema SHALL exibir apenas do projeto que participa

---

### Requirement 7: Perfil Architect (Analista)

**User Story:** Como um Architect, eu quero gerar arquitetura do sistema, para que os desenvolvedores tenham um guia de implementação.

#### Acceptance Criteria

1. WHEN o Architect acessa projeto com especificação THEN o sistema SHALL permitir gerar arquitetura
2. WHEN o Architect gera arquitetura THEN o sistema SHALL criar documento de arquitetura
3. WHEN o Architect revisa especificação THEN o sistema SHALL permitir adicionar comentários
4. WHEN o Architect tenta aprovar requisitos THEN o sistema SHALL negar acesso
5. WHEN o Architect tenta criar work items THEN o sistema SHALL negar acesso

---

### Requirement 8: Perfil Developer

**User Story:** Como um Developer, eu quero pegar work items e implementar, para que eu possa contribuir com o desenvolvimento do projeto.

#### Acceptance Criteria

1. WHEN o Developer visualiza work items THEN o sistema SHALL exibir apenas items do projeto que participa
2. WHEN o Developer pega um work item THEN o sistema SHALL atribuir a ele automaticamente
3. WHEN o Developer muda status para "in_progress" THEN o sistema SHALL permitir
4. WHEN o Developer muda status para "done" THEN o sistema SHALL permitir
5. WHEN o Developer tenta mudar work item de outro dev THEN o sistema SHALL negar
6. WHEN o Developer tenta aprovar work item THEN o sistema SHALL negar acesso
7. WHEN o Developer tenta gerar especificação THEN o sistema SHALL negar acesso

---

### Requirement 9: Perfil QA (Tester)

**User Story:** Como um QA, eu quero testar work items, para que eu possa garantir a qualidade do software.

#### Acceptance Criteria

1. WHEN o QA visualiza work items THEN o sistema SHALL exibir apenas items "done"
2. WHEN o QA pega work item para teste THEN o sistema SHALL atribuir a ele
3. WHEN o QA aprova work item THEN o sistema SHALL mudar status para "approved"
4. WHEN o QA rejeita work item THEN o sistema SHALL mudar status para "rejected"
5. WHEN o QA rejeita work item THEN o sistema SHALL solicitar motivo da rejeição
6. WHEN o QA tenta implementar work item THEN o sistema SHALL negar acesso

---

### Requirement 10: Kanban por Projeto

**User Story:** Como um usuário do sistema, eu quero visualizar o Kanban filtrado por projeto, para que eu possa focar apenas nos work items do projeto que estou trabalhando.

#### Acceptance Criteria

1. WHEN o usuário acessa o Kanban THEN o sistema SHALL exibir um dropdown de seleção de projeto
2. WHEN o usuário seleciona um projeto THEN o sistema SHALL exibir apenas work items daquele projeto no Kanban
3. WHEN nenhum projeto está selecionado THEN o sistema SHALL solicitar seleção de projeto
4. WHEN o usuário seleciona um projeto THEN o sistema SHALL salvar a seleção no localStorage
5. WHEN o usuário retorna ao Kanban THEN o sistema SHALL restaurar a última seleção de projeto
6. WHEN o usuário arrasta um work item THEN o sistema SHALL validar transições apenas para items do projeto selecionado
7. WHEN o usuário muda de projeto THEN o sistema SHALL recarregar o Kanban com work items do novo projeto

---

### Requirement 11: Isolamento Multi-Tenant

**User Story:** Como um usuário de uma empresa, eu quero ver apenas dados da minha empresa, para que haja privacidade e segurança dos dados.

#### Acceptance Criteria

1. WHEN qualquer query é executada THEN o sistema SHALL filtrar por tenant_id do usuário
2. WHEN um usuário tenta acessar dados de outra empresa THEN o sistema SHALL retornar 403 Forbidden
3. WHEN um usuário faz login THEN o sistema SHALL carregar apenas dados da sua empresa
4. WHEN um Super Admin acessa THEN o sistema SHALL permitir visualizar todas as empresas
5. WHEN um usuário é criado THEN o sistema SHALL vincular ao tenant_id automaticamente
6. WHEN um projeto é criado THEN o sistema SHALL vincular ao tenant_id automaticamente

---

### Requirement 11: Isolamento Multi-Tenant

**User Story:** Como um usuário de uma empresa, eu quero ver apenas dados da minha empresa, para que haja privacidade e segurança dos dados.

#### Acceptance Criteria

1. WHEN qualquer query é executada THEN o sistema SHALL filtrar por tenant_id do usuário
2. WHEN um usuário tenta acessar dados de outra empresa THEN o sistema SHALL retornar 403 Forbidden
3. WHEN um usuário faz login THEN o sistema SHALL carregar apenas dados da sua empresa
4. WHEN um Super Admin acessa THEN o sistema SHALL permitir visualizar todas as empresas
5. WHEN um usuário é criado THEN o sistema SHALL vincular ao tenant_id automaticamente
6. WHEN um projeto é criado THEN o sistema SHALL vincular ao tenant_id automaticamente

---

### Requirement 12: Auditoria de Ações

**User Story:** Como um Company Admin, eu quero ver log de ações dos usuários, para que eu possa auditar o uso do sistema.

#### Acceptance Criteria

1. WHEN um usuário executa ação importante THEN o sistema SHALL registrar no log
2. WHEN o Company Admin acessa auditoria THEN o sistema SHALL exibir ações da sua empresa
3. WHEN o log é criado THEN o sistema SHALL registrar: usuário, ação, data/hora, IP
4. WHEN o Super Admin acessa auditoria THEN o sistema SHALL exibir ações de todas as empresas
5. WHEN uma ação falha THEN o sistema SHALL registrar o erro no log

---

### Requirement 12: Auditoria de Ações

**User Story:** Como um Company Admin, eu quero ver log de ações dos usuários, para que eu possa auditar o uso do sistema.

#### Acceptance Criteria

1. WHEN um usuário executa ação importante THEN o sistema SHALL registrar no log
2. WHEN o Company Admin acessa auditoria THEN o sistema SHALL exibir ações da sua empresa
3. WHEN o log é criado THEN o sistema SHALL registrar: usuário, ação, data/hora, IP
4. WHEN o Super Admin acessa auditoria THEN o sistema SHALL exibir ações de todas as empresas
5. WHEN uma ação falha THEN o sistema SHALL registrar o erro no log

---

### Requirement 13: Permissões Granulares

**User Story:** Como um desenvolvedor do sistema, eu quero ter controle granular de permissões, para que cada perfil tenha acesso apenas ao necessário.

#### Acceptance Criteria

1. WHEN uma ação é executada THEN o sistema SHALL verificar permissões do usuário
2. WHEN o usuário não tem permissão THEN o sistema SHALL retornar 403 Forbidden
3. WHEN o usuário tem múltiplos perfis THEN o sistema SHALL combinar permissões
4. WHEN uma permissão é verificada THEN o sistema SHALL considerar contexto (projeto, empresa)
5. WHEN o frontend renderiza THEN o sistema SHALL ocultar ações sem permissão

---

## Non-Functional Requirements

### Performance
- Verificação de permissões deve ser < 50ms
- Cache de permissões por sessão
- Índices em tenant_id em todas as tabelas

### Security
- Todas as queries devem filtrar por tenant_id
- Tokens JWT devem incluir tenant_id e roles
- Auditoria de todas as ações sensíveis

### Usability
- Feedback claro quando ação é negada
- UI deve ocultar ações sem permissão
- Mensagens de erro amigáveis

### Scalability
- Suportar 1000+ empresas
- Suportar 10000+ usuários
- Suportar 100+ usuários simultâneos por empresa

---

**Data**: 24/02/2026  
**Versão**: 1.0  
**Status**: Em Revisão
