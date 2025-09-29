# ***********************************************************************************
#   ExibePoligonos.py
#       Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
#   Este programa cria um conjunto de INSTANCIAS
#   Para construir este programa, foi utilizada a biblioteca PyOpenGL, disponível em
#   http://pyopengl.sourceforge.net/documentation/index.html
#
#   Sugere-se consultar também as páginas listadas
#   a seguir:
#   http://bazaar.launchpad.net/~mcfletch/pyopengl-demo/trunk/view/head:/PyOpenGL-Demo/NeHe/lesson1.py
#   http://pyopengl.sourceforge.net/documentation/manual-3.0/index.html#GLUT
#
#   No caso de usar no MacOS, pode ser necessário alterar o arquivo ctypesloader.py,
#   conforme a descrição que está nestes links:
#   https://stackoverflow.com/questions/63475461/unable-to-import-opengl-gl-in-python-on-macos
#   https://stackoverflow.com/questions/6819661/python-location-on-mac-osx
#   Veja o arquivo Patch.rtf, armazenado na mesma pasta deste fonte.
# ***********************************************************************************

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Poligonos import *
from Instancia import *
from ModeloMatricial import *
from ListaDeCoresRGB import *
from datetime import datetime
import time
import random
import copy

# ***********************************************************************************
tiros_disparados = 0
tempo_inicio = time.time()
limite_tiros = 10
intervalo = 2 
vidas = 3
intervaloCriacao= 2
proximo_tiro_inimigo = time.time() + 2 
intervalo_tiro_inimigo = 4
# Modelos de Objetos
MeiaSeta = Polygon()
Mastro = Polygon()

# Limites da Janela de Seleção
Min = Ponto()
Max = Ponto()

# lista de instancias do Personagens
Personagens = [Instancia() for x in range(200)]

AREA_DE_BACKUP = 70 # posicao a partir da qual sao armazenados backups dos personagens

# lista de modelos
Modelos = []

angulo = 0.0
PersonagemAtual = -1
nInstancias = 0

imprimeEnvelope = False

LarguraDoUniverso = 10.0

TempoInicial = time.time()
TempoTotal = time.time()
TempoAnterior = time.time()

# define uma funcao de limpeza de tela
from os import system, name
def clear():
 
    # for windows
    if name == 'nt':
        _ = system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
        #print("*******************")
        #print ("PWD: ", os.getcwd()) 
        
def DesenhaLinha (P1, P2):
    glBegin(GL_LINES)
    glVertex3f(P1.x,P1.y,P1.z)
    glVertex3f(P2.x,P2.y,P2.z)
    glEnd()

# ****************************************************************
def RotacionaAoRedorDeUmPonto(alfa: float, P: Ponto):
    glTranslatef(P.x, P.y, P.z)
    glRotatef(alfa, 0,0,1)
    glTranslatef(-P.x, -P.y, -P.z)

# ***********************************************************************************
def reshape(w,h):

    global Min, Max
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Cria uma folga na Janela de Selecão, com 10% das dimensoes do poligono
    BordaX = abs(Max.x-Min.x)*0.1
    BordaY = abs(Max.y-Min.y)*0.1
    #glOrtho(Min.x-BordaX, Max.x+BordaX, Min.y-BordaY, Max.y+BordaY, 0.0, 1.0)
    glOrtho(Min.x, Max.x, Min.y, Max.y, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

# ***********************************************************************************
def DesenhaMastro():
    Mastro.desenhaPoligono()

# ***********************************************************************************
def DesenhaSeta():
    glPushMatrix()
    MeiaSeta.desenhaPoligono()
    glScaled(1,-1, 1)
    MeiaSeta.desenhaPoligono()
    glPopMatrix()

# ***********************************************************************************
def DesenhaApontador():
    glPushMatrix()
    glTranslated(-4, 0, 0)
    DesenhaSeta()
    glPopMatrix()
# **********************************************************************
def DesenhaHelice():
    glPushMatrix()
    for i in range (4):   
        glRotatef(90, 0, 0, 1)
        DesenhaApontador()
    glPopMatrix()

# ***********************************************************************************
def DesenhaHelicesGirando():
    global angulo
    #print ("angulo:", angulo)
    glPushMatrix()
    glRotatef(angulo, 0, 0, 1)
    DesenhaHelice()
    glPopMatrix()

# ***********************************************************************************
def DesenhaCatavento():
    #glLineWidth(3)
    glPushMatrix()
    DesenhaMastro()
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslated(0,3,0)
    glScaled(0.2, 0.2, 1)
    DesenhaHelicesGirando()
    glPopMatrix()
    glPopMatrix()

# **************************************************************
def DesenhaEixos():
    global Min, Max

    Meio = Ponto(); 
    Meio.x = (Max.x+Min.x)/2
    Meio.y = (Max.y+Min.y)/2
    Meio.z = (Max.z+Min.z)/2

    glBegin(GL_LINES)
    #  eixo horizontal
    glVertex2f(Min.x,Meio.y)
    glVertex2f(Max.x,Meio.y)
    #  eixo vertical
    glVertex2f(Meio.x,Min.y)
    glVertex2f(Meio.x,Max.y)
    glEnd()


def DesenhaCoracao():
    global vidas
    if vidas <= 0:
        return

    glPushMatrix()
    glLoadIdentity()  # desenha sempre em coordenadas fixas

    # posição inicial (canto superior esquerdo)
    margem_x = Min.x + 2
    topo_y = Max.y - 8  # 6 de altura + 2 de margem

    for i in range(vidas):
        glPushMatrix()
        glTranslatef(margem_x + i * 8, topo_y, 0)  # cada coração tem 7 de largura + 1 espaço
        DesenhaModelo(5)  # índice do coração no Modelos
        glPopMatrix()

    glPopMatrix()


def DesenhaModelo(idx):
    MM = Modelos[idx]
    larg = MM.nColunas
    alt = MM.nLinhas

    glPushMatrix()
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt - 1 - i, j)
            if cor != -1:
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()

# ***********************************************************************************
def TestaColisao(P1, P2) -> bool :
    global vidas
    # cout << "\n-----\n" << endl;
    # Personagens[Objeto1].ImprimeEnvelope("Envelope 1: ", "\n");
    # Personagens[Objeto2].ImprimeEnvelope("\nEnvelope 2: ", "\n");
    # cout << endl;

    # Testa todas as arestas do envelope de
    # um objeto contra as arestas do outro
       
    for i in range(4):
        A = Personagens[P1].Envelope[i]
        B = Personagens[P1].Envelope[(i+1)%4]
        for j in range(4):
            # print ("Testando ", i," contra ",j)
            # Personagens[Objeto1].ImprimeEnvelope("\nEnvelope 1: ", "\n");
            # Personagens[Objeto2].ImprimeEnvelope("Envelope 2: ", "\n");
            C = Personagens[P2].Envelope[j]
            D = Personagens[P2].Envelope[(j+1)%4]
            # A.imprime("A:","\n");
            # B.imprime("B:","\n");
            # C.imprime("C:","\n");
            # D.imprime("D:","\n\n");    
            if HaInterseccao(A, B, C, D):
                return True
    return False


# ***********************************************************************************
def AtualizaEnvelope(i):
    global Personagens
    id = Personagens[i].IdDoModelo
    MM = Modelos[id]

    P = Personagens[i]
    V = P.Direcao * (MM.nColunas/2.0)
    V.rotacionaZ(90)
    A = P.PosicaoDoPersonagem + V
    B = A + P.Direcao*MM.nLinhas
    
    V = P.Direcao * MM.nColunas
    V.rotacionaZ(-90)
    C = B + V

    V = P.Direcao * -1 * MM.nLinhas
    D = C + V

    # Desenha o envelope
    SetColor(Red)
    glBegin(GL_LINE_LOOP)
    glVertex2f(A.x, A.y)
    glVertex2f(B.x, B.y)
    glVertex2f(C.x, C.y)
    glVertex2f(D.x, D.y)
    glEnd()
    # if (imprimeEnvelope):
    #     A.imprime("A:");
    #     B.imprime("B:");
    #     C.imprime("C:");
    #     D.imprime("D:");
    #     print("");

    Personagens[i].Envelope[0] = A
    Personagens[i].Envelope[1] = B
    Personagens[i].Envelope[2] = C
    Personagens[i].Envelope[3] = D

# ***********************************************************************************
# Gera sempre uma posicao na metade de baixo da tela
def GeraPosicaoAleatoria():
        x = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
        y = random.randint(-LarguraDoUniverso, LarguraDoUniverso)
        return Ponto (x,y)


# ***********************************************************************************

   


def AtualizaJogo():
    global imprimeEnvelope, nInstancias, Personagens, vidas

    # Atualiza envelopes de colisão de todos os personagens
    for i in range(0, nInstancias):
        AtualizaEnvelope(i)
        if imprimeEnvelope:
            #print("Envelope ", i)
            Personagens[i].ImprimeEnvelope("", "")
    imprimeEnvelope = False

    # Verifica colisao do jogador com inimigos ou tiros
    for i in range(1, nInstancias):
        personagem = Personagens[i]

        # Ignora com o do jogador
        if getattr(personagem, "tipo", None) == "tiro" and getattr(personagem, "atirador", None) == 0:
            continue

        if TestaColisao(0, i):  # jogador é o índice 0
            #print(f"Colisão com personagem {i} do tipo {personagem.tipo}")
            vidas -= 1
            #print(f"Vidas restantes: {vidas}")

            if vidas <= 0:
                print("FIM DE JOGO")
                keyboard(ESCAPE, 0, 0)  # Fim

            # Reposiciona o personagem dps da colisão
            Personagens[i] = copy.deepcopy(Personagens[i + AREA_DE_BACKUP])
            Personagens[i].Posicao = GeraPosicaoAleatoria()
            ang = random.randint(0, 360)
            Personagens[i].Rotacao = ang
            Personagens[i].Direcao = Ponto(0, 1)
            Personagens[i].Direcao.rotacionaZ(ang)

    # Verifica colisões de tiros do jogador com inimigos
    for i in range(1, nInstancias):
        if getattr(Personagens[i], "tipo", None) != "tiro":
            continue
        if getattr(Personagens[i], "atirador", None) != 0:
            continue  # Só tiros do jogador

        for j in range(1, nInstancias):
            if i == j:
                continue
            if getattr(Personagens[j], "tipo", None) != "inimigo":
                continue

            if TestaColisao(i, j):
                #print(f"Inimigo {j} foi atingido pelo tiro {i}!")

                # Reposiciona inimigo após a morte
                Personagens[j] = copy.deepcopy(Personagens[j + AREA_DE_BACKUP])
                Personagens[j].Posicao = GeraPosicaoAleatoria()
                ang = random.randint(0, 360)
                Personagens[j].Rotacao = ang
                Personagens[j].Direcao = Ponto(0, 1)
                Personagens[j].Direcao.rotacionaZ(ang)

                # move o tiro pra fora e para de movimentar
                Personagens[i].Velocidade = 0
                Personagens[i].Posicao = Ponto(9999, 9999)

                break  # Um tiro mata o inimigo

        


# ***********************************************************************************
def AtualizaPersonagens(tempoDecorrido):
    global nInstancias
    for i in range (0, nInstancias):
       Personagens[i].AtualizaPosicao(tempoDecorrido)

    if getattr(Personagens[i], "tipo", None) == "inimigo":
            VerificaColisaoComLimites(Personagens[i])
    AtualizaJogo()

# ***********************************************************************************
def DesenhaPersonagens():
    global PersonagemAtual, nInstancias
    
    for i in range (0, nInstancias):
        PersonagemAtual = i
        Personagens[i].Desenha()
        
# ***********************************************************************************
def display():

    global TempoInicial, TempoTotal, TempoAnterior

    TempoAtual = time.time()

    TempoTotal =  TempoAtual - TempoInicial

    DiferencaDeTempo = TempoAtual - TempoAnterior

	# Limpa a tela coma cor de fundo
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    #glLineWidth(3)
    #glColor3f(1,1,1) # R, G, B  [0..1]
    #DesenhaEixos()

    DesenhaPersonagens()
    AtualizaPersonagens(DiferencaDeTempo)
    criacaoDeInimigos()
    inimigosAtiram()
    DesenhaCoracao()

    glutSwapBuffers()
    TempoAnterior = TempoAtual

# ***********************************************************************************
# The function called whenever a key is pressed. 
# Note the use of Python tuples to pass in: (key, x, y)
#ESCAPE = '\033'
ESCAPE = b'\x1b'
def keyboard(*args):
    global imprimeEnvelope
    print (args)
    # If escape is pressed, kill everything.
    if args[0] == b'q':
        os._exit(0)
    if args[0] == ESCAPE:
        os._exit(0)
    if args[0] == b'e':
        imprimeEnvelope = True
    if args[0] == b' ':  # Barra de espaço
        CriaTiro2(0)
    # Forca o redesenho da tela
    glutPostRedisplay()

# **********************************************************************
#  arrow_keys ( a_keys: int, x: int, y: int )   
# **********************************************************************
def arrow_keys(a_keys: int, x: int, y: int):
    if a_keys == GLUT_KEY_UP:         # Se pressionar UP
        Personagens[0].Velocidade=6
    if a_keys == GLUT_KEY_DOWN:       # Se pressionar DOWN
        Personagens[0].Velocidade=2
    if a_keys == GLUT_KEY_LEFT:       # Se pressionar LEFT
        Personagens[0].Rotacao += 5
        Personagens[0].Direcao.rotacionaZ(+5)
        Personagens[0].Velocidade=3
    if a_keys == GLUT_KEY_RIGHT:      # Se pressionar RIGHT
        Personagens[0].Rotacao -= 5
        Personagens[0].Direcao.rotacionaZ(-5)
        Personagens[0].Velocidade=3
    glutPostRedisplay()

# ***********************************************************************************
#
# ***********************************************************************************
def mouse(button: int, state: int, x: int, y: int):
    global PontoClicado
    if (state != GLUT_DOWN): 
        return
    if (button != GLUT_RIGHT_BUTTON):
        return
    #print ("Mouse:", x, ",", y)
    # Converte a coordenada de tela para o sistema de coordenadas do 
    # Personagens definido pela glOrtho
    vport = glGetIntegerv(GL_VIEWPORT)
    mvmatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
    projmatrix = glGetDoublev(GL_PROJECTION_MATRIX)
    realY = vport[3] - y
    worldCoordinate1 = gluUnProject(x, realY, 0, mvmatrix, projmatrix, vport)

    PontoClicado = Ponto (worldCoordinate1[0],worldCoordinate1[1], worldCoordinate1[2])
    PontoClicado.imprime("Ponto Clicado:")

    glutPostRedisplay()

# ***********************************************************************************
def mouseMove(x: int, y: int):
    #glutPostRedisplay()
    return

# ***********************************************************************************
def CarregaModelos():
    global MeiaSeta, Mastro
    MeiaSeta.LePontosDeArquivo("MeiaSeta.txt")
    Mastro.LePontosDeArquivo("Mastro.txt")

    Modelos.append(ModeloMatricial())
    Modelos[0].leModelo("MatrizExemplo0.txt");
    Modelos.append(ModeloMatricial())
    Modelos[1].leModelo("MatrizProjetil.txt");
    Modelos.append(ModeloMatricial())
    Modelos[2].leModelo("inimigo02.txt");
    Modelos.append(ModeloMatricial())
    Modelos[3].leModelo("inimigo01.txt");
    Modelos.append(ModeloMatricial())
    Modelos[4].leModelo("inimigo03.txt");
    Modelos.append(ModeloMatricial())
    Modelos[5].leModelo("heart.txt")
    #print ("Modelo 0");
   # Modelos[0].Imprime()
    #print ("Modelo 1");
    #Modelos[1].Imprime()


def DesenhaCelula():
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()
    pass

def DesenhaBorda():
    glBegin(GL_LINE_LOOP)
    glVertex2f(0,0)
    glVertex2f(0,1)
    glVertex2f(1,1)
    glVertex2f(1,0)
    glEnd()

# ***********************************************************************************
def DesenhaPersonagemMatricial():
    global PersonagemAtual, count

    MM = ModeloMatricial()
    
    ModeloDoPersonagem = Personagens[PersonagemAtual].IdDoModelo
        
    MM = Modelos[ModeloDoPersonagem]
    #MM.Imprime("Matriz:")
      
    glPushMatrix()
    larg = MM.nColunas
    alt = MM.nLinhas
    #print (alt, " LINHAS e ", larg, " COLUNAS")
    for i in range(alt):
        glPushMatrix()
        for j in range(larg):
            cor = MM.getColor(alt-1-i,j)
            if cor != -1: # nao desenha celulas com -1 (transparentes)
                SetColor(cor)
                DesenhaCelula()
                SetColor(Wheat)
                DesenhaBorda()
            glTranslatef(1, 0, 0)
        glPopMatrix()
        glTranslatef(0, 1, 0)
    glPopMatrix()



# ***********************************************************************************
# Esta função deve instanciar todos os personagens do cenário
# ***********************************************************************************

def CriaInstancias(TipoPersonagem: int):
    global Personagens, nInstancias

    i = TipoPersonagem
    ang = -90.0

    if TipoPersonagem == 0:  # Jogador da MatrizExemplo0, nave
        Personagens[i].Posicao = Ponto(-2.5, 0)
        Personagens[i].Escala = Ponto(1, 1)
        Personagens[i].Rotacao = ang
        Personagens[i].IdDoModelo = 0
        Personagens[i].Modelo = DesenhaPersonagemMatricial
        Personagens[i].Pivot = Ponto(3.5, 0)
        Personagens[i].Direcao = Ponto(0, 1)
        Personagens[i].Direcao.rotacionaZ(ang)
        Personagens[i].Velocidade = 3
        Personagens[i].tipo = "jogador"  # Tipo de jogador
        Personagens[i + AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])
        nInstancias = 1  # Inicia com 1

    else:
        Personagens[i + AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])
        nInstancias += 1
        ang = random.randint(0, 90)
        if TipoPersonagem == 1:  # exemplo de tiro
            Personagens[nInstancias].Posicao = Ponto(13.5, 0)
            Personagens[nInstancias].IdDoModelo = 1
        elif TipoPersonagem == 2:
            Personagens[nInstancias].Posicao = GeraPosicaoAleatoria()
            Personagens[nInstancias].IdDoModelo = 2
        elif TipoPersonagem == 3:
            Personagens[nInstancias].Posicao = GeraPosicaoAleatoria()
            Personagens[nInstancias].IdDoModelo = 3
        elif TipoPersonagem == 4:
            
            Personagens[nInstancias].Posicao = GeraPosicaoAleatoria()
            Personagens[nInstancias].IdDoModelo = 3
        
        Personagens[nInstancias].Escala = Ponto(1, 1)
        Personagens[nInstancias].Rotacao = ang
        Personagens[nInstancias].Modelo = DesenhaPersonagemMatricial
        Personagens[nInstancias].Pivot = Ponto(3.5, 0)
        Personagens[nInstancias].Direcao = Ponto(0, 1)
        Personagens[nInstancias].Direcao.rotacionaZ(ang)
        Personagens[nInstancias].Velocidade = 3
        Personagens[nInstancias].tipo = "inimigo"
        Personagens[nInstancias + AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])
        nInstancias += 1
    



# ***********************************************************************************
def init():
    global Min, Max
    global TempoInicial, LarguraDoUniverso
    # Define a cor do fundo da tela
    glClearColor(0,0,0,0)
    
    clear() # limpa o console
    CarregaModelos()
    
    LarguraDoUniverso = 40
    Min = Ponto(-LarguraDoUniverso,-LarguraDoUniverso)
    Max = Ponto(LarguraDoUniverso,LarguraDoUniverso)

    TempoInicial = time.time()
    #print("Inicio: ", datetime.now())
    #print("TempoInicial", TempoInicial)
    CriaInstancias(0)
    
    

def criacaoDeInimigos():
    global TempoInicial
    tempo_decorrido = time.time() - TempoInicial
    
    if tempo_decorrido >= random.randint(3,7):
        nroInimigo=random.randrange(2,4)
        CriaInstancias(nroInimigo)
        
        #reseta 
        TempoInicial = time.time()
def animate():
    global angulo
    angulo = angulo + 1
    glutPostRedisplay()



def pode_atirar():
    global tiros_disparados, tempo_inicio

    agora = time.time()

    # se passou reseta o contador
    if agora - tempo_inicio > intervalo:
        tiros_disparados = 0
        tempo_inicio = agora

    # Se ainda pode atirar
    if tiros_disparados < limite_tiros:
        tiros_disparados += 1
        return True
    else:
        return False
    

def CriaTiro2(nAtirador: int):
    if not pode_atirar():
        #print("Limite de tiros atingido. Aguarde 2 segundos")
        return
    
    global nInstancias, Personagens, Modelos, AREA_DE_BACKUP, DesenhaPersonagemMatricial
    
    i = nInstancias
    Atirador = Personagens[nAtirador]
    ang = Atirador.Rotacao

    Personagens[i].Escala = Ponto(1, 1)
    Personagens[i].Rotacao = ang
    Personagens[i].IdDoModelo = 1  
    Personagens[i].Modelo = DesenhaPersonagemMatricial
    Personagens[i].Pivot = Ponto(0.5, 0)
    Personagens[i].Direcao = Ponto(0, 1)
    Personagens[i].Direcao.rotacionaZ(ang)

    envelope = Atirador.Envelope
    direcao = Personagens[i].Direcao
    pos_base = Atirador.Posicao

    # Encontra os dois pontos mais na frente do envelope na direção do disparo
    frente = sorted(envelope, key=lambda p: (p - pos_base).x * direcao.x + (p - pos_base).y * direcao.y, reverse=True)[:2]
    centro_frente = (frente[0] + frente[1]) * 0.5

    # Posiciona o tiro um pouco na frente da ponta do atirador
    Personagens[i].Posicao = centro_frente + direcao * 0.3 - Personagens[i].Pivot

    Personagens[i].Velocidade = 5

    # marca como tiro e define quem atirou
    Personagens[i].tipo = "tiro"
    Personagens[i].atirador = nAtirador

    # backup
    Personagens[i + AREA_DE_BACKUP] = copy.deepcopy(Personagens[i])

    nInstancias += 1

def inimigosAtiram():
    global proximo_tiro_inimigo, intervalo_tiro_inimigo, nInstancias

    tempo_atual = time.time()
    if tempo_atual < proximo_tiro_inimigo:
        return

   
    for i in range(1, nInstancias):
        if getattr(Personagens[i], "tipo", None) == "inimigo":
            CriaTiro2(i)  # Inimigo atira

    # Define o próximo tempo de disparo
    proximo_tiro_inimigo = tempo_atual + intervalo_tiro_inimigo


def VerificaColisaoComLimites(personagem):
    global Min, Max
    bateu = False

    # Checa colisão horizontal
    if personagem.Posicao.x < Min.x or personagem.Posicao.x > Max.x:
        personagem.Direcao.x *= -1
        personagem.Posicao.x = max(Min.x, min(personagem.Posicao.x, Max.x))
        bateu = True

    # Checa colisão vertical
    if personagem.Posicao.y < Min.y or personagem.Posicao.y > Max.y:
        personagem.Direcao.y *= -1
        personagem.Posicao.y = max(Min.y, min(personagem.Posicao.y, Max.y))
        bateu = True

    # Atualiza a rotação do gráfico se houve colisão
    if bateu:

        angulo = math.degrees(math.atan2(personagem.Direcao.y, personagem.Direcao.x))
        personagem.Rotacao = angulo - 90



# ***********************************************************************************
# Programa Principal
# ***********************************************************************************

glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGBA)
# Define o tamanho inicial da janela grafica do programa
glutInitWindowSize(500, 500)
glutInitWindowPosition(100, 100)
wind = glutCreateWindow(b"Exemplo de Criacao de Instancias")
glutDisplayFunc(display)
glutIdleFunc(animate)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutSpecialFunc(arrow_keys)
glutMouseFunc(mouse)
init()

try:
    glutMainLoop()
except SystemExit:
    pass
