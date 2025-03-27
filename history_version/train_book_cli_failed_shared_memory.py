from multiprocessing.shared_memory import SharedMemory
import numpy as np

def initialize_shared_data(manager):
    """ Initialize shared memory for seat availability. """
    trains = manager.dict({
        "T123": {
            "departure": "08:00 AM",
            "arrival": "12:00 PM",
            "coaches": {f"C{i}": manager.dict({f"S{j}": None for j in range(1, 21)}) for i in range(1, 7)}
        }
    })
    return trains

def start_shared_memory_server(trains):
    """ Keeps the shared memory server running. """
    print("Shared memory server started.")
    while True:
        time.sleep(10)  # Keep process alive

def display_seats(trains, train_id, coach_id):
    """ Display seat availability. """
    coach = trains[train_id]["coaches"][coach_id]
    for seat, status in coach.items():
        print(f"{seat}: {'[X]' if status else '[ ]'}")
    print("\n")

def book_ticket(username, trains):
    """ Handle user booking. """
    train_id = "T123"
    print(f"Train {train_id} Schedule: {trains[train_id]['departure']} - {trains[train_id]['arrival']}")

    coach_id = input("Select Coach (C1-C6): ").strip().upper()
    if coach_id not in trains[train_id]["coaches"]:
        print("Invalid coach selection.")
        return

    display_seats(trains, train_id, coach_id)

    seat_id = input("Select Seat (S1-S20): ").strip().upper()
    if seat_id not in trains[train_id]["coaches"][coach_id]:
        print("Invalid seat selection.")
        return

    if trains[train_id]["coaches"][coach_id][seat_id] is None:
        trains[train_id]["coaches"][coach_id][seat_id] = username
        print(f"Seat {seat_id} locked. Confirm booking within 30 seconds.")

        confirm = input("Confirm booking? (yes/no): ").strip().lower()
        if confirm == "yes":
            print(f"Booking confirmed for {username}: Seat {seat_id} in Coach {coach_id}.")
        else:
            trains[train_id]["coaches"][coach_id][seat_id] = None
            print("Booking cancelled. Seat released.")
    else:
        print("Seat already taken. Try another.")

def cli(trains):
    """ Command-line interface for users. """
    username = input("Enter your username: ").strip()
    print(f"Welcome, {username}!\n")

    while True:
        print("\n1. Book Ticket\n2. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            book_ticket(username, trains)
        elif choice == "2":
            print(f"Goodbye, {username}!")
            break

if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("Starting shared memory server...")

    # Create a Manager for shared memory
    manager = multiprocessing.Manager()
    trains = initialize_shared_data(manager)

    # Start shared memory server
    shared_memory_process = multiprocessing.Process(target=start_shared_memory_server, args=(trains,))
    shared_memory_process.start()

    print("Shared memory server started.")

    # Start CLI
    cli(trains)
