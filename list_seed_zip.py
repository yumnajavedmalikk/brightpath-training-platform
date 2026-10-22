import zipfile, pathlib, json, sys
zip_path = r'C:/Users/pc/.gemini/antigravity/scratch/brightpath-training-platform/training-platform-seed.zip'
with zipfile.ZipFile(zip_path) as z:
    files = [f.filename for f in z.infolist()]
    print('Files in zip:', files)
    # Extract README.txt content
    readme_name = next((f for f in files if f.lower().endswith('readme.txt')), None)
    if readme_name:
        with z.open(readme_name) as r:
            txt = r.read().decode('utf-8')
            print('--- README.txt ---')
            print(txt)
    else:
        print('README.txt not found')
