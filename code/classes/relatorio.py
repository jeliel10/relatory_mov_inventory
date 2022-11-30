from calendar import isleap

import firebirdsql
from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar, DateEntry
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Image
import webbrowser  # Importação para chamar o navegador.

window_sped = Tk()

class Functions():
    def limpar_tela(self):
        self.entry_codigo.delete(0, END)
        self.entry_ano.delete(0, END)
        self.entry_mes.delete(0, END)
        self.entry_dia.delete(0, END)
        self.entry_client.delete(0, END)
        self.entry_sistema.delete(0, END)
        self.entry_observacao.delete(0, END)

    def conectar_bd(self):
        # self.conn = sqlite3.connect("armazenamento_speds.bd")
        # self.cursor = self.conn.cursor()

        self.conn = firebirdsql.connect(
            host='localhost',
            database='C:\\APS\\GenixGer\\Server\\Database\\UNIQUE.FDB',
            port=3050,
            user='SYSDBA',
            password='masterkey'
        )
        self.cur = self.conn.cursor()
        print("Conectado ao Banco de Dados")

    def desconecta_bd(self):
        self.conn.close()

    def select_bd(self):
        self.list.delete(*self.list.get_children())
        self.conectar_bd()
        lista = self.cur.execute("""
                            SELECT DESCCONTA 
                            FROM BANCOCONTA 
                            ORDER BY DESCCONTA ASC;
                            """)
        for i in lista:
            self.list.insert("", END, values= i)
        self.desconecta_bd()

    def OnDoubleClick(self, event):
        self.limpar_tela()
        self.list.selection()

    def search_sped(self):
        self.conectar_bd()
        self.list.delete(*self.list.get_children())
        self.lista_anterior = []
        self.lista = []
        self.lista1 = []
        self.lista_new = []
        self.contas = []
        self.lista_melhorada = []


        self.data_inicial = datetime.strptime(self.entry_data_inicial.get(), '%d/%m/%Y')
        self.data_final = datetime.strptime(self.entry_data_final.get(), '%d/%m/%Y')

        """ ----------- MONTAGEM DO SALDO ANTERIOR ----------"""
        mes_anterior = self.data_final.month - 1
        ano_anterior = self.data_inicial.year

        if mes_anterior == 0:
            mes_anterior = 12
            ano_anterior -= 1

        self.data_inicial_anterior = self.data_inicial.replace(day= self.data_inicial.day, month= mes_anterior, year= ano_anterior)
        self.data_final_anterior = self.data_final

        dia_fev = 0
        if isleap(self.data_inicial.year):
            dia_fev = 29
        else:
            dia_fev = 28

        if mes_anterior == 2:
            self.data_final_anterior = self.data_final_anterior.replace(day= dia_fev, month=mes_anterior, year= ano_anterior)
        elif mes_anterior == 4 or 6 or 9 or 11:
            self.data_final_anterior = self.data_final_anterior.replace(day= 30, month= mes_anterior, year= ano_anterior)
        elif mes_anterior == 1 or 3 or 5 or 7 or 8 or 10 or 12:
            self.data_final_anterior = self.data_final_anterior.replace(day= 31, month= mes_anterior, year= ano_anterior)

        self.data_inicial_anterior = self.data_inicial_anterior.replace(day= self.data_inicial.day, month= 1, year= 2015)

        self.cur.execute("""
                        select BANCOCONTA.descconta, SUM(BANCOCONTAMOV.valor)
                            from BANCOCONTAMOV
                            inner join BANCOCONTA ON BANCOCONTA.idbancoconta = BANCOCONTAMOV.idbancoconta_fk
                            where BANCOCONTAMOV.tipomov = 0 AND BANCOCONTAMOV.datamov BETWEEN ? and ?
                            group by descconta
                        """, (self.data_inicial_anterior, self.data_final_anterior))
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
        #print(lista_anterior_3)

        soma_lista_anterior = 0
        for i in lista_anterior_3:
            soma_lista_anterior += i

        #print(soma_lista_anterior)
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
            for j in range(0,2):
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
        lista2 = []
        for i in searchTar2:
            lista2.append(i[1])

        'CONTA CAIXA - CEF'
        'CONTA INTERNA (CAIXA)'
        'CONTA SICRED'

        if len(lista2) < 3:


        for i in range(0, len(self.lista)):
            self.lista[i].append(lista2[i])

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
           self.list.insert("", END, values= i)
        # #self.limpar_tela()
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

        lista_cabecalho = ['Período:', 'Nome conta', 'Saldo Anterior','Crédito', 'Débito', 'Saldo Atual']
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
                        #self.c.drawString(pos_linha, pos_altura, self.lista_final[i][j].rjust(-5))
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

        self.c.showPage()
        self.c.save()
        self.printRelatorio()

class Speds(Relatorios, Functions):

    cor_de_fundo = "LightSteelBlue"
    cor_dentro_frame = "LightSteelBlue"
    cor_bordas_frame = "Black"
    cor_texto_titulo = "Black"
    cor_botoes = "Silver"
    img = PhotoImage(file= "C:\\APS\\Util\\Meus Estudos\\PYTHON\\Relatorio Movimentacao Estoque\\code\\imagens\\FUNDO3.png")
    Label(window_sped, image= img).pack()

    def __init__(self):
        self.window_sped = window_sped
        self.home()
        self.frames_home()
        self.create_labels()
        self.create_buttons()
        self.list_frame()
        self.select_bd()
        self.window_sped.mainloop()

    def home(self):
        self.window_sped.title("Relatório de Saldo de Contas")
        self.window_sped.geometry("742x353")
        # self.window_sped.configure(background= self.cor_de_fundo)
        self.window_sped.resizable(True, True)

    def frames_home(self):
        # self.frame_1 = Frame(self.window_sped,
        #                      bd= 4,
        #                      bg= self.cor_dentro_frame,
        #                      highlightbackground= self.cor_bordas_frame,
        #                      highlightthickness= 5)
        # self.frame_1.place(rely=0.01, relx=0.01, relwidth=0.98, relheight=0.15)

        self.frame_2 = Frame(self.window_sped,
                             bd= 4,
                             bg= self.cor_dentro_frame,
                             highlightbackground= self.cor_bordas_frame,
                             highlightthickness= 1)
        self.frame_2.place(rely= 0.01, relx= 0.01, relwidth= 0.98, relheight= 0.28)

        # self.frame_3 = Frame(self.window_sped,
        #                      bd= 4,
        #                      bg= self.cor_dentro_frame,
        #                      highlightbackground= self.cor_bordas_frame,
        #                      highlightthickness= 5)
        # self.frame_3.place(rely= 0.42, relx= 0.01, relwidth= 0.98, relheight= 0.35)

    def create_labels(self):
        self.lb_title = Label(self.frame_2, text= "RELATÓRIO DE SALDO DE CONTAS", font= "-weight bold -size 20", bg= self.cor_dentro_frame, fg= self.cor_texto_titulo)
        self.lb_title.place(rely= 0.01, relx= 0.12, relwidth= 0.8)

        self.lb_data_inicial = Label(self.frame_2, text= "Data Inicial:", font= 20, bg= self.cor_botoes)
        self.lb_data_inicial.place(rely= 0.53, relx= 0.01, relwidth= 0.12)

        self.entry_data_inicial = Entry(self.frame_2)
        self.entry_data_inicial.place(rely= 0.53, relx= 0.135, relwidth= 0.12)

        self.lb_data_final = Label(self.frame_2, text= "Data Final:", font= 20, bg= self.cor_botoes)
        self.lb_data_final.place(rely= 0.53, relx= 0.28, relwidth= 0.12)

        self.entry_data_final = Entry(self.frame_2)
        self.entry_data_final.place(rely= 0.53, relx= 0.407, relwidth= 0.12)

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

        dt_inicial = '{}/{}/{}'.format(1, mes_now, ano_now)

        self.entry_data_inicial.insert(0, dt_inicial)
        self.entry_data_final.insert(0, dt_final)

    def create_buttons(self):
        # self.bt_buscar = Button(self.frame_2, text= "Buscar", background= self.cor_botoes, bd= 5, command= self.search_sped)
        # self.bt_buscar.place(rely= 0.01, relx= 0.3, relwidth= 0.1)

        self.bt_relat = Button(self.frame_2, text= "Imprimir", background= self.cor_botoes, bd= 5, command= self.geraRelatCliente)
        self.bt_relat.place(rely= 0.53, relx= 0.6, relwidth= 0.1)

        self.bt_quit = Button(self.frame_2, text= "Sair", background= self.cor_botoes, bd= 5, command= self.window_sped.destroy)
        self.bt_quit.place(rely= 0.53, relx= 0.75, relwidth= 0.1)

    def list_frame(self):
        self.list = ttk.Treeview(self.frame_2, height= 3, columns= ("col1", "col2", "col3", "col4", "col5", "col6"))

        self.list.heading("#0", text= "")
        self.list.heading("#1", text= "Conta Banco")
        self.list.heading("#2", text= "Periodo")
        self.list.heading("#3", text=" Saldo Anterior")
        self.list.heading("#4", text= "Credito")
        self.list.heading("#5", text= "Debito")
        self.list.heading("#6", text= "Saldo Atual")
        # self.list.heading("#7", text= "Observação")

        self.list.column("#0", width= 1)
        self.list.column("#1", width= 100)
        self.list.column("#2", width= 150)
        self.list.column("#3", width= 100)
        self.list.column("#4", width= 100)
        self.list.column("#5", width= 100)
        self.list.column("#6", width= 100)
        # self.list.column("#7", width= 500)

        #self.list.place(rely= 0.01, relx= 0.01, relwidth= 0.96, relheight= 0.98)

        #self.scrollList = Scrollbar(self.frame_3, orient= "vertical")
        #self.list.configure(yscroll= self.scrollList.set)
        #self.scrollList.place(relx= 0.97, rely= 0.01, relwidth= 0.02, relheight= 0.98)
        #self.list.bind("<Double-1>", self.OnDoubleClick)
Speds()
