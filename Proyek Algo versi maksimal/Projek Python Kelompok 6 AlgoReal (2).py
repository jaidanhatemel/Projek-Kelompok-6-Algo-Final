import datetime

FILE_COMMODITIES   = "commodities.csv"
FILE_PRICES        = "prices.csv"
FILE_TRANSACTIONS  = "transactions.csv"
FILE_USERS         = "users.csv"
FILE_LOG           = "users_log.csv"
FILE_LOCK          = "locked_users.csv"

# ===============================================
# 1. FUNGSI BACA FILE CSV
# ===============================================
def baca_csv(nama_file):
    data = []
    try:
        file = open(nama_file, "r", encoding="utf-8")
        semua_baris = file.readlines()
        file.close()
    except:
        return data

    if len(semua_baris) == 0:
        return data

    header = semua_baris[0].strip()
    header = header.replace("\ufeff", "")
    kolom = header.split(",")
    for i in range(len(kolom)):
        kolom[i] = kolom[i].strip()

    for i in range(1, len(semua_baris)):
        baris = semua_baris[i].strip()
        if baris == "":
            continue
        nilai = baris.split(",")
        for j in range(len(nilai)):
            nilai[j] = nilai[j].strip()

        satu_data = {}
        for j in range(len(kolom)):
            if j < len(nilai):
                satu_data[kolom[j]] = nilai[j]
            else:
                satu_data[kolom[j]] = ""
        data.append(satu_data)
    return data

# ===============================================
# 2. TULIS ULANG FILE CSV
# ===============================================
def tulis_csv(nama_file, header, data):
    file = open(nama_file, "w", encoding="utf-8")
    file.write(",".join(header) + "\n")
    for item in data:
        baris = []
        for kol in header:
            nilai = item.get(kol, "")
            if isinstance(nilai, str):
                nilai = nilai.replace("\n", " ")
                nilai = nilai.replace("\r", " ")
                nilai = nilai.replace(",", " ")
            else:
                nilai = str(nilai)
            baris.append(nilai)
        file.write(",".join(baris) + "\n")
    file.close()

# ===============================================
# 3. TAMBAH BARIS KE FILE CSV
# ===============================================
def tambah_baris(nama_file, header, data_baru):
    try:
        file = open(nama_file, "r", encoding="utf-8")
        isi = file.read().strip()
        file.close()
        if isi == "":
            tulis_csv(nama_file, header, [])
    except:
        tulis_csv(nama_file, header, [])

    file = open(nama_file, "a", encoding="utf-8")
    baris = []
    for kol in header:
        nilai = data_baru.get(kol, "")
        if isinstance(nilai, str):
            nilai = nilai.replace("\n", " ")
            nilai = nilai.replace("\r", " ")
            nilai = nilai.replace(",", " ")
        else:
            nilai = str(nilai)
        baris.append(nilai)
    file.write(",".join(baris) + "\n")
    file.close()

# ===============================================
# 4. FORMAT RUPIAH
# ===============================================
def format_rupiah(angka):
    try:
        n = int(angka)
        s = str(n)
        hasil = ""
        while len(s) > 3:
            hasil = "." + s[-3:] + hasil
            s = s[:-3]
        return "Rp " + s + hasil
    except:
        return "Rp 0"

# ===============================================
# 5. CETAK TABEL RAPI
# ===============================================
def cetak_tabel(data, daftar_kolom):
    if len(data) == 0:
        print("   → Belum ada data\n")
        return

    lebar = []
    for key, judul in daftar_kolom:
        panjang = len(judul)
        for baris in data:
            if len(str(baris.get(key, ""))) > panjang:
                panjang = len(str(baris.get(key, "")))
        lebar.append(panjang + 4)

    garis = "+"
    for w in lebar:
        garis = garis + "-" * w + "+"
    print("\n" + garis)

    header = "|"
    for i in range(len(daftar_kolom)):
        header = header + daftar_kolom[i][1].center(lebar[i]) + "|"
    print(header)
    print(garis)

    for baris in data:
        row = "|"
        for i in range(len(daftar_kolom)):
            nilai = str(baris.get(daftar_kolom[i][0], ""))
            row = row + nilai.ljust(lebar[i]) + "|"
        print(row)
    print(garis + "\n")

# ===============================================
# 6. FUNGSI AMBIL DATA
# ===============================================
def ambil_komoditas():
    return baca_csv(FILE_COMMODITIES)

def ambil_transaksi():
    return baca_csv(FILE_TRANSACTIONS)

def ambil_pengguna():
    return baca_csv(FILE_USERS)

def ambil_harga():
    semua = baca_csv(FILE_PRICES)
    hasil = []
    for h in semua:
        try:
            hasil.append({
                "commodity_id": h.get("commodity_id", ""),
                "month": int(h.get("month", "0")),
                "year": int(h.get("year", "0")),
                "price": float(h.get("price", "0"))
            })
        except:
            continue
    return hasil

# ===============================================
# 7. LOGIN (DENGAN LOG WAKTU REAL + AKUN TERKUNCI TIDAK TAMPIL "BERHASIL")
# ===============================================
def login():
    print("\n" + "="*60)
    print("    SELAMAT DATANG DI PENANSIL - PT Tani Sejahtera Jember")
    print("="*60)
    username = input("Username : ").strip()
    password = input("Password : ").strip()

    daftar_user = ambil_pengguna()
    user_found = None
    for user in daftar_user:
        if user.get("username", "") == username and user.get("password", "") == password:
            user_found = user
            break

    if user_found is None:
        print("Username atau password salah!")
        return None

    if user_terkunci(username):
        print("Akun Anda terkunci oleh admin. Hubungi administrator.")
        return None

    print("\nLogin berhasil! Selamat datang, " + username + "!")
    sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    catat_log(username, "Login berhasil")
    return user_found

# ===============================================
# 8. CEK USER TERKUNCI
# ===============================================
def user_terkunci(username):
    try:
        file = open(FILE_LOCK, "r", encoding="utf-8")
        baris = file.readlines()
        file.close()
        for b in baris:
            if b.strip() == username:
                return True
    except:
        pass
    return False

# ===============================================
# 9. CATAT LOG — RAPI (HANYA "Login berhasil" / "Logout" + WAKTU DI KOLOM TANGGAL)
# ===============================================
def catat_log(username, aksi):
    sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tambah_baris(FILE_LOG, ["username","action","date"],
                 {"username": username, "action": aksi, "date": sekarang})

# ===============================================
# 10. DASHBOARD HARGA TERBARU
# ===============================================
def dashboard():
    print("\n=== DASHBOARD HARGA TERBARU ===")
    harga = ambil_harga()
    komoditas = ambil_komoditas()
    terbaru = {}

    for h in harga:
        cid = h["commodity_id"]
        periode = (h["year"], h["month"])
        if cid not in terbaru or periode > (terbaru[cid]["year"], terbaru[cid]["month"]):
            terbaru[cid] = h

    tabel = []
    for k in komoditas:
        cid = k["commodity_id"]
        if cid in terbaru:
            t = terbaru[cid]
            tabel.append({
                "id": cid,
                "name": k["name"],
                "unit": k["unit"],
                "periode": str(t["month"]) + "/" + str(t["year"]),
                "harga": format_rupiah(int(t["price"]))
            })
        else:
            tabel.append({
                "id": cid,
                "name": k["name"],
                "unit": k["unit"],
                "periode": "-",
                "harga": "Belum ada harga"
            })
    cetak_tabel(tabel, [("id","ID"), ("name","Komoditas"), ("unit","Satuan"),
                        ("periode","Periode"), ("harga","Harga")])

# ===============================================
# 11. ANALISIS NAIK/TURUN
# ===============================================
def analisis_naik_turun():
    print("\n=== ANALISIS PERUBAHAN HARGA ===")
    komoditas = ambil_komoditas()
    semua_harga = ambil_harga()
    tabel = []

    for kom in komoditas:
        cid = kom["commodity_id"]
        riwayat = []
        for h in semua_harga:
            if h["commodity_id"] == cid:
                riwayat.append(h)

        if len(riwayat) < 2:
            continue

        for i in range(len(riwayat)):
            for j in range(i + 1, len(riwayat)):
                p1 = (riwayat[i]["year"], riwayat[i]["month"])
                p2 = (riwayat[j]["year"], riwayat[j]["month"])
                if p1 > p2:
                    riwayat[i], riwayat[j] = riwayat[j], riwayat[i]

        lama = riwayat[-2]
        baru = riwayat[-1]
        selisih = int(baru["price"] - lama["price"])
        status = "Naik" if selisih > 0 else ("Turun" if selisih < 0 else "Sama")

        tabel.append({
            "komoditas": kom["name"],
            "sebelum": str(lama["month"]) + "/" + str(lama["year"]),
            "terbaru": str(baru["month"]) + "/" + str(baru["year"]),
            "selisih": format_rupiah(selisih),
            "status": status
        })

    cetak_tabel(tabel, [("komoditas","Komoditas"), ("sebelum","Sebelum"),
                        ("terbaru","Terbaru"), ("selisih","Selisih"), ("status","Status")])

# ===============================================
# 12. RIWAYAT HARGA PER KOMODITAS
# ===============================================
def riwayat_harga():
    print("\n=== RIWAYAT HARGA KOMODITAS ===")
    daftar = ambil_komoditas()
    for i in range(len(daftar)):
        print(str(i + 1) + ". " + daftar[i]["commodity_id"] + " - " + daftar[i]["name"])

    pilihan = input("\nPilih nomor atau ketik ID (kosong = batal): ").strip()
    if pilihan == "":
        return

    terpilih = None
    if pilihan.isdigit():
        idx = int(pilihan) - 1
        if 0 <= idx < len(daftar):
            terpilih = daftar[idx]
    else:
        for k in daftar:
            if k["commodity_id"].upper() == pilihan.upper():
                terpilih = k
                break

    if terpilih is None:
        print("Komoditas tidak ditemukan!")
        return

    semua = ambil_harga()
    riwayat = []
    for h in semua:
        if h["commodity_id"] == terpilih["commodity_id"]:
            riwayat.append(h)

    for i in range(len(riwayat)):
        for j in range(i + 1, len(riwayat)):
            p1 = (riwayat[i]["year"], riwayat[i]["month"])
            p2 = (riwayat[j]["year"], riwayat[j]["month"])
            if p1 > p2:
                riwayat[i], riwayat[j] = riwayat[j], riwayat[i]

    if len(riwayat) == 0:
        print("Belum ada riwayat harga.")
        return

    tabel = []
    for h in riwayat:
        tabel.append({
            "periode": str(h["month"]) + "/" + str(h["year"]),
            "harga": format_rupiah(int(h["price"]))
        })
    print("\nRiwayat " + terpilih["name"] + " (" + terpilih["unit"] + ")")
    cetak_tabel(tabel, [("periode","Periode"), ("harga","Harga")])

# ===============================================
# 13. KELOLA KOMODITAS — TAMPILKAN DASHBOARD + KOMODITAS BARU LANGSUNG MUNCUL
# ===============================================
def kelola_komoditas():
    while True:
        print("\n=== KELOLA KOMODITAS ===")
        print("1. Lihat Semua Komoditas")
        print("2. Tambah Komoditas Baru")
        print("3. Ubah Data Komoditas")
        print("4. Hapus Komoditas")
        print("0. Kembali ke Menu Utama")
        pilihan = input("Pilih menu: ").strip()

        dashboard()

        if pilihan == "1":
            print("Data terbaru sudah ditampilkan di atas.\n")

        elif pilihan == "2":
            print("\n--- TAMBAH KOMODITAS BARU ---")
            print("Ketik 'batal' untuk membatalkan proses.\n")

            while True:
                iid = input("ID Komoditas (format: C + angka, contoh C005): ").strip().upper()
                if iid.lower() == "batal":
                    print("Penambahan dibatalkan.\n")
                    break
                if len(iid) >= 4 and iid[0] == "C" and iid[1:].isdigit():
                    semua = ambil_komoditas()
                    sudah_ada = False
                    for k in semua:
                        if k["commodity_id"].upper() == iid:
                            sudah_ada = True
                            break
                    if sudah_ada:
                        print("ID Komoditas sudah digunakan!")
                    else:
                        break
                else:
                    print("Format salah! Harus C + angka (contoh: C001, C123)")

            if iid.lower() == "batal":
                continue

            nama = input("Nama Komoditas: ").strip()
            if nama == "":
                print("Nama tidak boleh kosong!")
                continue
            if nama.lower() == "batal":
                print("Penambahan dibatalkan.\n")
                continue

            unit = input("Satuan: ").strip()
            if unit.lower() == "batal":
                print("Penambahan dibatalkan.\n")
                continue

            semua = ambil_komoditas()
            semua.append({"commodity_id": iid, "name": nama, "unit": unit})
            tulis_csv(FILE_COMMODITIES, ["commodity_id","name","unit"], semua)
            print("Komoditas berhasil ditambahkan!\n")
            dashboard()

        elif pilihan == "3":
            iid = input("ID yang diubah (atau 'batal'): ").strip().upper()
            if iid.lower() == "batal":
                print("Pengubahan dibatalkan.\n")
                continue
            semua = ambil_komoditas()
            ketemu = False
            for k in semua:
                if k["commodity_id"].upper() == iid:
                    nama_baru = input("Nama baru (kosong = tidak ubah): ").strip()
                    unit_baru = input("Satuan baru (kosong = tidak ubah): ").strip()
                    if nama_baru != "":
                        k["name"] = nama_baru
                    if unit_baru != "":
                        k["unit"] = unit_baru
                    ketemu = True
            if ketemu:
                tulis_csv(FILE_COMMODITIES, ["commodity_id","name","unit"], semua)
                print("Komoditas berhasil diubah!\n")
                dashboard()
            else:
                print("ID tidak ditemukan!\n")

        elif pilihan == "4":
            iid = input("ID yang dihapus (atau 'batal'): ").strip().upper()
            if iid.lower() == "batal":
                print("Penghapusan dibatalkan.\n")
                continue
            semua = ambil_komoditas()
            baru = []
            ketemu = False
            for k in semua:
                if k["commodity_id"].upper() != iid:
                    baru.append(k)
                else:
                    ketemu = True
            if ketemu:
                tulis_csv(FILE_COMMODITIES, ["commodity_id","name","unit"], baru)
                print("Komoditas berhasil dihapus!\n")
                dashboard()
            else:
                print("ID tidak ditemukan!\n")

        elif pilihan == "0":
            break

# ===============================================
# 14. INPUT HARGA BARU
# ===============================================
def input_harga_baru():
    print("\n=== INPUT HARGA BARU ===")

    while True:
        iid = input("ID Komoditas: ").strip().upper()
        if iid == "":
            print("ID tidak boleh kosong!")
            continue
        ada = False
        for k in ambil_komoditas():
            if k["commodity_id"].upper() == iid:
                ada = True
                break
        if not ada:
            print("ID Komoditas tidak ditemukan!")
            continue
        break

    while True:
        bln = input("Bulan (1-12): ").strip()
        if bln.isdigit() and 1 <= int(bln) <= 12:
            break
        print("Bulan harus angka 1-12!")

    while True:
        thn = input("Tahun (minimal 2000): ").strip()
        if thn.isdigit() and int(thn) >= 2000:
            break
        print("Tahun harus angka dan minimal 2000!")

    while True:
        hrg = input("Harga: ").strip()
        if hrg.replace(".", "").isdigit() and float(hrg) > 0:
            break
        print("Harga harus angka positif!")

    tambah_baris(FILE_PRICES, ["commodity_id","month","year","price"],
                 {"commodity_id": iid, "month": int(bln), "year": int(thn), "price": float(hrg)})
    print("Harga berhasil disimpan!")

# ===============================================
# 15. MENU TRANSAKSI
# ===============================================
def menu_transaksi():
    while True:
        print("\n=== MENU TRANSAKSI ===")
        print("1. Lihat Semua")
        print("2. Tambah Transaksi")
        print("0. Kembali")
        p = input("Pilih: ").strip()

        if p == "1":
            cetak_tabel(ambil_transaksi(),
                        [("trans_id","ID"), ("date","Tanggal"), ("commodity_id","Komoditas"),
                         ("type","Tipe"), ("quantity","Jumlah"), ("notes","Catatan")])

        elif p == "2":
            print("\n--- TAMBAH TRANSAKSI ---")
            print("Ketik 'batal' untuk batal.\n")

            while True:
                tid = input("ID Transaksi (T + angka, contoh T015): ").strip().upper()
                if tid.lower() == "batal":
                    print("Dibatalkan.\n")
                    break
                if len(tid) >= 2 and tid[0] == "T" and tid[1:].isdigit():
                    sudah_ada = False
                    for t in ambil_transaksi():
                        if t.get("trans_id","").upper() == tid:
                            sudah_ada = True
                            break
                    if sudah_ada:
                        print("ID sudah dipakai!")
                    else:
                        break
                else:
                    print("Format salah! Harus T + angka")

            if tid.lower() == "batal": continue

            while True:
                tgl = input("Tanggal (YYYY-MM-DD): ").strip()
                if tgl.lower() == "batal":
                    print("Dibatalkan.\n")
                    break

                if len(tgl) != 10 or tgl[4] != "-" or tgl[7] != "-":
                    print("Format salah! Harus YYYY-MM-DD")
                    continue

                tahun_str, bulan_str, hari_str = tgl[:4], tgl[5:7], tgl[8:]
                if not (tahun_str.isdigit() and bulan_str.isdigit() and hari_str.isdigit()):
                    print("Tahun, bulan, hari harus angka!")
                    continue

                tahun = int(tahun_str)
                bulan = int(bulan_str)
                hari = int(hari_str)

                if tahun < 2000:
                    print("Tahun minimal 2000!")
                    continue
                if not (1 <= bulan <= 12):
                    print("Bulan harus 1-12!")
                    continue
                if not (1 <= hari <= 31):
                    print("Hari maksimal 31!")
                    continue

                hari_dalam_bulan = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if bulan == 2 and (tahun % 4 == 0 and (tahun % 100 != 0 or tahun % 400 == 0)):
                    hari_dalam_bulan[1] = 29

                if hari > hari_dalam_bulan[bulan - 1]:
                    print(f"Bulan {bulan} hanya punya {hari_dalam_bulan[bulan-1]} hari!")
                    continue

                break

            if tgl.lower() == "batal": continue

            while True:
                kom = input("ID Komoditas: ").strip().upper()
                if kom.lower() == "batal":
                    print("Dibatalkan.\n")
                    break
                ada = False
                for k in ambil_komoditas():
                    if k["commodity_id"].upper() == kom:
                        ada = True
                        break
                if ada:
                    break
                print("ID tidak ditemukan!")

            if kom.lower() == "batal": continue

            while True:
                tipe = input("Tipe (IN/OUT): ").strip().upper()
                if tipe.lower() == "batal":
                    print("Dibatalkan.\n")
                    break
                if tipe in ["IN", "OUT"]:
                    break
                print("Hanya IN atau OUT!")

            if tipe.lower() == "batal": continue

            while True:
                jml = input("Jumlah: ").strip()
                if jml.lower() == "batal":
                    print("Dibatalkan.\n")
                    break
                if jml.replace(".", "").isdigit() and float(jml) > 0:
                    break
                print("Harus angka positif!")

            if jml.lower() == "batal": continue

            cat = input("Catatan: ").strip()
            if cat.lower() == "batal":
                print("Dibatalkan.\n")
                continue

            tambah_baris(FILE_TRANSACTIONS,
                         ["trans_id","date","commodity_id","type","quantity","notes"],
                         {"trans_id": tid, "date": tgl, "commodity_id": kom,
                          "type": tipe, "quantity": jml, "notes": cat})
            print("Transaksi berhasil disimpan!\n")

        elif p == "0":
            break

# ===============================================
# 16. MENU OPERATOR
# ===============================================
def menu_operator(user):
    while True:
        print("\n" + "="*60)
        print("                MENU OPERATOR - PENANSIL")
        print("="*60)
        print("1. Dashboard Harga Terbaru")
        print("2. Analisis Kenaikan/Penurunan Harga")
        print("3. Lihat Riwayat Harga per Komoditas")
        print("4. Kelola Data Komoditas")
        print("5. Input Harga Baru")
        print("6. Menu Transaksi")
        print("0. Logout dari Sistem")
        p = input("\nPilih menu: ").strip()

        if p == "1":
            dashboard()
        elif p == "2":
            analisis_naik_turun()
        elif p == "3":
            riwayat_harga()
        elif p == "4":
            kelola_komoditas()
        elif p == "5":
            input_harga_baru()
        elif p == "6":
            menu_transaksi()
        elif p == "0":
            while True:
                k = input("\nYakin logout? (y/n): ").strip().lower()
                if k == "y":
                    sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    catat_log(user, "Logout Operator")
                    print("Logout berhasil!")
                    return
                elif k == "n":
                    break
                else:
                    print("Ketik 'y' atau 'n' saja!")
        else:
            print("Pilihan tidak valid!")

# ===============================================
# 17. MENU ADMIN
# ===============================================
def menu_admin(user):
    while True:
        print("\n" + "="*60)
        print("                  MENU ADMIN - PENANSIL")
        print("="*60)
        print("1. Dashboard Harga Terbaru")
        print("2. Analisis Kenaikan/Penurunan Harga")
        print("3. Lihat Riwayat Harga per Komoditas")
        print("4. Kelola Data Komoditas")
        print("5. Input Harga Baru")
        print("6. Menu Transaksi")
        print("7. Kelola Pengguna")
        print("8. Lihat Log Aktivitas")
        print("9. Kunci/Buka Kunci User")
        print("0. Logout dari Sistem")
        p = input("\nPilih menu: ").strip()

        if p in ["1","2","3","4","5","6"]:
            if p == "1": dashboard()
            elif p == "2": analisis_naik_turun()
            elif p == "3": riwayat_harga()
            elif p == "4": kelola_komoditas()
            elif p == "5": input_harga_baru()
            elif p == "6": menu_transaksi()

        elif p == "7":
            while True:
                print("\n=== KELOLA PENGGUNA ===")
                print("1. Lihat User")
                print("2. Tambah User")
                print("3. Ubah Password")
                print("4. Hapus User")
                print("0. Kembali")
                sub = input("Pilih: ").strip()
                if sub == "1":
                    cetak_tabel(ambil_pengguna(), [("username","User"), ("password","Pass"), ("role","Role")])
                elif sub == "2":
                    u = input("Username: ").strip()
                    pw = input("Password: ").strip()
                    r = input("Role (admin/operator): ").strip().lower()
                    if r in ["admin","operator"]:
                        semua = ambil_pengguna()
                        semua.append({"username":u,"password":pw,"role":r})
                        tulis_csv(FILE_USERS, ["username","password","role"], semua)
                        print("User ditambah!")
                elif sub == "3":
                    u = input("Username: ").strip()
                    semua = ambil_pengguna()
                    for x in semua:
                        if x["username"] == u:
                            pw = input("Password baru: ").strip()
                            if pw: x["password"] = pw
                            tulis_csv(FILE_USERS, ["username","password","role"], semua)
                            print("Password diubah!")
                            break
                    else:
                        print("User tidak ada!")
                elif sub == "4":
                    u = input("Username: ").strip()
                    semua = ambil_pengguna()
                    baru = [x for x in semua if x["username"] != u]
                    if len(baru) < len(semua):
                        tulis_csv(FILE_USERS, ["username","password","role"], baru)
                        print("User dihapus!")
                    else:
                        print("User tidak ada!")
                elif sub == "0":
                    break

        elif p == "8":
            log = baca_csv(FILE_LOG)
            cetak_tabel(log, [("username","User"), ("action","Aksi"), ("date","Tanggal")])

        elif p == "9":
            print("\n=== KUNCI / BUKA KUNCI USER ===")
            print("Daftar pengguna saat ini:")
            semua_user = ambil_pengguna()
            tabel_user = []
            for usr in semua_user:
                status = "TERKUNCI" if user_terkunci(usr["username"]) else "AKTIF"
                tabel_user.append({
                    "username": usr["username"],
                    "role": usr["role"],
                    "status": status
                })
            cetak_tabel(tabel_user, [("username","Username"), ("role","Role"), ("status","Status")])

            print("Ketik 'batal' untuk kembali.\n")
            while True:
                u = input("Username yang akan dikunci/dibuka: ").strip()
                if u.lower() == "batal":
                    print("Kembali ke menu admin.\n")
                    break
                semua_user = ambil_pengguna()
                ada = False
                for usr in semua_user:
                    if usr["username"] == u:
                        ada = True
                        break
                if not ada:
                    print("Username tidak ditemukan!")
                    continue

                if user_terkunci(u):
                    while True:
                        k = input("User terkunci. Buka kunci? (y/n): ").strip().lower()
                        if k == "y":
                            f = open(FILE_LOCK, "r", encoding="utf-8")
                            lines = [l for l in f.readlines() if l.strip() != u]
                            f.close()
                            f = open(FILE_LOCK, "w", encoding="utf-8")
                            f.writelines(lines)
                            f.close()
                            print("User dibuka kuncinya!")
                            sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            catat_log(user, "Buka kunci user " + u)
                            break
                        elif k == "n":
                            print("Dibatalkan.")
                            break
                        else:
                            print("Ketik 'y' atau 'n' saja!")
                else:
                    while True:
                        k = input("User aktif. Kunci akun? (y/n): ").strip().lower()
                        if k == "y":
                            f = open(FILE_LOCK, "a", encoding="utf-8")
                            f.write(u + "\n")
                            f.close()
                            print("User dikunci!")
                            sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            catat_log(user, "Kunci user " + u)
                            break
                        elif k == "n":
                            print("Dibatalkan.")
                            break
                        else:
                            print("Ketik 'y' atau 'n' saja!")
                break

        elif p == "0":
            while True:
                k = input("\nYakin logout? (y/n): ").strip().lower()
                if k == "y":
                    sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    catat_log(user, "Logout Admin")
                    print("Logout berhasil!")
                    return
                elif k == "n":
                    break
                else:
                    print("Ketik 'y' atau 'n' saja!")

# ===============================================
# 18. BUAT SEMUA FILE
# ===============================================
def buat_file_default():
    if len(ambil_komoditas()) == 0:
        data = [
            {"commodity_id":"C001","name":"Beras","unit":"kg"},
            {"commodity_id":"C002","name":"Jagung","unit":"kg"},
            {"commodity_id":"C003","name":"Gandum","unit":"kg"},
            {"commodity_id":"C004","name":"Duren","unit":"kg"},
            {"commodity_id":"C005","name":"Kentang","unit":"kg"}
        ]
        tulis_csv(FILE_COMMODITIES, ["commodity_id","name","unit"], data)
    if len(ambil_harga()) == 0:
        data = [
            {"commodity_id":"C001","month":"1","year":"2024","price":"15000"},
            {"commodity_id":"C001","month":"2","year":"2024","price":"16000"},
            {"commodity_id":"C002","month":"1","year":"2024","price":"8000"},
            {"commodity_id":"C003","month":"1","year":"2024","price":"12000"}
        ]
        tulis_csv(FILE_PRICES, ["commodity_id","month","year","price"], data)
    if len(ambil_transaksi()) == 0:
        data = [
            {"trans_id":"T001","date":"2024-01-15","commodity_id":"C001","type":"IN","quantity":"100","notes":"Pembelian awal"},
            {"trans_id":"T002","date":"2024-01-20","commodity_id":"C001","type":"OUT","quantity":"30","notes":"Penjualan"},
            {"trans_id":"T003","date":"2024-02-10","commodity_id":"C002","type":"IN","quantity":"200","notes":"Restock"}
        ]
        tulis_csv(FILE_TRANSACTIONS, ["trans_id","date","commodity_id","type","quantity","notes"], data)
    if len(ambil_pengguna()) == 0:
        data = [
            {"username":"admin","password":"admin123","role":"admin"},
            {"username":"operator","password":"op123","role":"operator"}
        ]
        tulis_csv(FILE_USERS, ["username","password","role"], data)
    try:
        open(FILE_LOG, "r").close()
    except:
        tulis_csv(FILE_LOG, ["username","action","date"], [])
    try:
        open(FILE_LOCK, "r").close()
    except:
        open(FILE_LOCK, "w").close()

# ===============================================
# 19. MAIN PROGRAM
# ===============================================
def main():
    buat_file_default()
    print("Selamat datang di PENANSIL!")

    while True:
        user = login()
        if user is None:
            while True:
                k = input("\nCoba lagi? (y/n): ").strip().lower()
                if k == "y": break
                elif k == "n": print("Terima kasih!"); return
                print("Ketik y atau n!")
            continue

        username = user["username"]
        if user_terkunci(username):
            print("Akun terkunci!")
            continue

        role = user.get("role", "")
        if role == "operator":
            menu_operator(username)
        elif role == "admin":
            menu_admin(username)

        while True:
            k = input("\nKembali ke login? (y/n): ").strip().lower()
            if k == "y": break
            elif k == "n": print("Sampai jumpa!"); return
            print("Ketik y atau n!")

if __name__ == "__main__":
    main()