from graphviz import Digraph

# Membuat diagram
dot = Digraph("Penyusunan_Proyek")
dot.attr(rankdir='TB')

# Node utama
dot.node('A', 'PENYUSUNAN PROYEK', shape='box', style='filled', fillcolor='lightblue')

# Menu utama
dot.node('B', 'Menu Beranda\nInformasi singkat tentang aplikasi')
dot.node('C', 'Menu Materi\nPenjelasan kation dan anion')
dot.node('D', 'Menu Golongan Kation')
dot.node('E', 'Menu Anion\nIdentifikasi beberapa anion umum')
dot.node('F', 'Menu Kuis\nLatihan soal untuk pengguna')
dot.node('G', 'Menu Tentang Sistem\nInformasi pembuat aplikasi')

# Hubungan dari node utama
dot.edge('A', 'B')
dot.edge('A', 'C')
dot.edge('A', 'D')
dot.edge('A', 'E')
dot.edge('A', 'F')
dot.edge('A', 'G')

# Submenu Golongan Kation
dot.node('D1', 'Golongan I')
dot.node('D2', 'Golongan II')
dot.node('D3', 'Golongan III')
dot.node('D4', 'Golongan IV')
dot.node('D5', 'Golongan V')

dot.edge('D', 'D1')
dot.edge('D', 'D2')
dot.edge('D', 'D3')
dot.edge('D', 'D4')
dot.edge('D', 'D5')

# Simpan sebagai PNG
dot.render('penyusunan_proyek', format='png', view=True)

print("Bagan berhasil dibuat!")
