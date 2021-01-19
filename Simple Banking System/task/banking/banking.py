# Write your code here
import random
import luhn
import sqlite3

class Card:
    def __init__(self):
        self.pin = None
        self.account_number = None
        self.checksum = '0'
        self.number = None

    def generate_pin(self):
        self.pin = '{:04d}'.format(random.randrange(0000, 9999))

    def generate_account(self):
        self.account_number = '400000{:09d}'.format(random.randrange(000000000, 999999999))

    def check_sum(self):
        while not luhn.verify(self.account_number + str(self.checksum)):
            self.checksum = int(self.checksum) + 1

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()

while True:
    card = Card()
    print('''
    1. Create an account\n
    2. Log into account\n
    0. Exit\n 
    ''')
    choice_1 = input()
    if choice_1 == '0':
        break
    elif choice_1 == '1':
        card.generate_pin()
        card.generate_account()
        card.check_sum()
        card.number = str(card.account_number + str(card.checksum))
        print("Your card has been created\n")
        print("Your card number:\n")
        print(card.number)
        print("Your card PIN:\n")
        print(card.pin)
        cur.execute(f'INSERT INTO card (number, pin) VALUES({card.number},{card.pin})')
        conn.commit()
    elif choice_1 == '2':
        print("Enter your card number:\n")
        user_number = input()
        cur.execute(f'SELECT number FROM card WHERE number = {user_number};')
        try:
            card.number = cur.fetchone()[0]
        except TypeError:
            card.number = '0'
        print("Enter your PIN:\n")
        user_pin = input()
        cur.execute(f'SELECT pin FROM card WHERE pin = {user_pin};')
        try:
            card.pin = cur.fetchone()[0]
        except TypeError:
            card.pin = '0'
        if user_number == card.number and user_pin == card.pin:
            print("You have successfully logged in!")
            while True:
                print('''
                1. Balance\n
                2. Add income\n
                3. Do transfer\n
                4. Close account\n
                5. Log out\n
                0. Exit\n
                ''')
                choice_2 = input()
                if choice_2 == "1":
                    cur.execute(f"SELECT balance FROM card WHERE number = {card.number};")
                    print(cur.fetchone()[0])
                elif choice_2 == '2':
                    income = int(input())
                    cur.execute(f'UPDATE card SET balance = (balance + {income}) WHERE number = {card.number}')
                    conn.commit()
                elif choice_2 == '3':
                    print('Destination account:')
                    transfer_to = input()
                    cur.execute(f"SELECT number FROM card WHERE number = {transfer_to};")
                    try:
                        destination = cur.fetchone()[0]
                    except TypeError:
                        destination = False
                    if card.number == destination:
                        print("You can't transfer money to the same account!")
                        continue
                    elif not destination:
                        print("Such a card does not exists.")
                        continue
                    elif not luhn.verify(destination) or transfer_to[0] == '3':
                        print("Probably you made a mistake in the card number. Please try again!")
                        continue
                    else:
                        print('Amount to transfer:')
                        transfer_amount = int(input())
                        cur.execute(f"SELECT balance FROM card WHERE number = {card.number};")
                        balance = cur.fetchone()[0]
                        if transfer_amount > balance:
                            print('Not enough money!')
                        else:
                            cur.execute(f'UPDATE card SET balance = balance + {transfer_amount} WHERE number = {destination}')
                            cur.execute(f'UPDATE card SET balance = balance - {transfer_amount} WHERE number = {card.number}')
                            conn.commit()
                            print("Success!")
                            cur.execute(f'SELECT balance FROM card WHERE number = {destination}')
                            print(cur.fetchone()[0])

                elif choice_2 == '4':
                    cur.execute(f'DELETE FROM card WHERE number = {card.number}')
                    conn.commit()
                    print("The account has been closed.")
                    break
                elif choice_2 == "5":
                    print("You have successfully logged out!")
                    break
                elif choice_2 == "0":
                    print("Bye!")
                    exit()
        else:
            print("Wrong card number or pin!")
