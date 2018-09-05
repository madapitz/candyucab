from flask import render_template,url_for,flash,redirect,request,abort,jsonify
from candyucab.forms import RegistrationJForm,LoginForm,PersonaContactoForm,TlfForm,RegistrationNForm,UpdateJForm,UpdateNForm,TiendaJForm,TiendaNForm,UsuarioForm,RolForm,UsuarioCForm,UpdateUsuarioForm
from candyucab.forms import  ProductoForm,TiendaForm,UpdateTiendaForm,AsistenciaForm,TarjetaDebito,TarjetaCredito,ChequeForm,DiarioDulce,DescuentoForm,EstatusForm,PrecioForm,TiendaSelect
from candyucab import app,bcrypt
from candyucab.user import User
import secrets
import os
import datetime
import time
from datetime import date,timedelta
import pyexcel as p
from PIL import Image
import psycopg2
from candyucab.db import Database
from flask_login import login_user,current_user,logout_user,login_required


@app.route("/")
@app.route("/home")
def home():
   return render_template('home.html')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/images',picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

def roles():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT r_id,r_tipo FROM rol;")
    return cur.fetchall()

@app.route("/reporte/clientePunto")
-def clientePunto():
-    db = Database()
-    cur = db.cursor_dict()
-    cur.execute("""SELECT COUNT(P.*) as cantidad, CA.car_id AS car,C.cn_rif as rif  from clientenatural C, punto P , carnet CA
-                where CA.cn_id = C.cn_id AND P.car_id = CA.car_id GROUP BY car,rif
-                UNION
-                SELECT COUNT(P.*) as cantidad, CA.car_id as car,J.cj_rif as rif from clientejuridico J, punto P , carnet CA
-                where CA.cj_id = J.cj_id AND P.car_id = CA.car_id GROUP BY car,rif
-                ORDER BY cantidad  DESC LIMIT 10;""")
-    clientes = cur.fetchall()
-    return render_template('ReporteClientePunto.html',clientes=clientes)

@app.route("/reporte/tipoProducto")
def tipo_Producto():
    db = Database()
    cur = db.cursor_dict()
    cur.execute(""" SELECT TP.tp_id,COUNT(P.*) AS cantidad,TP.tp_nombre from producto P,tipo_producto TP
                    WHERE TP.tp_id = P.tp_id GROUP BY TP.tp_id,TP.tp_nombre
                    ORDER BY COUNT(*) DESC LIMIT 1;""")
    tipoProducto = cur.fetchone()
    return render_template('ReporteTipoProducto.html',tipoProducto=tipoProducto)

@app.route("/reporte/asistencia")
def r_asistencia():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT  to_char(A.as_fecha_entrada::date,'DD-MM-YY') as dia,concat(EXTRACT(HOUR FROM A.as_fecha_entrada),':',EXTRACT(minute FROM A.as_fecha_entrada) ) AS entrada ,
                    concat(EXTRACT(HOUR FROM A.as_fecha_salida),':',EXTRACT(minute FROM A.as_fecha_salida) ) AS salida ,
                    E.e_ci,E.e_nombre,E.e_apellido,T.ti_nombre from empleado E,tienda T, asistencia A
                    where E.e_id=A.e_id AND T.ti_id = E.ti_id ;""")
    empleados = cur.fetchall()
    return render_template('ReporteAsistencia.html',empleados=empleados)

@app.route("/reporte/marca")
def marca_tdc():
    db = Database()
    cur = db.cursor_dict()
    cur.execute(""" SELECT tc_marca,COUNT(*) AS cantidad from tarjetacredito GROUP BY tc_marca
                    ORDER BY COUNT(*) DESC LIMIT 1;""")
    marca = cur.fetchone()
    return render_template('marca.html',marca=marca)

@app.route("/reporte")
def reportes():
    return render_template('reportes.html')

@app.route("/diariodulce")
def diariodulce():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT P.p_nombre,P.p_precio, P.p_imagen,(P.p_precio-P.p_precio*PD.pd_descuento) AS descuento
                    from pro_diario PD,producto P,diariodulce D where
                    PD.dd_id = D.dd_id AND P.p_id=PD.p_id
                    AND CURRENT_DATE between D.dd_femision and D.dd_ffinal; """)
    productos = cur.fetchall()
    db.cerrar()
    return render_template('diariodulce.html',productos=productos)


@app.route("/rol/<int:r_id>/delete",methods=['GET','POST'])
def delete_rol(r_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE rol'))
        permiso = cur.fetchone()
        if permiso:
            db = Database()
            cur = db.cursor_dict()
            try:
                cur.execute("""DELETE FROM  rol WHERE r_id=%s;""",(r_id,))
            except:
                print("ERROR deleting into rol ")
                db.retroceder()
            db.actualizar()
            flash('Su rol eliminado exitosamente','success')
            return redirect(url_for('rol'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/rol/<int:r_id>/update",methods=['GET','POST'])
def update_rol(r_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE rol'))
        permiso = cur.fetchone()
        if permiso:
            form = RolForm()
            db = Database()
            cur = db.cursor_dict()
            cur.execute("""SELECT r.r_tipo,p.per_id from rol r,rol_per rp, permiso p
                        WHERE r.r_id = %s AND r.r_id = rp.r_id AND p.per_id = rp.per_id;""",(r_id,))
            rol = cur.fetchall()
            if form.validate_on_submit():
                try:
                    cur.execute("""DELETE FROM rol_per where r_id = %s;""",
                    (r_id,))
                except:
                    print("ERROR deleting into rol_per")
                    db.retroceder()
                try:
                    cur.execute("""UPDATE rol SET r_tipo=%s where r_id=%s;""",
                    (form.nombre.data,r_id,))
                except:
                    print("ERROR updating into rol")
                    db.retroceder()
                for permiso in form.permisos.data:
                    try:
                        cur.execute("""INSERT INTO rol_per (r_id, per_id)
                        VALUES (%s, %s);""",
                        (r_id,int(permiso)))
                    except:
                        print("ERROR inserting into rol_per")
                        db.retroceder()
                db.actualizar()
                return redirect(url_for('rol'))
            elif request.method == 'GET':
                form.nombre.data = rol[0]['r_tipo']
                list_permisos = []
                for x in rol:
                    list_permisos.append(str(x['per_id']))
                form.permisos.data = list_permisos
            return render_template('createRol.html',form=form,r_id=r_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/rol/create",methods=['GET','POST'])
def create_rol():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE rol'))
        permiso = cur.fetchone()
        if permiso:
            form = RolForm()
            if form.validate_on_submit():
                db = Database()
                cur = db.cursor_dict()
                try:
                    cur.execute("""INSERT INTO rol (r_tipo)
                    VALUES (%s) RETURNING r_id;""",
                    (form.nombre.data,))
                except:
                    print("ERROR inserting into rol")
                    db.retroceder()

                rol = cur.fetchone()[0]
                db.actualizar()
                for permiso in form.permisos.data:
                    try:
                        cur.execute("""INSERT INTO rol_per (r_id, per_id)
                        VALUES (%s, %s);""",
                        (rol,int(permiso)))
                    except:
                        print("ERROR inserting into rol_per")
                        db.retroceder()

                db.actualizar()
                flash('Su rol se ha creado exitosamente','success')
                return redirect(url_for('rol'))
            return render_template('createRol.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/rol",methods=['GET','POST'])
def rol():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ rol'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("""SELECT r.*,p.per_funcion from rol r,rol_per rp,permiso p
                        where p.per_id = rp.per_id AND r.r_id=rp.r_id ORDER BY r.r_id DESC;""")
            roles = cur.fetchall()
            db.cerrar()
            return render_template('roles.html',roles=roles)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')


@app.route("/usuarios/<int:u_id>/update/empleado",methods=['GET','POST'])
def update_usuario_empleado(u_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE usuario'))
        permiso = cur.fetchone()
        if permiso:
            form = UpdateUsuarioForm()
            form.rol.choices = [(g['r_id'], g['r_tipo']) for g in roles()]
            cur.execute("SELECT u_username,u_password from usuario WHERE u_id = %s;",(u_id,))
            usuario = cur.fetchone()
            form.current_username.data = usuario['u_username']
            if form.validate_on_submit():
                if form.rol.data != None:
                    try:
                        cur.execute("""UPDATE usuario SET u_username = %s,u_password =%s,r_id=%s WHERE u_id=%s;""",
                                (form.username.data,form.password.data,form.rol.data,u_id))
                    except:
                        print("ERROR updating into usuario empleado con rol")
                        db.retroceder()
                else:
                    try:
                        cur.execute("""UPDATE usuario SET u_username = %s,u_password = %s WHERE u_id=%s;""",
                                (form.username.data,form.password.data,u_id))
                    except:
                        print("ERROR updating into usuario empleado")
                        db.retroceder()
                db.actualizar()
                return redirect(url_for('usuarios'))
            elif request.method == 'GET':
                form.username.data = usuario['u_username']
                form.password.data = usuario['u_password']
            return render_template('createUsuario.html',form=form,u_id=u_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')


@app.route("/usuarios/<int:u_id>/update/cliente",methods=['GET','POST'])
def update_usuario_cliente(u_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE usuario'))
        permiso = cur.fetchone()
        if permiso:
            form = UsuarioCForm()
            cur.execute("SELECT u_username,u_password from usuario WHERE u_id = %s;",(u_id,))
            usuario = cur.fetchone()
            form.current_username.data = usuario['u_username']
            if form.validate_on_submit():
                try:
                    cur.execute("""UPDATE usuario SET u_username = %s,u_password = %s WHERE u_id=%s;""",
                                (form.username.data,form.password.data,u_id,))
                except:
                    print("ERROR updating into usuario")
                    db.retroceder()
                db.actualizar()
                return redirect(url_for('usuarios'))
            elif request.method == 'GET':
                form.username.data = usuario['u_username']
                form.password.data = usuario['u_password']
            return render_template('createUsuario.html',form=form,u_id=u_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/usuario/<int:u_id>/delete",methods=['GET','POST'])
def delete_usuario(u_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE usuario'))
        permiso = cur.fetchone()
        if permiso:
            try:
                cur.execute("""DELETE FROM  usuario WHERE u_id=%s;""",(u_id,))
            except:
                print("ERROR deleting into usuario ")
                db.retroceder()
            db.actualizar()
            flash('Su usuario eliminado exitosamente','success')
            return redirect(url_for('usuarios'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/usuario/create",methods=['GET','POST'])
def create_usuario():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE usuario'))
        permiso = cur.fetchone()
        if permiso:
            form = UsuarioForm()
            form.rol.choices = [(g['r_id'], g['r_tipo']) for g in roles()]
            if form.validate_on_submit():
                cur.execute("""SELECT e_id from empleado
                                WHERE e_ci=%s;""",(form.ci.data,))
                empleado=cur.fetchone()
                try:
                    cur.execute("""INSERT INTO usuario (u_username,u_password,e_id,r_id)
                                    VALUES (%s,%s,%s,%s);""",(form.username.data,form.password.data,empleado['e_id'],form.rol.data))
                except:
                    print("ERROR inserting into usuario ")
                    db.retroceder()
                db.actualizar()
                flash('Su usuario se ha creado exitosamente','success')
                return redirect(url_for('usuarios'))
            return render_template('createUsuario.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/usuarios",methods=['GET','POST'])
def usuarios():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ usuario'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("""SELECT u.u_id,u.u_username, cn.cn_rif as rif from usuario u,clientenatural cn where u.cn_id = cn.cn_id
                        UNION
                        SELECT u.u_id,u.u_username, cj.cj_rif as rif from usuario u,clientejuridico cj where u.cj_id = cj.cj_id
                        ORDER BY u_id DESC;""")
            usuariosC = cur.fetchall()
            cur.execute("""SELECT u.u_id ,u.u_username,e.e_ci,(SELECT r.r_tipo from rol r where u.r_id =r.r_id ) AS rol
                            from empleado e, usuario u where e.e_id=u.e_id ORDER BY u_id DESC;""")
            usuariosE = cur.fetchall()
            db.cerrar()
            return render_template('usuarios.html',usuariosC=usuariosC,usuariosE=usuariosE)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/puntos/<int:h_id>/update",methods=['GET','POST'])
def update_puntos(h_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE punto'))
        permiso = cur.fetchone()
        if permiso:
            form = PrecioForm()
            if form.validate_on_submit():
                try:
                    cur.execute("""UPDATE historial SET h_precio = %s WHERE h_id=%s;""",
                                (form.precio.data,h_id,))
                except:
                    print("ERROR updating into historial")
                    db.retroceder()
                db.actualizar()
                return redirect(url_for('puntos'))
            return render_template('createPunto.html',form=form,h_id=h_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/puntos/<int:h_id>/delete",methods=['GET','POST'])
def delete_puntos(h_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE punto'))
        permiso = cur.fetchone()
        if permiso:
            try:
                cur.execute("""DELETE FROM  historial WHERE h_id=%s;""",(h_id,))
            except:
                print("ERROR deleting into historial ")
                db.retroceder()
            db.actualizar()
            flash('Su precio del punto se ha eliminado exitosamente','success')
            return redirect(url_for('puntos'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/puntos/create",methods=['GET','POST'])
def create_puntos():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE punto'))
        permiso = cur.fetchone()
        if permiso:
            form = PrecioForm()
            if form.validate_on_submit():
                try:
                    cur.execute("""INSERT INTO historial (h_precio)
                                    VALUES (%s);""",(form.precio.data,))
                except:
                    print("ERROR inserting into historial ")
                    db.retroceder()
                db.actualizar()
                flash('Su precio del punto se ha creado exitosamente','success')
                return redirect(url_for('puntos'))
            return render_template('createPunto.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/puntos",methods=['GET','POST'])
def puntos():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ punto'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("SELECT *  FROM historial  ORDER BY h_id;")
            puntos = cur.fetchall()
            db.cerrar()
            return render_template('puntos.html',puntos=puntos)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/pedidos/<int:ped_id>/update",methods=['GET','POST'])
def update_estatus(ped_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE estatus'))
        permiso = cur.fetchone()
        if permiso:
            form = EstatusForm()
            if form.validate_on_submit():
                try:
                    cur.execute("""INSERT INTO  ped_est (ped_id,es_id) VALUES (%s,%s)""",
                                (ped_id,form.estatus.data,))
                except:
                    print("ERROR insertin into ped_est")
                    db.retroceder()
                db.actualizar()
                return redirect(url_for('pedidos'))
            return render_template('updateEstatus.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/pedidos/tiendas",methods=['GET','POST'])
def pedidos_tiendas():
    form = TiendaSelect()
    if form.validate_on_submit():
        return redirect(url_for('pedidos_tienda',ti_id=form.tienda.data))
    return render_template('tiendaSelect.html',form=form)

@app.route("/pedidos/<int:ti_id>",methods=['GET','POST'])
def pedidos_tienda(ti_id):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT P.ped_id,P.ped_fentrega,T.ti_nombre,E.es_tipo FROM pedido P, departamento D, estatus E,
                    (SELECT P.ped_id,MAX(PD.pe_id) as pe_id from ped_est PD,pedido P WHERE P.ped_id = PD.ped_id
                     GROUP BY P.ped_id) as PD1,Tienda T,ped_est PD2 WHERE P.d_id = D.d_id AND E.es_id=PD2.es_id AND
                     P.ped_id = PD1.ped_id AND D.ti_cod=T.ti_id AND PD2.pe_id=PD1.pe_id AND T.ti_id=%s;""",(ti_id,))
    tiendas = cur.fetchall()
    return render_template('pedidosTienda.html',tiendas = tiendas)

@app.route("/pedidos",methods=['GET','POST'])
def pedidos():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT P.ped_id,P.ped_fentrega,T.ti_nombre,E.es_tipo FROM pedido P, departamento D, estatus E,
                    (SELECT P.ped_id,MAX(PD.pe_id) as pe_id from ped_est PD,pedido P WHERE P.ped_id = PD.ped_id
                     GROUP BY P.ped_id) as PD1,Tienda T,ped_est PD2 WHERE P.d_id = D.d_id AND E.es_id=PD2.es_id AND
                     P.ped_id = PD1.ped_id AND D.ti_cod=T.ti_id AND PD2.pe_id=PD1.pe_id;""")
    tiendas = cur.fetchall()
    cur.execute(""" SELECT P.ped_id,P.ped_fentrega,CJ.cj_rif as rif,E.es_tipo FROM pedido P,clientejuridico CJ,estatus E,
                (SELECT P.ped_id,MAX(PD.pe_id) as pe_id from ped_est PD,pedido P WHERE P.ped_id = PD.ped_id
                GROUP BY P.ped_id) as PD1,ped_est PD2
	               WHERE P.cj_id =CJ.cj_id AND E.es_id=PD2.es_id AND P.ped_id = PD1.ped_id AND PD1.pe_id = PD2.pe_id
	               UNION
	               SELECT P.ped_id, P.ped_fentrega,CN.cn_rif,E.es_tipo FROM pedido P,clientenatural CN,estatus E,
                   (SELECT P.ped_id,MAX(PD.pe_id) as pe_id from ped_est PD,pedido P WHERE P.ped_id = PD.ped_id
                   GROUP BY P.ped_id) as PD1,ped_est PD2
	               WHERE P.cn_id =CN.cn_id AND E.es_id=PD2.es_id AND P.ped_id = PD1.ped_id AND PD1.pe_id = PD2.pe_id
	               ORDER BY ped_id;""")
    clientes = cur.fetchall()
    return render_template('pedidos.html',tiendas = tiendas,clientes=clientes)


@app.route("/ofertas/<int:dd_id>/<int:e_id>/registro",methods=['GET','POST'])
def create_oferta(dd_id,e_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE diariodulce'))
        permiso = cur.fetchone()
        if permiso:
            form = DiarioDulce()
            if form.validate_on_submit():
                try:
                    cur.execute("""INSERT INTO pro_diario (pd_descuento,dd_id,p_id)
                                    VALUES (%s,%s,%s);""",(form.descuento.data/100,dd_id,form.producto.data))
                except:
                    print("ERROR inserting into pro_diario")
                    db.retroceder()
                db.actualizar()
                flash('Su oferta se ha creado exitosamente','success')
                return redirect(url_for('ofertas',e_id=e_id))
            return render_template('createOferta.html',form=form,e_id=e_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/ofertas/update/<int:pd_id>/<int:e_id>",methods=['GET','POST'])
def update_oferta(pd_id,e_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE diariodulce'))
        permiso = cur.fetchone()
        if permiso:
            form = DescuentoForm()
            if form.validate_on_submit():
                try:
                    cur.execute("""UPDATE pro_diario SET pd_descuento = %s WHERE pd_id=%s;""",
                                (form.descuento.data/100,pd_id,))
                except:
                    print("ERROR updating into pro_diario")
                    db.retroceder()
                db.actualizar()
                return redirect(url_for('ofertas',e_id=e_id))
            return render_template('createOferta.html',form=form,pd_id=pd_id,e_id=e_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')


@app.route("/ofertas/delete/<int:pd_id>/<int:e_id>",methods=['GET','POST'])
def delete_oferta(pd_id,e_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE diariodulce'))
        permiso = cur.fetchone()
        if permiso:
            try:
                cur.execute("""DELETE FROM pro_diario WHERE pd_id=%s;""",(pd_id,))
            except:
                print("ERROR deleting into pro_diario")
                db.retroceder()
            db.actualizar()
            return redirect(url_for('ofertas',e_id=e_id))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/ofertas/<int:e_id>",methods=['GET','POST'])
def ofertas(e_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ diariodulce'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("SELECT * FROM diariodulce WHERE CURRENT_DATE between dd_femision and dd_ffinal;")
            diario = cur.fetchone()
            if diario:
                cur.execute("SELECT P.p_nombre,P.p_precio, PD.* from pro_diario PD,producto P where PD.dd_id = %s AND P.p_id=PD.p_id;",(diario['dd_id'],))
                productos = cur.fetchall()
                return render_template('ofertas.html',productos=productos,dd_id=diario['dd_id'],e_id=e_id)
            else:
                end_date = datetime.datetime.strptime(date.today().strftime("%d-%m-%Y"), "%d-%m-%Y") + timedelta(days=20)
                cur = db.cursor()
                try:
                    cur.execute("""INSERT INTO diariodulce (dd_ffinal,e_id)
                                    VALUES (%s,%s) RETURNING dd_id;""",(end_date.date(),e_id))
                except:
                    print("ERROR inserting into diariodulce")
                    db.retroceder()
                diario = cur.fetchone()[0]
                db.actualizar()
                return render_template('ofertas.html',dd_id=diario,e_id=e_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')


@app.route("/asistencia",methods=['GET','POST'])
def asistencia():
    form = AsistenciaForm()
    db = Database()
    cur = db.cursor_dict()
    if form.validate_on_submit():
        records = p.iget_records(file_name=form.excel.data.filename)
        for record in records:
            if record['CEDULA'] != '':
                cur.execute("SELECT e_id from empleado WHERE e_ci=%s;",(int(float(record['CEDULA'])),))
                id = cur.fetchone()
                if record['FECHA_HORA_SALIDA'] != '' and record['FECHA_HORA_ENTRADA'] != '':
                    try:
                        cur.execute("""INSERT INTO asistencia (as_fecha_entrada,as_fecha_salida,e_id) VALUES
                            (to_timestamp(%s, 'DD-MM-YYYY HH24:MI'),to_timestamp(%s, 'DD-MM-YYYY HH24:MI'),%s);""",
                            (record['FECHA_HORA_ENTRADA'],record['FECHA_HORA_SALIDA'],id['e_id'],))
                    except:
                        print("ERROR inserting into asistencia")
                        db.retroceder()
                    db.actualizar()
        return redirect(url_for('home'))

    return render_template('asistencia.html',form=form)

@app.route("/tiendas/registro",methods=['GET','POST'])
def create_tienda():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE tienda'))
        permiso = cur.fetchone()
        if permiso:
            form = TiendaForm()
            if form.validate_on_submit():
                cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                            E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                            P.l_nombre = %s AND P.fk_lugar = M.l_id;
                            """,(form.estados.data,form.municipios.data,form.parroquias.data,))
                direccion = cur.fetchone()
                if int(form.tipo.data) == 1:
                    tipo = 'Candy Shop'
                else:
                    tipo = 'Mini Candy Shop'
                try:
                    cur.execute("""INSERT INTO tienda (ti_nombre,ti_tipo,l_id)
                                VALUES (%s, %s,%s);""",
                                (form.nombre.data,tipo,direccion['l_id'],))
                except:
                    print("ERROR inserting into tienda")
                    db.retroceder()
                db.actualizar()
                flash('Su tienda se ha creado exitosamente','success')
                return redirect(url_for('tiendas'))
            return render_template('createTienda.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/tiendas/<int:ti_id>/delete",methods=['GET','POST'])
def delete_tienda(ti_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE tienda'))
        permiso = cur.fetchone()
        if permiso:
            try:
                cur.execute("DELETE FROM tienda WHERE ti_id = %s;",(ti_id,))
            except:
                print("ERROR deleting into tienda")
                db.retroceder()
            db.actualizar()
            return redirect(url_for('tiendas'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/tiendas/<int:ti_id>/update",methods=['GET','POST'])
def update_tienda(ti_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE tienda'))
        permiso = cur.fetchone()
        if permiso:
            form = UpdateTiendaForm()
            cur.execute("SELECT * FROM tienda WHERE ti_id =%s;",(ti_id,))
            tienda = cur.fetchone()
            if form.validate_on_submit():
                cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                            E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                            P.l_nombre = %s AND P.fk_lugar = M.l_id;
                            """,(form.estados.data,form.municipios.data,form.parroquias.data,))
                direccion = cur.fetchone()
                if direccion == None:
                    direccion = tienda
                if int(form.tipo.data) == 1:
                    tipo = 'Candy Shop'
                else:
                    tipo = 'Mini Candy Shop'

                try:
                    cur.execute("""UPDATE tienda SET ti_nombre=%s,ti_tipo=%s,l_id=%s WHERE ti_id=%s;""",
                                (form.nombre.data,tipo,direccion['l_id'],ti_id,))
                except:
                    print("ERROR updating into tienda")
                    db.retroceder()
                db.actualizar()
                flash('Su tienda se ha actualizado exitosamente','success')
                return redirect(url_for('tiendas'))
            elif request.method == 'GET':
                form.nombre.data = tienda['ti_nombre']
            return render_template('createTienda.html',form=form,ti_id = ti_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/tiendas",methods=['GET','POST'])
def tiendas():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ tienda'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("SELECT T.*,L.l_nombre AS dir FROM tienda T,lugar L WHERE L.l_id=T.l_id ORDER BY T.ti_id;")
            tiendas = cur.fetchall()
            db.cerrar()
            return render_template('tiendas.html',tiendas=tiendas)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/productos/<int:p_id>/update",methods=['GET','POST'])
def update_producto(p_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE producto'))
        permiso = cur.fetchone()
        if permiso:
            form = ProductoForm()
            cur.execute("SELECT * FROM producto WHERE p_id =%s;",(p_id,))
            producto = cur.fetchone()
            if form.validate_on_submit():
                if form.picture.data :
                    picture_file = save_picture(form.picture.data)
                    try:
                        cur.execute("""UPDATE producto SET p_nombre = %s,p_imagen=%s,p_desc=%s,p_precio=%s,tp_id =%s WHERE p_id =%s;""",
                        (form.nombre.data,picture_file,form.desc.data,form.precio.data,form.tp.data,p_id))
                    except:
                        print("ERROR updating into producto")
                        db.retroceder()
                    db.actualizar()
                else:
                    try:
                        cur.execute("""UPDATE producto SET p_nombre = %s,p_desc=%s,p_precio=%s,tp_id =%s WHERE p_id=%s;""",
                        (form.nombre.data,form.desc.data,form.precio.data,form.tp.data,p_id))
                    except:
                        print("ERROR updating into producto")
                        db.retroceder()
                    db.actualizar()
                flash('Su producto se ha actualizado exitosamente','success')
                return redirect(url_for('productos'))
            elif request.method == 'GET':
                form.nombre.data = producto['p_nombre']
                form.desc.data = producto['p_desc']
                form.precio.data = producto['p_precio']
            return render_template('createProducto.html',form=form,p_id = p_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/productos/<int:p_id>/delete",methods=['GET','POST'])
def delete_producto(p_id):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE producto'))
        permiso = cur.fetchone()
        if permiso:
            try:
                cur.execute("DELETE FROM producto WHERE p_id = %s;",(p_id,))
            except:
                print("ERROR deleting into producto")
                db.retroceder()
            db.actualizar()
            return redirect(url_for('productos'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/productos",methods=['GET','POST'])
def productos():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ producto'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("SELECT T.tp_nombre,P.* FROM producto P,tipo_producto T WHERE P.tp_id = T.tp_id;")
            productos = cur.fetchall()
            return render_template('productos.html',productos = productos)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/productos/registro",methods=['GET','POST'])
def create_producto():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE producto'))
        permiso = cur.fetchone()
        if permiso:
            form = ProductoForm()
            if form.validate_on_submit():
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    try:
                        cur.execute("""INSERT INTO producto (p_nombre,p_imagen,p_desc,p_precio,tp_id)
                                    VALUES (%s, %s,%s,%s,%s);""",
                                    (form.nombre.data,picture_file,form.desc.data,form.precio.data,form.tp.data))
                    except:
                        print("ERROR inserting into producto")
                        db.retroceder()
                    db.actualizar()
                    flash('Su producto se ha creado exitosamente','success')
                else:
                    flash('Su producto no se ha guardado porque no se suministro imagen','danger')
                return redirect(url_for('productos'))
            return render_template('createProducto.html',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/clientes",methods=['GET','POST'])
def clientes():
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'READ cliente'))
        permiso = cur.fetchone()
        if permiso:
            cur.execute("SELECT C.*,L.l_nombre AS dir FROM clientenatural C,lugar L WHERE L.l_id=C.l_id ORDER BY C.cn_id DESC;")
            cn = cur.fetchall()
            cur.execute("""SELECT C.*,fisica.l_nombre as fisica,fiscal.l_nombre as fiscal FROM clientejuridico C,jur_lug FL,jur_lug FA ,lugar as fiscal,lugar as fisica
                                WHERE C.cj_id = FL.cj_id  AND C.cj_id = FA.cj_id
                                AND FL.l_id=fiscal.l_id AND FL.jl_tipo='fiscal'  AND FA.l_id=fisica.l_id AND FA.jl_tipo='fisica'
        						ORDER BY C.cj_id DESC;""")
            cj = cur.fetchall()
            db.cerrar()
            return render_template('clientes.html',title = 'Clientes',cj = cj,cn = cn)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route('/municipio/<int:fk_lugar>',methods=['GET','POST'])
def municipio(fk_lugar):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT M.* from lugar M WHERE  M.fk_lugar = %s;",(fk_lugar,))
    municipios = cur.fetchall()
    db.cerrar()
    munArray = []
    for municipio in municipios:
        munArray.append(municipio)

    return jsonify({'municipios': munArray})

@app.route('/parroquia/<string:municipio>/<int:estado>',methods=['GET','POST'])
def parroquia(municipio,estado):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT distinct P.* from lugar M,lugar P,lugar E where M.l_nombre =%s AND P.fk_lugar = M.l_id AND M.fk_lugar = %s ;",(municipio,estado,))
    parroquias = cur.fetchall()
    db.cerrar()
    paqArray = []
    for parroquia in parroquias:
        paqArray.append(parroquia)

    return jsonify({'parroquias': paqArray})

@app.route("/clientes/<int:c_id>/<string:tipo>",methods=['GET','POST'])
def update_cliente(c_id,tipo):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'UPDATE cliente'))
        permiso = cur.fetchone()
        if permiso:
            db = Database()
            cur = db.cursor_dict()
            if tipo == 'cj':
                cur.execute("SELECT * FROM clientejuridico WHERE cj_id = %s",(c_id,))
                cliente = cur.fetchone()
                form = UpdateJForm()
                form.current_rif.data = cliente['cj_rif']
                form.current_email.data = cliente['cj_email']
                if form.validate_on_submit():
                    try:
                        cur.execute("""UPDATE clientejuridico SET cj_rif = %s,cj_email = %s,cj_capdis = %s,cj_demcom = %s,cj_razsoc=%s ,cj_pagweb = %s WHERE cj_id= %s;""",
                        (form.rif.data, form.email.data,form.capdis.data,form.demcom.data,form.razsoc.data,form.pagweb.data,c_id))
                    except:
                        print("ERROR updating into clientejuridico")
                        db.retroceder()
                    db.actualizar()

                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados1.data,form.municipios1.data,form.parroquias1.data,))
                    dirFiscal = cur.fetchone()
                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados2.data,form.municipios2.data,form.parroquias2.data,))
                    dirFisica = cur.fetchone()
                    if dirFisica != None:
                        try:
                            cur.execute("""UPDATE jur_lug SET l_id = %s WHERE cj_id = %s AND jl_tipo = 'fisica';""",
                            (dirFisica['l_id'],c_id,))
                        except:
                            print("ERROR updating into lugar_clientej fisica")
                            db.retroceder()

                    if dirFiscal != None:
                        try:
                            cur.execute("""UPDATE jur_lug SET l_id = %s WHERE cj_id = %s AND jl_tipo = 'fiscal';""",
                            (dirFiscal['l_id'],c_id,))
                        except:
                            print("ERROR updating into lugar_clientej fiscal")
                            db.retroceder()
                    db.actualizar()
                    flash('Tu cliente ha sido actualizada','success')
                    return redirect(url_for('clientes'))
                elif request.method == 'GET':
                    form.rif.data = cliente['cj_rif']
                    form.email.data = cliente['cj_email']
                    form.capdis.data = cliente['cj_capdis']
                    form.demcom.data = cliente['cj_demcom']
                    form.razsoc.data = cliente['cj_razsoc']
                    form.pagweb.data = cliente['cj_pagweb']
                return render_template('clienteJ.html',form = form,c_id = c_id)
            elif tipo == 'cn':

                cur.execute("SELECT * FROM clientenatural WHERE cn_id = %s",(c_id,))
                cliente = cur.fetchone()
                form = UpdateNForm()
                form.current_rif.data = cliente['cn_rif']
                form.current_email.data = cliente['cn_email']
                form.current_ci.data = cliente['cn_ci']
                if form.validate_on_submit():
                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados.data,form.municipios.data,form.parroquias.data,))
                    direccion = cur.fetchone()
                    if direccion == None:
                        direccion = cliente
                    try:
                        cur.execute("""UPDATE clientenatural SET cn_rif = %s,cn_email = %s,cn_nom1 = %s,cn_nom2 = %s,cn_ap1=%s, cn_ap2=%s,cn_ci = %s,l_id = %s WHERE cn_id= %s;""",
                        (form.rif.data, form.email.data,form.nom1.data,form.nom2.data,form.ap1.data,form.ap2.data,form.ci.data,direccion['l_id'],c_id))
                    except:
                        print("ERROR updating into clientenatural")
                        db.retroceder()
                    db.actualizar()
                    flash('Tu cliente ha sido actualizada','success')
                    return redirect(url_for('clientes'))
                elif request.method == 'GET':
                    form.rif.data = cliente['cn_rif']
                    form.email.data = cliente['cn_email']
                    form.nom1.data = cliente['cn_nom1']
                    form.nom2.data = cliente['cn_nom2']
                    form.ap1.data = cliente['cn_ap1']
                    form.ap2.data = cliente['cn_ap2']
                    form.ci.data = cliente['cn_ci']

                return render_template('clienteN.html',form = form,c_id = c_id)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/clientes/<int:c_id>/<string:tipo>/delete",methods=['GET','POST'])
def delete_cliente(c_id,tipo):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'DELETE cliente'))
        permiso = cur.fetchone()
        if permiso:
            db = Database()
            cur = db.cursor_dict()
            if tipo == 'cj':
                try:
                    cur.execute("DELETE FROM clientejuridico WHERE cj_id = %s;",(c_id,))
                except:
                    print("ERROR deleting clientejuridico")
                    db.retroceder()
                db.actualizar()
                db.cerrar()
                flash('Tu cliente ha sido eliminado','success')
                return redirect(url_for('clientes'))
            elif tipo == 'cn':
                print(c_id)
                try:
                    cur.execute("DELETE FROM clientenatural WHERE cn_id = %s;",(c_id,))
                except:
                    print("ERROR deleting clientenatural")
                    db.retroceder()
                db.actualizar()
                db.cerrar()
                flash('Tu cliente ha sido eliminado','success')
                return redirect(url_for('clientes'))
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@app.route("/clientes/<int:c_id>/<string:tipo>/carnet",methods=['GET','POST'])
def carnet(c_id,tipo):
    db = Database()
    cur = db.cursor_dict()
    if tipo == 'cj':
        cur.execute("""SELECT C.car_num,J.cj_demcom,J.cj_rif,ti_nombre FROM carnet C,clientejuridico J,tienda
                    WHERE J.ti_cod = ti_id AND J.cj_id=%s AND J.cj_id=C.cj_id;""",(c_id,))
        cliente = cur.fetchone()
        return render_template('carnet.html',cliente=cliente,tipo = 'cj')
    else:
        cur.execute("""SELECT C.car_num,N.cn_nom1,N.cn_ap1,N.cn_ci,ti_nombre FROM carnet C,clientenatural N,tienda
                    WHERE N.ti_cod = ti_id AND N.cn_id=%s AND N.cn_id=C.cn_id;""",(c_id,))
        cliente = cur.fetchone()
        return render_template('carnet.html',cliente=cliente,tipo = 'cn')

@app.route("/clientes/register/<string:tipo>",methods=['GET','POST'])  #Registro de tienda
def registro(tipo):
    if current_user.is_authenticated:
        db = Database()
        cur = db.cursor_dict()
        cur.execute(""" SELECT p.per_funcion from rol r, rol_per rp,permiso p where r.r_id = %s AND rp.r_id = r.r_id
                        AND p.per_id =rp.per_id AND p.per_funcion = %s;""",(current_user.r_id,'CREATE cliente'))
        permiso = cur.fetchone()
        if permiso:
            if tipo == 'cj':
                form = TiendaJForm()
                if form.validate_on_submit():
                    db = Database()
                    cur = db.cursor_dict()
                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados1.data,form.municipios1.data,form.parroquias1.data,))
                    dirFiscal = cur.fetchone()
                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados2.data,form.municipios2.data,form.parroquias2.data,))
                    dirFisica = cur.fetchone()
                    cur = db.cursor()
                    try:
                        cur.execute("""INSERT INTO clientejuridico (cj_rif, cj_email,cj_demcom,cj_razsoc,cj_capdis,cj_pagweb,ti_cod)
                        VALUES (%s, %s,%s,%s,%s,%s,%s) RETURNING cj_id;""",
                        (form.rif.data,form.email.data,form.demcom.data,form.razsoc.data,form.capdis.data,form.pagweb.data,form.tienda.data,))
                    except:
                        print("ERROR inserting into clientejuridico")
                        db.retroceder()
                    cj = cur.fetchone()[0]
                    db.actualizar()
                    try:
                        cur.execute("""INSERT INTO jur_lug (l_id,cj_id,jl_tipo)
                        VALUES (%s, %s,%s);""",
                        (dirFiscal['l_id'],cj,'fiscal',))
                    except:
                        print("ERROR inserting into lugar_clientej fiscal")
                        db.retroceder()
                    #dirFisica
                    try:
                        cur.execute("""INSERT INTO jur_lug (l_id,cj_id,jl_tipo)
                        VALUES (%s, %s,%s);""",
                        (dirFisica['l_id'],cj,'fisica',))
                    except:
                        print("ERROR inserting into lugar_clientej fisica")
                        db.retroceder()
                    db.actualizar()
                    if form.carnet.data == True:
                        cur = db.cursor_dict()
                        cur.execute("SELECT C.car_num,C.d_id from carnet C, departamento D where D.ti_cod = %s AND C.d_id = D.d_id ORDER BY C.car_num DESC LIMIT 1;",(form.tienda.data,))
                        carnet_num = cur.fetchone()
                        num = carnet_num['car_num'][3:]
                        if int(form.tienda.data) < 10:
                            carnet = "0{}-{}"
                            if int(num)+1 < 10:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0000000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()

                            elif int (num)+1 <100:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"000000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"00000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 100000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"00"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                        else:
                            carnet = "{}-{}"
                            if int(num)+1 < 10:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0000000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int (num)+1 <100:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"000000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"00000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 100000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"000"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"00"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cj_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0"+str(int(num)+1)),cj,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                        db.actualizar()
                        return redirect(url_for('carnet',c_id = cj,tipo = 'cj'))

                    flash('Su cuenta se ha creado exitosamente','success')
                    return redirect(url_for('clientes'))
                return render_template('TiendaJ.html',title='Register',form=form)
            elif tipo == 'cn':
                form = TiendaNForm()
                if form.validate_on_submit():
                    db = Database()
                    cur = db.cursor_dict()
                    cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                                E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                                P.l_nombre = %s AND P.fk_lugar = M.l_id;
                                """,(form.estados.data,form.municipios.data,form.parroquias.data,))
                    direccion = cur.fetchone()
                    cur = db.cursor()
                    try:
                        cur.execute("""INSERT INTO clientenatural (cn_rif, cn_email,cn_nom1,cn_nom2,cn_ap1,cn_ap2,l_id,cn_ci,ti_cod)
                        VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s) RETURNING cn_id;""",
                        (form.rif.data,form.email.data,form.nom1.data,form.nom2.data,form.ap1.data,form.ap2.data,direccion['l_id'],form.ci.data,form.tienda.data))
                    except:
                        print("ERROR inserting into clientenatural")
                        db.retroceder()

                    cn = cur.fetchone()[0]
                    db.actualizar()
                    if form.carnet.data == True:
                        cur = db.cursor_dict()
                        cur.execute("SELECT C.car_num,C.d_id from carnet C, departamento D where D.ti_cod = %s AND C.d_id = D.d_id ORDER BY C.car_num DESC LIMIT 1;",(form.tienda.data,))
                        carnet_num = cur.fetchone()
                        num = carnet_num['car_num'][3:]
                        if int(form.tienda.data) < 10:
                            carnet = "0{}-{}"
                            if int(num)+1 < 10:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0000000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()

                            elif int (num)+1 <100:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"000000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"00000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 100000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"00"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s);""",
                                    (carnet.format(form.tienda.data,"0"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                        else:
                            carnet = "{}-{}"
                            if int(num)+1 < 10:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0000000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int (num)+1 <100:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"000000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"00000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 100000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"000"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 1000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"00"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                            elif int(num)+1 < 10000000:
                                try:
                                    cur.execute("""INSERT INTO carnet (car_num,cn_id,d_id) VALUES (%s,%s,%s)""",
                                    (carnet.format(form.tienda.data,"0"+str(int(num)+1)),cn,carnet_num['d_id'],))
                                except:
                                    print("ERROR inserting into carnet")
                                    db.retroceder()
                        db.actualizar()
                        return redirect(url_for('carnet',c_id = cn,tipo = 'cn'))

                    flash('Su cuenta se ha creado exitosamente','success')
                    return redirect(url_for('clientes'))
                return render_template('TiendaN.html',title='Register',form=form)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')         #Registro tienda fisica

@app.route("/register")  #Registro online
def register():
   return render_template('register.html')  #Registro online

@app.route("/metodo")
@login_required
def metodo():
   return render_template('metodo.html')

@app.route("/credito/<string:tipo>/<int:c_id>",methods=['GET','POST'])
@login_required
def credito(tipo,c_id):
    form = TarjetaCredito()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        if tipo == 'cj':
            try:
                cur.execute("""INSERT INTO tarjetacredito (tc_num,tc_fvenc,tc_codseg,tc_ncompl,tc_marca,cj_id)
                            VALUES (%s, %s,%s,%s,%s);""",
                (form.numero.data,form.fvenc.data,form.codigo.data,form.nombre.data,form.marca.data,c_id,))
            except:
                print("ERROR inserting into tarjetacredito cj")
                db.retroceder()
            db.actualizar()
        elif tipo == 'cn':
            try:
                cur.execute("""INSERT INTO tarjetacredito (tc_num,tc_fvenc,tc_codseg,tc_ncompl,tc_marca,cn_id)
                            VALUES (%s, %s,%s,%s,%s);""",
                (form.numero.data,form.fvenc.data,form.codigo.data,form.nombre.data,form.marca.data,c_id,))
            except:
                print("ERROR inserting into tarjetacredito cn")
                db.retroceder()
            db.actualizar()
        flash('Su tarjeta de credito se ha guardado exitosamente','success')
        return redirect(url_for('cliente_home'))

    return render_template('credito.html',title='Tarjeta Credito',form=form)

@app.route("/debito/<string:tipo>/<int:c_id>",methods=['GET','POST'])
@login_required
def debito(tipo,c_id):
    form = TarjetaDebito()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        if int(form.banco.data) == 1:
            banco = 'Mercantil'
        elif int(form.banco.data) == 2:
            banco = 'BOD'
        elif int(form.banco.data) == 3:
            banco = 'Banesco'
        elif int(form.banco.data) == 4:
            banco = 'Banco Plaza'
        elif int(form.banco.data) == 5:
            banco = 'Provincial'

        if tipo == 'cj':
            try:
                cur.execute("""INSERT INTO tarjetadebito (td_num,td_banco,td_fvenc,td_ncompl,cj_id)
                            VALUES (%s, %s,%s,%s,%s);""",
                (form.numero.data,banco,form.fvenc.data,form.nombre.data,c_id,))
            except:
                print("ERROR inserting into tarjetadebito cj")
                db.retroceder()
            db.actualizar()
        elif tipo == 'cn':
            try:
                cur.execute("""INSERT INTO tarjetadebito (td_num,td_banco,td_fvenc,td_ncompl,cn_id)
                        VALUES (%s, %s,%s,%s,%s);""",
                        (form.numero.data,banco,form.fvenc.data,form.nombre.data,c_id,))
            except:
                print("ERROR inserting into tarjetadebito cn")
                db.retroceder()
            db.actualizar()
            flash('Su tarjeta de debito se ha guardado exitosamente','success')
        return redirect(url_for('cliente_home'))
    return render_template('debito.html',title='Tarjeta Debito',form=form)

@app.route("/cheque/<string:tipo>/<int:c_id>",methods=['GET','POST'])
@login_required
def cheque(tipo,c_id):
    form = ChequeForm()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        if tipo == 'cj':
            try:
                cur.execute("""INSERT INTO cheque (ch_num,ch_faplicar,ch_ncompl,cj_id)
                            VALUES (%s, %s,%s,%s);""",
                (form.numero.data,form.faplicar.data,form.nombre.data,c_id,))
            except:
                print("ERROR inserting into cheque cj")
                db.retroceder()
            db.actualizar()
        elif tipo == 'cn':
            try:
                cur.execute("""INSERT INTO cheque (ch_num,ch_faplicar,ch_ncompl,cn_id)
                            VALUES (%s, %s,%s,%s);""",
                (form.numero.data,form.faplicar.data,form.nombre.data,c_id,))
            except:
                print("ERROR inserting into cheque cn")
                db.retroceder()
            db.actualizar()
        flash('Su cheque se ha guardado exitosamente','success')
        return redirect(url_for('cliente_home'))

    return render_template('cheque.html',title='Cheque',form=form)

@app.route("/new_tlf/<string:tipo>/<int:c_id>",methods=['GET','POST'])
@login_required
def new_tlf(tipo,c_id):
    form = TlfForm()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        if tipo == 'cj':
            try:
                cur.execute("""INSERT INTO telefono (t_num,cj_id)
                            VALUES (%s, %s);""",
                (form.numero.data,c_id,))
            except:
                print("ERROR inserting into telefono")
                db.retroceder()
            db.actualizar()
        else:
            try:
                cur.execute("""INSERT INTO telefono (t_num,cn_id)
                            VALUES (%s, %s);""",
                (form.numero.data,c_id,))
            except:
                print("ERROR inserting into telefono")
                db.retroceder()
            db.actualizar()
        flash('Su telefono se ha guardado exitosamente','success')
        return redirect(url_for('home'))

    return render_template('new_tlf.html',title='Nuevo Telefono',form=form)

@app.route("/new_persona/<int:c_id>",methods=['GET','POST'])
@login_required
def new_persona(c_id):
    form = PersonaContactoForm()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        try:
            cur.execute("""INSERT INTO personadecontacto (pc_nombre,pc_apellido,cj_id)
            VALUES (%s, %s,%s);""",
            (form.nombre.data,form.apellido.data,c_id,))
        except:
            print("ERROR inserting into telefono")
            db.retroceder()
        db.actualizar()
        flash('Su persona de contacto se ha guardado exitosamente','success')
        return redirect(url_for('home'))

    return render_template('new_persona.html',title='Nueva Persona',form=form)

@app.route("/registerJ",methods=['GET','POST'])
def registerJ():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationJForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db = Database()
        cur = db.cursor_dict()
        cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                    E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                    P.l_nombre = %s AND P.fk_lugar = M.l_id;
                    """,(form.estados1.data,form.municipios1.data,form.parroquias1.data,))
        dirFiscal = cur.fetchone()
        cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                    E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                    P.l_nombre = %s AND P.fk_lugar = M.l_id;
                    """,(form.estados2.data,form.municipios2.data,form.parroquias2.data,))
        dirFisica = cur.fetchone()
        print(dirFisica['l_id'])
        try:
            cur.execute("""INSERT INTO clientejuridico (cj_rif, cj_email,cj_demcom,cj_razsoc,cj_capdis,cj_pagweb)
            VALUES (%s, %s,%s,%s,%s,%s) RETURNING cj_id;""",
            (form.rif.data,form.email.data,form.demcom.data,form.razsoc.data,form.capdis.data,form.pagweb.data,))
        except:
            print("ERROR inserting into clientejuridico")
            db.retroceder()
        cj = cur.fetchone()[0]
        db.actualizar()
        #cur.execute("SELECT cj_id FROM clientejuridico WHERE cj_email = %s;",(form.email.data,))
        #cj = cur.fetchone()
        #dirFiscal
        try:
            cur.execute("""INSERT INTO jur_lug (l_id,cj_id,jl_tipo)
            VALUES (%s, %s,%s);""",
            (dirFiscal['l_id'],cj,'fiscal',))
        except:
            print("ERROR inserting into lugar_clientej fiscal")
            db.retroceder()
        #dirFisica
        try:
            cur.execute("""INSERT INTO jur_lug (l_id,cj_id,jl_tipo)
            VALUES (%s, %s,%s);""",
            (dirFisica['l_id'],cj,'fisica',))
        except:
            print("ERROR inserting into lugar_clientej fisica")
            db.retroceder()
        try:
            cur.execute("""INSERT INTO usuario (u_username, u_password,cj_id)
            VALUES (%s, %s,%s);""",
            (form.username.data,form.password.data,cj))
        except:
            print("ERROR inserting into user")
            db.retroceder()
        db.actualizar()

        flash('Su cuenta se ha creado exitosamente','success')
        return redirect(url_for('login'))
    return render_template('registerJ.html',title='Register',form=form)

@app.route("/registerN",methods=['GET','POST'])
def registerN():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationNForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db = Database()
        cur = db.cursor_dict()
        cur.execute("""SELECT P.l_id from lugar E, lugar M , lugar P where
                    E.l_id = %s AND E.l_tipo = 'E' AND M.l_nombre = %s AND M.fk_lugar= E.l_id AND
                    P.l_nombre = %s AND P.fk_lugar = M.l_id;
                    """,(form.estados.data,form.municipios.data,form.parroquias.data,))
        direccion = cur.fetchone()
        cur = db.cursor()
        try:
            cur.execute("""INSERT INTO clientenatural (cn_rif, cn_email,cn_nom1,cn_nom2,cn_ap1,cn_ap2,l_id,cn_ci)
            VALUES (%s, %s,%s,%s,%s,%s,%s,%s) RETURNING cn_id;""",
            (form.rif.data,form.email.data,form.nom1.data,form.nom2.data,form.ap1.data,form.ap2.data,direccion['l_id'],form.ci.data))
        except:
            print("ERROR inserting into clientenatural")
            db.retroceder()

        cn = cur.fetchone()[0]
        db.actualizar()
        try:
            cur.execute("""INSERT INTO usuario (u_username, u_password,cn_id)
            VALUES (%s, %s,%s);""",
            (form.username.data,form.password.data,cn))
        except:
            print("ERROR inserting into user")
            db.retroceder()
        db.actualizar()

        flash('Su cuenta se ha creado exitosamente','success')
        return redirect(url_for('login'))
    return render_template('registerN.html',title='Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        db = Database()
        cur = db.cursor_dict()
        cur.execute("SELECT * from usuario WHERE u_username = %s;",(form.username.data,))
        user_type = cur.fetchone()
        if user_type:
            user = User(user_type)
            if user and user.u_password == form.password.data:
                login_user(user,remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(url_for('home'))
            else:
                flash('Contraseña Incorrecta','danger')
        else:
            flash('Usuario no encontrado','danger')
    return render_template('login.html',title='Login',form=form)

@app.route('/nombre_tienda',methods=['GET','POST'])
def nombre_tienda():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT ti_nombre, ti_tipo, l_nombre, ti_id from tienda, lugar WHERE tienda.l_id=lugar.l_id")
    nombre_tiendas = cur.fetchall()
    db.cerrar()
    nomArray = []
    for nombre in nombre_tiendas:
        nomArray.append(nombre)

    return jsonify({'nombre_tiendas': nomArray})


@app.route("/cliente_home",methods=['GET','POST'])
def cliente_home():
    return render_template('cliente_home.html')


@app.route("/inventario/<int:ti_id>/<string:nombret>", methods=['GET', 'POST'])
def inventario(ti_id, nombret):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT p_nombre,p_precio,i_cant, p_imagen, p.p_id, i.i_id from producto as p, inventario as i where i.ti_id=%s and p.p_id=i.p_id;""",(ti_id,))
    productos = cur.fetchall()
    db.cerrar()
    proArray = []
    for producto in productos:
        proArray.append(producto)

    print(proArray)
    return render_template('inventario.html', nombret=nombret, productos=productos)

@app.route("/presupuesto/<int:u_id>/<int:pid>/<int:iid>", methods=['GET', 'POST'])
def presupuesto(u_id, pid, iid):
    cantidadp = request.form['cantidadp']

    db = Database()
    cur = db.cursor_dict()

    cur.execute("""INSERT INTO presupuesto (pre_femision) VALUES (%s) RETURNING pre_id;""",(time.strftime("%d-%m-%Y"),))
    preid = cur.fetchone()
    cur.execute("""INSERT INTO compravirtual (cv_cant, pre_id, u_id, p_id, i_id) VALUES (%s, %s, %s, %s, %s);""",(cantidadp,preid[0],u_id,pid,iid,))
    cur.execute("UPDATE inventario SET i_cant=i_cant - %s WHERE i_id=%s RETURNING i_cant;",(cantidadp,iid,))
    cantact = cur.fetchone()
    if cantact[0] < 100:
        cur.execute("INSERT INTO orden (o_fecha,i_id) VALUES (%s,%s) RETURNING o_id;",(time.strftime("%d-%m-%Y"),iid,))
        miosid = cur.fetchone()
        cur.execute("INSERT INTO reposicion (o_id, i_id) VALUES (%s,%s);",(miosid[0],iid,))

    cur.execute("SELECT i_id from reposicion where i_id=%s;",(iid,))
    diezk = cur.fetchone()
    print(diezk)
    if diezk!=None:
        cur.execute("UPDATE inventario SET i_cant=i_cant + 10000 WHERE i_id=%s;",(iid,))


    db.actualizar()
    print(preid[0])
    return redirect(url_for('cliente_home'))

@app.route("/compras/<int:u_id>", methods=['GET', 'POST'])
def compras(u_id):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("""SELECT distinct p.p_nombre, cv.cv_cant ,cv.cv_cant * p.p_precio FROM producto p, compravirtual cv, presupuesto pr WHERE cv.u_id=%s and cv.p_id=p.p_id and pr.pre_id is not null""", (u_id,))
    comprasv = cur.fetchall()
    cur.execute("""SELECT  SUM(cv.cv_cant * p.p_precio) FROM producto p, compravirtual cv, presupuesto pr WHERE cv.u_id=%s and cv.p_id=p.p_id and pr.pre_id=cv.pre_id""", (u_id,))
    total = cur.fetchone()
    db.cerrar()

    return render_template('compras.html', comprasv=comprasv, total=total)


@app.route("/proust/<int:cant>/<string:tipo>/<int:car_id>/<string:tipop>/<int:c_id>/<int:u_id>/<string:op>", methods=['GET', 'POST'])
def proust(cant,tipo,car_id,tipop,c_id,u_id,op):
    if tipo=='r':
        pusar = int(request.form['cantpu'])
        if pusar > cant:
            print("error")
            return redirect(url_for('cliente_home'))
        else:
            return redirect(url_for('pagando',tipo=tipop,c_id=c_id,u_id=u_id,op='s',pusar=pusar))
    return render_template('proust.html', cant=cant,tipo=tipo,car_id=car_id,tipop=tipop,c_id=c_id,u_id=u_id,op=op)


@app.route("/pagando/<string:tipo>/<int:c_id>/<int:u_id>/<string:op>/<int:pusar>", methods=['GET','POST'])
def pagando(tipo, c_id, u_id,op,pusar):
    db = Database()
    cur = db.cursor_dict()
    print(u_id)
    cur.execute("SELECT cv.cv_id, cv.cv_cant * p.p_precio from compravirtual cv, presupuesto pr, producto p where cv.pre_id=pr.pre_id and cv.u_id=%s and p.p_id=cv.p_id;",(u_id,))
    pagospen = cur.fetchall()
    print(pagospen)
    if tipo=='cj':
        cur.execute("SELECT tc_id from tarjetacredito where cj_id=%s;", (c_id,))
        tarjeta=cur.fetchone()
        cur.execute("SELECT car_id FROM carnet WHERE cj_id=%s;",(c_id,))
        carnet = cur.fetchone()
        if carnet[0]!=None and op=='n':
            cur.execute("SELECT COUNT(*) FROM punto WHERE car_id=%s;",(carnet[0],))
            puntos = cur.fetchone()
            if puntos[0]!=None:
                return redirect(url_for('proust', cant=puntos[0], tipo='n', car_id=carnet[0], tipop=tipo, c_id=c_id,u_id=u_id,op=op))

        if op=='s':
            cur.execute("SELECT COUNT(*) FROM punto WHERE car_id=%s;", (carnet[0],))
            puntos = cur.fetchone()
            cur.execute("SELECT pu.pu_id, h.h_precio FROM punto pu, historial h WHERE pu.car_id=%s and h.h_id=pu.h_id;",(carnet[0],))
            epicuro = cur.fetchall()
            preciopunto= 0
            i=0
            for hedonista in epicuro:
                preciopunto += hedonista[1]
                i+=1
                if i >= puntos[0]:
                    break

            if tarjeta:
                trudat = False
                for pago in pagospen:
                    if trudat == False:
                        cur.execute("INSERT into pagovirtual (pv_fpago, cv_id, tc_id, pv_monto) values (%s, %s, %s, %s - %s) RETURNING pv_id;",(time.strftime('%d-%m-%Y'),pago['cv_id'],tarjeta['tc_id'],pago[1],preciopunto,))
                        pvid = cur.fetchone()
                        cur.execute("INSERT INTO factura (pv_id,f_femision) VALUES (%s,%s);",
                                    (pvid[0], time.strftime("%d-%m-%Y"),))
                        trudat = True
                    else:
                        preciopunto = 0
                        trudat=False

                j=0
                for gorgias in epicuro:
                   cur.execute("DELETE FROM punto WHERE pu_id=%s", (gorgias[0],))
                   j+=1
                   if j>=puntos[0]:
                       break

                db.actualizar()
                flash('Su compra ha sido exitosa', 'success')
                return redirect(url_for('cliente_home'))
            else:
                return redirect(url_for('credito', tipo=tipo, c_id=c_id))

        if op=='p':
            if tarjeta:
                for pago in pagospen:
                    cur.execute("INSERT into pagovirtual (pv_fpago, cv_id, tc_id, pv_monto) values (%s, %s, %s, %s) RETURNING pv_id;",(time.strftime('%d-%m-%Y'),pago['cv_id'],tarjeta['tc_id'],pago[1],))
                    pvid = cur.fetchone()
                    cur.execute("INSERT INTO factura (pv_id,f_femision) VALUES (%s,%s);",(pvid[0],time.strftime("%d-%m-%Y"),))
                db.actualizar()
                flash('Su compra ha sido exitosa', 'success')
                return redirect(url_for('cliente_home'))
            else:
                return redirect(url_for('credito', tipo=tipo, c_id=c_id))

    else:
        cur.execute("SELECT tc_id from tarjetacredito where cn_id=%s;", (c_id,))
        tarjeta=cur.fetchone()
        cur.execute("SELECT car_id FROM carnet WHERE cn_id=%s;", (c_id,))
        carnet = cur.fetchone()
        if carnet[0] != None and op == 'n':
            cur.execute("SELECT COUNT(*) FROM punto WHERE car_id=%s;", (carnet[0],))
            puntos = cur.fetchone()
            print(puntos)
            if puntos[0] != None:
                return redirect(
                    url_for('proust', cant=puntos[0], tipo='n', car_id=carnet[0], tipop=tipo, c_id=c_id, u_id=u_id,
                            op=op))

        if op == 's':
            cur.execute("SELECT COUNT(*) FROM punto WHERE car_id=%s;", (carnet[0],))
            puntos = cur.fetchone()
            cur.execute("SELECT pu.pu_id, h.h_precio FROM punto pu, historial h WHERE pu.car_id=%s and h.h_id=pu.h_id;",(carnet[0],))
            epicuro = cur.fetchall()
            preciopunto = 0
            i = 0
            for hedonista in epicuro:
                preciopunto += hedonista[1]
                i += 1
                if i >= puntos[0]:
                    break

            if tarjeta:
                trudat = False
                for pago in pagospen:
                    if trudat == False:
                        cur.execute(
                            "INSERT into pagovirtual (pv_fpago, cv_id, tc_id, pv_monto) values (%s, %s, %s, %s - %s) RETURNING pv_id;",
                            (time.strftime('%d-%m-%Y'), pago['cv_id'], tarjeta['tc_id'], pago[1], preciopunto,))
                        pvid = cur.fetchone()
                        cur.execute("INSERT INTO factura (pv_id,f_femision) VALUES (%s,%s);",
                                    (pvid[0], time.strftime("%d-%m-%Y"),))
                        trudat = True
                    else:
                        preciopunto = 0
                        trudat = False

                j = 0
                for gorgias in epicuro:
                    cur.execute("DELETE FROM punto WHERE pu_id=%s", (gorgias[0],))
                    j += 1
                    if j >= puntos[0]:
                        break

                db.actualizar()
                flash('Su compra ha sido exitosa', 'success')
                return redirect(url_for('cliente_home'))
            else:
                return redirect(url_for('credito', tipo=tipo, c_id=c_id))

        if op=='p':
            if tarjeta:
                for pago in pagospen:
                    cur.execute("INSERT into pagovirtual (pv_fpago, cv_id, tc_id, pv_monto) values (%s, %s, %s, %s) RETURNING pv_id;",(time.strftime('%d-%m-%Y'),pago['cv_id'],tarjeta['tc_id'],pago[1]))
                    pvid = cur.fetchone()
                    cur.execute("INSERT INTO factura (pv_id,f_femision) VALUES (%s,%s);",(pvid[0], time.strftime("%d-%m-%Y"),))
                db.actualizar()
                flash('Su compra ha sido exitosa', 'success')
                return redirect(url_for('cliente_home'))
            else:
                return redirect(url_for('credito', tipo=tipo, c_id=c_id))


@app.route("/zaratustra/<int:i_id>/<int:precio>", methods=['GET', 'POST'])
def zaratustra(i_id,precio):
    cantidadp = request.form['cantidadp']
    return render_template('zaratustra.html', i_id=i_id, cantidadp=cantidadp, precio=precio)


@app.route("/datos_compra/<int:i_id>/<int:cantidadp>/<int:precio>", methods=['GET', 'POST'])
def datos_compra(i_id, cantidadp,precio):
    return render_template('datos_compra.html', i_id=i_id, cantidadp=cantidadp,precio=precio)


@app.route("/elegir/<int:cf_id>/<int:precio>/<string:tipo>/<int:cid>/<string:op>/<int:car_id>", methods=['GET','POST'])
def elegir(cf_id,precio,tipo,cid,op,car_id):
    medios=0
    if op=='tc':
        db = Database()
        cur = db.cursor_dict()
        if tipo=='cj':
            cur.execute("SELECT tc_num,tc_id FROM tarjetacredito WHERE cj_id=%s",(cid,))
            medios = cur.fetchall()
            db.cerrar()
        if tipo=='cn':
            cur.execute("SELECT tc_num,tc_id FROM tarjetacredito WHERE cn_id=%s", (cid,))
            medios = cur.fetchall()
            db.cerrar()
    elif op=='td':
        db = Database()
        cur = db.cursor_dict()
        if tipo == 'cj':
            cur.execute("SELECT td_num,td_banco,td_id FROM tarjetadebito WHERE cj_id=%s", (cid,))
            medios = cur.fetchall()
            db.cerrar()
        if tipo == 'cn':
            cur.execute("SELECT td_num, td_banco, td_id FROM tarjetadebito WHERE cn_id=%s", (cid,))
            medios = cur.fetchall()
            db.cerrar()
    elif op=='ch':
        db = Database()
        cur = db.cursor_dict()
        if tipo == 'cj':
            cur.execute("SELECT ch_num, ch_id FROM cheque WHERE cj_id=%s", (cid,))
            medios = cur.fetchall()
            db.cerrar()
        if tipo == 'cn':
            cur.execute("SELECT ch_num, ch_id FROM cheque WHERE cn_id=%s", (cid,))
            medios = cur.fetchall()
            db.cerrar()

    return render_template('elegir.html', cf_id=cf_id, precio=precio, tipo=tipo, cid=cid, op=op,medios=medios, car_id=car_id)


@app.route("/comprafisica/<int:i_id>/<string:tipo>/<int:cantidadp>/<int:precio>", methods=['GET', 'POST'])
def comprafisica(i_id,tipo, cantidadp, precio):
    cfid=0
    if tipo=='s':
        db = Database()
        cur = db.cursor_dict()
        nombrec=request.form['nombrec']
        cur.execute("SELECT cn_id FROM usuario WHERE u_username=%s;", (nombrec,))
        cnid = cur.fetchone()
        cur.execute("SELECT cj_id FROM usuario WHERE u_username=%s;", (nombrec,))
        cjid = cur.fetchone()
        if cnid[0]==None and cjid[0]==None:
            print("error")
        elif cnid[0]==None and cjid[0]!=None:
            try:
                cur.execute("INSERT INTO comprafisica (cf_cant, cj_id, i_id) VALUES (%s,%s,%s) RETURNING cf_id;",(cantidadp,cjid[0],i_id,))
                cfid = cur.fetchone()
            except:
                db.retroceder()

            db.actualizar()

            cur.execute("SELECT car_id FROM carnet WHERE cj_id=%s;",(cjid[0],))
            carnet = cur.fetchone()
            if carnet[0]!=None:
                db.cerrar()
                return redirect(url_for('elegir', cf_id=cfid[0], precio=precio * cantidadp, tipo='cj', cid=cjid[0], op='n', car_id=carnet[0]))

            db.cerrar()
            return redirect(url_for('elegir',cf_id=cfid[0],precio=precio*cantidadp,tipo='cj',cid=cjid[0],op='n',car_id=0))

        elif cnid[0]!=None and cjid[0]==None:
            try:
                cur.execute("INSERT INTO comprafisica (cf_cant, cn_id, i_id) VALUES (%s,%s,%s) RETURNING cf_id;",(cantidadp, cnid[0], i_id,))
                cfid = cur.fetchone()
            except:
                db.retroceder()

            db.actualizar()

            cur.execute("SELECT car_id FROM carnet WHERE cn_id=%s;", (cnid[0],))
            carnet = cur.fetchone()
            if carnet[0]!=None:
                db.cerrar()
                return redirect(url_for('elegir', cf_id=cfid[0], precio=precio * cantidadp, tipo='cn', cid=cnid[0], op='n', car_id=carnet[0]))


            db.cerrar()
            return redirect(url_for('elegir', cf_id=cfid[0], precio=precio*cantidadp, tipo='cn', cid=cnid[0],op='n', car_id=0))



    else:
        db = Database()
        cur = db.cursor_dict()
        try:
            cur.execute("INSERT INTO comprafisica(cf_cant, i_id) VALUES (%s, %s) RETURNING cf_id;",(cantidadp,i_id,))
            cfid = cur.fetchone()
        except:
            db.retroceder()


        db.actualizar()

        return redirect(url_for('pagandof',cf_id=cfid[0], op="n", mid=0, precio=precio*cantidadp, car_id=0))

@app.route("/pagandof/<int:cf_id>/<string:op>/<int:mid>/<int:precio>/<int:car_id>", methods=['GET', 'POST'])
def pagandof(cf_id,op,mid,precio,car_id):
    db = Database()
    cur = db.cursor_dict()
    if op=='n':

        cur.execute("INSERT INTO pagofisico (pf_monto,cf_id) VALUES (%s,%s);",(precio,cf_id))
        db.actualizar()

    elif op=='tc':
        cur.execute("INSERT INTO pagofisico (pf_monto,cf_id,tc_id) VALUES (%s,%s,%s) RETURNING pf_id;", (precio, cf_id,mid))
        pfid = cur.fetchone()
        db.actualizar()
        if car_id!=0:
            cur.execute("SELECT MAX(h_id) from historial;")
            h_id=cur.fetchone()
            cur.execute("INSERT INTO punto (pf_id,car_id,h_id) VALUES (%s,%s,%s);",(pfid[0],car_id,h_id[0]))
            db.actualizar()
    elif op=='td':
        cur.execute("INSERT INTO pagofisico (pf_monto,cf_id,td_id) VALUES (%s,%s,%s);", (precio, cf_id,mid))
        db.actualizar()
        if car_id!=0:
            cur.execute("SELECT MAX(h_id) from historial;")
            h_id=cur.fetchone()
            cur.execute("INSERT INTO punto (pf_id,car_id,h_id) VALUES (%s,%s,%s);",(pfid[0],car_id,h_id[0]))
            db.actualizar()
    elif op=='ch':
        cur.execute("INSERT INTO pagofisico (pf_monto,cf_id,ch_id) VALUES (%s,%s,%s);", (precio, cf_id,mid))
        db.actualizar()
        if car_id!=0:
            cur.execute("SELECT MAX(h_id) from historial;")
            h_id=cur.fetchone()
            cur.execute("INSERT INTO punto (pf_id,car_id,h_id) VALUES (%s,%s,%s);",(pfid[0],car_id,h_id[0]))
            db.actualizar()

    return redirect(url_for('cliente_home'))

@app.route("/caja/<string:tipo>/<int:c_id>/<int:u_id>", methods=['GET','POST'])
def caja(tipo, c_id, u_id):
    db = Database()
    cur = db.cursor_dict()
    print(u_id)
    cur.execute("SELECT cv.cv_id from compravirtual cv, presupuesto pr where cv.pre_id=pr.pre_id and cv.u_id=%s;",(u_id,))
    pagospen = cur.fetchall()
    for pago in pagospen:
        cur.execute("INSERT into pagovirtual (pv_fpago, cv_id, tc_id) values (%s, %s, %s);",(time.strftime('%d-%m-%Y'),pago['cv_id'],tarjeta['tc_id'],))
        print(pago['cv_id'])
    db.actualizar()
    flash('Su compra ha sido exitosa', 'success')
    return redirect(url_for('cliente_home'))


@app.route("/factura/<int:u_id>", methods=['GET','POST'])
def factura(u_id):
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT p.p_nombre,cv.cv_cant, pv.pv_monto, f.f_femision FROM producto p,compravirtual cv, pagovirtual pv, factura f WHERE cv.u_id=%s and cv.cv_id=pv.cv_id and pv.pv_id=f.pv_id and p.p_id=cv.p_id;",(u_id,))
    fac = cur.fetchall()
    return render_template('factura.html', fac=fac)



@app.route("/masut", methods=['GET','POST'])
def masut():
    db = Database()
    cur = db.cursor_dict()
    cur.execute("SELECT COUNT(*) FROM pagofisico WHERE tc_id is not null;")
    tc = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM pagofisico WHERE td_id is not null;")
    td = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM pagofisico WHERE ch_id is not null;")
    ch = cur.fetchone()
    if tc[0] > td[0] and tc[0] > ch[0]:
        metodo = 'Tarjeta de crédito'
    elif td[0] > tc[0] and td[0] > ch[0]:
        metodo = 'Tarjeta de débito'
    elif ch[0] > tc[0] and ch[0] > td[0]:
        metodo = 'Cheque'
    else:
        metodo = 'Otro'
    return render_template('masut.html', metodo=metodo)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
