from calculator import add, subtract, multiply, divide

def main():
    print("--- Aplikasi Perhitungan Python ---")
    while True:
        print("\nOpsi:")
        print("1. Tambah (+)")
        print("2. Kurang (-)")
        print("3. Kali (*)")
        print("4. Bagi (/)")
        print("5. Keluar")
        
        choice = input("Pilih menu (1-5): ")
        
        if choice == '5':
            print("Keluar dari aplikasi...")
            break
            
        if choice in ['1', '2', '3', '4']:
            try:
                num1 = float(input("Angka pertama: "))
                num2 = float(input("Angka kedua: "))
                
                if choice == '1':
                    print(f"Hasil: {add(num1, num2)}")
                elif choice == '2':
                    print(f"Hasil: {subtract(num1, num2)}")
                elif choice == '3':
                    print(f"Hasil: {multiply(num1, num2)}")
                elif choice == '4':
                    print(f"Hasil: {divide(num1, num2)}")
            except ValueError:
                print("Error: Masukkan angka yang valid!")
        else:
            print("Pilihan tidak tersedia.")

if __name__ == "__main__":
    main()
