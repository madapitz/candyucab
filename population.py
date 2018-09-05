from faker import Faker
import random
from dateGenerator import randomDate,strTimeProp
fake = Faker('es_ES')

myfile = open("clientes.txt","a")
myfile.write("INSERT INTO clientenatural (cn_rif, cn_email,cn_nom1,cn_nom2,cn_ap1,cn_ap2,l_id,cn_ci,ti_cod) VALUES ")
myfile.write("\n")
for _ in range(41):
    #clientes naturales
    insert_n = "('{}','{}','{}','{}','{}','{}',{},{},{}),"
    rif1 = "V-{}-{}"
    myfile.write(insert_n.format(rif1.format(str(random.randint(1000000,99999999)),str(random.randint(0,9))),
                    fake.simple_profile(sex=None)['mail'],fake.first_name(),fake.first_name(),fake.last_name(),
                    fake.last_name(),str(random.randint(463,1600)),str(random.randint(1000000,25999999)),str(_+1)))
    myfile.write("\n")

    myfile.write(insert_n.format(rif1.format(str(random.randint(1000000,99999999)),random.randint(0,9)),
                    fake.simple_profile(sex=None)['mail'],fake.first_name(),fake.first_name(),fake.last_name(),
                    fake.last_name(),str(random.randint(463,1600)),str(random.randint(1000000,25999999)),str(_+1)))
    myfile.write("\n")
    #clientes Juridicos

myfile.write("\n")
myfile.write("INSERT INTO clientejuridico (cj_rif, cj_email,cj_razsoc,cj_demcom,cj_pagweb,cj_capdis,ti_cod) VALUES ")
myfile.write("\n")
for _ in range(41):
    insert_j = "('{}','{}','{}','{}','{}',{},{}),"
    rif2 = "J-{}-{}"
    profile = fake.profile()
    myfile.write(insert_j.format(rif2.format(str(random.randint(1000000,99999999)),str(random.randint(0,9))),
                    profile['mail'],profile['company'],fake.company_suffix()+fake.company(),profile['website'][0],
                    str(random.randint(100000,1000000)),str(_+1)))
    myfile.write("\n")

    profile1 = fake.profile()
    myfile.write(insert_j.format(rif2.format(str(random.randint(1000000,99999999)),str(random.randint(0,9))),
                    profile1['mail'],profile1['company'],fake.company_suffix()+fake.company(),profile1['website'][0],
                    str(random.randint(100000,1000000)),str(_+1)))
    myfile.write("\n")

myfile.close()

myfile = open ("direccionCJ.txt","a")
myfile.write("INSERT INTO jur_lug (l_id,cj_id,jl_tipo) VALUES ")
myfile.write("\n")
tipo_dir = ['fiscal','fisica']
insert_jl = "({},{},'{}')"
for _ in range(82):
    for i in range(2):
        myfile.write(insert_e.format(str(random.randint(463,1600)),str(_+1),tipo_dir[i+1]))
        myfile.write("\n")
myfile.close()
#empleados, recordar colocar el ; al final del insert
myfile = open("empleados.txt","a")
myfile.write("INSERT INTO empleado (e_nombre, e_apellido,e_ci,e_salario,ti_cod) VALUES ")
myfile.write("\n")
for _ in range(41):
    for i in range(4):
        insert_e = "('{}','{}',{},{},{}),"
        myfile.write(insert_e.format(fake.first_name(),fake.last_name(),str(random.randint(1000000,21999999)),str(random.randint(10000,100000)),str(_+1)))
        myfile.write("\n")
myfile.close()

myfile = open("asistencia.txt","a")
myfile.write("INSERT INTO asistencia (as_fecha_entrada, as_fecha_salida,e_id) VALUES ")
myfile.write("\n")
for _ in range(4):
    for i in range(20):
        insert_a = "(to_timestamp('{}', 'DD-MM-YYYY HH24:MI'),to_timestamp('{}', 'DD-MM-YYYY HH24:MI'),{}),"
        date = "{}-06-2018 {}:00"
        myfile.write(insert_a.format(randomDate(date.format(str(i+1),"5"),date.format(str(i+1),"10"), random.random()),
                    randomDate(date.format(str(i+1),"12"),date.format(str(i+1),"20"), random.random()),str(_+1)))
        myfile.write("\n")
myfile.close()

myfile = open("carnet.txt","a")
myfile.write("INSERT INTO carnet (car_num, cj_id,d_id) VALUES ")
myfile.write("\n")
dept = 1
count = 0
for _ in range(41):
    insert_c = "('{}',{},{}),"
    for i in range(2):
        if _+1 < 10:
            num_c = "0{}-0000000{}"
        else:
            num_c = "{}-0000000{}"
        count = count+1
        myfile.write(insert_c.format(num_c.format(str(_+1),str(i+1)),str(count),str(dept)))
        myfile.write("\n")
    dept = dept+5

myfile.write("\n")
myfile.write("INSERT INTO carnet (car_num, cn_id,d_id) VALUES ")
myfile.write("\n")
dept = 1
count = 0
for _ in range(41):
    insert_c = "('{}',{},{}),"
    for i in range(2):
        if _+1 < 10:
            num_c = "0{}-0000000{}"
        else:
            num_c = "{}-0000000{}"
        count = count+1
        myfile.write(insert_c.format(num_c.format(str(_+1),str(i+3)),str(count),str(dept)))
        myfile.write("\n")
    dept = dept+5
myfile.close()

myfile = open("usuarios.txt","a")
myfile.write("INSERT INTO usuario (u_username, u_password,cn_id) VALUES ")
myfile.write("\n")
for _ in range(82):
    insert_u = "('{}','{}',{}),"
    myfile.write(insert_u.format(fake.simple_profile()['username'],
                    fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
                    ,str(_+1)))
    myfile.write("\n")

myfile.write("\n")
myfile.write("INSERT INTO usuario (u_username, u_password,cj_id) VALUES ")
myfile.write("\n")
for _ in range(82):
    insert_u = "('{}','{}',{}),"
    myfile.write(insert_u.format(fake.simple_profile()['username'],fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True),str(_+1)))
    myfile.write("\n")

myfile.write("\n")
myfile.write("INSERT INTO usuario (u_username, u_password,e_id) VALUES ")
myfile.write("\n")
for _ in range(164):
    insert_u = "('{}','{}',{}),"
    myfile.write(insert_u.format(fake.simple_profile()['username'],fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True),str(_+1)))
    myfile.write("\n")
myfile.close()

myfile = open("puntos.txt","a")
myfile.write("INSERT INTO puntos (car_id,h_id) VALUES ")
myfile.write("\n")
for _ in range(164):
    insert_u = "({},{}),"
    myfile.write(insert_u.format(str(_+1),str(random.randint(1,10))))
    myfile.write("\n")
myfile.close()

myfile = open("departamentos.txt","a")
myfile.write("INSERT INTO departamento (d_nombre,ti_cod) VALUES ")
myfile.write("\n")
insert = "('{}',{}),"
depts = ['Ventas en Linea','Talento Humano','Despacho','Entrega','Pedidos Internos']
for _ in range(41):
    for i in range(5):
        myfile.write(insert.format(depts[i+1],str(_+1)))
        myfile.write("\n")

myfile.close()

myfile = open("metodos.txt","a")
myfile.write("INSERT INTO tarjetacredito (tc_num,tc_fvenc,tc_codseg,tc_ncompl,tc_marca,cn_id) VALUES ")
myfile.write("\n")
tipo_marca = ['VISA','MASTERCARD','AMERICAN EXPRESS','DINERS CLUB']
insert = "({},'{}',{},'{}','{}',{}),"
for _ in range(82):
    myfile.write(insert.format(fake.credit_card_number(),
                fake.credit_card_expire(start="now", end="+10y", date_format="%d-%m-%Y"),
                fake.credit_card_security_code(),fake.name(),tipo_marca[random.randint(0,3)],str(_+1)))
    myfile.write("\n")

myfile.write("\n")
myfile.write("INSERT INTO tarjetacredito (tc_num,tc_fvenc,tc_codseg,tc_ncompl,tc_marca,cj_id) VALUES ")
myfile.write("\n")
insert = "({},'{}',{},'{}',{}),"
for _ in range(82):
    myfile.write(insert.format(fake.credit_card_number(),
                fake.credit_card_expire(start="now", end="+10y", date_format="%d-%m-%Y"),
                fake.credit_card_security_code(),fake.name(),tipo_marca[random.randint(0,3)],str(_+1)))
    myfile.write("\n")

myfile.close()

myfile = open ("personas.txt","a")
myfile.write("INSERT INTO personadecontacto (pc_nombre,pc_apellido,cj_id) VALUES ")
myfile.write("\n")
insert = "('{}','{}',{})"
for _ in range(82):
    for i in range(2):
        myfile.write(insert.format(fake.first_name(),fake.last_name(),str(_+1)))
        myfile.write("\n")

myfile.close()
