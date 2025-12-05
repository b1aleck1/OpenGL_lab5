#!/usr/bin/env python3
import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

viewer = [0.0, 0.0, 10.0]

theta = 0.0
pix2angle = 1.0

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0

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

selection_index = 0

param_names = [
    "Light Ambient R", "Light Ambient G", "Light Ambient B",
    "Light Diffuse R", "Light Diffuse G", "Light Diffuse B",
    "Light Specular R", "Light Specular G", "Light Specular B"
]


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

    print("Instrukcja:")
    print("[TAB] - Zmień edytowany parametr")
    print("[UP]  - Zwiększ wartość (+0.1)")
    print("[DOWN]- Zmniejsz wartość (-0.1)")
    print_selection()


def shutdown():
    pass


def render(time):
    global theta

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle

    glRotatef(theta, 0.0, 1.0, 0.0)

    # AKTUALIZACJA ŚWIATŁA W KAŻDEJ KLATCE
    # Aby widzieć zmiany wprowadzane klawiaturą
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluSphere(quadric, 3.0, 10, 10)
    gluDeleteQuadric(quadric)

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


def print_selection():
    # Wypisuje aktualnie wybrany parametr i jego wartość
    global selection_index

    # Określenie, która tablica i który indeks w tablicy
    array_idx = selection_index // 3  # 0=Ambient, 1=Diffuse, 2=Specular
    color_idx = selection_index % 3  # 0=R, 1=G, 2=B

    val = 0.0
    if array_idx == 0:
        val = light_ambient[color_idx]
    elif array_idx == 1:
        val = light_diffuse[color_idx]
    elif array_idx == 2:
        val = light_specular[color_idx]

    print(f"Wybrany parametr: {param_names[selection_index]} | Wartość: {val:.1f}")


def keyboard_key_callback(window, key, scancode, action, mods):
    global selection_index
    global light_ambient, light_diffuse, light_specular

    if action == GLFW_PRESS:
        if key == GLFW_KEY_ESCAPE:
            glfwSetWindowShouldClose(window, GLFW_TRUE)

        # Zmiana wybranego parametru (TAB)
        if key == GLFW_KEY_TAB:
            selection_index = (selection_index + 1) % 9
            print_selection()

        # Zmiana wartości (Góra/Dół)
        if key == GLFW_KEY_UP or key == GLFW_KEY_DOWN:
            array_idx = selection_index // 3
            color_idx = selection_index % 3

            change = 0.1 if key == GLFW_KEY_UP else -0.1

            # Aktualizacja odpowiedniej tablicy
            if array_idx == 0:
                light_ambient[color_idx] += change
                if light_ambient[color_idx] > 1.0: light_ambient[color_idx] = 1.0
                if light_ambient[color_idx] < 0.0: light_ambient[color_idx] = 0.0
            elif array_idx == 1:
                light_diffuse[color_idx] += change
                if light_diffuse[color_idx] > 1.0: light_diffuse[color_idx] = 1.0
                if light_diffuse[color_idx] < 0.0: light_diffuse[color_idx] = 0.0
            elif array_idx == 2:
                light_specular[color_idx] += change
                if light_specular[color_idx] > 1.0: light_specular[color_idx] = 1.0
                if light_specular[color_idx] < 0.0: light_specular[color_idx] = 0.0

            print_selection()



def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old

    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, "Lab 5 (Ocena 3.5)", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

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