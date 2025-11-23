from PIL import Image, ImageDraw

# Create 16x16 icon
img16 = Image.new('RGBA', (16, 16), (255, 69, 0, 255))
draw16 = ImageDraw.Draw(img16)
draw16.ellipse([3, 3, 13, 13], fill=(10, 10, 10, 255))
img16.save('C:/Projekti/YandexAI-hackathon/scam-checker-extension/assets/icons/icon16.png')

# Create 48x48 icon
img48 = Image.new('RGBA', (48, 48), (255, 69, 0, 255))
draw48 = ImageDraw.Draw(img48)
draw48.ellipse([8, 8, 40, 40], fill=(10, 10, 10, 255))
img48.save('C:/Projekti/YandexAI-hackathon/scam-checker-extension/assets/icons/icon48.png')

# Create 128x128 icon
img128 = Image.new('RGBA', (128, 128), (255, 69, 0, 255))
draw128 = ImageDraw.Draw(img128)
draw128.ellipse([20, 20, 108, 108], fill=(10, 10, 10, 255))
img128.save('C:/Projekti/YandexAI-hackathon/scam-checker-extension/assets/icons/icon128.png')

print('Icons created successfully!')

