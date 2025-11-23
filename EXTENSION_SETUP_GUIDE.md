# Chrome Extension Setup & Deployment Guide

## 📦 Šta je urađeno:

### 1. **Frontend - Download Button**
- ✅ Dodato dugme "Download Extension" na HomeView (desktop only)
- ✅ Link koji downloaduje: `/downloads/checkmate-extension-chrome.zip`
- ✅ Instrukcije za instalaciju ispod dugmeta
- ✅ Auto-analyze kada se otvori sa `?q=` parametrom

**Lokacija**: `frontend/app/src/views/HomeView.vue` (linija 53-65)

### 2. **Extension Files**
- ✅ Kreiran `public/downloads/` folder (automatski se deploya)
- ✅ Primer extension sa svim potrebnim fajlovima:
  - `manifest.json` - Chrome Extension config
  - `popup.html` - UI ekstenzije (dark theme)
  - `popup.js` - Funkcionalnost (quick analyze, current domain)
  - `background.js` - Service worker
  - `content.js` - Content script

**Lokacija**: `frontend/app/public/downloads/extension-example/`

### 3. **Deploy Pipeline**
- ✅ GitHub Actions već konfigurisano (`deploy.yml`)
- ✅ `public/` folder se automatski kopira u build
- ✅ Download link će raditi na: `https://www.check-mate.systems/downloads/checkmate-extension-chrome.zip`

---

## 🚀 Kako da deplojuješ ekstenziju:

### Korak 1: Dodaj ikonice

Kreira 3 PNG fajla (koristi vaš logo):
```bash
frontend/app/public/downloads/extension-example/icons/
├── icon16.png   (16x16px)
├── icon48.png   (48x48px)
└── icon128.png  (128x128px)
```

### Korak 2: Testiraj lokalno

```bash
# Otvori Chrome
chrome://extensions

# Uključi "Developer mode" (gornji desni ugao)
# Klikni "Load unpacked"
# Odaberi folder: frontend/app/public/downloads/extension-example/

# Testiraj extension:
# - Klikni na extension icon
# - Unesi query ili koristi current domain
# - Klikni "Analyze on CheckMate"
```

### Korak 3: Zip i deploy

```bash
cd frontend/app/public/downloads/extension-example

# Zip sve fajlove
zip -r ../checkmate-extension-chrome.zip .

# Proveri da je sve u zip-u
unzip -l ../checkmate-extension-chrome.zip

# Trebalo bi da vidiš:
# manifest.json
# popup.html
# popup.js
# background.js
# content.js
# icons/icon16.png
# icons/icon48.png
# icons/icon128.png
```

### Korak 4: Git commit i push

```bash
cd /home/bogdan-hsc/YandexAI-hachathon

git add frontend/app/public/downloads/
git add frontend/app/src/views/HomeView.vue
git commit -m "Add Chrome extension download with auto-deployment"
git push origin develop
```

### Korak 5: Automatski deploy

GitHub Actions će automatski:
1. Pull repo na VM
2. Build frontend (`npm run build`)
3. Copy `public/downloads/` u `/var/www/frontend/downloads/`
4. Restart nginx

---

## 📱 Kako ekstenzija radi:

### User Flow:
1. User otvara bilo koji website (npr. Amazon)
2. Klikne na CheckMate extension icon
3. Vidi current domain već popunjeno: `amazon.com`
4. Klikne "Analyze on CheckMate"
5. Otvara se CheckMate u novom tabu sa URL: `https://www.check-mate.systems/?q=amazon.com`
6. HomeView detektuje `?q=` parametar i automatski pokreće analizu

### Features:
- ✅ **Quick analyze**: Auto-popuni current domain
- ✅ **Custom query**: User može uneti svoj query
- ✅ **Keyboard shortcut**: Enter za analizu
- ✅ **Dark theme**: Matching sa CheckMate website-om
- ✅ **Auto-analyze**: HomeView automatski analizira ako ima `?q=` parametar

---

## 🔗 URL-ovi nakon deploya:

- **Download link**: `https://www.check-mate.systems/downloads/checkmate-extension-chrome.zip`
- **Extension opens**: `https://www.check-mate.systems/?q=<domain>`
- **API endpoint**: `https://www.check-mate.systems/api/analyze`

---

## 🛠️ Troubleshooting:

### Problem: Download ne radi
```bash
# Proveri da li je zip fajl na VM-u:
ssh ubuntu@<VM_IP>
ls -la /var/www/frontend/downloads/

# Ako nema, ručno kopiraj:
sudo cp /home/ubuntu/hackathon/YandexAI-hackathon/frontend/app/dist/downloads/* /var/www/frontend/downloads/
```

### Problem: Extension ne otvara CheckMate
```bash
# Proveri manifest.json da li ima ispravne permissions:
"host_permissions": ["https://www.check-mate.systems/*"]

# Proveri popup.js da li koristi ispravan URL:
const checkmateUrl = `https://www.check-mate.systems/?q=${encodeURIComponent(query)}`;
```

### Problem: Auto-analyze ne radi
```bash
# Proveri HomeView.vue mounted() hook:
const queryParam = urlParams.get('q')
if (queryParam) {
  this.prompt = queryParam
  setTimeout(() => this.onAnalyzeClick(), 500)
}
```

---

## 📊 Stats:

- **Extension size**: ~10KB (bez ikonica), ~50KB (sa ikonicama)
- **Permissions**: `activeTab`, `storage`, `host_permissions` za CheckMate domain
- **Manifest version**: V3 (latest Chrome standard)
- **Compatible**: Chrome 88+, Edge 88+, Opera 74+

---

## 🎯 Next Steps (Opciono):

1. **Chrome Web Store**: Submit extension za javni download
2. **Firefox Add-on**: Konvertuj za Firefox (minimal changes needed)
3. **Context menu**: Dodaj right-click "Analyze with CheckMate"
4. **History**: Čuvaj istoriju analiza u extension storage
5. **Notifications**: Push notifications za cached results

---

## ✅ Checklist:

- [x] Download button na HomeView
- [x] Extension files kreirani
- [x] Manifest.json config
- [x] Popup UI (dark theme)
- [x] Auto-analyze sa `?q=` parametrom
- [ ] Dodaj ikonice (16x16, 48x48, 128x128)
- [ ] Zip extension files
- [ ] Git commit + push to develop
- [ ] Proveri deploy na VM
- [ ] Testiraj download link

