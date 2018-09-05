from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField,IntegerField,FieldList,FormField,SelectField,TextAreaField,SelectMultipleField,widgets
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError,Optional,InputRequired
from candyucab.db import Database
import psycopg2,psycopg2.extras

def estados():
    db =Database()
    cur = db.cursor_dict()
    cur.execute("SELECT l_id,l_nombre FROM lugar WHERE l_tipo = 'E';")
    return cur.fetchall()


def tiendas():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT ti_id,ti_nombre FROM tienda;")
    return cur.fetchall()

def tipo_productos():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT * FROM tipo_producto;")
    return cur.fetchall()

def productos():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT p_id,p_nombre FROM producto;")
    return cur.fetchall()

def estatus():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT es_id,es_tipo FROM estatus;")
    return cur.fetchall()

def permisos():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT per_id,per_funcion from permiso WHERE per_funcion like '%cliente' OR per_funcion like '%usuario'
                OR per_funcion like '%tienda' OR per_funcion like '%diariodulce'
                OR per_funcion like '%punto' OR per_funcion like '%rol'
                OR per_funcion in ('CREATE producto','DELETE producto','UPDATE producto','READ producto')
                OR per_funcion='UPDATE estatus';""")
    return cur.fetchall()

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass

class NonValidatingSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass

class MultiCheckboxField(NonValidatingSelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class UsuarioCForm(FlaskForm):
    username=StringField('Nombre de Usuario',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
    password = PasswordField('Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Actualizar')
    current_username = StringField()

    def validate_username(self,username):
        db = Database()
        cur = db.cursor_dict()
        if self.current_username.data != username.data:
            cur.execute("SELECT u_username from usuario WHERE u_username = %s;",(username.data,))
            if cur.fetchone():
                raise ValidationError('El username ya esta tomada')

class UpdateUsuarioForm(FlaskForm):
    username=StringField('Nombre de Usuario',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
    password = PasswordField('Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    rol = NonValidatingSelectField('Rol')
    submit=SubmitField('Actualizar')
    current_username = StringField()
    def validate_username(self,username):
        db = Database()
        cur = db.cursor_dict()
        if self.current_username.data != username.data:
            cur.execute("SELECT u_username from usuario WHERE u_username = %s;",(username.data,))
            if cur.fetchone():
                raise ValidationError('El username ya esta tomado')

class UsuarioForm(FlaskForm):
    ci = IntegerField('Cedula del empleado',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    username=StringField('Nombre de Usuario',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
    password = PasswordField('Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    rol = NonValidatingSelectField('Rol')
    submit=SubmitField('Actualizar')

    def validate_username(self,username):
        db = Database()
        cur = db.cursor_dict()
        cur.execute("SELECT u_username from usuario WHERE u_username = %s;",(username.data,))
        if cur.fetchone():
            raise ValidationError('El username ya esta tomado')

    def validate_ci(self,ci):
        db = Database()
        cur = db.cursor_dict()
        cur.execute("SELECT e_ci from empleado WHERE e_ci = %s;",(ci.data,))
        if cur.fetchone() == None:
            raise ValidationError('El empleado no existe')

    def validate_rol(self,rol):
        x =str(rol.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

class RolForm(FlaskForm):
    nombre = StringField('Nombre del Rol',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=60)])
    permisos = MultiCheckboxField('Permisos', choices=tuple(permisos()))
    submit=SubmitField('Actualizar')

class PrecioForm(FlaskForm):
    precio = IntegerField('Precio',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Actualizar')

class TiendaSelect(FlaskForm):
    tienda = NonValidatingSelectField('Estatus',choices=tuple(tiendas()))
    submit=SubmitField('Mostrar')
    def validate_producto(self,tienda):
        x =str(tienda.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

class EstatusForm(FlaskForm):
    estatus = NonValidatingSelectField('Estatus',choices=tuple(estatus()))
    submit=SubmitField('Cambiar')
    def validate_producto(self,estatus):
        x =str(estatus.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

class TarjetaCredito(FlaskForm):
    fvenc = DateField ('Fecha de vencimiento',format='%Y-%m-%d')
    nombre = StringField('Nombre Completo',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    numero = IntegerField('Numero',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    codigo = IntegerField('Codigo de seguridad',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    marca = NonValidatingSelectField('Marca',choices=[('VISA','VISA'),('MASTERCARD','MASTERCARD'),('AMERICAN EXPRESS','AMERICAN EXPRESS'),('DINERS CLUB','DINERS CLUB')])
    submit=SubmitField('Registrar')

    def validate_codigo(self,codigo):
        if len(str(codigo.data)) > 4:
            raise ValidationError('El codigo es invalido')

    def validate_numero(self,numero):
        if len(str(numero.data)) < 12:
            raise ValidationError('El numero de tarjeta invalido')

class TarjetaDebito(FlaskForm):
    fvenc = DateField ('Fecha de vencimiento',format='%Y-%m-%d')
    banco = NonValidatingSelectField('Banco',choices=[(1,'Mercantil'),(2,'BOD'),(3,'Banesco'),(4,'Banco Plaza'),(5,'Provincial')])
    nombre = StringField('Nombre Completo',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    numero = IntegerField('Numero',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Registrar')

    def validate_banco(self,banco):
        x =str(banco.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

    def validate_codigo(self,numero):
        if len(str(numero.data)) < 12:
            raise ValidationError('El numero de tarjeta invalido')

class ChequeForm(FlaskForm):
    faplicar = DateField ('Fecha a aplicar',format='%Y-%m-%d')
    nombre = StringField('Nombre Completo',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    numero = IntegerField('Numero del cheque',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Registrar')

    def validate_codigo(self,numero):
        if len(str(numero.data)) < 12:
            raise ValidationError('El numero de cheque invalido')

class DiarioDulce(FlaskForm):
    producto = NonValidatingSelectField('Producto',choices=tuple(productos()))
    descuento = IntegerField('Ingrese el descuento del producto, el valor es en %',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Registrar')
    def validate_producto(self,producto):
        x =str(producto.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

    def validate_descuento(self,descuento):
        if descuento.data > 100:
            raise ValidationError('El descuento no puede ser mayor al 100%')

class DescuentoForm(FlaskForm):
    descuento = IntegerField('Ingrese el descuento del producto, el valor es en %',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Registrar')
    def validate_descuento(self,descuento):
        if descuento.data > 100:
            raise ValidationError('El descuento no puede ser mayor al 100%')

class UpdateTiendaForm(FlaskForm):
    nombre = StringField('Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    estados = NonValidatingSelectField('Estado',choices=tuple(estados()))
    municipios = NonValidatingSelectField('Municipio',choices=[])
    parroquias = NonValidatingSelectField('Parroquia',choices=[])
    tipo = NonValidatingSelectField('Tipo de tienda',choices=[(2,'Mini Candy Shop'),(1,'Candy Shop')])
    submit=SubmitField('Actualizar')

class TiendaForm(FlaskForm):
    nombre = StringField('Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    estados = NonValidatingSelectField('Estado',choices=tuple(estados()))
    municipios = NonValidatingSelectField('Municipio',choices=[])
    parroquias = NonValidatingSelectField('Parroquia',choices=[])
    tipo = NonValidatingSelectField('Tipo de tienda',choices=[(2,'Mini Candy Shop'),(1,'Candy Shop')])
    submit=SubmitField('Registrar')

    def validate_estados(self,estados):
        x =str(estados.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

    def validate_municipios(self,municipios):
        x =str(municipios.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

    def validate_parroquias(self,parroquias):
        x =str(parroquias.data)
        if x == 'None':
            raise ValidationError('Este campo no puede dejarse vacio')

class AsistenciaForm(FlaskForm):
    excel = FileField('Ingrese el archivo excel',validators=[FileAllowed(['xlsx','xls'])])
    submit=SubmitField('Registar asistencia')

class ProductoForm(FlaskForm):
    picture = FileField('Ingrese foto del caramelo',validators=[FileAllowed(['jpg','png'])])
    nombre = StringField('Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    desc = TextAreaField('Descripcion del caramelo',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    tp = NonValidatingSelectField('Tipo de producto',choices=tuple(tipo_productos()))
    precio = IntegerField('Precio del producto',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Añadir Producto')

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember =BooleanField('Recuerdame')
    submit=SubmitField('Iniciar')

class TlfForm(FlaskForm):
    numero = IntegerField('Ingrese el Telefono sin el 0',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Añadir Telefono')

    def validate_numero(self,numero):
        if len(str(numero.data)) != 10 :
            raise ValidationError('El numero de telefono es invalido')

class PersonaContactoForm(FlaskForm):
    nombre = StringField('Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    apellido = StringField('Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
    submit=SubmitField('Añadir Persona')

class UpdateNForm(FlaskForm):
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido')])
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=2,max=20)])
        nom1 = StringField('Primer Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        nom2 = StringField('Segundo Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap1 = StringField('Primer Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap2 = StringField('Segundo Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ci = IntegerField('Cedula',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion
        estados = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios = NonValidatingSelectField('Municipio',choices=[])
        parroquias = NonValidatingSelectField('Parroquia',choices=[])
        submit=SubmitField('Actualizar')

        current_ci = IntegerField()
        current_rif = StringField()
        current_email = StringField()

        def validate_ci(self,ci):
            db = Database()
            cur = db.cursor_dict()
            if self.current_ci.data != ci.data:
                cur.execute("SELECT cn_ci from clientenatural WHERE cn_ci = %s;",(ci.data,))
                if cur.fetchone():
                    raise ValidationError('La cedula ya esta tomada')

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            if self.current_email.data != email.data:
                cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')
                else:
                    cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                    if cur.fetchone():
                        raise ValidationError('El email ya esta tomado')

        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            if self.current_rif.data != rif.data:
                cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')
                else:
                    cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                    if cur.fetchone():
                        raise ValidationError('El rif ya esta tomado')

        def validate_estados(self,estados):
            if (estados.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios(self,municipios):
            if (municipios.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias(self,parroquias):
            if (parroquias.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

class UpdateJForm(FlaskForm):
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido'),])
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
        demcom = StringField('Denominacion Comercial',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        razsoc = StringField('Razon Social',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        pagweb = StringField('Pagina Web',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=30)])
        capdis = IntegerField('Capital Disponible',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion Fiscal
        estados1 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios1 = NonValidatingSelectField('Municipio',choices=[])
        parroquias1 = NonValidatingSelectField('Parroquia',choices=[])
        # Direccion Fisica
        estados2 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios2 = NonValidatingSelectField('Municipio',choices=[])
        parroquias2 = NonValidatingSelectField('Parroquia',choices=[])
        #tlf1 = IntegerField('Capital Disponible',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        submit=SubmitField('Actualizar')
        current_rif = StringField()
        current_email = StringField()

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            if self.current_email.data != email.data:
                cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')
                else:
                    cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                    if cur.fetchone():
                        raise ValidationError('El email ya esta tomado')

        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            if self.current_rif.data != rif.data:
                cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')
                else:
                    cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                    if cur.fetchone():
                        raise ValidationError('El rif ya esta tomado')

        def validate_estados1(self,estados1):
            if (estados1.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_estados2(self,estados2):
            if (estados2.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios1(self,municipios1):
            if (municipios1.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios2(self,municipios2):
            if (municipios2.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias1(self,parroquias1):
            if (parroquias1.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias2(self,parroquias2):
            if (parroquias2.data == None):
                raise ValidationError('Este campo no puede dejarse vacio')

class RegistrationJForm(FlaskForm):
        username=StringField('Nombre de Usuario',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido')])
        password = PasswordField('Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        confim_password = PasswordField('Confirmar Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio'),EqualTo('password')])
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
        demcom = StringField('Denominacion Comercial',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        razsoc = StringField('Razon Social',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        pagweb = StringField('Pagina Web',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=30)])
        capdis = IntegerField('Capital Disponible',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion Fiscal
        estados1 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios1 = NonValidatingSelectField('Municipio',choices=[])
        parroquias1 = NonValidatingSelectField('Parroquia',choices=[])
        # Direccion Fisica
        estados2 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios2 = NonValidatingSelectField('Municipio',choices=[])
        parroquias2 = NonValidatingSelectField('Parroquia',choices=[])
        #tlf1 = IntegerField('Capital Disponible',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        submit=SubmitField('Registrate')

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
            if cur.fetchone():
                raise ValidationError('El email ya esta tomado')
            else:
                cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')


        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
            if cur.fetchone():
                raise ValidationError('El rif ya esta tomado')
            else:
                cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')

        def validate_estados1(self,estados1):
            x =str(estados1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_estados2(self,estados2):
            x =str(estados2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios1(self,municipios1):
            x = str(municipios1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios2(self,municipios2):
            x =str(municipios2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias1(self,parroquias1):
            x =str(parroquias1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias2(self,parroquias2):
            x =str(parroquias2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

class RegistrationNForm(FlaskForm):
        username=StringField('Nombre de Usuario',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=2,max=20)])
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido')])
        password = PasswordField('Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        confim_password = PasswordField('Confirmar Contraseña',validators=[DataRequired(message='Este campo no puede dejarse vacio'),EqualTo('password')])
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=2,max=20)])
        nom1 = StringField('Primer Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        nom2 = StringField('Segundo Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap1 = StringField('Primer Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap2 = StringField('Segundo Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ci = IntegerField('Cedula',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion
        estados = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios = NonValidatingSelectField('Municipio',choices=[])
        parroquias = NonValidatingSelectField('Parroquia',choices=[])
        submit=SubmitField('Registrate')
        def validate_username(self,username):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT u_username from usuario WHERE u_username = %s;",(username.data,))
            if cur.fetchone():
                raise ValidationError('El nombre de usuario ya esta tomado')


        def validate_ci(self,ci):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cn_ci from clientenatural WHERE cn_ci = %s;",(ci.data,))
            if cur.fetchone():
                raise ValidationError('La cedula ya esta tomada')

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
            if cur.fetchone():
                raise ValidationError('El email ya esta tomado')
            else:
                cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')


        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
            if cur.fetchone():
                raise ValidationError('El rif ya esta tomado')
            else:
                cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')

        def validate_estados(self,estados):
            x =str(estados.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios(self,municipios):
            x =str(municipios.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias(self,parroquias):
            x =str(parroquias.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

class TiendaJForm(FlaskForm):
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=20)])
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido')])
        demcom = StringField('Denominacion Comercial',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        razsoc = StringField('Razon Social',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=50)])
        pagweb = StringField('Pagina Web',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=1,max=30)])
        capdis = IntegerField('Capital Disponible',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion Fiscal
        estados1 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios1 = NonValidatingSelectField('Municipio',choices=[])
        parroquias1 = NonValidatingSelectField('Parroquia',choices=[])
        # Direccion Fisica
        estados2 = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios2 = NonValidatingSelectField('Municipio',choices=[])
        parroquias2 = NonValidatingSelectField('Parroquia',choices=[])
        carnet =BooleanField('Desea generar carnet?')
        tienda = NonValidatingSelectField('Seleccione la tienda',choices=tuple(tiendas()))
        submit=SubmitField('Registrar Cliente')

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
            if cur.fetchone():
                raise ValidationError('El email ya esta tomado')
            else:
                cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')


        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
            if cur.fetchone():
                raise ValidationError('El rif ya esta tomado')
            else:
                cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')

        def validate_estados1(self,estados1):
            x =str(estados1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_estados2(self,estados2):
            x =str(estados2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios1(self,municipios1):
            x = str(municipios1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios2(self,municipios2):
            x =str(municipios2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias1(self,parroquias1):
            x =str(parroquias1.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias2(self,parroquias2):
            x =str(parroquias2.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

class TiendaNForm(FlaskForm):
        email = StringField('Email',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Email(message='Ingrese un email valido')])
        rif = StringField('RIF',validators=[DataRequired(message='Este campo no puede dejarse vacio'),Length(min=2,max=20)])
        nom1 = StringField('Primer Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        nom2 = StringField('Segundo Nombre',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap1 = StringField('Primer Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ap2 = StringField('Segundo Apellido',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        ci = IntegerField('Cedula',validators=[DataRequired(message='Este campo no puede dejarse vacio')])
        #Direccion
        estados = NonValidatingSelectField('Estado',choices=tuple(estados()))
        municipios = NonValidatingSelectField('Municipio',choices=[])
        parroquias = NonValidatingSelectField('Parroquia',choices=[])
        carnet =BooleanField('Desea generar carnet?')
        tienda = NonValidatingSelectField('Seleccione la tienda',choices=tuple(tiendas()))
        submit=SubmitField('Registrar Cliente')

        def validate_ci(self,ci):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cn_ci from clientenatural WHERE cn_ci = %s;",(ci.data,))
            if cur.fetchone():
                raise ValidationError('La cedula ya esta tomada')

        def validate_email(self,email):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_email from clientejuridico WHERE cj_email = %s;",(email.data,))
            if cur.fetchone():
                raise ValidationError('El email ya esta tomado')
            else:
                cur.execute("SELECT cn_email from clientenatural WHERE cn_email = %s;",(email.data,))
                if cur.fetchone():
                    raise ValidationError('El email ya esta tomado')


        def validate_rif(self,rif):
            db = Database()
            cur = db.cursor_dict()
            cur.execute("SELECT cj_rif from clientejuridico WHERE cj_rif = %s;",(rif.data,))
            if cur.fetchone():
                raise ValidationError('El rif ya esta tomado')
            else:
                cur.execute("SELECT cn_rif from clientenatural WHERE cn_rif = %s;",(rif.data,))
                if cur.fetchone():
                    raise ValidationError('El rif ya esta tomado')

        def validate_estados(self,estados):
            x =str(estados.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_municipios(self,municipios):
            x =str(municipios.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')

        def validate_parroquias(self,parroquias):
            x =str(parroquias.data)
            if x == 'None':
                raise ValidationError('Este campo no puede dejarse vacio')
