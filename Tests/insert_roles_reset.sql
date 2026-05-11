DELETE FROM rol_asignaciones_rol_permiso;
DELETE FROM rol_asignaciones_usuario_rol;
DELETE FROM rol_permisos;
DELETE FROM rol_roles;

ALTER SEQUENCE rol_roles_id_seq RESTART WITH 1;
ALTER SEQUENCE rol_permisos_id_seq RESTART WITH 1;

INSERT INTO rol_roles (nombre, descripcion, estado, created_at, updated_at)
VALUES 
  ('Admin', 'Administrador del sistema', 'activo', NOW(), NOW()),
  ('Estudiante', 'Estudiante de la universidad', 'activo', NOW(), NOW()),
  ('Docente', 'Profesor de la universidad', 'activo', NOW(), NOW());

INSERT INTO rol_permisos (codigo, nombre, descripcion, modulo, microservicio_origen, funcionalidad_asociada, metodo_operacion, created_at, updated_at)
VALUES
  ('USR_CREATE', 'Crear usuarios', 'Permiso para crear nuevos usuarios', 'Usuarios', 'ms-usuarios', 'Gestión de usuarios', 'creacion', NOW(), NOW()),
  ('USR_EDIT', 'Editar usuarios', 'Permiso para editar usuarios', 'Usuarios', 'ms-usuarios', 'Gestión de usuarios', 'actualizacion', NOW(), NOW()),
  ('USR_DELETE', 'Eliminar usuarios', 'Permiso para eliminar usuarios', 'Usuarios', 'ms-usuarios', 'Gestión de usuarios', 'eliminacion', NOW(), NOW()),
  ('USR_VIEW', 'Ver usuarios', 'Permiso para ver usuarios', 'Usuarios', 'ms-usuarios', 'Gestión de usuarios', 'consulta', NOW(), NOW()),
  ('ROL_CREATE', 'Crear roles', 'Permiso para crear roles', 'Roles', 'ms-roles', 'Gestión de roles', 'creacion', NOW(), NOW()),
  ('ROL_EDIT', 'Editar roles', 'Permiso para editar roles', 'Roles', 'ms-roles', 'Gestión de roles', 'actualizacion', NOW(), NOW()),
  ('ROL_DELETE', 'Eliminar roles', 'Permiso para eliminar roles', 'Roles', 'ms-roles', 'Gestión de roles', 'eliminacion', NOW(), NOW()),
  ('ROL_VIEW', 'Ver roles', 'Permiso para ver roles', 'Roles', 'ms-roles', 'Gestión de roles', 'consulta', NOW(), NOW());

INSERT INTO rol_asignaciones_usuario_rol (usuario_id, rol_id, estado, asignado_por_usuario_id, created_at, updated_at)
VALUES 
  (5, 1, 'activo', 5, NOW(), NOW()),
  (6, 2, 'activo', 5, NOW(), NOW());

INSERT INTO rol_asignaciones_rol_permiso (rol_id, permiso_id, asignado_por_usuario_id, created_at, updated_at)
SELECT 1, id, 5, NOW(), NOW() FROM rol_permisos;

INSERT INTO rol_asignaciones_rol_permiso (rol_id, permiso_id, asignado_por_usuario_id, created_at, updated_at)
SELECT 2, id, 5, NOW(), NOW() FROM rol_permisos WHERE codigo LIKE '%_VIEW';

SELECT 'Roles:' as section;
SELECT id, nombre FROM rol_roles;

SELECT 'User-Role Assignments:' as section;
SELECT usuario_id, rol_id FROM rol_asignaciones_usuario_rol;

SELECT 'Admin Permissions Count:' as section;
SELECT COUNT(*) FROM rol_asignaciones_rol_permiso WHERE rol_id = 1;
