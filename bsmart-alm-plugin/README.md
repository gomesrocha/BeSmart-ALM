# Bsmart-ALM Integration Plugin

Integrate your IDE with Bsmart-ALM for seamless work item management directly in your development environment.

## Features

- **Authentication**: Securely login to Bsmart-ALM
- **Work Item Management**: View and manage your assigned work items
- **Project Selection**: Switch between projects easily
- **AI Integration**: Export work items to AI coding assistants (Copilot, Continue, Kiro, Cursor)
- **Git Integration**: Automatic work item updates on commits
- **Offline Mode**: Continue working even without connection

## Installation

1. Download the `.vsix` file
2. Open VS Code
3. Go to Extensions view (Ctrl+Shift+X)
4. Click on "..." menu and select "Install from VSIX..."
5. Select the downloaded file

## Usage

### Login

1. Open Command Palette (Ctrl+Shift+P)
2. Type "Bsmart: Login to Bsmart-ALM"
3. Enter your credentials

### View Work Items

1. Open the Explorer view
2. Find "Bsmart Work Items" section
3. Your assigned work items will be listed

### Export to AI Tool

1. Right-click on a work item
2. Select "Export to AI Tool"
3. The context will be sent to your configured AI assistant

## Configuration

Open Settings (Ctrl+,) and search for "Bsmart":

- `bsmart.serverUrl`: Bsmart-ALM server URL (default: http://localhost:8086)
- `bsmart.defaultAITool`: Default AI tool for exports (copilot, continue, kiro, cursor, clipboard)
- `bsmart.autoRefresh`: Automatically refresh work items
- `bsmart.refreshInterval`: Refresh interval in seconds

## Requirements

- VS Code 1.80.0 or higher
- Bsmart-ALM server access

## Development

```bash
# Install dependencies
npm install

# Compile
npm run compile

# Watch mode
npm run watch

# Package
npm run package
```

## License

MIT
