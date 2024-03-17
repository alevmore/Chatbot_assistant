from collections import UserDict
from functools import reduce
import datetime as dt
import pickle

class Field:
    def __init__(self, value):
        self.value = value
        self.name = value
     
    def __str__(self):
        return str(self.value) # реалізація 
  

class Name(Field): 
   
    def __init__(self):
        pass
        
             
class Phone(Field):
    MAX_LEN = 10
    def __init__(self, value):
        self.phone = value
        if len (self.phone) > 10:
            raise ValueError (f'There is too many digits in the entered phone number: {self.phone}. The max length is 10 symbols.')
    
class Birthday(Field):
   
    def __init__(self, value):
        self.birthday = value
        try:
            if dt.datetime.strptime(self.birthday, "%d.%m.%Y").date():
                return self.birthday
        except ValueError:
            raise ValueError ("Invalid date format. Use DD.MM.YYYY")  


class Record (Field):
   
    def __init__(self, name):
        self.name = Field(name)
        self.birthday = None
        self.phones= []

     
    def add_phone (self, phone):
        self.phone = Phone (phone)
        for user_phone in self.phones:
            if user_phone == phone:
                return 'Phone exists'
        self.phones.append(phone)
        return f" {self.name} : {self.phones}"

    
    def find_phone(self, phone):
        self.phone = Phone (phone)
        try:
            [self.phone for self.phone in self.phones if self.phone in self.phones]
            return f"The phone number: {self.phone} is found in {self.name} contacts"
        except: 
            raise f'The phone number: {self.phone} is not found'
  
   
    def edit_phones(self, phone, new_phone) :
        self.phone, self.new_phone = phone, new_phone
        if [self.phone for self.phone in self.phones if self.phone in self.phones]:
            self.phones = reduce(lambda a, b : a + [self.new_phone] if b == self.phone else a + [b], self.phones, [])
        return f" The contact \' {self.name} \' edited phone numbers are: {self.phones}"
            
         
    def  delete_phone (self, phone):
        self.phone = Phone (phone)
        if [self.phone for self.phone in self.phones if self.phone in self.phones]:
            self.phones.remove (self.phone)
            return f"The phone number: {self.phone} is deleted. Contact \'{self.name}\' phones remained are: {self.phones}"
        else: f" The phone number: {self.phone} is not found"

    
    def add_birthday (self, birthday:Birthday):
        self.birthday = birthday
        return f" The conract \'{self.name}\' birthday date is {self.birthday}"
    
            
    def __str__(self):
        
        return f" Name : \'{self.name}\' , Phone number: \'{", ".join(self.phone for self.phone in self.phones)}\', Date of birthday: \'{self.birthday}\'"
    
    def __repr__(self):
        
        return f" Name : \'{self.name}\' , Phone number: \'{", ".join(self.phone for self.phone in self.phones)}\', Date of birthday: \'{self.birthday}\'"
            

class AddressBook(UserDict): # реалізація класу

    def add_record (self, record): 
        record = Record(name)
        name= record.name.value
        if name not in self.data:
            self.data [name] = record
                   
            return f"Contact: {self.data [name]} - is added"
        else: 
            return f"Contact: {self.data [name]} - already exists!"
    
  
    def find_record (self, name, record):
        if name in self.data:
            return f"Contact: {name:15} : {record:15} - is found"
        else: 
            return F"Contact: {name:15} : {record:15} - is not found"
           
    def  delete_record (self, name, record):
        if name in self.data:
            self.data.pop(name) 
            return f"The contact of {name} is removed from Addressbook "
        else:
            return f'{name} is not found in the Addressbook'
        
    def get_birthdays_per_week(self):
        """Function prints a list of colleagues' birthdays for the following 7 days"""
        today = datetime.today().date()
        list_of_birthday_colleagues = defaultdict(list)
        for name, record in self.items():
            birthday = record.birthday.value.date()
            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year+1)
            else:
                birthday_this_year = birthday.replace(year=today.year)
            record.birthday = birthday_this_year
        # sorted_list = sorted(self, key = lambda contact: contact["birthday"])
        for name, record in self.items():
            next_birthday = record.birthday
            delta_days = (next_birthday - today).days
            str_next_birthday = str(next_birthday)
            if delta_days < 7:
                formatted = datetime.strptime(str_next_birthday, '%Y-%m-%d')
                day_of_the_week = datetime.strftime(formatted, "%A")
                if day_of_the_week == "Saturday" or day_of_the_week == "Sunday":
                    list_of_birthday_colleagues['Monday'].append(name)
                else:
                    list_of_birthday_colleagues[day_of_the_week].append(name)
        for day, names in list_of_birthday_colleagues.items():
            return f"{day}: {', '.join(names)}"
        
      
    def save_data (book, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(book, f)

    def load_data(filename="addressbook.pkl"):

        try:
            with open(filename, "rb", ) as f:
                return pickle.load(f)
        except FileNotFoundError:
            return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

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
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    """Function adds new contacts in the contact dictionary"""
    name, phone, *_ = args
    if record is None:
        record = Record(name)
        book.add_record(record)
        return "Contact added."
    if phone:
        record.add_phone(phone)
        return "Phone added."
    

@input_error
def change_contact(args, book):
    """Function checks if a contact is in contacts and substitutes the phone number"""
    name, phone = args
    if name in book.keys():
        record = book.get(name)
        old_phone = record.phones[0]
        record.edit_phone(old_phone, phone)
        return "Contact updated."
    else:
        raise KeyError

@input_error
def show_phone(args, book):
    """Function checks if a contact is in contacts and prints user's phone number"""
    name = args[0]
    if name in book:
        
        return book[name].phones
    else:
        raise KeyError
    
def add_birthday(args, book):
    name, birthday = args
    if name in book.keys():
        record = book.get(name)
        return record.add_birthday(birthday)
    else:
        record = Record(name)
        record.add_birthday(birthday)


def birthdays(book):
    return book.get_birthdays_per_week()

@input_error
def show_all(args, book):
    s=''
    for name in book:
        s+=(f"{name:15} : {book[name]}\n")
    return s


def main():
    book = AddressBook()
    book =AddressBook.load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input (user_input)

        if command in ["close", "exit"]:
            AddressBook.save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
        
        elif command == "add":
            print(add_contact (args, book))

        elif command == "change":
            print (change_contact(args, book))

        elif command == "show":
            print(show_phone(args,book))
        
        elif command == "all":
            print(show_all (args,book))

        elif command == "add_birthday":
            print(add_birthday (args,book))

        elif command == "show_birthdays":
            print(birthdays (args,book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()          

