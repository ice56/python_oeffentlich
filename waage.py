import asyncio
from bleak import BleakScanner

# Trage hier wieder deine korrekte MAC-Adresse ein (oder UUID falls macOS)
TARGET_MAC = "F8:8F:C8:1A:95:66".lower() 

def callback(device, advertising_data):
    if device.address.lower() == TARGET_MAC:
        manufact_data = advertising_data.manufacturer_data
        
        if manufact_data:
            # Wir nehmen einfach das erste verfügbare Datenpaket der Waage
            for company_id, raw_bytes in manufact_data.items():
                byte_list = list(raw_bytes)
                
                # Wir brauchen mindestens 2 Bytes für das Gewicht
                if len(byte_list) >= 2:
                    # Extrahiere Byte 0 und Byte 1
                    byte0 = byte_list[0]
                    byte1 = byte_list[1]
                    
                    # Berechne das Gewicht (Big-Endian-Format)
                    gewicht_roh = (byte0 * 256) + byte1
                    gewicht_kg = gewicht_roh / 100.0
                    
                    # Plausibilitäts-Check: Werte unter 5 kg ignorieren (z.B. Sensorrauschen)
                    if gewicht_kg > 5.0:
                        print(f"⚖️ Aktuelles Gewicht: {gewicht_kg:.2f} kg (Signalstärke RSSI: {advertising_data.rssi})")

async def main():
    print("🚀 Skript gestartet. Scanne nach Daten der OOAK-Waage...")
    print("Bitte stelle dich jetzt auf die Waage!")
    
    scanner = BleakScanner(detection_callback=callback)
    
    async with scanner:
        # Scannt für 60 Sekunden, damit du genug Zeit hast, dich zu wiegen
        await asyncio.sleep(60.0) 

if __name__ == "__main__":
    asyncio.run(main())
