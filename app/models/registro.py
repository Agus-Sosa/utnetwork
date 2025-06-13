import hashlib
from app.models.Data_Base import DataBase
from dotenv import load_dotenv
import os
from mysql.connector import Error
from app.models.Mail_Send import Send_Mail
import random
load_dotenv(dotenv_path='../.env')


DB_NAME = os.getenv('DB_NAME')
DB_KEY = os.getenv('DB_KEY')
HOST = os.getenv('HOST')
USER = os.getenv('USER')
db_user = DataBase(HOST, USER, DB_KEY, DB_NAME)


class Registro:

    def __init__(self, nombre, mail, key):
        self.nombre = nombre
        self.mail = mail
        self.key = key

    def __hashear(self):  # podria incluir esta en registrar directamente pero prefiero manejarlo de manera separada
        """
        Hashea la contraseña
        """
        self.key = hashlib.sha256(self.key.encode()).hexdigest(
        )  # se supone que flask viene con una funcion para hacer esto piola

    def __existe(self):
        """
        revisa si el mail ya fue registrado y devuelve true o false
        si el mail no esta registrado devuelve false, en caso contrario true

        """
        db_user.conectar()

        check_mail = []
        check_mail = db_user.consulta(
            f"SELECT mail FROM usuarios WHERE mail = '{self.mail}'"
        )
        db_user.cerrar()

        if len(check_mail) < 1:
            return False
        else:
            return True

    def registrar(self):
        """
        Registra los usuarios en la base de datos
        """
        existe = self.__existe()
        if existe:
            print('el mail ya esta registrado') #esto debe ser enviado al front
            return False
        else:
            self.__hashear()
            if self.key:
                numero = random.randrange(0,30,1) #podria configurar esto para hacerlo mas dinamico
                #que leea la cantidad de imagenes en la carpeta avatar y de ahi lo ponga como parametro maximo
                #entonces cada vez que agreguemos un avatar eso se actualiza solo y no seria necesario ajustarlo
                #manualmente


                #esto asigna de manera aletoria un avatar para cada persona al momento del registro
                if numero < 10:
                    avatar_path= f'static/images/avatars/avatar_0{numero}.jpg'
                else:
                    avatar_path= f'static/images/avatars/avatar_{numero}.jpg' #no deberian existir avatars like 001
                #solucion momentanea revisar en casa
                print(avatar_path)

                db_user.conectar()
                db_user.consulta(
                    "INSERT INTO usuarios (nombre, mail,contrasena,state,avatar) VALUES (%s, %s,%s,%s,%s)", (self.nombre, self.mail, self.key, False, avatar_path))

                db_user.cerrar()
                #Los errores de consulta se maneja en  la clase base de datos
                MAIL = os.getenv('MAIL')
                MAIL_KEY = os.getenv('MAIL_KEY')
                avisar = Send_Mail(MAIL, MAIL_KEY, self.mail)
                # el contenido de abajo es solo representativo por el momento, armar uno decente
                contenido = """
                            <html>
<body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
    <tr>
        <td style="padding: 30px; text-align: center;">
        <h1 style="color: #2c3e50; margin-bottom: 10px;">¡Bienvenido a UTNetwork! 🎉</h1>
        <p style="color: #555555; font-size: 16px; line-height: 1.6;">
            Acabás de registrarte exitosamente en <strong>UTNetwork</strong>, la plataforma donde la comunidad tecnológica se conecta, comparte y crece.
        </p>
        <p style="color: #555555; font-size: 16px; line-height: 1.6;">
            Desde ahora vas a poder acceder a contenido exclusivo, eventos en vivo, foros técnicos y mucho más.
        </p>
        <a href="https://utnetwork.com/login" style="display: inline-block; background-color: #0066cc; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-top: 20px;">
            Accedé a tu cuenta
        </a>
        <hr style="margin: 40px 0; border: none; border-top: 1px solid #eeeeee;">
        <p style="font-size: 13px; color: #999999;">
Si no fuiste vos quien se registró, podés ignorar este mensaje o contactarnos.
</p>
</td>
</tr>
</table>
</body>
</html>
                            """
                avisar.enviarMail('Bienvenido a UTNetwork', contenido)
                return True

            else:
                print('no registrado') #eliminar esto y poner en el front que hubo un error en el registro
                #IMPORTANTE no especificar al usuario examente el error, solo decir que fue del sistema.
                # Para evitar vulnerabilidades expuestas.
                return False

    def __str__(self):
        return f'nombre: {self.nombre} mail: {self.mail} key:{self.key}'
