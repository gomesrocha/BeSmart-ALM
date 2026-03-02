"""Prompts for specification generation."""

SPECIFICATION_SYSTEM = """Você é um Analista de Sistemas especializado em criar documentos de especificação técnica detalhados e profissionais em português.

Sua tarefa é gerar uma especificação completa baseada nos requisitos do projeto, seguindo as melhores práticas de engenharia de software."""

SPECIFICATION_PROMPT = """Com base nos seguintes requisitos do projeto, gere uma especificação técnica completa em formato Markdown.

Projeto: {project_name}
Descrição: {project_description}
Target Cloud: {target_cloud}
Nível MPS.BR: {mps_br_level}

Requisitos do Projeto:
{requirements_summary}

Gere uma especificação técnica completa em Markdown com as seguintes seções:

# 1. Visão Geral do Projeto
- Objetivo do projeto
- Escopo
- Stakeholders
- Benefícios esperados

# 2. Requisitos Funcionais
- Liste todos os requisitos funcionais de forma detalhada
- Organize por módulos/funcionalidades
- Inclua prioridade e complexidade

# 3. Requisitos Não-Funcionais
- Performance (tempo de resposta, throughput)
- Segurança (autenticação, autorização, criptografia)
- Escalabilidade (usuários simultâneos, crescimento)
- Disponibilidade (uptime, SLA)
- Usabilidade (acessibilidade, responsividade)
- Manutenibilidade (código limpo, documentação)
- Compatibilidade (browsers, dispositivos)

# 4. Regras de Negócio
- Regras críticas do negócio
- Validações
- Fluxos de processo

# 5. Integrações
- Sistemas externos
- APIs
- Serviços de terceiros

# 6. Restrições e Premissas
- Restrições técnicas
- Restrições de negócio
- Premissas do projeto

# 7. Glossário
- Termos técnicos
- Termos de negócio
- Acrônimos

Responda APENAS com o conteúdo Markdown, sem texto adicional."""
