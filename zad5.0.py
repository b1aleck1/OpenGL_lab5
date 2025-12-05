#!/usr/bin/env python3
import sys
import math

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

N = 50

vertices = [[[0.0] * 3 for i in range(N)] for j in range(N)]
normals = [[[0.0] * 3 for i in range(N)] for j in range(N)]

viewer = [0.0, 0.0, 10.0]

theta = 0.0
phi = 0.0
R_light = 6.0
pix2angle = 1.0

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

# Przelacznik wektorow
show_normals = False

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Wazne przy skalowaniu/obrotach, zeby swiatlo nie "glupialo"
    glEnable(GL_NORMALIZE)

    pi = math.pi

    for i in range(N):
        for j in range(N):
            u = i / (N - 1)
            v = j / (N - 1)

            # 1. Pozycja (x, y, z)
            u2 = u * u;
            u3 = u2 * u;
            u4 = u3 * u;
            u5 = u4 * u
            poly_u = (-90 * u5 + 225 * u4 - 270 * u3 + 180 * u2 - 45 * u)

            x = poly_u * math.cos(pi * v)
            y = 160 * u4 - 320 * u3 + 160 * u2 - 5.0
            z = poly_u * math.sin(pi * v)

            vertices[i][j][0] = x
            vertices[i][j][1] = y
            vertices[i][j][2] = z

            # 2. Pochodne
            xu = (-450 * u4 + 900 * u3 - 810 * u2 + 360 * u - 45) * math.cos(pi * v)
            xv = pi * (90 * u5 - 225 * u4 + 270 * u3 - 180 * u2 + 45 * u) * math.sin(pi * v)
            yu = 640 * u3 - 960 * u2 + 320 * u
            yv = 0
            zu = (-450 * u4 + 900 * u3 - 810 * u2 + 360 * u - 45) * math.sin(pi * v)
            zv = -pi * (90 * u5 - 225 * u4 + 270 * u3 - 180 * u2 + 45 * u) * math.cos(pi * v)

            # 3. Iloczyn wektorowy
            nx = yu * zv - zu * yv
            ny = zu * xv - xu * zv
            nz = xu * yv - yu * xv

            # 4. Normalizacja i poprawki
            length = math.sqrt(nx * nx + ny * ny + nz * nz)

            # NAPRAWA BIEGUNOW (zeby nie bylo plam)
            if i == 0:
                nx, ny, nz = 0.0, -1.0, 0.0
            elif i == N - 1:
                nx, ny, nz = 0.0, 1.0, 0.0
            elif length > 0:
                nx /= length
                ny /= length
                nz /= length

                # --- AUTOMATYCZNE ODWRACANIE WEKTOROW ---
                # Sprawdzamy iloczyn skalarny pozycji i wektora normalnego.
                # Jesli jest < 0, to wektor "patrzy" do srodka jajka, wtedy go odwracamy.

                if (x * nx + y * ny + z * nz) < 0:
                    nx = -nx
                    ny = -ny
                    nz = -nz

            normals[i][j][0] = nx
            normals[i][j][1] = ny
            normals[i][j][2] = nz


def shutdown():
    pass


def spin(angle):
    # Losowy obrot (wszystkie osie)
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


def render(time):
    global theta, phi, light_position, show_normals

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta -= delta_x * pix2angle
        phi -= delta_y * pix2angle

    theta_rad = theta * math.pi / 180.0
    phi_rad = phi * math.pi / 180.0

    # Pozycja swiatla
    xs = R_light * math.cos(theta_rad) * math.cos(phi_rad)
    ys = R_light * math.sin(phi_rad)
    zs = R_light * math.sin(theta_rad) * math.cos(phi_rad)

    light_position = [xs, ys, zs, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Rysowanie ruchomego zrodla swiatla
    glPushMatrix()
    glTranslatef(xs, ys, zs)
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 0.0)
    quadric_light = gluNewQuadric()
    gluQuadricDrawStyle(quadric_light, GLU_FILL)
    gluSphere(quadric_light, 0.2, 10, 10)
    gluDeleteQuadric(quadric_light)
    glEnable(GL_LIGHTING)
    glPopMatrix()

    # Obrot calego jajka
    spin(time * 20.0)

    # Rysowanie jajka
    glBegin(GL_TRIANGLES)
    for i in range(N - 1):
        for j in range(N - 1):
            glNormal3fv(normals[i][j]);
            glVertex3fv(vertices[i][j])
            glNormal3fv(normals[i + 1][j]);
            glVertex3fv(vertices[i + 1][j])
            glNormal3fv(normals[i][j + 1]);
            glVertex3fv(vertices[i][j + 1])

            glNormal3fv(normals[i + 1][j]);
            glVertex3fv(vertices[i + 1][j])
            glNormal3fv(normals[i + 1][j + 1]);
            glVertex3fv(vertices[i + 1][j + 1])
            glNormal3fv(normals[i][j + 1]);
            glVertex3fv(vertices[i][j + 1])
    glEnd()

    # Rysowanie WSZYSTKICH wektorow (klawisz N)
    if show_normals:
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)  # Zeby nie migalo

        glColor3f(0.0, 1.0, 1.0)
        glBegin(GL_LINES)

        for i in range(N):
            for j in range(N):
                v = vertices[i][j]
                n = normals[i][j]
                glVertex3fv(v)
                glVertex3f(v[0] + n[0] * 0.5, v[1] + n[1] * 0.5, v[2] + n[2] * 0.5)

        glEnd()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    glFlush()


def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, 1.0, 0.1, 300.0)
    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def keyboard_key_callback(window, key, scancode, action, mods):
    global show_normals
    if action == GLFW_PRESS:
        if key == GLFW_KEY_ESCAPE:
            glfwSetWindowShouldClose(window, GLFW_TRUE)
        if key == GLFW_KEY_N:
            show_normals = not show_normals
            print(f"Wektory: {show_normals}")


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, mouse_x_pos_old, delta_y, mouse_y_pos_old
    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos
    delta_y = y_pos - mouse_y_pos_old
    mouse_y_pos_old = y_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0


def main():
    if not glfwInit(): sys.exit(-1)
    window = glfwCreateWindow(400, 400, "Lab 5 (5.0) - Jajko Final 100%", None, None)
    if not window: glfwTerminate(); sys.exit(-1)
    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()
    glfwTerminate()


if __name__ == '__main__':
    main()