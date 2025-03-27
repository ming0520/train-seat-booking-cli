import numpy as np
from multiprocessing.shared_memory import SharedMemory
from multiprocessing import Lock
import time
import sys

# Constants
NUM_COACHES = 6
SEATS_PER_COACH = 20
TOTAL_SEATS = NUM_COACHES * SEATS_PER_COACH
SEAT_MAP_NAME = 'train_seat_map'

def initialize_shared_memory():
    """Initialize shared memory for seat availability."""
    try:
        shm = SharedMemory(name=SEAT_MAP_NAME, create=True, size=TOTAL_SEATS)
        seat_map = np.ndarray((NUM_COACHES, SEATS_PER_COACH), dtype=np.uint8, buffer=shm.buf)
        seat_map.fill(0)  # 0 indicates available seats
    except FileExistsError:
        shm = SharedMemory(name=SEAT_MAP_NAME)
        seat_map = np.ndarray((NUM_COACHES, SEATS_PER_COACH), dtype=np.uint8, buffer=shm.buf)
    return shm, seat_map

def display_seats(seat_map):
    """Display the current seat availability."""
    print("\nCurrent Seat Availability:")
    for coach in range(NUM_COACHES):
        print(f"Coach C{coach + 1}: ", end="")
        for seat in range(SEATS_PER_COACH):
            status = 'X' if seat_map[coach, seat] else 'O'
            print(f"S{seat + 1}({status}) ", end="")
        print()
    print("O: Available, X: Booked\n")

def book_seat(seat_map, coach, seat, lock):
    """Attempt to book a seat."""
    with lock:
        if seat_map[coach, seat] == 0:
            seat_map[coach, seat] = 1
            print(f"Seat S{seat + 1} in Coach C{coach + 1} successfully booked.")
            return True
        else:
            print(f"Seat S{seat + 1} in Coach C{coach + 1} is already booked.")
            return False

def main():
    # Initialize shared memory and seat map
    shm, seat_map = initialize_shared_memory()
    lock = Lock()

    # Welcome user
    username = input("Enter your username: ")
    print(f"Welcome, {username}!")

    while True:
        print("\n1. View Seat Availability")
        print("2. Book a Seat")
        print("3. Exit")
        choice = input("Enter choice: ")

        if choice == '1':
            display_seats(seat_map)
        elif choice == '2':
            display_seats(seat_map)
            coach_input = input(f"Select Coach (C1-C{NUM_COACHES}): ").strip().upper()
            if not (coach_input.startswith('C') and coach_input[1:].isdigit()):
                print("Invalid coach selection.")
                continue
            coach = int(coach_input[1:]) - 1
            if coach < 0 or coach >= NUM_COACHES:
                print("Invalid coach selection.")
                continue

            seat_input = input(f"Select Seat (S1-S{SEATS_PER_COACH}): ").strip().upper()
            if not (seat_input.startswith('S') and seat_input[1:].isdigit()):
                print("Invalid seat selection.")
                continue
            seat = int(seat_input[1:]) - 1
            if seat < 0 or seat >= SEATS_PER_COACH:
                print("Invalid seat selection.")
                continue

            if book_seat(seat_map, coach, seat, lock):
                print("Booking confirmed.")
            else:
                print("Booking failed. Seat may already be booked.")
        elif choice == '3':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    # Cleanup
    shm.close()
    if input("Do you want to release shared memory? (yes/no): ").strip().lower() == 'yes':
        shm.unlink()

if __name__ == '__main__':
    main()
