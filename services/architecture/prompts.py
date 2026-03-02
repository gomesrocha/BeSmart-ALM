"""Prompts for architecture generation."""

ARCHITECTURE_SYSTEM = """Você é um Arquiteto de Software sênior especializado em criar arquiteturas escaláveis, seguras e bem documentadas em português.

Sua tarefa é propor uma arquitetura técnica completa baseada nos requisitos do projeto, incluindo diagramas Mermaid, decisões arquiteturais e requisitos não-funcionais detalhados."""

ARCHITECTURE_PROMPT = """Com base nos seguintes requisitos do projeto, gere uma proposta de arquitetura técnica completa em formato Markdown com diagramas Mermaid.

Projeto: {project_name}
Descrição: {project_description}
Target Cloud: {target_cloud}
Nível MPS.BR: {mps_br_level}

Requisitos do Projeto:
{requirements_summary}

Gere uma arquitetura técnica completa em Markdown com as seguintes seções:

# 1. Visão Geral da Arquitetura
- Estilo arquitetural (Microserviços, Monolito, Serverless, etc.)
- Justificativa da escolha
- Princípios arquiteturais

# 2. Diagrama de Contexto (C4 - Nível 1)
```mermaid
graph TB
    %% Diagrama de contexto mostrando sistema e atores externos
```

# 3. Diagrama de Containers (C4 - Nível 2)
```mermaid
graph TB
    %% Diagrama mostrando containers (apps, databases, etc.)
```

# 4. Componentes Principais
- Frontend (tecnologias sugeridas)
- Backend (tecnologias sugeridas)
- Banco de Dados (tipo e justificativa)
- Cache (se aplicável)
- Fila de Mensagens (se aplicável)

# 5. Diagrama de Componentes
```mermaid
graph TB
    %% Diagrama detalhado dos componentes
```

# 6. Fluxo de Dados
```mermaid
sequenceDiagram
    %% Diagrama de sequência para fluxo principal
```

# 7. Stack Tecnológico Recomendado
## Frontend
- Framework: [React/Vue/Angular]
- Linguagem: TypeScript
- UI: [Tailwind/Material-UI]
- Estado: [Redux/Zustand]

## Backend
- Framework: [FastAPI/NestJS/Spring Boot]
- Linguagem: [Python/TypeScript/Java]
- API: REST/GraphQL
- Autenticação: JWT/OAuth2

## Banco de Dados
- Principal: [PostgreSQL/MongoDB/MySQL]
- Cache: Redis
- Busca: Elasticsearch (se necessário)

## Infraestrutura ({target_cloud})
- Compute: [EC2/App Service/Compute Engine]
- Storage: [S3/Blob Storage/Cloud Storage]
- CDN: [CloudFront/Azure CDN/Cloud CDN]
- Monitoramento: [CloudWatch/Application Insights/Cloud Monitoring]

# 8. Requisitos Não-Funcionais Detalhados

## 8.1 Performance
- Tempo de resposta: < 200ms (p95)
- Throughput: X requisições/segundo
- Tempo de carregamento: < 3s
- Otimizações: Cache, CDN, Lazy Loading

## 8.2 Segurança
- Autenticação: JWT com refresh tokens
- Autorização: RBAC (Role-Based Access Control)
- Criptografia: TLS 1.3, dados em repouso
- Proteção: CORS, Rate Limiting, WAF
- Compliance: LGPD, {mps_br_level}

## 8.3 Escalabilidade
- Horizontal: Auto-scaling baseado em métricas
- Vertical: Recursos ajustáveis
- Usuários simultâneos: X usuários
- Crescimento: Y% ao ano

## 8.4 Disponibilidade
- SLA: 99.9% (8.76h downtime/ano)
- Redundância: Multi-AZ
- Backup: Diário com retenção de 30 dias
- Disaster Recovery: RTO < 4h, RPO < 1h

## 8.5 Manutenibilidade
- Código: Clean Code, SOLID
- Testes: Cobertura > 80%
- Documentação: OpenAPI, README
- CI/CD: Pipeline automatizado

## 8.6 Observabilidade
- Logs: Centralizados (ELK/CloudWatch)
- Métricas: Prometheus/Grafana
- Tracing: Distributed tracing
- Alertas: Proativos

# 9. Decisões Arquiteturais (ADRs)

## ADR-001: Escolha do Estilo Arquitetural
**Contexto**: [Descrever contexto]
**Decisão**: [Decisão tomada]
**Consequências**: [Impactos positivos e negativos]

## ADR-002: Escolha do Banco de Dados
**Contexto**: [Descrever contexto]
**Decisão**: [Decisão tomada]
**Consequências**: [Impactos positivos e negativos]

# 10. Padrões e Práticas

## Padrões de Design
- Repository Pattern
- Factory Pattern
- Observer Pattern
- [Outros relevantes]

## Práticas de Desenvolvimento
- Git Flow
- Code Review
- Pair Programming
- TDD/BDD

## Qualidade de Código
- Linting: ESLint, Pylint
- Formatação: Prettier, Black
- Análise Estática: SonarQube

# 11. Estratégia de Deploy

## Ambientes
- Desenvolvimento
- Homologação
- Produção

## Pipeline CI/CD
```mermaid
graph LR
    A[Commit] --> B[Build]
    B --> C[Tests]
    C --> D[Security Scan]
    D --> E[Deploy Dev]
    E --> F[Deploy Staging]
    F --> G[Deploy Prod]
```

## Estratégia de Release
- Blue-Green Deployment
- Canary Releases
- Feature Flags

# 12. Monitoramento e Alertas

## Métricas Chave
- Latência (p50, p95, p99)
- Taxa de erro
- Throughput
- Uso de recursos

## Alertas Críticos
- Downtime
- Alta latência
- Taxa de erro > 1%
- Uso de recursos > 80%

# 13. Segurança em Profundidade

## Camadas de Segurança
1. Rede: VPC, Security Groups, WAF
2. Aplicação: Input validation, CSRF, XSS
3. Dados: Encryption at rest/transit
4. Identidade: MFA, SSO
5. Auditoria: Logs de acesso, compliance

# 14. Plano de Capacidade

## Estimativas Iniciais
- Usuários: X usuários/dia
- Requisições: Y req/s
- Armazenamento: Z GB
- Banda: W GB/mês

## Crescimento Projetado
- Ano 1: [Estimativas]
- Ano 2: [Estimativas]
- Ano 3: [Estimativas]

# 15. Riscos e Mitigações

## Riscos Técnicos
1. **Risco**: [Descrição]
   **Impacto**: Alto/Médio/Baixo
   **Mitigação**: [Estratégia]

2. **Risco**: [Descrição]
   **Impacto**: Alto/Médio/Baixo
   **Mitigação**: [Estratégia]

Responda APENAS com o conteúdo Markdown completo, incluindo todos os diagramas Mermaid."""
