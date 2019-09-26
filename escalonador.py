import os

# VARIÁVEIS GLOBAIS DOS PROCESSOS
executando = 'x'
apto = '.'
dispositivo = 'd'
bloqueado = 'b'
fim = ' '

# VARIÁVEIS GLOBAIS DOS ESCALONADOR
MAX_TIME = 20

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

    def __init__(self, id, t_start, t_device, t_end):
        self.id = id
        self.tStart = t_start
        self.tDevice = t_device
        self.tEnd = t_end
        self.status = apto

    def __str__(self):
        return '{:2}{:3}{:2}{:2} '.format(self.id, self.tStart, self.tDevice, self.tEnd)

    def tem_tStart(self):
        if self.tStart > 0:
            return True
        return False

    def tem_tDevice(self):
        if self.tDevice > 0:
            return True
        return False

    def tem_tEnd(self):
        if self.tEnd > 0:
            return True
        return False

    def finalizou_processo(self):
        if not self.tem_tStart() and not self.tem_tDevice() and not self.tem_tEnd():
            return True
        return False


class Scheduler:

    def __init__(self, id, ts, pcb):
        # self.pid_has_processor = None
        # self.pid_has_device = None
        self.id = id
        self.ts = ts
        self.ts_counter = 0
        self.pcb = pcb
        self.current_time = 0
        # self.processor_available = True
        # self.device_available = True  # todo: implement device class
        self.log = []
        self.timeline = []
        self.process_timeline = []
        for i in range(len(self.pcb)):
            self.process_timeline.append([]*1)

        # Fila de PID para uso em fila de PID LIVRE
        self.fila_pid_livre = self.init_fila_pid_livre(self.pcb)

        # Fila de PID para uso em fila de PID APTO
        self.fila_pid_apto = Fila()
        # ?Neste momento a fila de APTO será igual à de LIVRE
        # self.fila_pid_apto = self.fila_pid_livre

        # Fila de PID para uso em fila de PID EXEC - SOMENTE 1 ELEMENTO
        self.fila_pid_exec = Fila()

        # Fila de PID para uso em fila de PID BLOQUEADO
        self.fila_pid_bloq = Fila()

        # Fila de PID para uso em fila de PID DEVICE
        self.fila_pid_devc = Fila()

        # Fila de PID para uso em fila de PID FINALIZADO
        self.fila_pid_finalizado = Fila()

    def __str__(self):
        text = 'Escalonador: {}'.format(self.id)
        text += '\n TS: {}'.format(self.ts)
        text += '\nPid T D T\n'
        row = 0
        for process in self.pcb:
            # print process
            text += str(process)
            # print process_timeline
            for j in range(len(self.process_timeline[row])):
                text += ' {}'.format(self.process_timeline[row][j])
            text += '\n'
            row += 1

        # print timeline
        text += '          '
        for t in self.timeline:
            text += ' {}'.format(t % 10)

        # print availability
        # text += '\n      proc'
        # text += ' {}'.format('s' if self.processor_available else 'n')
        #
        # text += '\n      devc'
        # text += ' {}'.format('s' if self.device_available else 'n')

        #print FILAS
        text += '\n FILA DE PID LIVRE: ' + str(self.fila_pid_livre)
        text += '\n FILA DE PID  APTO: ' + str(self.fila_pid_apto)
        text += '\n FILA DE PID  EXEC: ' + str(self.fila_pid_exec)
        text += '\n FILA DE PID  BLOQ: ' + str(self.fila_pid_bloq)
        text += '\n FILA DE PID  DEVC: ' + str(self.fila_pid_devc)
        # TESTES
        text += '\n FILA DE PID   FIM: ' + str(self.fila_pid_finalizado)
        text += '\n        TS counter: ' + str(self.ts_counter)

        text += '\n-------------------------------------------------\n'

        return text

    def keep_log(self, txt):
        self.log.append(txt)


    def init_fila_pid_livre(self, pcb):
        # Fila de PID para uso em fila de PID LIVRE
        fila_pid = Fila()
        for i in range(len(pcb)):
            fila_pid.entra(pcb[i].id)
        return fila_pid

    def set_fila_pid_apto(self):  # considera que aptos são para uso do processador ou device
        if self.fila_pid_livre.len() > 0:
            pid = self.fila_pid_livre.first()
            process = self.get_process_by_pid(pid)
            process.status = apto  # somente para impressao???
            self.fila_pid_livre.sai()
            self.fila_pid_apto.entra(pid)

    def set_fila_pid_exec(self):  # considera para uso do processador

        if self.fila_pid_exec.len() == 0:  # processador livre
            if self.fila_pid_apto.len() > 0:
                pid = self.fila_pid_apto.first()
                process = self.get_process_by_pid(pid)
                if process.tem_tStart() or process.tem_tEnd():
                    if self.ts_counter < self.ts:  # tem TS  #Proc está livre, porém garante caso TS seja 0, o que não deveria ocorrer
                        self.fila_pid_apto.sai()
                        self.fila_pid_exec.entra(pid)
                        self.ts_counter += 1  # incrementa contador do TS
                        process.status = executando
                        if process.tem_tStart():
                            process.tStart -= 1  # decrementa tStart
                        elif process.tem_tEnd():
                            process.tEnd -= 1  # decrementa tEnd

        else:  # processador executando
            pid = self.fila_pid_exec.first()
            process = self.get_process_by_pid(pid)
            self.continua_ou_troca_processo(process)

    def continua_ou_troca_processo(self, process):
        pid = process.id
        #1-CONTINUA NESTE TS NO PROXIMO CLOCK: se tem TS, se processo tem algum tempo pra executar tStart ou tEnd
            #1-2 Incrementa TS
            #1-1 Para tStart ou tEnd - fica na fila_EXEC
        if self.ts_counter < self.ts:  # tem TS
            if process.tem_tStart() or process.tem_tEnd():
                self.ts_counter += 1  # incrementa contador do TS
                if process.tem_tStart():
                    process.tStart -= 1  # decrementa tStart
                elif process.tem_tEnd():
                    process.tEnd -= 1  # decrementa tEnd
            # 2-TROCA E REINICIA TS: se tem TS, mas processo não tem tempo pra executar
                # 2-1 reinicia TS
                # 2-2 Se não tem tempo tStart e tEnd - finaliza processo?
            #elif not process.tem_tStart() and not process.tem_tEnd():
            else:
                self.ts_counter = 0  # reinicia contador do TS
                self.fila_pid_exec.sai()  # libera o processador
                if process.finalizou_processo():  # nao tem tDevice
                    process.status = fim
                    self.fila_pid_finalizado.entra(pid)
                else:  # ainda tem tDevice
                    self.fila_pid_apto.entra(pid)
                    process.status = apto
                self.set_fila_pid_exec()  # RECURSIVIDADE !? Agora já saiu da própria funçõa. Já deve executar próximo da lista de apto, se não vazia. NECESSARIO aqui ou só embaixo? Necessário, senao CPU fica ociosa

        #3-TROCA e REINICIA TS: se não tem TS, independente se processo ter tempo pra executar
            #3-1 reinicia TS
            #3-2 processo vai para fila_APTO
        else: # acabou TS
            self.ts_counter = 0  # reinicia contador do TS
            self.fila_pid_exec.sai()  # libera o processador
            if process.finalizou_processo():  # nao tem tDevice
                process.status = fim
                self.fila_pid_finalizado.entra(pid)
            else:  # ainda tem tDevice
                self.fila_pid_apto.entra(pid)
                process.status = apto
            self.set_fila_pid_exec()  # RECURSIVIDADE !? Agora já saiu da própria funçõa. Já deve executar próximo da lista de apto, se não vazia.

    def set_fila_pid_devc(self):  #todo implementar
        pass
        # if self.fila_pid_apto.len() > 0:
        #     pid = self.fila_pid_livre.first()
        #     process = self.get_process_by_pid(pid)
        #     if process.tStart > 0 or process.tEnd > 0:
        #         self.fila_pid_livre.sai()
        #         self.fila_pid_apto.entra(pid)

    def get_process_by_pid(self, pid):
        for i in range(len(self.pcb)):
            if self.pcb[i].id == pid:
                return self.pcb[i]
        return None

    def clock(self):
        self.current_time += 1

    def set_scheduler_timeline(self):
        self.timeline.append(self.current_time)

    def set_process_timeline(self):
        for i in range(len(self.pcb)):
            self.process_timeline[i].append(self.pcb[i].status)

    # def set_process_availability(self):
    #     if self.fila_pid_exec.len() > 0:
    #         self.processor_available = False
    #     else:
    #         self.processor_available = True
    #
    # def set_device_availability(self):
    #     if self.fila_pid_devc.len() > 0:
    #         self.device_available = False
    #     else:
    #         self.device_available = True

    def run(self):
        while self.current_time <= MAX_TIME:

            self.set_fila_pid_apto()
            self.set_fila_pid_exec()
            self.set_fila_pid_devc()
            self.set_scheduler_timeline()
            self.set_process_timeline()
            # print or keep log per time unit
            print(self)
            self.keep_log(self.__str__())

            self.clock()

# ---------------------------------------------------------

#Cenario 01
p1 = Process(1, 3, 4, 2)
p2 = Process(2, 2, 5, 1)
p3 = Process(3, 3, 3, 2)
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

s3.run()
print(s3.log[MAX_TIME])


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