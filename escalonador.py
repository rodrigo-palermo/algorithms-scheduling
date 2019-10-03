import copy
import time
import sys

movement = True
refresh_rate = 0.5
debbug = False

# VARIÁVEIS GLOBAIS DOS ESCALONADOR
executando = 'x'
apto = '.'
dispositivo = 'd'
bloq = 'b'
fim = ' '
livre = 'l'
cpuTimeVar = 'T'
dvcTimeVar = 'D'


# MAX_TIME = 50

# CLASSES


class Fila:

    def __init__(self):
        self.fila = []

    def entra(self, valor):
        self.fila.append(valor)

    def sai(self):
        self.fila.pop(0)

    def len(self):
        return len(self.fila)

    def first(self):
        if len(self.fila) > 0:
            return self.fila[0]
        return None

    def __str__(self):
        return str(self.fila)


class Process:

    def __init__(self, times_list):
        # self.id = id
        self.timesList = times_list
        self.len = len(times_list)

    def __str__(self):
        return str(self.timesList)


class Scheduler:

    def __init__(self, id, time_slice, process_list):
        self.id = id
        self.ts = time_slice
        self.ts_counter = 0
        self.pcb = self.set_pcb(process_list)
        self.pcb_buffer = copy.deepcopy(self.pcb)
        self.len_bigger_process_time_list = self.len_bigger_process_time_list()
        self.current_time = 0
        self.log = []
        self.timeline = []
        self.process_timeline = []
        self.set_scheduler_pcb_header()
        self.pcb_header = '\nPid |' + self.pcb_times_header  # T D T ...\n'  # cabeçalho para impressao de tempos

        # criar array com linha de tempo para cada processo conforme qtde de processos
        for i in range(len(self.pcb)):
            self.process_timeline.append([] * 1)

        # Fila de PID LIVRE
        self.fila_pid_livre = self.init_fila_pid_livre(self.pcb)
        # self.fila_pid_livre = Fila()

        # Fila de PID APTO
        self.fila_pid_apto = Fila()
        # ?Neste momento a fila de APTO será igual à de LIVRE
        # self.fila_pid_apto = self.fila_pid_livre

        # Fila de PID EXEC - SOMENTE 1 ELEMENTO
        self.fila_pid_exec = Fila()

        # Fila de PID BLOQUEADO
        self.fila_pid_bloq = Fila()

        # Fila de PID DEVICE
        self.fila_pid_devc = Fila()

        # Fila de PID FINALIZADO
        self.fila_pid_fim = Fila()

    # def fila_pid_entra(self, pid, status):
    #     pass

    def set_pcb(self, process_list):
        cols = 4  # [id, process_list, status, next_time]
        pcb = []
        for i in range(len(process_list)):
            pcb.append([i] * cols)
        for row in range(len(process_list)):
            pcb[row][1] = process_list[row]
            pcb[row][2] = livre  # status inicial
            pcb[row][3] = cpuTimeVar  # marca tempo de CPU no início
        return pcb

    def init_fila_pid_livre(self, pcb):
        # Fila de PID LIVRE
        fila_pid = Fila()
        for i in range(len(pcb)):
            fila_pid.entra(pcb[i][0])  # pid
        return fila_pid

    def set_fila_pid_apto_ou_bloq(self):  # considera que aptos são para uso do processador somente?

        # LOOP
        iter = len(self.pcb) - self.fila_pid_fim.len()
        for i in range(iter):
            if self.fila_pid_livre.len() > 0:
                pid = self.fila_pid_livre.first()
                process = self.get_process_by_pid(pid)
                self.fila_pid_livre.sai()
                if process[1].timesList and process[1].timesList[0] > 0:
                    if process[3] == cpuTimeVar:  # se tem lista de tempos # todo: confirmar se tempo 0 já foi retirado da fila
                        process[2] = apto
                        self.fila_pid_apto.entra(pid)
                    elif process[3] == dvcTimeVar:
                        if self.fila_pid_devc.len() == 0:
                            process[2] = dispositivo
                            self.fila_pid_devc.entra(pid)
                        else:
                            process[2] = bloq
                            self.fila_pid_bloq.entra(pid)

                else:  # se inicia já sem tempos, vai para fim  # todo: confirmar se só neste caso ou se entra pid com tempo 0
                    process[2] = fim
                    self.fila_pid_fim.entra(pid)

    def set_fila_pid_exec(self):  # considera para uso do processador

        if self.fila_pid_exec.len() == 0:  # processador livre
            if self.fila_pid_apto.len() > 0:  # tem apto
                pid = self.fila_pid_apto.first()
                process = self.get_process_by_pid(pid)

                self.fila_pid_apto.sai()
                self.fila_pid_exec.entra(pid)
                self.ts_counter += 1  # incrementa contador do TS
                process[1].timesList[0] -= 1
                process[2] = executando  # ou self.pcb[pid][2] = executando

        elif self.fila_pid_exec.len() > 0:  # processador executando
            pid = self.fila_pid_exec.first()
            process = self.get_process_by_pid(pid)

            if self.ts_counter < self.ts:
                if process[1].timesList and process[1].timesList[0] > 0:
                    process[1].timesList[0] -= 1
                    self.ts_counter += 1
                elif process[1].timesList and process[1].timesList[0] == 0:
                    self.ts_counter = 0
                    self.fila_pid_exec.sai()
                    process[1].timesList.pop(0)  # ???  e para onde vai? Depende dos seus tempos  # Colocar em outra parte do codigo?
                    if not process[1].timesList:
                        process[2] = fim
                        self.fila_pid_fim.entra(pid)
                    else:
                            self.fila_pid_bloq.entra(pid)
                            process[2] = bloq
                            process[3] = dvcTimeVar

                elif not process[1].timesList:
                    self.ts_counter = 0
                    self.fila_pid_exec.sai()
                    self.fila_pid_fim.entra(pid)
                    process[2] = fim

            elif self.ts_counter == self.ts:
                if process[1].timesList and process[1].timesList[0] > 0:
                    self.fila_pid_exec.sai()
                    self.fila_pid_apto.entra(pid)
                    self.ts_counter = 0
                    process[2] = apto
                elif process[1].timesList and process[1].timesList[0] == 0:
                    self.ts_counter = 0
                    self.fila_pid_exec.sai()
                    process[1].timesList.pop(0)  # ???  e para onde vai? Depende dos seus tempos  # Colocar em outra parte do codigo?
                    if not process[1].timesList:
                        process[2] = fim
                        self.fila_pid_fim.entra(pid)
                    else:
                        self.fila_pid_bloq.entra(pid)
                        process[2] = bloq
                        process[3] = dvcTimeVar

                elif not process[1].timesList:
                    self.ts_counter = 0
                    self.fila_pid_exec.sai()
                    self.fila_pid_fim.entra(pid)
                    process[2] = fim

    def set_fila_pid_devc(self):  # todo implementar

        if self.fila_pid_devc.len() == 0:  # dispositivo livre
            if self.fila_pid_bloq.len() > 0:  # tem bloqueado esperando dispositivo
                pid = self.fila_pid_bloq.first()
                process = self.get_process_by_pid(pid)

                self.fila_pid_bloq.sai()
                self.fila_pid_devc.entra(pid)
                process[1].timesList[0] -= 1
                process[2] = dispositivo

        elif self.fila_pid_devc.len() > 0:  # dispositivo ocupado
            pid = self.fila_pid_devc.first()
            process = self.get_process_by_pid(pid)

            if process[1].timesList and process[1].timesList[0] > 0:
                process[1].timesList[0] -= 1
            elif process[1].timesList and process[1].timesList[0] == 0:
                #self.ts_counter = 0
                self.fila_pid_devc.sai()
                process[1].timesList.pop(0)  # ???  e para onde vai? Depende dos seus tempos  # Colocar em outra parte do codigo?
                if not process[1].timesList:
                    process[2] = fim
                    self.fila_pid_fim.entra(pid)
                else:
                    self.fila_pid_apto.entra(pid)
                    process[2] = apto
                    process[3] = cpuTimeVar
            elif not process[1].timesList:
                #self.ts_counter = 0
                self.fila_pid_devc.sai()
                self.fila_pid_fim.entra(pid)
                process[2] = fim

    def get_process_by_pid(self, pid):
        for i in range(len(self.pcb)):
            if self.pcb[i][0] == pid:
                return self.pcb[i]
        return None

    def clock(self):
        self.current_time += 1

    def set_scheduler_timeline(self):
        self.timeline.append(self.current_time)

    def set_scheduler_pcb_header(self):
        # imprime alternadamente T (cpu time) e D (device time) coforme ainda tenha tempo em algum processo
        self.pcb_times_header = ''
        maior = self.len_bigger_process_time_list
        for i in range(maior):
            if i % 2 == 0:  # cpuTime
                self.pcb_times_header += ' ' + cpuTimeVar
            else:
                self.pcb_times_header += ' ' + dvcTimeVar
        self.pcb_times_header += ' |'

    def len_bigger_process_time_list(self):
        maior = self.pcb[0][1].len
        for i in range(len(self.pcb)):
            if self.pcb[i][1].len > maior:
                maior = self.pcb[i][1].len
        return maior

    def set_process_timeline(self):
        for i in range(len(self.pcb)):
            self.process_timeline[i].append(self.pcb[i][2])  # status?

    def run(self):

        while self.fila_pid_fim.len() < len(self.pcb):  # self.current_time <= MAX_TIME:
            self.set_fila_pid_apto_ou_bloq()

            self.set_fila_pid_exec()
            self.set_fila_pid_devc()
            self.set_scheduler_timeline()
            self.set_process_timeline()
            # print or keep log per time unit
            #print(self)

            if movement:
                time.sleep(refresh_rate)
                sys.stdout.write("%s" % self)
                sys.stdout.flush()
            
            
            if debbug:
                input()
            
            # self.keep_log(self.__str__())

            self.clock()
        if not movement:
            print(self)

    def keep_log(self, txt):
        self.log.append(txt)

    def __str__(self):
        text = 'ESCALONADOR: {}'.format(self.id)
        text += '\n Time Slice: {}\n'.format(self.ts)

        # print header separator
        text += '----+'
        for i in range(self.len_bigger_process_time_list):
            text += '--'
        text += '-+'
        for t in self.timeline:
            text += '--'

        # print header
        text += ' {}\n'.format(self.pcb_header)

        # print header separator
        text += '----+'
        for i in range(self.len_bigger_process_time_list):
            text += '--'
        text += '-+'
        for t in self.timeline:
            text += '--'
        text += '\n'
        row = 0
        for pcb_item in self.pcb_buffer:
            # print pcb_item id
            text += ' ' + str(pcb_item[0]) + '  |'
            # print pcb_item times (BUFFER para mostrat tempos iniciais)
            for i in range(self.len_bigger_process_time_list):
                if pcb_item[1].len > i:
                    text += ' ' + str(pcb_item[1].timesList[i])
                else:
                    text += '  '
            # print process_timeline
            text += ' |'
            for j in range(len(self.process_timeline[row])):
                text += ' {}'.format(self.process_timeline[row][j])
            text += '\n'
            row += 1

        # print footer separator
        text += '----+'
        for i in range(self.len_bigger_process_time_list):
            text += '--'
        text += '-+'
        for t in self.timeline:
            text += '--'
        text += '\n'

        # print timeline
        text += '       '
        for i in range(self.len_bigger_process_time_list):
            text += '  '
        for t in self.timeline:
            text += ' {}'.format(t % 10)

        # print FILAS
        text += '\n\n      FILA | PID'
        text += '\n   --------+--------'
        text += '\n LIVRE (' + livre + ') | ' + str(self.fila_pid_livre)
        text += '\n  APTO (' + apto + ') | ' + str(self.fila_pid_apto)
        text += '\n  EXEC (' + executando + ') | ' + str(self.fila_pid_exec)
        text += '\n  BLOQ (' + bloq + ') | ' + str(self.fila_pid_bloq)
        text += '\n  DEVC (' + dispositivo + ') | ' + str(self.fila_pid_devc)
        # TESTES
        text += '\n   FIM (' + fim + ') | ' + str(self.fila_pid_fim)
        text += '\nTS counter | ' + str(self.ts_counter) + '/' + str(self.ts)

        text += '\n============================================================\n'

        return text


# ---------------------------------------------------------
# TIME SLICE
time_slice_2 = 2
time_slice_4 = 4

# Cenario 01
p0 = Process([1])
px = Process([1])
p1 = Process([1, 2])
p2 = Process([2, 3])
p3 = Process([4, 5, 6])
p4 = Process([])  # para testar com lista de tempos vazia (não passa para fila de aptos, mas para de fim)
lista_de_processos_cenario_01 = [p0, p1, p2, p4, p3]
s1 = Scheduler(1, 2, lista_de_processos_cenario_01)
# print(s1.pcb)

s1.run()

"""
p1 = Process(1, )
p2 = Process(2, 2, 2, 1)
p3 = Process(3, 3, 2, 2)
lista_de_processos_cenario_01 = [p1, p2, p3]
#Cenario 02
p1 = Process(3, 0, 1, 1)
p2 = Process(4, 0, 0, 0)
p3 = Process(5, 1, 0, 0)
lista_de_processos_cenario_02 = [p1, p2, p3]
#Cenario 03
p1 = Process(1, 3, 0, 2)
p2 = Process(2, 2, 0, 1)
p3 = Process(3, 3, 0, 2)
lista_de_processos_cenario_03 = [p1, p2, p3]
# TIME SLICE
time_slice_2 = 2
time_slice_4 = 4
# ESCALONADOR
s1 = Scheduler(1, time_slice_2, lista_de_processos_cenario_01)
s2 = Scheduler(2, time_slice_4, lista_de_processos_cenario_02)
s3 = Scheduler(3, time_slice_2, lista_de_processos_cenario_03)
# EXECUTAR O PROGRAMA
# s1.run()
print("\n\n=============================================================\n\n")
#s2.run()
#s1.run()
#print(s1.log[MAX_TIME])
#testes
#print(s.process_timeline[0][10])
# print(p1)
# print(s.pcb[0])
# print(s.pcb[0].tStart)
# fila_pid_apto = Fila()
# fila_pid_apto.entra(1)
# fila_pid_apto.entra(2)
# fila_pid_apto.entra(3)
# fila_pid_apto.sai()
# print(fila_pid_apto)
"""
