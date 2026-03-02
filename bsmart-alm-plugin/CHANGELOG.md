# Changelog

All notable changes to the "Bsmart-ALM Integration" extension will be documented in this file.

## [1.0.2] - 2026-02-28

### Added
- ✨ **Specification Viewer**: View project specifications directly in VS Code
- ✨ **Architecture Viewer**: View project architecture and diagrams
- ✨ **Improved Tree Structure**: Organized view with Specification, Architecture, and Work Items sections
- 📝 **Better Logging**: Added debug logs for troubleshooting

### Fixed
- 🐛 **Work Items Not Loading**: Fixed incorrect API endpoint (`/api/v1/work-items?project_id=` instead of `/api/v1/projects/{id}/work-items`)
- 🐛 **Error Handling**: Improved error messages and handling for API failures
- 🐛 **Cache Management**: Better cache handling for specifications and architecture

### Changed
- 🔄 **Tree View Reorganization**: Work items now appear under a collapsible "Work Items" group
- 🔄 **UI Improvements**: Better icons and visual hierarchy in the tree view
- 🔄 **Performance**: Added caching for specifications (10 minutes) and architecture (10 minutes)

## [1.0.1] - 2026-02-20

### Added
- Initial release with basic work item management
- Login/logout functionality
- Project selection
- Work item viewing and status updates
- AI tool integration
- Git integration

### Features
- View assigned work items
- Update work item status
- Add comments to work items
- Export work items to AI tools (Copilot, Continue, Kiro, Cursor)
- Automatic status updates when starting work

## [1.0.0] - 2026-02-15

### Added
- Initial beta release
- Basic authentication
- Work item tree view
- Status bar integration
