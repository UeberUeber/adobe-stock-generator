import os, json, csv
DIR = r'E:\codeWantigravity\AdobeStock_Automation Service\adobe-stock-generator\generations\2026-03-11_11-24-10'
OUT_CSV = os.path.join(DIR, 'upscaled', 'submission_fixed.csv')
fieldnames = ['Filename', 'Title', 'Keywords', 'Category', 'Releases']
with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for img in os.listdir(os.path.join(DIR, 'upscaled')):
        if img.endswith('.png'):
            base = img.split('.')[0]
            with open(os.path.join(DIR, f'{base}.json'), 'r', encoding='utf-8') as jf:
                d = json.load(jf)
            writer.writerow({'Filename': img, 'Title': d['title'], 'Keywords': ', '.join(d['keywords']), 'Category': d['category'], 'Releases': ''})
print(f'Done writing {OUT_CSV}')
