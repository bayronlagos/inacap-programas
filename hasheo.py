import bcrypt
#paso 1: obtener contraseña en plano
incoming_password = input("ingrese su contraseña: ").encode("UTF-8")
#paso 2: crear un pedazo de sal
salt= bcrypt.gensalt(rounds=12)
#paso 3: hashear una contraseña en plano y dar sal al hasheo
hashed_password = bcrypt.hashpw(password=incoming_password,salt=salt)

print("contraseña hasheada", hashed_password)

#paso 4: ingresar de nuevo la contraseña
confirm_password = input("ingrese nuevamente la contraseña: ").encode("UTF-8")
#paso5 comparar contraseñas
if bcrypt.checkpw(confirm_password, hashed_password):
    print("contraseña correcta")
else:
    print("contraseña incorrecta")