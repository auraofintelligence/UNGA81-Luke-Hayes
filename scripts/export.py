"""Copy the public site into _site for GitHub Pages."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'_site';out.mkdir(exist_ok=True)
for path in list(ROOT.glob('*.html'))+[ROOT/n for n in ['LICENCE.md','sitemap.xml','robots.txt','.nojekyll','favicon.ico','site.webmanifest']]:shutil.copy2(path,out/path.name)
for name in ['assets','documents','data']:shutil.copytree(ROOT/name,out/name,dirs_exist_ok=True)
print('Exported public files to _site.')
