from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import math



app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'fuzzysemen'

mysql = MySQL(app)


@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_semen")
    data = cur.fetchall()
    cur.close()
    return render_template('Menu1/semen.html', menu='semen', barang = data)

#Menu 1
@app.route('/semen')
def semen():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_semen")
    data = cur.fetchall()
    cur.close()
    return render_template('Menu1/semen.html', menu='semen', barang = data)

@app.route('/formsemen')
def formsemen():
    return render_template('Menu1/formsemen.html', menu='formsemen')

@app.route('/simpanformsemen', methods=["POST"])
def simpanformsemen():
    nama = request.form['nama']
    harga = request.form['harga']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tb_semen(nama,harga) VALUES(%s,%s)", (nama,harga))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('semen'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tb_semen SET nama = %s, harga = %s WHERE kode = %s", (nama, harga, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('semen'))
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tb_semen WHERE kode = %s", (id,))
        data = cur.fetchone()
        cur.close()
        return render_template('Menu1/updatesemen.html', barang=data)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_semen WHERE kode = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('semen'))


#Menu 2
@app.route('/penjualan')
def penjualan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT p.nojual, s.nama, p.terjual, p.tersisa, p.keuntungan, p.tanggal FROM tb_penjualan p JOIN tb_semen s ON p.kode = s.kode")
    penjualan = cur.fetchall()
    cur.close()
    return render_template('Menu2/penjualan.html', penjualan=penjualan, menu='penjualan')

@app.route('/add_penjualan', methods=['GET', 'POST'])
def add_penjualan():
        cur = mysql.connection.cursor()
        cur.execute("SELECT kode, nama FROM tb_semen")
        barang = cur.fetchall()
        if request.method == 'POST':
            kode = request.form['kode']
            terjual = request.form['terjual']
            tersisa = request.form['tersisa']
            tanggal = request.form['tanggal']
            
            cur.execute("SELECT harga FROM tb_semen WHERE kode = %s", [kode])
            harga = cur.fetchone()[0]
            
            keuntungan = int(harga) * int(terjual)
            
            cur.execute("""
                INSERT INTO tb_penjualan (kode, terjual, tersisa, keuntungan, tanggal) 
                VALUES (%s, %s, %s, %s, %s)
            """, (kode, terjual, tersisa, keuntungan, tanggal))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('penjualan'))
        cur.close()

        return render_template('Menu2/add_penjualan.html', barang=barang)

@app.route('/edit_penjualan/<int:nojual>', methods=['GET', 'POST'])
def edit_penjualan(nojual):
    cur = mysql.connection.cursor()
    cur.execute("SELECT kode, nama FROM tb_semen")
    barang = cur.fetchall()
    if request.method == 'POST':
        kode = request.form['kode']
        terjual = request.form['terjual']
        tersisa = request.form['tersisa']
        tanggal = request.form['tanggal']
        
        cur.execute("SELECT harga FROM tb_semen WHERE kode = %s", [kode])
        harga = cur.fetchone()[0]
        
        keuntungan = int(harga) * int(terjual)
        
        cur.execute("""
            UPDATE tb_penjualan 
            SET kode = %s, terjual = %s, tersisa = %s, keuntungan = %s, tanggal = %s 
            WHERE nojual = %s
        """, (kode, terjual, tersisa, keuntungan, tanggal, nojual))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('penjualan'))
    cur.execute("SELECT * FROM tb_penjualan WHERE nojual = %s", [nojual])
    penjualan = cur.fetchone()
    cur.close()
    return render_template('Menu2/edit_penjualan.html', penjualan=penjualan, barang=barang)

@app.route('/delete_penjualan/<int:nojual>')
def delete_penjualan(nojual):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_penjualan WHERE nojual = %s", [nojual])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('penjualan'))

#Menu 3
@app.route('/prediksi', methods=['GET', 'POST'])
def prediksi():
    if request.method == 'POST':
        kode = request.form['kode']
        terjual = int(request.form['terjual'])
        tersisa = int(request.form['tersisa'])

        # Ambil harga dari database
        cur = mysql.connection.cursor()
        cur.execute("SELECT harga FROM tb_semen WHERE kode = %s", (kode,))
        harga = cur.fetchone()[0]
        cur.close()

        # Ambil data dari tb_penjualan untuk menghitung keuntungan
        cur = mysql.connection.cursor()
        cur.execute("SELECT terjual, tersisa, keuntungan FROM tb_penjualan")
        data_penjualan = cur.fetchall()
        cur.close()

        # Hitung nilai minimum dan maksimum untuk fuzzyfikasi
        min_terjual = min([x[0] for x in data_penjualan])
        max_terjual = max([x[0] for x in data_penjualan])
        min_tersisa = min([x[1] for x in data_penjualan])
        max_tersisa = max([x[1] for x in data_penjualan])
        min_keuntungan = min([x[2] for x in data_penjualan])
        max_keuntungan = max([x[2] for x in data_penjualan])

        # Hitung keuntungan
        keuntungan = harga * terjual

        # Fuzzyfikasi
        def fuzzy_sedikit(val, min_val, max_val):
            return (max_val - val) / (max_val - min_val)

        def fuzzy_banyak(val, min_val, max_val):
            return (val - min_val) / (max_val - min_val)

        terjual_sedikit = fuzzy_sedikit(terjual, min_terjual, max_terjual)
        terjual_banyak = fuzzy_banyak(terjual, min_terjual, max_terjual)
        tersisa_sedikit = fuzzy_sedikit(tersisa, min_tersisa, max_tersisa)
        tersisa_banyak = fuzzy_banyak(tersisa, min_tersisa, max_tersisa)
        keuntungan_sedikit = fuzzy_sedikit(keuntungan, min_keuntungan, max_keuntungan)
        keuntungan_banyak = fuzzy_banyak(keuntungan, min_keuntungan, max_keuntungan)

        # Rule implementation
        alpha1 = min(terjual_banyak, tersisa_banyak, keuntungan_banyak)
        alpha2 = min(terjual_sedikit, tersisa_banyak, keuntungan_banyak)
        alpha3 = min(terjual_banyak, tersisa_sedikit, keuntungan_banyak)
        alpha4 = min(terjual_sedikit, tersisa_sedikit, keuntungan_banyak)
        alpha5 = min(terjual_banyak, tersisa_banyak, keuntungan_sedikit)
        alpha6 = min(terjual_sedikit, tersisa_banyak, keuntungan_sedikit)
        alpha7 = min(terjual_banyak, tersisa_sedikit, keuntungan_sedikit)
        alpha8 = min(terjual_sedikit, tersisa_sedikit, keuntungan_sedikit)

        z1 = alpha1 * max_terjual  # Misalnya z1 adalah nilai maksimum
        z2 = alpha2 * min_terjual  # Misalnya z2 adalah nilai minimum
        z3 = alpha3 * max_terjual
        z4 = alpha4 * ((min_terjual + max_terjual) / 2)
        z5 = alpha5 * ((min_terjual + max_terjual) / 2)
        z6 = alpha6 * min_terjual
        z7 = alpha7 * ((min_terjual + max_terjual) / 2)
        z8 = alpha8 * min_terjual

        # Defuzzifikasi
        Z = (alpha1 * z1 + alpha2 * z2 + alpha3 * z3 + alpha4 * z4 + alpha5 * z5 + alpha6 * z6 + alpha7 * z7 + alpha8 * z8) / (alpha1 + alpha2 + alpha3 + alpha4 + alpha5 + alpha6 + alpha7 + alpha8)

        Z = math.floor(Z)
        
        # Ambil nama semen
        cur = mysql.connection.cursor()
        cur.execute("SELECT nama FROM tb_semen WHERE kode = %s", (kode,))
        nama = cur.fetchone()[0]
        cur.close()

        return render_template('Menu3/hasil_prediksi.html', Z=Z, nama=nama, terjual=terjual, tersisa=tersisa, keuntungan=keuntungan,
                               alpha_values=[alpha1, alpha2, alpha3, alpha4, alpha5, alpha6, alpha7, alpha8])
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT kode, nama FROM tb_semen")
        barang = cur.fetchall()
        cur.close()
        return render_template('Menu3/prediksi.html', barang=barang, menu='prediksi')
    
@app.route('/hasil_prediksi', methods=['POST'])

def hasil_prediksi():
    # Data yang telah dikirim dari form di 'prediksi.html'
    kode = request.form['kode']
    terjual = int(request.form['terjual'])
    tersisa = int(request.form['tersisa'])

    # Ambil data nama dan harga berdasarkan kode semen dari tb_semen
    cur = mysql.connection.cursor()
    cur.execute("SELECT nama, harga FROM tb_semen WHERE kode = %s", (kode,))
    semen_data = cur.fetchone()
    nama = semen_data[0]
    harga = semen_data[1]
    keuntungan = terjual * harga

    # Hitung prediksi
    hasil_prediksi = prediksi_fuzzy(terjual, tersisa, keuntungan)

    return render_template('Menu3/hasil_prediksi.html', nama=nama, terjual=terjual, tersisa=tersisa, keuntungan=keuntungan, hasil_prediksi=hasil_prediksi)


if __name__ == '__main__':
    app.run(debug=True)