import json
import time
import threading
from uuid import uuid4

# Global seat lock dictionary
seat_locks = {}
lock = threading.Lock()

# Sample train schedule
trains = {
    "T123": {
        "departure": "08:00 AM",
        "arrival": "12:00 PM",
        "coaches": {f"C{i}": {f"S{j}": None for j in range(1, 21)} for i in range(1, 7)}
    }
}

# Function to display available seats
def display_seats(train_id, coach_id):
    coach = trains[train_id]["coaches"][coach_id]
    for seat, status in coach.items():
        state = "[X]" if status else "[ ]"
        print(f"{seat}: {state}", end="  ")
    print("\n")

# Function to lock a seat
def lock_seat(train_id, coach_id, seat_id, user_id):
    with lock:
        if trains[train_id]["coaches"][coach_id][seat_id] is None:
            trains[train_id]["coaches"][coach_id][seat_id] = user_id
            seat_locks[(train_id, coach_id, seat_id)] = time.time()
            return True
        return False

# Function to unlock seats after timeout
def unlock_seat(train_id, coach_id, seat_id):
    with lock:
        trains[train_id]["coaches"][coach_id][seat_id] = None
        seat_locks.pop((train_id, coach_id, seat_id), None)

def book_ticket():
    user_id = str(uuid4())
    train_id = "T123"
    print(f"Train {train_id} Schedule: {trains[train_id]['departure']} - {trains[train_id]['arrival']}")

    coach_id = input("Select Coach (C1-C6): ").strip().upper()
    if coach_id not in trains[train_id]["coaches"]:
        print("Invalid coach selection.")
        return

    display_seats(train_id, coach_id)

    seat_id = input("Select Seat (S1-S20): ").strip().upper()
    if seat_id not in trains[train_id]["coaches"][coach_id]:
        print("Invalid seat selection.")
        return

    if lock_seat(train_id, coach_id, seat_id, user_id):
        print(f"Seat {seat_id} locked. Confirm booking within 30 seconds.")

        # Allow user to confirm booking
        confirm = input("Confirm booking? (yes/no): ").strip().lower()
        if confirm == "yes":
            print(f"Booking confirmed for Seat {seat_id} in Coach {coach_id}.")
            return  # Do not unlock since booking is confirmed

        # If user does not confirm, unlock the seat
        print("Booking cancelled. Seat will be released.")
        unlock_seat(train_id, coach_id, seat_id)
    else:
        print("Seat already taken. Try another.")


# Run the CLI
if __name__ == "__main__":
    while True:
        print("1. Book Ticket\n2. Exit")
        choice = input("Enter choice: ")
        if choice == "1":
            book_ticket()
        elif choice == "2":
            break