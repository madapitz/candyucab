﻿DROP DATABASE IF EXISTS proyecto;
CREATE DATABASE proyecto;
\c proyecto;
SET DATESTYLE TO ISO,DMY;
CREATE TABLE clientenatural (
  cn_id SERIAL,
  cn_rif varchar(15) NOT NULL UNIQUE,
  cn_email varchar(50) NOT NULL UNIQUE,
  cn_ci numeric(15) NOT NULL UNIQUE,
  cn_nom1 varchar(20) NOT NULL,
  cn_nom2 varchar(20) NOT NULL,
  cn_ap1 varchar(20) NOT NULL,
  cn_ap2 varchar(20) NOT NULL,
  l_id integer NOT NULL,
  ti_cod integer,
  CONSTRAINT pk_clienten PRIMARY KEY (cn_id)
);

CREATE TABLE clientejuridico (
  cj_id SERIAL,
  cj_rif varchar(15) NOT NULL UNIQUE,
  cj_email varchar(50) NOT NULL UNIQUE,
  cj_demcom varchar(50) NOT NULL,
  cj_razsoc varchar(50) NOT NULL,
  cj_pagweb varchar(50) NOT NULL,
  cj_capdis numeric(20) NOT NULL,
  ti_cod integer,
  CONSTRAINT pk_clientej PRIMARY KEY (cj_id)
);

CREATE TABLE telefono (
  t_id SERIAL,
  t_num numeric(10) NOT NULL,
  cj_id integer,
  cn_id integer,
  CONSTRAINT pk_telefono PRIMARY KEY (t_id)
);

CREATE TABLE personadecontacto (
  pc_id SERIAL,
  pc_nombre varchar(20) NOT NULL,
  pc_apellido varchar(20) NOT NULL,
  cj_id integer NOT NULL,
  CONSTRAINT pk_percontacto PRIMARY KEY (pc_id)
);

CREATE TABLE usuario (
  u_id SERIAL,
  u_username varchar(40) NOT NULL UNIQUE,
  u_password varchar(60) NOT NULL,
  cj_id integer,
  cn_id integer,
  e_id integer,
  r_id integer,
  CONSTRAINT pk_usuario PRIMARY KEY (u_id)
);

CREATE TABLE empleado (
  e_id SERIAL,
  e_nombre varchar(20) NOT NULL,
  e_apellido varchar(20) NOT NULL,
  e_ci numeric(15) NOT NULL UNIQUE,
  e_salario numeric(15) NOT NULL,
  ti_id integer NOT NULL,
  CONSTRAINT pk_empleado PRIMARY KEY (e_id)
);

CREATE TABLE lugar (
  l_id integer,
  l_tipo char(1) NOT NULL,
  l_nombre varchar(40) NOT NULL,
  fk_lugar integer,
  CONSTRAINT pk_lugar PRIMARY KEY (l_id),
  CONSTRAINT check_tipo CHECK(l_tipo in ('M','P','E'))
);

CREATE TABLE jur_lug(
  jl_id SERIAL,
  l_id integer NOT NULL,
  cj_id integer NOT NULL,
  jl_tipo varchar(10) NOT NULL,
  CONSTRAINT pk_lugar_clientej PRIMARY KEY (jl_id),
  CONSTRAINT check_tipodir CHECK(jl_tipo in ('fisica','fiscal'))
);

CREATE TABLE departamento (
  d_id SERIAL,
  d_nombre varchar(20) NOT NULL,
  ti_cod integer NOT NULL,
  CONSTRAINT pk_departamento PRIMARY KEY (d_id)
);

CREATE TABLE fabrica (
  f_id SERIAL,
  f_nombre varchar(20) NOT NULL,
  l_id integer NOT NULL,
  CONSTRAINT pk_fabrica PRIMARY KEY (f_id)
);

CREATE TABLE tienda (
  ti_id SERIAL,
  ti_tipo varchar(20) NOT NULL,
  ti_nombre varchar(40) NOT NULL,
  l_id integer NOT NULL,
  CONSTRAINT check_tipo_tienda CHECK (ti_tipo IN ('Mini Candy Shop','Candy Shop')),
  CONSTRAINT pk_tienda PRIMARY KEY (ti_id)
);

CREATE TABLE rol (
  r_id SERIAL,
  r_tipo varchar(30) NOT NULL,
  CONSTRAINT pk_rol PRIMARY KEY (r_id)
);

CREATE TABLE rol_per (
  rp_id SERIAL,
  r_id integer NOT NULL,
  per_id integer NOT NULL,
  CONSTRAINT pk_rol_per PRIMARY KEY (rp_id)
);

CREATE TABLE permiso (
  per_id SERIAL,
  per_funcion varchar(30) NOT NULL,
  CONSTRAINT pk_permiso PRIMARY KEY (per_id)
);

CREATE TABLE asistencia (
  as_cod SERIAL,
  as_fecha_entrada TIMESTAMP NOT NULL,
  as_fecha_salida TIMESTAMP NOT NULL,
  e_id integer NOT NULL,
  CONSTRAINT pk_asistencia PRIMARY KEY (as_cod)
);

CREATE TABLE beneficio (
  b_id SERIAL,
  b_ingreso numeric(10) NOT NULL,
  b_nombre varchar(30) NOT NULL,
  e_id integer NOT NULL,
  CONSTRAINT pk_beneficio PRIMARY KEY (b_id)
);

CREATE TABLE horario (
  h_id SERIAL,
  h_fecha_entrada TIMESTAMP NOT NULL,
  h_fecha_salida TIMESTAMP NOT NULL,
  h_dia varchar(20) NOT NULL,
  e_id integer NOT NULL,
  CONSTRAINT pk_horario PRIMARY KEY (h_id)
);

CREATE TABLE diariodulce (
  dd_id SERIAL,
  dd_femision DATE NOT NULL DEFAULT CURRENT_DATE,
  dd_ffinal DATE NOT NULL,
  e_id integer NOT NULL,
  CONSTRAINT pk_diarioducle PRIMARY KEY (dd_id)
);

CREATE TABLE pasillo (
  pas_id SERIAL,
  pas_nombre varchar(20) NOT NULL,
  ti_id integer NOT NULL,
  CONSTRAINT pk_pasillo PRIMARY KEY (pas_id)
);

CREATE TABLE anaquel (
  an_id SERIAL,
  an_nombre varchar(20) NOT NULL,
  pas_id integer NOT NULL,
  CONSTRAINT pk_anaquel PRIMARY KEY (an_id)
);

CREATE TABLE inventario (
  i_id SERIAL,
  i_cant numeric(20) NOT NULL,
  an_id integer NOT NULL,
  ti_id integer NOT NULL,
  p_id integer NOT NULL,
  CONSTRAINT pk_inventario PRIMARY KEY (i_id)
);

CREATE TABLE pro_diario (
  pd_id SERIAL,
  pd_descuento numeric(4,2) NOT NULL,
  dd_id integer NOT NULL,
  p_id integer,
  CONSTRAINT pk_pro_diario PRIMARY KEY (pd_id)
);

CREATE TABLE presupuesto (
  pre_id SERIAL,
  pre_femision DATE NOT NULL DEFAULT CURRENT_DATE,
  pre_nombre varchar(40),
  CONSTRAINT pk_presupuesto PRIMARY KEY (pre_id)
);

CREATE TABLE tarjetacredito (
  tc_id SERIAL,
  tc_ncompl varchar(60) NOT NULL,
  tc_num numeric(40) NOT NULL,
  tc_codseg numeric(5) NOT NULL,
  tc_fvenc DATE NOT NULL,
  tc_marca varchar(30) NOT NULL,
  cj_id integer,
  cn_id integer,
  CONSTRAINT pk_tarjetac PRIMARY KEY (tc_id)
);

CREATE TABLE tarjetadebito (
  td_id SERIAL,
  td_ncompl varchar(60) NOT NULL,
  td_num numeric(40) NOT NULL,
  td_banco varchar(20) NOT NULL,
  td_fvenc DATE NOT NULL,
  cj_id integer,
  cn_id integer,
  CONSTRAINT pk_tarjetad PRIMARY KEY (td_id)
);

CREATE TABLE cheque (
  ch_id SERIAL,
  ch_ncompl varchar(60) NOT NULL,
  ch_num numeric(40) NOT NULL,
  ch_faplicar DATE NOT NULL,
  cj_id integer,
  cn_id integer,
  CONSTRAINT pk_cheque PRIMARY KEY (ch_id)
);

CREATE TABLE producto (
  p_id SERIAL,
  p_nombre varchar(60) NOT NULL,
  p_precio numeric(16) NOT NULL,
  p_imagen varchar(60) NOT NULL,
  p_desc TEXT NOT NULL,
  tp_id integer NOT NULL,
  CONSTRAINT pk_producto PRIMARY KEY (p_id)
);

CREATE TABLE comprafisica (
  cf_id SERIAL,
  cf_fcompra DATE NOT NULL DEFAULT CURRENT_DATE,
  cf_cant integer NOT NULL,
  cj_id integer,
  cn_id integer,
  i_id integer NOT NULL,
  CONSTRAINT pk_cfisica PRIMARY KEY (cf_id)
);

CREATE TABLE compravirtual (
  cv_id SERIAL,
  cv_cant numeric(10) NOT NULL,
  cv_fcompra DATE NOT NULL DEFAULT CURRENT_DATE,
  pre_id integer NOT NULL,
  u_id integer NOT NULL,
  pre2_id integer,
  p_id integer NOT NULL,
  i_id integer,
  CONSTRAINT pk_cvirtual PRIMARY KEY (cv_id)
);

CREATE TABLE pagovirtual (
  pv_id SERIAL,
  pv_puntos numeric(10),
  pv_fpago DATE NOT NULL,
  pv_monto numeric(10) NOT NULL,
  cv_id integer NOT NULL,
  tc_id integer,
  CONSTRAINT pk_pvirtual PRIMARY KEY (pv_id)
);

CREATE TABLE factura (
  f_numero SERIAL,
  f_femision DATE NOT NULL,
  pv_id integer,
  CONSTRAINT pk_factura PRIMARY KEY (f_numero)
);

CREATE TABLE carnet (
  car_id SERIAL,
  car_num varchar(11) NOT NULL,
  cj_id integer,
  cn_id integer,
  d_id integer NOT NULL,
  CONSTRAINT pk_carnet PRIMARY KEY (car_id)
);

CREATE TABLE orden (
  o_id SERIAL,
  o_fecha DATE NOT NULL,
  o_monto_total numeric(20),
  d_id integer,
  i_id integer,
  pv_id integer,
  CONSTRAINT pk_orden PRIMARY KEY (o_id)
);

CREATE TABLE estatus (
  es_id SERIAL,
  es_tipo varchar(20),
  CONSTRAINT pk_estatus PRIMARY KEY (es_id)
);

CREATE TABLE pedido (
  ped_id SERIAL,
  ped_fentrega DATE NOT NULL,
  pv_id integer,
  cn_id integer,
  cj_id integer,
  d_id integer,
  CONSTRAINT pk_pedido PRIMARY KEY (ped_id)
);

CREATE TABLE punto (
  pu_id SERIAL,
  pf_id integer,
  car_id integer NOT NULL,
  h_id integer NOT NULL,
  CONSTRAINT pk_punto PRIMARY KEY (pu_id)
);

CREATE TABLE historial (
  h_id SERIAL,
  h_precio numeric(10) NOT NULL,
  h_fecha DATE NOT NULL DEFAULT CURRENT_DATE,
  CONSTRAINT pk_historial PRIMARY KEY (h_id)
);

CREATE TABLE tipo_producto (
  tp_id SERIAL,
  tp_nombre varchar(30) NOT NULL,
  CONSTRAINT pk_tipo_producto PRIMARY KEY (tp_id)
);

CREATE TABLE reposicion (
  re_id SERIAL,
  f_id integer,
  i_id integer,
  o_id integer NOT NULL,
  CONSTRAINT pk_reposicion PRIMARY KEY (re_id)
);

CREATE TABLE pagofisico (
  pf_id SERIAL,
  pf_monto numeric(20) NOT NULL,
  pf_fecha DATE NOT NULL DEFAULT CURRENT_DATE,
  cf_id integer NOT NULL,
  tc_id integer,
  td_id integer,
  ch_id integer,
  CONSTRAINT pk_pagofisico PRIMARY KEY (pf_id)
);

CREATE TABLE or_est (
  oe_id SERIAL,
  oe_fecha DATE NOT NULL DEFAULT CURRENT_DATE,
  o_id integer NOT NULL,
  es_id integer NOT NULL,
  CONSTRAINT pk_orden_estatus PRIMARY KEY (oe_id)
);

CREATE TABLE ped_est (
  pe_id SERIAL,
  pe_fecha DATE NOT NULL DEFAULT CURRENT_DATE,
  ped_id integer NOT NULL,
  es_id integer NOT NULL,
  CONSTRAINT pk_pedido_estatus PRIMARY KEY (pe_id)
);
