import geopandas as gpd
import os

# 1️⃣ — Shapefile joylashgan papka
BASE_DIR = r"C:\Users\user\Downloads\hotosm_uzb_buildings_polygons_shp"
SHAPE_FILE = os.path.join(BASE_DIR, "hotosm_uzb_buildings_polygons_shp.shp")

# 2️⃣ — Natija fayl joylashadigan manzil
OUTPUT_FILE = r"C:\Users\user\Downloads\tashkent_buildings.geojson"

print("⏳ Ma'lumotlar yuklanmoqda...")
gdf = gpd.read_file(SHAPE_FILE)

print("✅ Umumiy obyektlar soni:", len(gdf))

# 3️⃣ — Qaysi ustunlar mavjudligini tekshirib ko‘ramiz
print("Ustunlar:", list(gdf.columns))

# 4️⃣ — Toshkent shahriga tegishlilarni ajratamiz
# Ba'zi shapefile'larda "addr:city" yoki "is_in:city" ustunlari bo'ladi
city_columns = [col for col in gdf.columns if "city" in col]
print("Aniqlangan city ustunlari:", city_columns)

if "addr:city" in gdf.columns:
    tashkent_gdf = gdf[gdf["addr:city"].str.contains("Tashkent", case=False, na=False)]
elif "is_in:city" in gdf.columns:
    tashkent_gdf = gdf[gdf["is_in:city"].str.contains("Tashkent", case=False, na=False)]
else:
    print("⚠️ Toshkent uchun 'city' ustuni topilmadi. Faqat nomi orqali filtrlanadi.")
    tashkent_gdf = gdf[gdf["name"].str.contains("Tashkent", case=False, na=False)]

print("🏙️ Toshkentdagi obyektlar soni:", len(tashkent_gdf))

# 5️⃣ — GeoJSON formatga o‘tkazamiz
if len(tashkent_gdf) > 0:
    tashkent_gdf.to_file(OUTPUT_FILE, driver="GeoJSON")
    print(f"✅ Tayyor! Fayl saqlandi: {OUTPUT_FILE}")
else:
    print("❌ Toshkent shahriga oid ma'lumot topilmadi.")

print("🎯 Yakunlandi.")
