import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import sleep

base_ip = "192.168.1."  # Base IP to scan, adjust according to your network
timeout_duration = 2  # Timeout duration in seconds
max_workers = 40  # Number of threads to use for parallel requests

def apply_effect_to_wled(ip, effect_id, color):
    try:
        response = requests.post(f"http://{ip}/json/state", json={
            "seg": [{
                "id": 0,  # Ensure we apply to the default segment
                "fx": effect_id,  # Set the effect ID (0 for solid)
                "frz": False,  # Ensure it's not frozen
                "on": True,  # Ensure the segment is on
                "col": [color],  # Set the color
                "sx": 57,
                "ix": 255,
                "pal": 27,
                "c1": 128,
                "c2": 128,
                "c3": 16,
            }]
        }, timeout=timeout_duration)
        
        if response.status_code == 200:
            print(f"Effect {effect_id} with color {color} applied to segment 0 of {ip}")
        else:
            print(f"Failed to apply effect on segment 0 of {ip}")
    except requests.exceptions.RequestException as e:
        print(f"Error applying effect on segment 0 of {ip}: {e}")

def check_ip(ip):
    try:
        response = requests.get(f"http://{ip}/json", timeout=timeout_duration)
        if response.status_code == 200 and "WLED" in response.text:
            print(f"WLED Device Found: {ip}")
            # Apply the custom LED range effect
            apply_custom_led_range(ip)
            sleep(4)
            # Now, apply the sequence of solid color effects
            apply_effect_to_wled(ip, 0, [255, 0, 0])  # Red
            sleep(2)
            apply_effect_to_wled(ip, 0, [0, 255, 0])  # Green
            sleep(2)
            apply_effect_to_wled(ip, 0, [0, 0, 255])  # Blue
            sleep(2)
            apply_effect_to_wled(ip, 0, [255, 255, 255])  # White
            sleep(2)
            apply_effect_to_wled(ip, 28, [0, 255, 0])  # Final animation (current effect)
    except requests.exceptions.RequestException:
        pass

def apply_custom_led_range(ip):
    try:
        led_data = {
            "seg": {
                "i": [
                    0, 40, "FF0000",  # Red for LEDs 0-20
                    40, 80, "00FF00",  # Green for LEDs 20-60
                    80, 120, "0000FF"   # Blue for LEDs 60-80
                ]
            }
        }
        response = requests.post(f"http://{ip}/json/state", json=led_data, timeout=timeout_duration)
        if response.status_code == 200:
            print(f"Custom LED ranges applied to {ip}")
        else:
            print(f"Failed to apply custom LED range to {ip}")
    except requests.exceptions.RequestException as e:
        print(f"Error applying custom LED range on {ip}: {e}")

def discover_and_apply_effect():
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_ip, f"{base_ip}{i}"): i for i in range(1, 255) if i != 250}
        for future in as_completed(futures):
            ip = f"{base_ip}{futures[future]}"
            try:
                future.result()
            except Exception as e:
                print(f"Error with IP {ip}: {e}")

    print("Full scan complete. Restarting...")
    sleep(1)

# Main loop to continuously scan and apply effects
while True:
    discover_and_apply_effect()
