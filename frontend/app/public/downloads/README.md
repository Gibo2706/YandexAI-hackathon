# Extension Downloads

Place your browser extension files here:

1. **Chrome Extension**: `checkmate-extension-chrome.zip`
2. **Firefox Extension**: `checkmate-extension-firefox.xpi` (optional)

These files will be available at:
- `https://www.check-mate.systems/downloads/checkmate-extension-chrome.zip`
- `https://www.check-mate.systems/downloads/checkmate-extension-firefox.xpi`

## To add extension file:

1. Build your Chrome extension
2. Create a `.zip` file with all extension files
3. Place it in this directory: `frontend/app/public/downloads/`
4. Commit and push to `develop` branch
5. GitHub Actions will automatically deploy it to VM

## Extension should include:

- `manifest.json` (Chrome Extension Manifest V3)
- Background scripts
- Content scripts
- Popup HTML/JS
- Icons (16x16, 48x48, 128x128)
