# CheckMate Browser Extension

## How to Build and Package:

1. **Create icons** (16x16, 48x48, 128x128 PNG):
   - Create `icons/` folder
   - Add icon16.png, icon48.png, icon128.png

2. **Zip all files**:
   ```bash
   cd frontend/app/public/downloads/extension-example
   zip -r ../checkmate-extension-chrome.zip *
   ```

3. **Test locally**:
   - Open Chrome: `chrome://extensions`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `extension-example` folder

4. **Deploy to production**:
   - Move the `.zip` file to `frontend/app/public/downloads/`
   - Commit and push to `develop` branch
   - GitHub Actions will deploy to VM

## Files Structure:

```
extension-example/
├── manifest.json          # Extension configuration
├── popup.html             # Extension popup UI
├── popup.js               # Popup functionality
├── background.js          # Background service worker
├── content.js             # Content script (runs on pages)
└── icons/
    ├── icon16.png
    ├── icon48.png
    └── icon128.png
```

## Features:

- ✅ Quick analyze current domain
- ✅ Custom query input
- ✅ Opens CheckMate in new tab
- ✅ Dark theme matching website
- ✅ Keyboard shortcut (Enter to analyze)

## To add icons:

Use your logo and create 3 sizes using any image editor or online tool:
- 16x16px (browser toolbar)
- 48x48px (extensions page)
- 128x128px (Chrome Web Store)

Save them in `icons/` folder.
