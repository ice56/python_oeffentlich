import asyncio
import csv
import os
from datetime import datetime
from bleak import BleakScanner

# Konfiguration
TARGET_MAC = "F8:8F:C8:1A:95:66".lower()  # Deine MAC-Adresse
CSV_FILENAME = "waagen_daten.csv"

# Globale Variable, um doppelte Speicherungen direkt hintereinander zu vermeiden
letztes_gewicht = 0.0

def in_csv_speichern(gewicht):
    global letztes_gewicht
    
    # Toleranzgrenze: Nur speichern, wenn sich das Gewicht um mehr als 0.2 kg unterscheidet
    # Verhindert, dass während eines einzigen Wiegevorgangs 20 Zeilen geschrieben werden
    if abs(gewicht - letztes_gewicht) < 0.2:
        return
        
    letztes_gewicht = gewicht
    zeitstempel = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(CSV_FILENAME)
    
    # CSV-Datei im "Append"-Modus (Anhängen) öffnen
    with open(CSV_FILENAME, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Falls die Datei neu ist, Spaltenüberschriften schreiben
        if not file_exists:
            writer.writerow(["Zeitstempel", "Gewicht_KG"])
            
        writer.writerow([zeitstempel, f"{gewicht:.2f}"])
        print(f"💾 In {CSV_FILENAME} gespeichert: {zeitstempel} -> {gewicht:.2f} kg")

def callback(device, advertising_data):
    if device.address.lower() == TARGET_MAC:
        manufact_data = advertising_data.manufacturer_data
        
        if manufact_data:
            for company_id, raw_bytes in manufact_data.items():
                byte_list = list(raw_bytes)
                
                if len(byte_list) >= 2:
                    byte0 = byte_list[0]
                    byte1 = byte_list[1]
                    
                    gewicht_roh = (byte0 * 256) + byte1
                    gewicht_kg = gewicht_roh / 100.0
                    
                    # Nur plausible Werte über 5 kg verarbeiten
                    if gewicht_kg > 5.0:
                        print(f"⚖️ Waage sendet: {gewicht_kg:.2f} kg")
                        in_csv_speichern(gewicht_kg)

async def main():
    print(f"🚀 Scanne nach OOAK-Waage. Daten werden in '{CSV_FILENAME}' gesichert...")
    print("Bitte jetzt auf die Waage stellen!")
    
    scanner = BleakScanner(detection_callback=callback)
    
    async with scanner:
        # Scannt für 60 Sekunden
        await asyncio.sleep(60.0)

if __name__ == "__main__":
    asyncio.run(main())
