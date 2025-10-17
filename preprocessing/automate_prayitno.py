import pandas as pd
import numpy as np
import os

# Import library yang dibutuhkan untuk preprocessing canggih
from sklearn.preprocessing import LabelEncoder
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def preprocess_data(input_path, output_dir):
    """
    Fungsi untuk memuat, membersihkan, dan menyimpan dataset penyakit jantung.

    Args:
        input_path (str): Path ke file CSV dataset mentah.
        output_dir (str): Path ke direktori untuk menyimpan data yang sudah bersih.

    Returns:
        pandas.DataFrame: DataFrame yang sudah dibersihkan.
    """
    print(f"Memuat dataset dari: {input_path}")
    df = pd.read_csv(input_path)
    print("Dataset berhasil dimuat.")
    
    print("\nMemulai proses preprocessing...")

    # 1. Membuat Target Biner (Sakit vs Tidak Sakit)
    df['target'] = df['num'].apply(lambda x: 1 if x > 0 else 0)
    
    # 2. Menghapus Kolom yang Tidak Diperlukan
    df = df.drop(['id', 'dataset', 'num'], axis=1)
    
    # 3. Menangani Data Tidak Logis (Outlier)
    df['trestbps'] = df['trestbps'].replace(0, np.nan)
    
    # 4. Encoding Kolom Kategorikal menjadi Angka
    categorical_cols = df.select_dtypes(include=['object', 'bool']).columns
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    
    # 5. Menangani Nilai Hilang (Missing Values) dengan IterativeImputer
    imputer = IterativeImputer(max_iter=10, random_state=42)
    original_columns = df.columns
    df_imputed_np = imputer.fit_transform(df)
    df = pd.DataFrame(df_imputed_np, columns=original_columns)
    
    print("Preprocessing selesai.")

    # 6. Membuat direktori output jika belum ada
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Direktori '{output_dir}' berhasil dibuat.")

    # 7. Menyimpan dataset yang sudah bersih
    cleaned_file_path = os.path.join(output_dir, 'heart_cleaned_automated.csv')
    df.to_csv(cleaned_file_path, index=False)
    print(f"Dataset bersih telah disimpan di: {cleaned_file_path}")

    return df

# Blok ini akan dieksekusi jika file ini dijalankan secara langsung
if __name__ == '__main__':
    # Menentukan path input dan output
    # Path dataset mentah
    raw_data_path = 'heart_disease_dataset/heart_disease_uci.csv'
    
    # Direktori untuk menyimpan hasil preprocessing
    processed_data_dir = 'membangun_model/heart_disease_preprocessing'

    # Menjalankan fungsi preprocessing
    cleaned_df = preprocess_data(input_path=raw_data_path, output_dir=processed_data_dir)

    print("\nProses otomatisasi selesai.")
    print("Contoh 5 baris pertama dari data yang sudah bersih:")
    print(cleaned_df.head())