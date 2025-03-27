import numpy as np
from multiprocessing import shared_memory, Lock
import time

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

def display_coaches():
    """Display available coaches."""
    print("\nAvailable Coaches:")
    for i in range(NUM_COACHES):
        print(f"- C{i + 1}")
    print()

def display_seats(seat_map, coach):
    """Display seat availability for a specific coach."""
    print(f"\nSeat Availability for Coach C{coach + 1}:")
    for seat in range(SEATS_PER_COACH):
        status = '[X]' if seat_map[coach, seat] else '[ ]'
        print(f"S{seat + 1}: {status}", end='  ')
        if (seat + 1) % 4 == 0:
            print()
    print("\n")

def select_coach():
    """Prompt user to select a coach."""
    coach_input = input(f"Select Coach (C1-C{NUM_COACHES}): ").strip().upper()
    if not (coach_input.startswith('C') and coach_input[1:].isdigit()):
        print("Invalid coach selection.")
        return None
    coach = int(coach_input[1:]) - 1
    if coach < 0 or coach >= NUM_COACHES:
        print("Invalid coach selection.")
        return None
    return coach

def select_seat():
    """Prompt user to select a seat."""
    seat_input = input(f"Select Seat (S1-S{SEATS_PER_COACH}): ").strip().upper()
    if not (seat_input.startswith('S') and seat_input[1:].isdigit()):
        print("Invalid seat selection.")
        return None
    seat = int(seat_input[1:]) - 1
    if seat < 0 or seat >= SEATS_PER_COACH:
        print("Invalid seat selection.")
        return None
    return seat

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
        print("\n1. View Available Coaches")
        print("2. View Seat Availability")
        print("3. Book a Seat")
        print("4. Release a Seat")
        print("5. Exit")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            display_coaches()
        elif choice == '2':
            coach = select_coach()
            if coach is not None:
                display_seats(seat_map, coach)
        elif choice == '3':
            coach = select_coach()
            if coach is not None:
                display_seats(seat_map, coach)
                seat = select_seat()
                if seat is not None:
                    book_seat(seat_map, coach, seat, lock)
        elif choice == '4':
            coach = select_coach()
            if coach is not None:
                display_seats(seat_map, coach)
                seat = select_seat()
                if seat is not None:
                    release_seat(seat_map, coach, seat, lock)
        elif choice == '5':
            print(f"Goodbye, {username}!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

    shm.close()
    if input("Do you want to release shared memory? (yes/no): ").strip().lower() == 'yes':
        shm.unlink()

if __name__ == '__main__':
    user_interface()
