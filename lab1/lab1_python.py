# Листы с шифрованным и расшифрованным текстом
decrypted_text = []
encrypted_text = []

# Допустимый алфавит символов
alpha = ['a', 'b', 'c', 'd', 'e','f', 
         'g', 'h', 'i', 'j','k', 'l', 
         'm', 'n', 'o', 'p', 'q', 'r', 
         's', 't', 'u', 'v', 'w', 'x', 
         'y', 'z', '.', ',', '!', '?', 
         ';', ':', '%', ' ', '(', ')']

# Функция шифрования
def encript():
    res = []
    len_text = len(text)
    for i in range(len_text):
        res.append(text[i])

    offset = 30
    for char in res:
        if char not in alpha:
            print("Нет такого символа: ", char)
            exit()
        else:
            decrypted_text.append(alpha[alpha.index(char) - offset])

# Функция расшифрования
def decript():
    offset = 6
    for char in decrypted_text:
        encrypted_text.append(alpha[alpha.index(char) - offset])

text = input("Введите слово\предложение на английском: ").lower()
print('Исходный текст:', text)

# Вызов функции шифрования
encript()

# Вызов функции расшифрования
decript()

print('Зашифрованный текст: ' ,*decrypted_text, sep = '')
print('Расшифрованный текст: ' ,*encrypted_text, sep = '')