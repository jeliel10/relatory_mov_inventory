import webbrowser  # Importação para chamar o navegador.
from calendar import isleap
from datetime import datetime, date
from tkinter import *
from tkinter import ttk, messagebox
from tkinter.ttk import Combobox
import firebirdsql
from reportlab.pdfgen import canvas

window_sped = Tk()

class Functions():

    caminho_banco = 'C:\\APS\\GenixGer\\Server\\Database\\UNIQUE.FDB'
    host = 'localhost'
    porta = 3050
    def conectar_bd(self):

        print("Iniciando conexão")
        self.conn = firebirdsql.connect(
            host= self.host,
            database= self.caminho_banco,
            port= self.porta,
            user='SYSDBA',
            password='masterkey'
        )
        self.cur = self.conn.cursor()
        print("Conectado ao Banco de Dados")
        print(self.caminho_banco)

    """Função que vai alterar o caminho do banco com o que foi colocado na tela de config."""
    def alterar_bd(self):

        self.caminho_banco = self.entry_caminho_banco.get()
        self.host = self.entry_host.get()
        self.porta = self.entry_porta.get()
        self.conectar_bd()

        print(self.host)
        print(self.porta)

    def desconecta_bd(self):
        self.conn.close()


    def search_sped(self):
        self.conectar_bd()
        self.list.delete(*self.list.get_children())
        self.lista_anterior = []
        self.lista = []
        self.lista1 = []
        self.lista_new = []
        self.contas = []
        self.lista_melhorada = []


        try:
            self.data_inicial = datetime.strptime(self.entry_data_inicial.get(), '%d/%m/%Y')
            self.data_final = datetime.strptime(self.entry_data_final.get(), '%d/%m/%Y')
        except:
            messagebox.showinfo("Relatorio de Saldo de Contas.", "Sem movimentações nesse periodo")

        """ ----------- MONTAGEM DO SALDO ANTERIOR ---------- """
        mes_anterior = self.data_final.month - 1
        ano_anterior = self.data_inicial.year

        if mes_anterior == 0:
            mes_anterior = 12
            ano_anterior -= 1


        self.data_inicial_anterior = self.data_inicial.replace(day=self.data_inicial.day, month=mes_anterior,
                                                               year=ano_anterior)
        self.data_final_anterior = self.data_final


        dia_fev = 0
        if isleap(self.data_inicial.year):
            dia_fev = 29
        else:
            dia_fev = 28

        if mes_anterior == 1:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 2:
            self.data_final_anterior = self.data_final_anterior.replace(day=dia_fev, month=mes_anterior,
                                                                        year=ano_anterior)
        elif mes_anterior == 3:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 4:
            self.data_final_anterior = self.data_final_anterior.replace(day=30, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 5:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 6:
            self.data_final_anterior = self.data_final_anterior.replace(day=30, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 7:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 8:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 9:
            self.data_final_anterior = self.data_final_anterior.replace(day=30, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 10:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)
        elif mes_anterior == 11:
            self.data_final_anterior = self.data_final_anterior.replace(day=30, month=mes_anterior, year=ano_anterior)
        else:
            self.data_final_anterior = self.data_final_anterior.replace(day=31, month=mes_anterior, year=ano_anterior)

        self.data_inicial_anterior = self.data_inicial_anterior.replace(day=self.data_inicial.day, month=1, year=2015)

        self.cur.execute("""
                        select BANCOCONTA.descconta, SUM(BANCOCONTAMOV.valor)
                            from BANCOCONTAMOV
                            inner join BANCOCONTA ON BANCOCONTA.idbancoconta = BANCOCONTAMOV.idbancoconta_fk
                            where BANCOCONTAMOV.tipomov = 0 AND BANCOCONTAMOV.datamov BETWEEN ? and ?
                            group by descconta
                        """, (self.data_inicial_anterior, self.data_final_anterior))

        print("Data inicial: ", end="")
        print(self.data_inicial_anterior)

        print("Data Final: ", end="")
        print(self.data_final_anterior)

        searchTar3 = self.cur.fetchall()
        for i in searchTar3:
            lista_anterior_2 = []
            for j in range(0, 2):
                lista_anterior_2.append(i[j])
            self.lista_anterior.append(lista_anterior_2)

        self.cur.execute("""
                        select BANCOCONTA.descconta, SUM(BANCOCONTAMOV.valor)
                            from BANCOCONTAMOV
                            inner join BANCOCONTA ON BANCOCONTA.idbancoconta = BANCOCONTAMOV.idbancoconta_fk
                            where BANCOCONTAMOV.tipomov = 1 AND BANCOCONTAMOV.datamov BETWEEN ? and ?
                            group by descconta
                        """, (self.data_inicial_anterior, self.data_final_anterior))

        searchTar4 = self.cur.fetchall()
        lista_anterior_2 = []
        for i in searchTar4:
            lista_anterior_2.append(i[1])

        for i in range(0, len(self.lista_anterior)):
            self.lista_anterior[i].append(lista_anterior_2[i])

        lista_anterior_3 = []
        for i in self.lista_anterior:
            lista_anterior_3.append(i[1] - i[2])

        # print("Saldo Anterior", end=" ")
        # print(lista_anterior_3)

        soma_lista_anterior = 0
        for i in lista_anterior_3:
            soma_lista_anterior += i

        """ ----------- MONTAGEM DO SALDO ATUAL ----------"""
        self.cur.execute("""
                        select BANCOCONTA.descconta, SUM(BANCOCONTAMOV.valor)
                                 from BANCOCONTAMOV
                                inner join BANCOCONTA ON BANCOCONTA.idbancoconta = BANCOCONTAMOV.idbancoconta_fk
                                where BANCOCONTAMOV.tipomov = 0 AND BANCOCONTAMOV.datamov BETWEEN ? and ?
                               group by descconta
                        """, (self.data_inicial, self.data_final))
        searchTar = self.cur.fetchall()
        for i in searchTar:
            lista2 = []
            for j in range(0, 2):
                lista2.append(i[j])
            self.lista.append(lista2)

        self.cur.execute("""
                                select BANCOCONTA.descconta, SUM(BANCOCONTAMOV.valor)
                                         from BANCOCONTAMOV
                                        inner join BANCOCONTA ON BANCOCONTA.idbancoconta = BANCOCONTAMOV.idbancoconta_fk
                                        where BANCOCONTAMOV.tipomov = 1 AND BANCOCONTAMOV.datamov BETWEEN ? and ?
                                       group by descconta
                                """, (self.data_inicial, self.data_final))

        searchTar2 = self.cur.fetchall()

        for i in searchTar2:
            print(i)
        # lista2 = []
        # for i in searchTar2:
        #     lista2.append(i[1])

        bancos = ['CONTA CAIXA - CEF', 'CONTA INTERNA', 'CONTA SICRED']

        lista_teste = []

        for i in bancos:
            lista_teste.append([i, 0])

        print("LISTA TESTE: ", end= "")
        print(lista_teste)

        for i in lista_teste:
            for j in range(0, len(searchTar2)):
                if i[0] == searchTar2[j][0]:
                    i[1] = searchTar2[j][1]

        print("LISTA TESTE APÓS MUDANÇAS: ", end="")
        print(lista_teste)

        lista2 = []
        for i in lista_teste:
            lista2.append(i[1])

        # print("Searchtar2: ", end="")
        # print(searchTar2)
        #
        # print("Lista2: ", end="")
        # print(lista2)

        for i in range(0, len(self.lista)):
            self.lista[i].append(lista2[i])

        # print("Lista: ",end="")
        # print(self.lista)

        for i in range(0, len(self.lista)):
            self.lista[i].insert(1, lista_anterior_3[i])

        # print(self.lista)

        lista3 = []
        for i in self.lista:
            lista3.append((i[1] + i[2]) - i[3])

        for i in range(0, len(self.lista)):
            self.lista[i].append(f'R$ {lista3[i]:,.2f}')

        # print(self.lista)

        contas = []
        contas.append("VALOR TOTAL DAS MOVIMENTAÇÕES")
        periodo = " {} à {}".format(self.data_inicial.strftime('%d/%m/%Y'),
                                    self.data_final.strftime('%d/%m/%Y'))
        contas.append(periodo)
        contas.append(f'R$ {soma_lista_anterior:,.2f}')

        valor_total = 0
        for i in lista3:
            valor_total += i
        contas.append(f'R$ {valor_total:,.2f}')

        self.lista_new.append(contas)

        # print(self.lista_new)

        aux = []
        for i in self.lista:
            for j in range(0, len(i)):
                if j == 0 or j == 4:
                    aux.append(i[j])
                if j == 1:
                    aux.append(" ")
                    aux.append(f'R$ {i[j]:,.2f}')
                if j != 0 and j != 4 and j != 1:
                    aux.append(f'R$ {i[j]:,.2f}')

            self.lista_melhorada.append(aux)
            aux = []
        self.lista_melhorada.append(contas)
        self.lista_final = []
        for i in self.lista_melhorada:
            lista_melhorada2 = []
            for j in range(0, len(i)):
                lista_melhorada2.append(i[j])
            self.lista_final.append(lista_melhorada2)

        # print(self.lista_final)

        self.conta = 0
        self.credito = 0
        self.debito = 0
        self.saldo_atual = 0
        self.saldo_anterior = 0

        for i in self.lista_final:
            for j in range(0, len(i)):
                if j == 0:
                    self.conta = i[j]
                if j == 1:
                    self.credito = i[j]
                if j == 2:
                    self.debito = i[j]
                if j == 3:
                    self.saldo_atual = i[j]
                if j == 4:
                    self.saldo_anterior = i[j]

        for i in self.lista_final:
            for j in range(0, len(i)):
                i[j] = i[j].replace(',', '_')

        for i in self.lista_final:
            for j in range(0, len(i)):
                i[j] = i[j].replace('.', ',')

        for i in self.lista_final:
            for j in range(0, len(i)):
                i[j] = i[j].replace('_', '.')

        # print(self.lista_final)

        for i in self.lista_final:
            self.list.insert("", END, values=i)
        self.desconecta_bd()


class Relatorios(Functions):
    def printRelatorio(self):
        webbrowser.open("Relatorio.pdf")

    def geraRelatCliente(self):

        self.search_sped()

        self.c = canvas.Canvas("Relatorio.pdf")

        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(210, 790, 'SALDO DE CONTAS')

        self.c.setFont("Helvetica-Bold", 10)
        # self.c.drawString(150, 700, self.lista_rel)

        lista_cabecalho = ['Período:', 'Nome conta', 'Saldo Anterior', 'Crédito', 'Débito', 'Saldo Atual']
        lista_cabecalho2 = ['Total']

        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')

        lista_cabecalho3 = ['Impresso:', data_e_hora_em_texto]

        pos_linha = 460
        pos_altura = 760
        for i in range(0, len(lista_cabecalho3)):
            self.c.setFont("Helvetica", 7)
            self.c.drawString(pos_linha, pos_altura, lista_cabecalho3[i])
            pos_linha += 35

        self.c.setFont("Helvetica-Bold", 10)

        pos_altura = 760
        pos_linha = 35
        for i in range(0, len(lista_cabecalho)):

            self.c.rect(40, 745, 520, 0.5, fill=True, stroke=False)
            self.c.rect(40, 725, 520, 0.5, fill=True, stroke=False)
            self.c.rect(40, 660, 520, 0.5, fill=True, stroke=False)

            if i == 0:
                pos_linha = 210
                self.c.drawString(pos_linha, pos_altura, lista_cabecalho[i])
                pos_altura -= 30
            if i == 1:
                pos_linha = 50
                self.c.drawString(pos_linha, pos_altura, lista_cabecalho[i])
            if i == 2:
                pos_linha += 215
                self.c.drawRightString(pos_linha, pos_altura, lista_cabecalho[i])
            if i == 3:
                pos_linha += 95
                self.c.drawRightString(pos_linha, pos_altura, lista_cabecalho[i])
            if i == 4:
                pos_linha += 95
                self.c.drawRightString(pos_linha, pos_altura, lista_cabecalho[i])
            if i == 5:
                pos_linha += 95
                self.c.drawRightString(pos_linha, pos_altura, lista_cabecalho[i])

        # f"{self.lista_final[i][j] : >20}"
        self.c.setFont("Helvetica", 10)
        pos_altura = 705
        for i in range(0, len(self.lista_final)):
            pos_linha = 50
            if i != 3:
                for j in range(0, len(self.lista_final[i])):
                    if j == 0:
                        self.c.drawString(pos_linha, pos_altura, self.lista_final[i][j])
                    if j == 2:
                        pos_linha += 215
                        # self.lista_final[i][j] = self.lista_final[i][j].replace('.', ',')
                        # self.c.drawString(pos_linha, pos_altura, self.lista_final[i][j].rjust(-5))
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])
                    if j == 3:
                        pos_linha += 95
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])
                    if j == 4:
                        pos_linha += 95
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])
                    if j == 5:
                        pos_linha += 95
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])
                pos_altura -= 20
            if i == 3:

                for j in range(0, len(self.lista_final[i])):
                    if j == 0:
                        self.c.setFont("Helvetica-Bold", 12)
                        pos_altura = 645
                        pos_linha = 50
                        self.c.drawString(pos_linha, pos_altura, lista_cabecalho2[0])

                    if j == 1:
                        self.c.setFont("Helvetica", 10)
                        pos_altura = 760
                        pos_linha = 250
                        self.c.drawString(pos_linha, pos_altura, self.lista_final[i][j])

                    if j == 2:
                        self.c.setFont("Helvetica-Bold", 10)
                        pos_altura = 645
                        pos_linha = 265
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])
                    if j == 3:
                        pos_altura = 645
                        pos_linha += 285
                        self.c.drawRightString(pos_linha, pos_altura, self.lista_final[i][j])

        if len(self.lista_final) == 1:
            messagebox.showinfo("Relatorio de Saldo de Contas.", "Sem movimentações nesse periodo")
        else:
            self.c.showPage()
            self.c.save()
            self.printRelatorio()


class Speds(Relatorios, Functions):
    cor_de_fundo = "LightSteelBlue"
    cor_dentro_frame = "LightSteelBlue"
    cor_bordas_frame = "Black"
    cor_texto_titulo = "Black"
    cor_botoes = "Silver"
    img = PhotoImage(
       file="C:\\APS\\GenixGer\\Client\\fundoHome.png")
    Label(window_sped, image=img).pack()

    img2 = PhotoImage(
        file="C:\\APS\\GenixGer\\Client\\FUNDO3.png")

    img3 = PhotoImage(file= "C:\\APS\\GenixGer\\Client\\fundoConfig.png")

    def center(self, page):
        """ FUNÇÃO RESPONSAVEL POR CENTRALIZAR AS PAGES NA TELA"""

        page.withdraw()
        page.update_idletasks()  # Update "requested size" from geometry manager

        x = (page.winfo_screenwidth() - page.winfo_reqwidth()) / 2
        y = (page.winfo_screenheight() - page.winfo_reqheight()) / 2
        page.geometry("+%d+%d" % (x, y))

        # This seems to draw the window frame immediately, so only call deiconify()
        # after setting correct window position
        page.deiconify()

    def __init__(self):
        self.window_sped = window_sped
        self.homePage()

        self.center(self.window_sped)

        self.window_sped.mainloop()

    def home(self):
        self.home = Toplevel(self.window_sped)

        self.home.title("Relatório de Saldo de Contas " + (" " * 50) + "Fênix Tecnologia")
        self.home.geometry("350x350")
        self.home.configure(background= self.cor_de_fundo)
        self.home.resizable(True, True)

        Label(self.home, image= self.img2).pack()
        self.frames_home()
        self.create_labels()
        self.create_buttons()
        self.list_frame()
        self.center(self.home)
        self.home.mainloop()


    def acessarHome(self):
        self.conectar_bd()

        self.login = self.entry_login.get()
        self.senha = self.entry_senha.get()

        self.cur.execute("""
                        select usu.usu_login, usu.usu_senha
                        from usuarios usu
                        """)

        list_acesso = []

        usuarios = self.cur.fetchall()
        for i in usuarios:
            list_acesso.append([i[0], i[1]])

        erro = False
        for i in list_acesso:
            if self.login == i[0] and self.senha == i[1]:
                print(i)
                print("Logado")
                erro = False
                self.home()
                break
            else:
                erro = True
        if erro == True:
            messagebox.showinfo("Relatorio de Saldo de Contas.", "ACESSO NEGADO! Tente Novamente")
        self.desconecta_bd()


    def homePage(self):
        self.window_sped.title("Relatório de Saldo de Contas " + (" " * 50) + "Fênix Tecnologia")
        self.window_sped.geometry("250x250")
        self.window_sped.resizable(True, True)

        self.frame_4 = Frame(self.window_sped,
                             bd= 4,
                             bg= self.cor_dentro_frame,
                             highlightbackground= self.cor_bordas_frame,
                             highlightthickness= 1)
        self.frame_4.place(rely= 0.1, relx= 0.05, relwidth= 0.9, relheight= 0.65)


        self.lb_login = Label(self.frame_4, text= "Login", font= 15, bg= self.cor_botoes)
        self.lb_login.place(rely= 0.1, relx=0.01, relwidth= 0.25)

        self.entry_login = Combobox(window_sped, values= ['CHICO', 'IVANIRA', 'VITOR'])
        self.entry_login.place(rely= 0.2, relx= 0.33, relwidth= 0.35)


        self.lb_senha = Label(self.frame_4, text= "Senha", font= 15, bg= self.cor_botoes)
        self.lb_senha.place(rely= 0.3, relx= 0.01, relwidth= 0.25)

        self.entry_senha = Entry(self.frame_4, show= "*")
        self.entry_senha.place(rely= 0.3, relx= 0.3, relwidth= 0.4, relheight= 0.13)

        self.bt_entrar = Button(self.frame_4, text="Entrar", background=self.cor_botoes, bd=5, command= self.acessarHome)
        self.bt_entrar.place(rely=0.55, relx=0.33, relwidth=0.3)

    def openNewWindow(self):
        self.new_window = Toplevel(self.window_sped)

        self.new_window.title("Configuração")
        self.new_window.geometry("700x300")
        self.new_window.resizable(False, False)
        self.center(self.new_window)

        Label(self.new_window, image= self.img3).pack()

        self.frame_3 = Frame(self.new_window,
                             bd=4,
                             bg=self.cor_dentro_frame,
                             highlightbackground=self.cor_bordas_frame,
                             highlightthickness=1)
        self.frame_3.place(rely=0.01, relx=0.01, relwidth=0.98, relheight=0.7)


        self.lb_caminho_banco = Label(self.frame_3, text="Caminho Banco", font=20, bg=self.cor_botoes)
        self.lb_caminho_banco.place(rely=0.1, relx=0.01, relwidth=0.18)

        self.entry_caminho_banco = Entry(self.frame_3)
        self.entry_caminho_banco.place(rely=0.1, relx=0.2, relwidth=0.48)


        self.lb_host = Label(self.frame_3, text= "Host", font= 20, bg= self.cor_botoes)
        self.lb_host.place(rely= 0.3, relx= 0.01, relwidth= 0.18)

        self.entry_host = Entry(self.frame_3)
        self.entry_host.place(rely= 0.3, relx= 0.2, relwidth= 0.2)


        self.lb_porta = Label(self.frame_3, text= "Porta", font= 20, bg= self.cor_botoes)
        self.lb_porta.place(rely= 0.5, relx= 0.01, relwidth= 0.18)

        self.entry_porta = Entry(self.frame_3)
        self.entry_porta.place(rely= 0.5, relx= 0.2, relwidth= 0.2)

        self.bt_relat = Button(self.frame_3, text="Alterar banco", background=self.cor_botoes, bd=5, command= self.alterar_bd)
        self.bt_relat.place(rely=0.7, relx=0.75, relwidth=0.15)


        self.entry_caminho_banco.insert(0, self.caminho_banco)
        self.entry_host.insert(0, self.host)
        self.entry_porta.insert(0, self.porta)


        print(self.entry_host)
        print(self.entry_porta)

    def frames_home(self):

        self.frame_2 = Frame(self.home,
                            bd=4,
                            bg= self.cor_dentro_frame,
                            highlightbackground= self.cor_bordas_frame,
                            highlightthickness=1)
        self.frame_2.place(rely=0.01, relx=0.01, relwidth=0.98, relheight=0.2)

        self.frame_3 = Frame(self.home,
                                   bd= 4,
                                   bg= self.cor_dentro_frame,
                                   highlightbackground= self.cor_bordas_frame,
                                   highlightthickness= 1)
        self.frame_3.place(rely= 0.25, relx= 0.01, relwidth= 0.98, relheight= 0.5)
        # Label(self.frame_3, image= self.img).pack()

    def format_data_inicial(self, event=None):

        """ ESSE CÓDIGO É RESPONSAVEL POR COLOCAR OS PONTOS E O TRAÇO DE UM CPF AUTOMATICAMENTE
        EU PRECISO ALTERAR NELE PARA COLOCAR SOMENTE AS BARRAS DAS DATAS.
        LINK DO STACKOVERFLOW: https://pt.stackoverflow.com/questions/492705/criando-um-entry-formatado-para-cpf-em-python-tkinter
        """

        text = self.entry_data_inicial.get().replace("/", "")[:8]
        new_text = ""

        if event.keysym.lower() == "backspace": return

        for index in range(len(text)):

            if not text[index] in "0123456789": continue
            if index in [1, 3]:
                new_text += text[index] + "/"
            # elif index == 8:
            #     new_text += text[index] + "-"
            else:
                new_text += text[index]

        self.entry_data_inicial.delete(0, "end")
        self.entry_data_inicial.insert(0, new_text)

    def format_data_final(self, event=None):

        """ ESSE CÓDIGO É RESPONSAVEL POR COLOCAR OS PONTOS E O TRAÇO DE UM CPF AUTOMATICAMENTE
        EU PRECISO ALTERAR NELE PARA COLOCAR SOMENTE AS BARRAS DAS DATAS.
        LINK DO STACKOVERFLOW: https://pt.stackoverflow.com/questions/492705/criando-um-entry-formatado-para-cpf-em-python-tkinter
        """

        text2 = self.entry_data_final.get().replace("/", "")[:8]
        new_text2= ""

        if event.keysym.lower() == "backspace": return

        for index in range(len(text2)):

            if not text2[index] in "0123456789": continue
            if index in [1, 3]:
                new_text2 += text2[index] + "/"
            else:
                new_text2 += text2[index]

        self.entry_data_final.delete(0, "end")
        self.entry_data_final.insert(0, new_text2)

    def create_labels(self):
        self.lb_title = Label(self.frame_2, text="RELATÓRIO", font="-weight bold -size 15",
                              bg=self.cor_dentro_frame, fg=self.cor_texto_titulo)
        self.lb_title.place(rely=0.01, relx=0.12, relwidth=0.8)

        self.lb_title_2 = Label(self.frame_2, text= "SALDO DE CONTAS", font= "-weight bold -size 15",
                                bg= self.cor_dentro_frame, fg= self.cor_texto_titulo)
        self.lb_title_2.place(rely=0.4, relx=0.12, relwidth=0.8)

        self.lb_data_inicial = Label(self.frame_3, text="Data Inicial:", font=90, bg=self.cor_botoes)
        self.lb_data_inicial.place(rely=0.1, relx=0.08, relwidth=0.25)

        """ CÓDIGO DA ENTRY DATA INICIAL ALTERADO JÁ PARA COLOCAR AUTOMATICAMENTE AS BARRAS.
        """
        self.entry_data_inicial = Entry(self.frame_3)
        self.entry_data_inicial.place(rely=0.1, relx=0.4, relwidth=0.23)
        self.entry_data_inicial.bind("<KeyRelease>", self.format_data_inicial)
        # self.entry_data_inicial.pack()

        self.lb_data_final = Label(self.frame_3, text="Data Final:", font=90, bg=self.cor_botoes)
        self.lb_data_final.place(rely=0.3, relx=0.08, relwidth=0.25)

        self.entry_data_final = Entry(self.frame_3)
        self.entry_data_final.place(rely=0.3, relx=0.4, relwidth=0.23)
        self.entry_data_final.bind("<KeyRelease>", self.format_data_final)

        date_now = date.today()
        mes_now = date_now.month
        ano_now = date_now.year

        dia_fev = 0
        if isleap(ano_now):
            dia_fev = 29
        else:
            dia_fev = 28

        dt_final = 0
        if mes_now == 2:
            dt_final = '{}/{}/{}'.format(dia_fev, mes_now, ano_now)
        elif mes_now == 4 or 6 or 9 or 11:
            dt_final = '{}/{}/{}'.format(30, mes_now, ano_now)
        elif mes_now == 1 or 3 or 5 or 7 or 8 or 10 or 12:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)

        if mes_now == 1:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 2:
            dt_final = '{}/{}/{}'.format(dia_fev, mes_now, ano_now)
        elif mes_now == 3:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 4:
            dt_final = '{}/{}/{}'.format(30, mes_now, ano_now)
        elif mes_now == 5:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 6:
            dt_final = '{}/{}/{}'.format(30, mes_now, ano_now)
        elif mes_now == 7:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 8:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 9:
            dt_final = '{}/{}/{}'.format(30, mes_now, ano_now)
        elif mes_now == 10:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)
        elif mes_now == 11:
            dt_final = '{}/{}/{}'.format(30, mes_now, ano_now)
        else:
            dt_final = '{}/{}/{}'.format(31, mes_now, ano_now)


        dt_inicial = '{}/{}/{}'.format('01', mes_now, ano_now)

        self.entry_data_inicial.insert(0, dt_inicial)
        self.entry_data_final.insert(0, dt_final)

    def create_buttons(self):
        # self.bt_buscar = Button(self.frame_2, text= "Buscar", background= self.cor_botoes, bd= 5, command= self.search_sped)
        # self.bt_buscar.place(rely= 0.01, relx= 0.3, relwidth= 0.1)

        self.bt_relat = Button(self.frame_3, text="Visualizar", background=self.cor_botoes, bd=5,
                               command=self.geraRelatCliente)
        self.bt_relat.place(rely=0.5, relx=0.08, relwidth=0.2)

        self.bt_quit = Button(self.frame_3, text="Sair", background=self.cor_botoes, bd=5,
                              command=self.window_sped.destroy)
        self.bt_quit.place(rely=0.5, relx=0.4, relwidth=0.12)

        self.bt_config = Button(self.frame_3, text= "Config", background= self.cor_botoes, bd= 5, command= self.openNewWindow)
        self.bt_config.place(rely= 0.5, relx= 0.8, relwidth= 0.17)

    def list_frame(self):
        self.list = ttk.Treeview(self.frame_3, height=3, columns=("col1", "col2", "col3", "col4", "col5", "col6"))

        self.list.heading("#0", text="")
        self.list.heading("#1", text="Conta Banco")
        self.list.heading("#2", text="Periodo")
        self.list.heading("#3", text=" Saldo Anterior")
        self.list.heading("#4", text="Credito")
        self.list.heading("#5", text="Debito")
        self.list.heading("#6", text="Saldo Atual")
        # self.list.heading("#7", text= "Observação")

        self.list.column("#0", width=1)
        self.list.column("#1", width=100)
        self.list.column("#2", width=150)
        self.list.column("#3", width=100)
        self.list.column("#4", width=100)
        self.list.column("#5", width=100)
        self.list.column("#6", width=100)
        # self.list.column("#7", width= 500)

        # self.list.place(rely= 0.01, relx= 0.01, relwidth= 0.96, relheight= 0.98)

        # self.scrollList = Scrollbar(self.frame_3, orient= "vertical")
        # self.list.configure(yscroll= self.scrollList.set)
        # self.scrollList.place(relx= 0.97, rely= 0.01, relwidth= 0.02, relheight= 0.98)
        # self.list.bind("<Double-1>", self.OnDoubleClick)


Speds()
