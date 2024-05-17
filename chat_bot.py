from collections import UserDict, defaultdict
from functools import reduce
import datetime as dt
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.value == other.value
        return False

class Name(Field):
    pass

class Phone(Field):
    MAX_LEN = 10

    def __init__(self, value):
        super().__init__(value)
        if len(self.value) > Phone.MAX_LEN:
            raise ValueError(f'There are too many digits in the entered phone number: {self.value}. The max length is 10 symbols.')

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            self.value = dt.datetime.strptime(self.value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone):
        phone = Phone(phone)
        if phone in self.phones:
            return 'Phone exists'
        self.phones.append(phone)
        return f"{self.name.value} : {', '.join(str(p) for p in self.phones)}"

    def find_phone(self, phone):
        phone = Phone(phone)
        if phone in self.phones:
            return f"The phone number: {phone} is found in {self.name.value} contacts"
        return f'The phone number: {phone} is not found'

    def edit_phone(self, old_phone, new_phone):
        old_phone, new_phone = Phone(old_phone), Phone(new_phone)
        if old_phone in self.phones:
            self.phones = [new_phone if phone == old_phone else phone for phone in self.phones]
            return f"The contact '{self.name.value}' edited phone number is: {', '.join(str(p) for p in self.phones)}"
        return f"The phone number: {old_phone} is not found"

    def delete_phone(self, phone):
        phone = Phone(phone)
        if phone in self.phones:
            self.phones.remove(phone)
            return f"The phone number: {phone} is deleted. Contact '{self.name.value}' phones remained are: {', '.join(str(p) for p in self.phones)}"
        return f"The phone number: {phone} is not found"

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday).value
        return f"The contact '{self.name.value}' birthday date is {self.birthday}"

    def __str__(self):
        return f"Name: '{self.name.value}', Phone number(s): '{', '.join(str(p) for p in self.phones)}', Date of birthday: '{self.birthday}'"

    def __repr__(self):
        return self.__str__()

class AddressBook(UserDict):
    def add_record(self, record):
        if record.name.value not in self.data:
            self.data[record.name.value] = record
            return f"Contact: {record.name.value} - is added"
        return f"Contact: {record.name.value} - already exists!"

    def find_record(self, name):
        if name in self.data:
            return f"Contact: {name} : {self.data[name]} - is found"
        return f"Contact: {name} - is not found"
           
    def delete_record(self, name):
        if name in self.data:
            self.data.pop(name)
            return f"The contact {name} is removed from the Addressbook"
        return f"{name} is not found in the Addressbook"
        
    def get_birthdays_per_week(self):
        today = dt.datetime.today().date()
        list_of_birthday_colleagues = defaultdict(list)
        for name, record in self.items():
            if record.birthday:
                birthday_this_year = record.birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                delta_days = (birthday_this_year - today).days
                if 0 <= delta_days < 7:
                    day_of_the_week = birthday_this_year.strftime("%A")
                    if day_of_the_week in ["Saturday", "Sunday"]:
                        list_of_birthday_colleagues['Monday'].append(name)
                    else:
                        list_of_birthday_colleagues[day_of_the_week].append(name)
        return {day: ', '.join(names) for day, names in list_of_birthday_colleagues.items()}
        
    def add_birthday(args, book):
        if len(args) < 2:
            raise ValueError("Provide both name and birthday.")
        name, birthday = args
        if name in book:
            record = book[name]
            return record.add_birthday(birthday)
        raise KeyError

    def show_birthdays(args, book):
        if len(args) < 1:
            raise ValueError("Provide the day of the week.")
        day = args[0].capitalize()  # Перевірка наявності дня тижня
        if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
            raise ValueError("Invalid day of the week.")
        birthdays = book.get_birthdays_per_week()
        return birthdays.get(day, f"No birthdays on {day}.")

    def show_contact(args, book):
        if len(args) < 1:
            raise ValueError("Provide the name.")
        name = args[0]
        if name in book:
            return str(book[name])
        raise KeyError

    def show_all(args, book):
        return '\n'.join(f"{record}" for name, record in book.items())
    
    def save_data(self, filename="addressbook.pkl"):
            with open(filename, "wb") as f:
                pickle.dump(self, f)

    def load_data(filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except (FileNotFoundError, pickle.UnpicklingError):
            return AddressBook()

# Бот для завантаження і перевірки даних:

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "No such name found"
        except IndexError:
            return "Not found"
        except Exception as e:
            return f"Error: {e}"
    return inner

@input_error
def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    cmd = cmd.lower()
    return cmd, args

@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError("Provide both name and phone number.")
    name, phone = args
    if name not in book:
        record = Record(name)
        book.add_record(record)
    else:
        record = book[name]
    return record.add_phone(phone)

@input_error
def change_contact(args, book):
    if len(args) < 2:
        raise ValueError("Provide both name and new phone number.")
    name, new_phone = args
    if name in book:
        record = book[name]
        if record.phones:
            old_phone = record.phones[0].value
            return record.edit_phone(old_phone, new_phone)
        return "No phones to update."
    raise KeyError

@input_error
def delete_contact(args, book):
    if len(args) < 1:
        raise ValueError("Provide the name of the contact to delete.")
    name = args[0]
    if name in book:
        return book.delete_record(name)
    else:
        raise KeyError(f"Contact '{name}' not found.")

@input_error
def show_phone(args, book):
    if len(args) < 1:
        raise ValueError("Provide the name.")
    name, = args
    if name in book:
        record = book[name]
        return f"{name}'s phones: {', '.join(str(phone) for phone in record.phones)}"
    raise KeyError

@input_error
def show_contact(args, book):
    if len(args) < 1:
        raise ValueError("Provide the name.")
    name = args[0]
    if name in book:
        return str(book[name])
    raise KeyError(f"No contact found with name: {name}")


@input_error
def add_birthday(args, book):
    if len(args) < 2:
        raise ValueError("Provide both name and birthday.")
    name, birthday = args
    if name in book:
        record = book[name]
        return record.add_birthday(birthday)
    raise KeyError

@input_error
def show_all(args, book):
    return '\n'.join(f"{name:15} : {record}" for name, record in book.items())

@input_error
def show_birthdays(args, book):
    if len(args) < 1:
        raise ValueError("Provide the day of the week.")
    day = args[0].capitalize()

    if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        raise ValueError("Invalid day of the week.")

    birthdays = book.get_birthdays_per_week()
    return birthdays.get(day, f"No birthdays on {day}.")


def main():
    book = AddressBook.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save_data()
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "delete":
            print(delete_contact (args, book))
        elif command == "edit":
            print(change_contact(args, book))
        elif command == "show_phone":
            print(show_phone(args, book))
        elif command == "show_contact":
            if args and args[0] == "show_all":
                print(show_all(args, book))
            else:
                print(show_contact(args, book))

        elif command == "all":
            print(show_all(args, book))
        elif command == "add_birthday":
            print(add_birthday(args, book))
        elif command == "show_birthdays":
            print(show_birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
