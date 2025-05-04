from werkzeug.security import generate_password_hash

password = input("PASSWORD: ")

PASSWORD_HASH = generate_password_hash(password)

with open("password.txt", "w") as file:
    file.write(PASSWORD_HASH)
