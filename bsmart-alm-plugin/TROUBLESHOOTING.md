# 🔧 Troubleshooting - Problemas Comuns

## Problema: npm install com timeout

### Erro:
```
npm ERR! code ERR_SOCKET_TIMEOUT
npm ERR! network Socket timeout
```

### Soluções:

#### Solução 1: Script Automático (Recomendado)
```bash
cd bsmart-alm-plugin
chmod +x fix-install.sh
./fix-install.sh
```

#### Solução 2: Manual Passo a Passo

**1. Limpar cache:**
```bash
npm cache clean --force
```

**2. Aumentar timeout:**
```bash
npm config set fetch-timeout 60000
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000
```

**3. Limpar instalações anteriores:**
```bash
rm -rf node_modules
rm -f package-lock.json
```

**4. Tentar instalar novamente:**
```bash
npm install
```

#### Solução 3: Registry Alternativo

Se o registry padrão estiver lento:

```bash
# Usar mirror chinês (geralmente mais rápido)
npm config set registry https://registry.npmmirror.com

# Ou voltar ao padrão
npm config set registry https://registry.npmjs.org/
```

#### Solução 4: Instalar com flags especiais

```bash
# Com legacy peer deps
npm install --legacy-peer-deps

# Preferir cache offline
npm install --prefer-offline

# Sem optional dependencies
npm install --no-optional
```

#### Solução 5: Usar yarn (alternativa ao npm)

```bash
# Instalar yarn
npm install -g yarn

# Usar yarn ao invés de npm
yarn install
```

---

## Problema: Warnings de pacotes deprecated

### Warnings:
```
npm WARN deprecated inflight@1.0.6
npm WARN deprecated glob@7.2.3
```

### Solução:
Esses são apenas warnings, não impedem a instalação. São dependências transitivas (de outros pacotes). Você pode:

**Ignorar** (não afeta o funcionamento):
```bash
npm install --no-warnings
```

**Ou atualizar forçadamente:**
```bash
npm update
npm audit fix
```

---

## Problema: Erro de compilação TypeScript

### Erro:
```
error TS2307: Cannot find module
```

### Solução:

**1. Reinstalar dependências:**
```bash
rm -rf node_modules
npm install
```

**2. Verificar tsconfig.json:**
```bash
cat tsconfig.json
```

**3. Compilar novamente:**
```bash
npm run compile
```

---

## Problema: vsce não encontrado

### Erro:
```
vsce: command not found
```

### Solução:

```bash
# Instalar globalmente
npm install -g @vscode/vsce

# Ou usar npx (sem instalar)
npx vsce package
```

---

## Problema: Erro ao gerar .vsix

### Erro:
```
ERROR  Missing publisher name
```

### Solução:

Adicione publisher no package.json:
```json
{
  "publisher": "bsmart"
}
```

Ou use flag:
```bash
vsce package --allow-star-activation
```

---

## Problema: Plugin não aparece no VS Code

### Solução:

**1. Recarregar janela:**
```
Ctrl+Shift+P > "Reload Window"
```

**2. Verificar instalação:**
```bash
code --list-extensions | grep bsmart
```

**3. Ver logs de erro:**
```
Ctrl+Shift+P > "Developer: Toggle Developer Tools"
```

**4. Reinstalar:**
```bash
code --uninstall-extension bsmart.bsmart-alm-plugin
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

---

## Problema: Erro de permissão

### Erro:
```
EACCES: permission denied
```

### Solução:

**Linux/Mac:**
```bash
sudo npm install -g @vscode/vsce
```

**Ou configurar npm para não usar sudo:**
```bash
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## Problema: Conexão atrás de proxy

### Solução:

**Configurar proxy:**
```bash
npm config set proxy http://proxy.empresa.com:8080
npm config set https-proxy http://proxy.empresa.com:8080
```

**Com autenticação:**
```bash
npm config set proxy http://usuario:senha@proxy.empresa.com:8080
npm config set https-proxy http://usuario:senha@proxy.empresa.com:8080
```

**Remover proxy:**
```bash
npm config delete proxy
npm config delete https-proxy
```

---

## Problema: Espaço em disco insuficiente

### Solução:

**Limpar cache do npm:**
```bash
npm cache clean --force
```

**Limpar node_modules globais:**
```bash
npm list -g --depth=0
npm uninstall -g <pacote-nao-usado>
```

---

## Problema: Versão do Node.js incompatível

### Verificar versão:
```bash
node --version
npm --version
```

### Requisitos:
- Node.js: >= 18.0.0
- npm: >= 9.0.0

### Atualizar:

**Linux (usando nvm):**
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

**Ou via package manager:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Fedora
sudo dnf install nodejs
```

---

## Instalação Offline (sem internet)

Se você precisa instalar sem internet:

**1. Em uma máquina com internet:**
```bash
cd bsmart-alm-plugin
npm install
tar -czf node_modules.tar.gz node_modules/
```

**2. Copie para máquina sem internet:**
```bash
# Copie node_modules.tar.gz para a máquina
tar -xzf node_modules.tar.gz
npm run compile
vsce package --allow-star-activation
```

---

## Logs e Debug

### Ver logs detalhados:
```bash
npm install --verbose
```

### Ver logs do npm:
```bash
cat ~/.npm/_logs/*-debug-0.log
```

### Debug do VS Code:
```
Ctrl+Shift+P > "Developer: Toggle Developer Tools"
```

---

## Ainda com problemas?

### Opção 1: Instalação Simplificada

Use apenas as dependências essenciais:

```bash
# Criar package.json mínimo
cat > package-minimal.json << 'EOF'
{
  "name": "bsmart-alm-plugin",
  "version": "1.0.0",
  "engines": {
    "vscode": "^1.80.0"
  },
  "devDependencies": {
    "@types/vscode": "^1.80.0",
    "typescript": "^5.3.0"
  }
}
EOF

# Instalar apenas o essencial
npm install --package-lock-only
```

### Opção 2: Usar Docker

```bash
# Criar Dockerfile
cat > Dockerfile << 'EOF'
FROM node:18
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run compile
RUN npm install -g @vscode/vsce
RUN vsce package --allow-star-activation
EOF

# Build
docker build -t bsmart-plugin .
docker run -v $(pwd):/output bsmart-plugin cp *.vsix /output/
```

### Opção 3: Pedir ajuda

- Abra uma issue no repositório
- Inclua:
  - Versão do Node.js (`node --version`)
  - Versão do npm (`npm --version`)
  - Sistema operacional
  - Log completo do erro
  - Saída de `npm config list`

---

## Comandos Úteis

```bash
# Ver configuração do npm
npm config list

# Resetar configuração
npm config delete <key>

# Ver versões instaladas
npm list --depth=0

# Verificar integridade
npm audit

# Corrigir vulnerabilidades
npm audit fix

# Limpar tudo e recomeçar
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```
