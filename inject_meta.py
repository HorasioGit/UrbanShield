import streamlit
import os

# Cari lokasi instalasi Streamlit di server
streamlit_dir = os.path.dirname(streamlit.__file__)
index_path = os.path.join(streamlit_dir, 'static', 'index.html')

with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

meta_tag = '<meta name="dicoding:email" content="rizkipiji0907@gmail.com">'

# Jika belum ada tag tersebut, sisipkan tepat di bawah <head>
if meta_tag not in html:
    html = html.replace('<head>', f'<head>\n    {meta_tag}')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Berhasil menyisipkan meta tag Dicoding ke Streamlit!")
else:
    print("Meta tag sudah ada, aman!")
