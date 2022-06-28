import string
import random

characters = list(string.ascii_letters + string.digits + '!@#$%^&*()')

def generatepass():
    lenght = random.randint(15, 20)
    random.shuffle(characters)
    password = []
    for i in range(lenght):
        password.append(random.choice(characters))
    
    random.shuffle(password)

    psw = ''.join(password)

    return psw