# 🚀 Como Instalar o Plugin v1.0.2

## ✅ Arquivo Gerado

O arquivo **`bsmart-alm-plugin-1.0.2.vsix`** foi gerado com sucesso!

- **Tamanho**: 225 KB
- **Localização**: `bsmart-alm-plugin/bsmart-alm-plugin-1.0.2.vsix`
- **Arquivos incluídos**: 75 arquivos

## Instalação

### Opção 1: Via Linha de Comando

```bash
code --install-extension bsmart-alm-plugin/bsmart-alm-plugin-1.0.2.vsix
```

### Opção 2: Via Interface do VS Code

1. Abra o VS Code
2. Vá para **Extensions** (Ctrl+Shift+X)
3. Clique nos **"..."** no topo da barra lateral
4. Selecione **"Install from VSIX..."**
5. Navegue até `bsmart-alm-plugin/bsmart-alm-plugin-1.0.2.vsix`
6. Clique em **"Install"**
7. Reinicie o VS Code

## Verificação

Após instalar, verifique se o plugin está ativo:

1. Abra a paleta de comandos (Ctrl+Shift+P)
2. Digite "Bsmart"
3. Você deve ver os comandos:
   - **Bsmart: Login to Bsmart-ALM**
   - **Bsmart: Select Project**
   - **Bsmart: View Specification**
   - **Bsmart: View Architecture**
   - E outros...

## Primeiro Uso

### 1. Fazer Login

```
Ctrl+Shift+P → "Bsmart: Login to Bsmart-ALM"
```

Insira suas credenciais:
- **Email**: seu-email@example.com
- **Senha**: sua-senha

### 2. Selecionar Projeto

```
Ctrl+Shift+P → "Bsmart: Select Project"
```

Escolha um projeto da lista.

### 3. Ver Work Items

Na barra lateral esquerda, clique no ícone do **Bsmart-ALM** (🚀).

Você verá:
```
📋 Specification
🏗️ Architecture
📝 Work Items
   ├── Work Item 1
   ├── Work Item 2
   └── ...
```

### 4. Ver Especificação

Clique em **"📋 Specification"** para ver a especificação do projeto.

### 5. Ver Arquitetura

Clique em **"🏗️ Architecture"** para ver a arquitetura do projeto.

## Configuração

Você pode configurar o plugin em:

**File → Preferences → Settings → Extensions → Bsmart-ALM**

Configurações disponíveis:
- **Server URL**: URL do servidor Bsmart-ALM (padrão: http://localhost:8086)
- **Default AI Tool**: Ferramenta de IA padrão (Copilot, Continue, Kiro, Cursor)
- **Auto Refresh**: Atualizar automaticamente work items
- **Refresh Interval**: Intervalo de atualização em segundos

## Desinstalar Versão Anterior

Se você tinha a versão 1.0.1 instalada:

1. Vá para **Extensions** (Ctrl+Shift+X)
2. Procure por "Bsmart-ALM"
3. Clique em **"Uninstall"**
4. Reinicie o VS Code
5. Instale a versão 1.0.2

## Troubleshooting

### Plugin não aparece após instalação

1. Reinicie o VS Code completamente
2. Verifique se o plugin está habilitado em Extensions

### Erro ao fazer login

1. Verifique se o servidor está rodando
2. Verifique a URL do servidor nas configurações
3. Verifique suas credenciais

### Work items não carregam

1. Certifique-se de que selecionou um projeto
2. Verifique se o backend está rodando
3. Verifique os logs: **View → Output → Bsmart-ALM**

### Specification/Architecture não aparecem

Isso é normal se o projeto ainda não tem especificação ou arquitetura definidas. O plugin mostrará uma mensagem informativa.

## Novidades da v1.0.2

✨ **Novas Funcionalidades**:
- Visualização de Especificação do Projeto
- Visualização de Arquitetura do Projeto
- Estrutura em árvore melhorada

🐛 **Correções**:
- Work items agora carregam corretamente após selecionar projeto
- Melhor tratamento de erros
- Logs de debug adicionados

## Suporte

Para problemas ou dúvidas:
1. Verifique os logs: **View → Output → Bsmart-ALM**
2. Consulte a documentação: `bsmart-alm-plugin/README.md`
3. Entre em contato com a equipe de desenvolvimento

---

🎉 **Aproveite o plugin v1.0.2!**
