import numpy as np
from multiprocessing import shared_memory, Lock, Process
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
        shm = shared_memory.SharedMemory(name=SEAT_MAP_NAME, create=True, size=TOTAL_SEATS)
        seat_map = np.ndarray((NUM_COACHES, SEATS_PER_COACH), dtype=bool, buffer=shm.buf)
        seat_map.fill(False)  # False indicates available seats
        print("Shared memory created and initialized.")
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=SEAT_MAP_NAME)
        seat_map = np.ndarray((NUM_COACHES, SEATS_PER_COACH), dtype=bool, buffer=shm.buf)
        print("Attached to existing shared memory.")
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
        if not seat_map[coach, seat]:
            seat_map[coach, seat] = True
            print(f"Seat S{seat + 1} in Coach C{coach + 1} successfully booked.")
            return True
        else:
            print(f"Seat S{seat + 1} in Coach C{coach + 1} is already booked.")
            return False

def release_seat(seat_map, coach, seat, lock):
    """Release a previously booked seat."""
    with lock:
        if seat_map[coach, seat]:
            seat_map[coach, seat] = False
            print(f"Seat S{seat + 1} in Coach C{coach + 1} has been released.")
            return True
        else:
            print(f"Seat S{seat + 1} in Coach C{coach + 1} was not booked.")
            return False

def user_interface():
    """Command-line interface for booking system."""
    shm, seat_map = initialize_shared_memory()
    lock = Lock()

    username = input("Enter your username: ").strip()
    print(f"Welcome, {username}!")

    while True:
        print("\n1. View Seat Availability")
        print("2. Book a Seat")
        print("3. Release a Seat")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            display_seats(seat_map)
        elif choice in ['2', '3']:
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

            if choice == '2':
                book_seat(seat_map, coach, seat, lock)
            else:
                release_seat(seat_map, coach, seat, lock)
        elif choice == '4':
            print(f"Goodbye, {username}!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

    shm.close()
    if input("Do you want to release shared memory? (yes/no): ").strip().lower() == 'yes':
        shm.unlink()

if __name__ == '__main__':
    user_interface()
