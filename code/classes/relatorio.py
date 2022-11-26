import firebirdsql
from tkinter import *
from tkinter import ttk
from datetime import datetime
from calendar import isleap

# conn = firebirdsql.connect(
#     host='localhost',
#     database='C:\\APS\\BANCOS\\GENIX\\UNIQUE-CDL-SOUSA.FDB',
#     port=3050,
#     user='SYSDBA',
#     password='masterkey'
# )
# cur = conn.cursor()
# cur.execute("select * from baz")
# for c in cur.fetchall():
#     print(c)
# conn.close()

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
            database='C:\\APS\\BANCOS\\GENIX\\UNIQUE-CDL-SOUSA.FDB',
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

        for n in self.list.selection():
            col1, col2, col3, col4, col5, col6, col7 = self.list.item(n, 'values')
            self.entry_codigo.insert(END, col1)
            self.entry_ano.insert(END, col2)
            self.entry_mes.insert(END, col3)
            self.entry_dia.insert(END, col4)
            self.entry_client.insert(END, col5)
            self.entry_sistema.insert(END, col6)
            self.entry_observacao.insert(END, col7)

    def search_sped(self):
        self.conectar_bd()
        self.list.delete(*self.list.get_children())
        lista_anterior = []
        lista = []
        lista_new = []
        contas = []
        lista_melhorada = []


        # self.entry_ano.insert(END, '%')
        # self.entry_mes.insert(END, '%')
        # self.ano = self.entry_ano.get()
        # self.mes = self.entry_mes.get()
        # self.dia = self.entry_dia.get()
        # self.conta = self.entry_contabanco.get()
        # self.inicial = self.entry_data_inicial.get()
        # self.final = self.entry_data_final.get()



        self.data_inicial = datetime.strptime(self.entry_data_inicial.get(), '%d/%m/%Y')
        self.data_final = datetime.strptime(self.entry_data_final.get(), '%d/%m/%Y')

        """ ----------- MONTAGEM DO SALDO ANTERIOR ----------"""
        # self.data_inicial_anterior = self.data_inicial.replace(month=self.data_inicial.month - 1,
        #                                               year=self.data_inicial.year)
        # self.data_final_anterior = self.data_final.replace(month=self.data_final.month - 1,
        #                                           year=self.data_final.year)

        mes_anterior = self.data_final.month - 1
        self.data_inicial_anterior = self.data_inicial.replace(day= self.data_inicial.day, month= mes_anterior, year= self.data_inicial.year)
        self.data_final_anterior = self.data_final

        dia_fev = 0
        if isleap(self.data_inicial.year):
            dia_fev = 29
        else:
            dia_fev = 28

        if mes_anterior == 2:
            self.data_final_anterior = self.data_final_anterior.replace(day= dia_fev, month=mes_anterior, year=self.data_final.year)
        elif mes_anterior == 4 or 6 or 9 or 11:
            self.data_final_anterior = self.data_final_anterior.replace(day= 30, month= mes_anterior, year= self.data_final.year)
        elif mes_anterior == 1 or 3 or 5 or 7 or 8 or 10 or 12:
            self.data_final_anterior = self.data_final_anterior.replace(day= 31, month= mes_anterior, year= self.data_final.year)


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
            lista_anterior.append(lista_anterior_2)
        print(lista_anterior)

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

        for i in range(0, len(lista_anterior)):
            lista_anterior[i].append(lista_anterior_2[i])

        lista_anterior_3 = []
        for i in lista_anterior:
            lista_anterior_3.append(i[1] - i[2])

        # print(lista_anterior)
        print(lista_anterior_3)


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
            lista.append(lista2)
        # print(lista)

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

        for i in range(0, len(lista)):
            lista[i].append(lista2[i])
        # print(lista)

        lista3 = []
        for i in lista:
            lista3.append(i[1] - i[2])

        for i in range(0, len(lista)):
            lista[i].append("R${}".format(lista3[i]))

        for i in range(0, len(lista)):
            lista[i].append(lista_anterior_3[i])

        contas = []
        contas.append("VALOR TOTAL DAS MOVIMENTAÇÕES")

        valor_total = 0
        for i in lista3:
            valor_total += i
        contas.append("R${}".format(valor_total))

        lista_new.append(contas)

        # print(lista_new)
        # print(lista)

        aux = []
        for i in lista:
            for j in range(0, len(i)):
                if j == 0 or j == 3:
                    aux.append(i[j])
                if j != 0 and j != 3:
                    aux.append("R${}".format(i[j]))

            lista_melhorada.append(aux)
            aux = []
        # lista_melhorada.append("")
        lista_melhorada.append(contas)
        # print(lista_melhorada)

        for i in lista_melhorada:
           self.list.insert("", END, values= i)
        # #self.limpar_tela()
        self.desconecta_bd()

class Speds(Functions):

    cor_de_fundo = "RoyalBlue"
    cor_dentro_frame = "SteelBlue"
    cor_bordas_frame = "LightSlateGray"
    cor_texto_titulo = "Blue"
    cor_botoes = "SlateGray"

    def __init__(self):
        self.window_sped = window_sped
        self.home()
        self.frames_home()
        self.create_labels()
        self.create_buttons()
        self.list_frame()
        # self.montaTabelas()
        self.select_bd()
        self.window_sped.mainloop()

    def home(self):
        self.window_sped.title("Relatorio Movimentação de Estoque")
        self.window_sped.geometry("1000x400")
        self.window_sped.configure(background= self.cor_de_fundo)
        self.window_sped.resizable(True, True)
        #self.window_sped.minsize(width= 1000, height= 800)

    def frames_home(self):
        self.frame_1 = Frame(self.window_sped,
                             bd= 4,
                             bg= self.cor_dentro_frame,
                             highlightbackground= self.cor_bordas_frame,
                             highlightthickness= 5)
        self.frame_1.place(rely=0.01, relx=0.01, relwidth=0.98, relheight=0.2)

        self.frame_2 = Frame(self.window_sped,
                             bd= 4,
                             bg= self.cor_dentro_frame,
                             highlightbackground= self.cor_bordas_frame,
                             highlightthickness= 5)
        self.frame_2.place(rely= 0.24, relx= 0.01, relwidth= 0.98, relheight= 0.3)

        self.frame_3 = Frame(self.window_sped,
                             bd= 4,
                             bg= self.cor_dentro_frame,
                             highlightbackground= self.cor_bordas_frame,
                             highlightthickness= 5)
        self.frame_3.place(rely= 0.58, relx= 0.01, relwidth= 0.98, relheight= 0.35)

        # self.frame_4 = Frame(self.window_sped,
        #                      bd= 4,
        #                      bg= self.cor_dentro_frame,
        #                      highlightbackground= self.cor_bordas_frame,
        #                      highlightthickness= 5)
        # self.frame_4.place(rely= 0.5, relx= 0.01, relwidth= 0.37, relheight= 0.1)

    def create_labels(self):
        self.lb_title = Label(self.frame_1, text= "RELATORIO MOVIMENTAÇÃO DE ESTOQUE", font= "-weight bold -size 20", bg= self.cor_dentro_frame, fg= self.cor_texto_titulo)
        self.lb_title.place(rely= 0.01, relx= 0.2, relwidth= 0.6)

        # self.lb_contabanco = Label(self.frame_2, text= "Conta Banco", font= 15)
        # self.lb_contabanco.place(rely= 0.01, relx= 0.01, relwidth= 0.1)
        #
        # self.entry_contabanco = Entry(self.frame_2)
        # self.entry_contabanco.place(rely= 0.2, relx= 0.01, relwidth= 0.065)

        self.lb_data_inicial = Label(self.frame_2, text= "Data Inicial", font= 20)
        self.lb_data_inicial.place(rely= 0.01, relx= 0.01, relwidth= 0.12)

        self.entry_data_inicial = Entry(self.frame_2)
        self.entry_data_inicial.place(rely= 0.27, relx= 0.01, relwidth= 0.12)

        self.lb_data_final = Label(self.frame_2, text= "Data Final", font= 20)
        self.lb_data_final.place(rely= 0.01, relx= 0.15, relwidth= 0.12)

        self.entry_data_final = Entry(self.frame_2)
        self.entry_data_final.place(rely= 0.27, relx= 0.15, relwidth= 0.12)

    def create_buttons(self):
        # self.bt_cadastrar = Button(self.frame_2, text= "Cadastrar", background= self.cor_botoes, bd= 5, command= self.adicionarSped)
        # self.bt_cadastrar.place(rely= 0.45, relx= 0.35, relwidth= 0.045)
        #
        # self.bt_alterar = Button(self.frame_2, text= "Alterar", background= self.cor_botoes, bd= 5, command= self.updateSped)
        # self.bt_alterar.place(rely= 0.45, relx= 0.41, relwidth= 0.045)

        self.bt_buscar = Button(self.frame_2, text= "Buscar", background= self.cor_botoes, bd= 5, command= self.search_sped)
        self.bt_buscar.place(rely= 0.68, relx= 0.01, relwidth= 0.1)

        # self.bt_apagar = Button(self.frame_2, text= "Apagar", background= self.cor_botoes, bd= 5, command= self.deletaSped)
        # self.bt_apagar.place(rely= 0.45, relx= 0.53, relwidth= 0.045)

    def list_frame(self):
        self.list = ttk.Treeview(self.frame_3, height= 3, columns= ("col1", "col2", "col3", "col4", "col5"))

        self.list.heading("#0", text= "")
        self.list.heading("#1", text= "Conta Banco")
        self.list.heading("#2", text= "Credito")
        self.list.heading("#3", text= "Debito")
        self.list.heading("#4", text= "Saldo Atual")
        self.list.heading("#5", text= "Saldo Anterior")
        # self.list.heading("#7", text= "Observação")

        self.list.column("#0", width= 1)
        self.list.column("#1", width= 200)
        self.list.column("#2", width= 100)
        self.list.column("#3", width= 100)
        self.list.column("#4", width= 100)
        self.list.column("#5", width= 100)
        # self.list.column("#7", width= 500)

        self.list.place(rely= 0.01, relx= 0.01, relwidth= 0.96, relheight= 0.98)

        self.scrollList = Scrollbar(self.frame_3, orient= "vertical")
        self.list.configure(yscroll= self.scrollList.set)
        self.scrollList.place(relx= 0.97, rely= 0.01, relwidth= 0.02, relheight= 0.98)
        self.list.bind("<Double-1>", self.OnDoubleClick)
Speds()
