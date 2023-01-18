import random
import sqlite3
import os


class SimpleBankingSystem:
    def __init__(self):
        self.card_number = ''
        self.pin_number = ''
        self.balance = 0

    @staticmethod
    def createDB(dbname: str):
        if not os.path.exists(dbname):
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS card (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        number TEXT,
                        pin TEXT,
                        balance INTEGER DEFAULT 0)''')
            conn.commit()
            conn.close()

    @staticmethod
    def generateCardNumber() -> str:
        iin = [4, 0, 0, 0, 0, 0]
        random.seed()
        iin.extend([random.randint(0, 9) for i in range(9)])
        check_sum = 0
        for idx, num in enumerate(iin, 1):
            if idx % 2 != 0:
                num = num * 2
            if num > 9:
                num = num - 9
            check_sum += num
        final_num = 10 - (check_sum % 10)
        iin.append(final_num)
        return ''.join(map(str, iin))

    @staticmethod
    def generatePin() -> str:
        random.seed()
        return ''.join(map(str, [random.randint(0, 9) for i in range(4)]))

    @staticmethod
    def create_account():
        card_number = SimpleBankingSystem.generateCardNumber()
        pin_number = SimpleBankingSystem.generatePin()
        conn = sqlite3.connect('card.s3db')
        c = conn.cursor()
        c.execute(f" INSERT INTO card(number, pin) VALUES('{card_number}', '{pin_number}')")
        conn.commit()
        print("Your card has been created\n"
              f"Your card number:\n{card_number}\n"
              f"Your card PIN:\n{pin_number}\n")

    def login(self):
        self.card_number = input("Enter your card number:\n")
        self.pin_number = input("Enter your PIN:\n")
        conn = sqlite3.connect('card.s3db')
        c = conn.cursor()
        account = c.execute(f"SELECT pin, balance FROM card WHERE number = '{self.card_number}'").fetchone()
        c.close()
        if account is None or self.pin_number != account[0]:
            print("\nWrong card number or PIN!\n")
        else:
            print("\nYou have successfully logged in!\n")
            while True:
                print("1. Balance\n"
                      "2. Add income\n"
                      "3. Do transfer\n"
                      "4. Close account\n"
                      "5. Log out\n"
                      "0. Exit")
                action = int(input())
                if action == 1:
                    c = conn.cursor()
                    self.balance = c.execute(
                        f"SELECT balance FROM card WHERE number = '{self.card_number}'").fetchone()[0]
                    c.close()
                    print(f"Balance: {self.balance}\n")
                elif action == 2:
                    self.add_income(conn)
                elif action == 3:
                    print('\nTransfer')
                    self.do_transfer(conn)
                elif action == 4:
                    self.close_account(conn)
                    break
                elif action == 5:
                    c.close()
                    conn.close()
                    self.card_number = ''
                    self.pin_number = ''
                    self.balance = 0
                    print("\nYou have successfully logged out!\n")
                    break
                elif action == 0:
                    print("\nBye!")
                    exit()

    @staticmethod
    def is_luhn(card: str):
        body = [int(i) for i in card[:15]]
        control = int(card[-1])
        check_sum = 0
        for idx, num in enumerate(body, 1):
            if idx % 2 != 0:
                num = num * 2
            if num > 9:
                num = num - 9
            check_sum += num
        final_num = 10 - (check_sum % 10)
        return final_num == control

    def add_income(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        try:
            income = int(input("Enter income:\n"))
        except ValueError:
            return None
        self.balance = cursor.execute(
            f"SELECT balance FROM card WHERE number = '{self.card_number}'").fetchone()[0] + income
        cursor.execute(f"UPDATE card SET balance = {self.balance} WHERE number == '{self.card_number}'")
        conn.commit()
        cursor.close()
        print("Income was added!\n")

    def do_transfer(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        to_card = input("Enter card numer:\n")
        if not SimpleBankingSystem.is_luhn(to_card):
            print('Probably you made a mistake in the card number. Please try again!\n')
        elif self.card_number == to_card:
            print("You can't transfer money to the same account!")
        else:
            try:
                self.balance = cursor.execute(
                    f"SELECT balance FROM card WHERE number = '{self.card_number}'").fetchone()[0]
                to_card_balance = cursor.execute(f"SELECT balance FROM card WHERE number = '{to_card}'").fetchone()[0]
                to_transfer = int(input('Enter how much money you want to transfer:\n'))
                if self.balance < to_transfer:
                    print('Not enough money!')
                else:
                    self.balance = self.balance - to_transfer
                    cursor.execute(f"UPDATE card SET balance = {self.balance} WHERE number == '{self.card_number}'")
                    to_card_balance = to_card_balance + to_transfer
                    cursor.execute(f"UPDATE card SET balance = {to_card_balance} WHERE number == '{to_card}'")
                    cursor.close()
                    conn.commit()
                    print('Success!\n')
            except TypeError:
                print('Such a card does not exist.\n')

    def close_account(self, conn: sqlite3.Connection):
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM card WHERE number == {self.card_number}")
        conn.commit()
        cursor.close()
        print('\nThe account has been closed!\n')

    def menu(self) -> None:
        SimpleBankingSystem.createDB('card.s3db')
        while True:
            print("1. Create an account\n"
                  "2. Log into account\n"
                  "0. Exit")
            action = int(input())
            if action == 1:
                SimpleBankingSystem.create_account()
            elif action == 2:
                self.login()
            else:
                print("\nBye!")
                exit()


SimpleBankingSystem().menu()
