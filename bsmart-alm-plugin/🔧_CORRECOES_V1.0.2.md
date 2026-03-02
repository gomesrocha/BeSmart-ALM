# Correções para Versão 1.0.2

## Problemas Identificados

### 1. Work Items não carregam após selecionar projeto
**Causa**: O endpoint `/api/v1/projects/${projectId}/work-items` está incorreto
**Solução**: Corrigir para `/api/v1/work-items?project_id=${projectId}`

### 2. Falta Arquitetura e Especificação
**Causa**: Plugin não busca nem exibe arquitetura e especificação do projeto
**Solução**: Adicionar serviços e UI para arquitetura e especificação

### 3. Versão desatualizada
**Causa**: Versão atual é 1.0.1
**Solução**: Atualizar para 1.0.2

## Correções a Implementar

### 1. Corrigir WorkItemService.ts
- Linha 24: Corrigir endpoint de `/api/v1/projects/${projectId}/work-items` para `/api/v1/work-items?project_id=${projectId}`
- Adicionar tratamento de erro melhor
- Adicionar logs de debug

### 2. Adicionar SpecificationService.ts (NOVO)
```typescript
- Buscar especificação do projeto
- Exibir em webview
- Cache de 10 minutos
```

### 3. Adicionar ArchitectureService.ts (NOVO)
```typescript
- Buscar arquitetura do projeto
- Exibir em webview
- Cache de 10 minutos
```

### 4. Atualizar WorkItemTreeProvider.ts
- Adicionar nós para "Specification" e "Architecture"
- Estrutura em árvore:
  ```
  📁 Project Name
    ├── 📋 Specification
    ├── 🏗️ Architecture
    └── 📝 Work Items
        ├── Work Item 1
        ├── Work Item 2
        └── ...
  ```

### 5. Atualizar package.json
- Versão: 1.0.1 → 1.0.2
- Adicionar comandos:
  - `bsmart.viewSpecification`
  - `bsmart.viewArchitecture`

### 6. Atualizar extension.ts
- Registrar novos serviços
- Registrar novos comandos

## Estrutura de Dados

### Specification
```typescript
interface Specification {
    id: string;
    project_id: string;
    content: string;
    version: string;
    created_at: string;
    updated_at: string;
}
```

### Architecture
```typescript
interface Architecture {
    id: string;
    project_id: string;
    content: string;
    diagram_url?: string;
    created_at: string;
    updated_at: string;
}
```

## Endpoints da API

### Work Items
- **ANTES**: `GET /api/v1/projects/${projectId}/work-items`
- **DEPOIS**: `GET /api/v1/work-items?project_id=${projectId}`

### Specification
- `GET /api/v1/projects/${projectId}/specification`

### Architecture
- `GET /api/v1/projects/${projectId}/architecture`

## Changelog v1.0.2

### Added
- ✨ Visualização de Especificação do Projeto
- ✨ Visualização de Arquitetura do Projeto
- ✨ Estrutura em árvore melhorada com projeto, spec, arquitetura e work items

### Fixed
- 🐛 Corrigido endpoint de work items que não carregava após selecionar projeto
- 🐛 Melhorado tratamento de erros na busca de work items
- 🐛 Adicionados logs de debug para facilitar troubleshooting

### Changed
- 🔄 Reorganizada estrutura da árvore de work items
- 🔄 Melhorada experiência de usuário ao selecionar projeto

## Ordem de Implementação

1. ✅ Corrigir WorkItemService.ts (endpoint)
2. ✅ Criar SpecificationService.ts
3. ✅ Criar ArchitectureService.ts
4. ✅ Atualizar types.ts (adicionar Specification e Architecture)
5. ✅ Atualizar WorkItemTreeProvider.ts (nova estrutura)
6. ✅ Atualizar extension.ts (registrar serviços e comandos)
7. ✅ Atualizar package.json (versão e comandos)
8. ✅ Testar e gerar VSIX

## Como Testar

1. Instalar plugin atualizado
2. Fazer login
3. Selecionar projeto
4. Verificar se aparecem:
   - 📋 Specification
   - 🏗️ Architecture
   - 📝 Work Items (com lista de work items)
5. Clicar em cada item e verificar se abre corretamente
