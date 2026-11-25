from PIL import Image
import os

os.makedirs('assets/report', exist_ok=True)
base_dir = r'C:\Users\Snehithraj\.gemini\antigravity\brain\d90ca0bb-7a01-47f0-b18e-09f0cc4efd87\.user_uploaded'

# 1. Comparison Viewer: Tower in fog vs enhanced side-by-side
img_compare = Image.open(os.path.join(base_dir, 'media_1795545251366_39714217.png'))
img_compare.save('assets/report/screenshot_viewer.png')

# 2. Controls & Sliders
img_sliders = Image.open(os.path.join(base_dir, 'media_1795547371635_f6fa2087.jpg'))
w, h = img_sliders.size
# Crop sliders card
img_sliders_crop = img_sliders.crop((int(w*0.06), int(h*0.22), int(w*0.94), int(h*0.78)))
img_sliders_crop.save('assets/report/screenshot_sliders.png')

# 3. Copilot & Metrics
img_copilot = Image.open(os.path.join(base_dir, 'media_1795555472464_9609e76f.jpg'))
cw, ch = img_copilot.size
# Crop metrics + copilot
img_copilot_crop = img_copilot.crop((int(cw*0.12), int(ch*0.08), int(cw*0.88), int(ch*0.88)))
img_copilot_crop.save('assets/report/screenshot_copilot.png')

print("Screenshots updated successfully:")
print("Viewer:", img_compare.size)
print("Sliders crop:", img_sliders_crop.size)
print("Copilot crop:", img_copilot_crop.size)
