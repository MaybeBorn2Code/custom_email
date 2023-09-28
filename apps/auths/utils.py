def save_password_to_file(email, password):
    file_path = "password.txt"

    with open(file_path, 'a') as file:
        file.write(f"Email: {email}\nPassword: {password}\n\n")
