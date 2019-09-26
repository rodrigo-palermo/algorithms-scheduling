import os

# variaveis dos processos
executando = 'x'
apto = '.'
dispositivo = 'd'
bloqueado = 'b'
fim = ' '

MAX_TIME = 20


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


class Scheduler:

    def __init__(self, id, ts, pcb):
        self.pid_has_processor = None
        self.pid_has_device = None
        self.id = id
        self.ts = ts
        self.ts_counter = 0
        self.pcb = pcb
        self.current_time = 0
        self.processor_available = True
        self.device_available = True  # todo: implement device class
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

    def __str__(self):
        text = 'Escalonador: {}\n'.format(self.id)
        text += 'Pid T D T\n'
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
        text += '\n      proc'
        text += ' {}'.format('s' if self.processor_available else 'n')

        text += '\n      devc'
        text += ' {}'.format('s' if self.device_available else 'n')

        #print FILAS
        text += '\n FILA DE PID LIVRE: ' + str(self.fila_pid_livre)
        text += '\n FILA DE PID  APTO: ' + str(self.fila_pid_apto)
        text += '\n FILA DE PID  EXEC: ' + str(self.fila_pid_exec)
        text += '\n FILA DE PID  BLOQ: ' + str(self.fila_pid_bloq)
        text += '\n FILA DE PID  DEVC: ' + str(self.fila_pid_devc)

        text += '\n-------------------------------------------------\n'

        return text

    def init_fila_pid_livre(self, pcb):
        # Fila de PID para uso em fila de PID LIVRE
        fila_pid = Fila()
        for i in range(len(pcb)):
            fila_pid.entra(pcb[i].id)
        return fila_pid

    # def set_fila_pid_apto(self):  # loop
    #     for i in range(self.fila_pid_livre.len()):
    #         pid = self.fila_pid_livre.first()
    #         process = self.get_process_by_pid(pid)
    #         if process.tStart > 0 or process.tEnd > 0:
    #             self.fila_pid_livre.sai()
    #             self.fila_pid_apto.entra(pid)

    # def set_fila_pid_apto(self):  # considera que aptos são somente para processador,e não devc. Para devc irá direto para fila correspondente
    #     if self.fila_pid_livre.len() > 0:
    #         pid = self.fila_pid_livre.first()
    #         process = self.get_process_by_pid(pid)
    #         if process.tStart > 0 or process.tEnd > 0:
    #             self.fila_pid_livre.sai()
    #             self.fila_pid_apto.entra(pid)

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
            elif not process.tem_tStart() and not process.tem_tEnd():
                self.ts_counter = 0
                self.fila_pid_exec.sai()
                if process.finalizou_processo():  # nao tem tDevice
                    process.status = fim
                else:  # ainda tem tDevice
                    self.fila_pid_apto.entra(pid)
                    process.status = apto

        #3-TROCA e REINICIA TS: se não tem TS, independente se processo ter tempo pra executar
            #3-1 reinicia TS
            #3-2 processo vai para fila_APTO
        else: # acabou TS
            self.ts_counter = 0 # reinicia contador do TS
            self.fila_pid_exec.sai()  # libera o processador
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

    # def get_process_status(self, order, time):
    #     return self.process_timeline[order][time]

    # def get_process_status(self, order):
    #     return self.pcb[order].status

    def set_process_availability(self):
        if self.fila_pid_exec.len() > 0:
            self.processor_available = False
        else:
            self.processor_available = True

    def set_device_availability(self):
        if self.fila_pid_devc.len() > 0:
            self.device_available = False
        else:
            self.device_available = True


    def execute(self):  # a cada unidade de tempo
        if self.ts_counter > self.ts:
            self.ts_counter = 0

        self.set_process_availability()
        self.set_device_availability()

        # for i in range(len(self.pcb)):
        #
        #     self.set_process_availability()
        #     self.set_device_availability()

            # if self.processor_available:
            #
            #     if self.fila_pid_apto.len() > 0:
            #         if self.pcb[i].tStart > 0:
            #             self.pcb[i].status = executando
            #             self.pcb[i].tStart -= 1
            #             self.pid_has_processor = i  # ganhou o processador  # DEVE PASSAR PRA OUTRO i
            #         elif self.pcb[i].tDevice > 0:
            #             if self.device_available:
            #                 self.pcb[i].status = dispositivo
            #                 self.pid_has_device = i  # ganhou o dispositivo  # DEVE PASSAR PRA OUTRO i
            #                 self.pcb[i].tDevice -= 1
            #             else:  # se nao tem device disponivel, entao não é dele, já que ele agora é apto
            #                 self.pcb[i].status = bloqueado  # DEVE PASSAR PRA OUTRO i
            #         else:
            #             if self.pcb[i].tEnd > 0:
            #                 self.pcb[i].status = executando
            #                 self.pcb[i].tEnd -= 1
            #                 self.pid_has_processor = i  # ganhou o processador  # DEVE PASSAR PRA OUTRO i
            #             else:
            #                 self.pcb[i].status = fim
            #
            #
            #
            # elif self.pcb[i].status == executando:
            #     if self.ts_counter < self.ts:  # ainda tem TS
            #         if self.pcb[i].tStart > 0:
            #             self.pcb[i].tStart -= 1  # DEVE PASSAR PRA OUTRO i
            #         elif self.pcb[i].tDevice > 0 and self.pcb[i].tStart == 0:  # todo: device nada a ver com tstart q acabou
            #             if self.device_available:
            #                 self.pcb[i].status = dispositivo
            #                 self.pid_has_device = i  # ganhou o dispositivo  # DEVE PASSAR PRA OUTRO i
            #                 self.pcb[i].tDevice -= 1
            #             else:  # se nao tem device disponivel, entao não é dele, já que ele agora é apto
            #                 self.pcb[i].status = bloqueado  # DEVE PASSAR PRA OUTRO i
            #         elif self.pcb[i].tEnd > 0 and self.pcb[i].tStart == 0:
            #             self.pcb[i].tEnd -= 1  # DEVE PASSAR PRA OUTRO i
            #         else:
            #             self.pcb[i].status = fim
            #     else:
            #         self.pcb[i].status = apto
            #         self.pid_has_processor = None  # liberou o processador
            #
            # if self.pcb[i].status in [apto, bloqueado, dispositivo]:
            #     if self.pcb[i].tStart == 0:
            #         if self.pcb[i].tDevice > 0:
            #             if self.device_available:
            #                 self.pcb[i].status = dispositivo
            #                 self.pid_has_device = i  # ganhou o dispositivo  #todo: e na proxima já deve usar dispositivo ou ficar bloqueado
            #                 self.pcb[i].tDevice -= 1
            #             elif self.pid_has_device == i:  # dispositivo em uso pelo processo atual
            #                 # permanece status dispositivo
            #                 self.pcb[i].tDevice -= 1
            #             else:  # muda para bloqueado e tenta na proxima
            #                 self.pcb[i].status = bloqueado
            #         else:
            #             self.pcb[i].status = apto
            #             self.pid_has_device = None  # liberou o dispositivo









            # if self.processor_available:
            #
            #     if self.get_process_status(i) == apto:
            #         if self.pcb[i].tStart > 0:
            #             self.pcb[i].status = executando
            #             self.pcb[i].tStart -= 1
            #             self.pid_has_processor = i  # ganhou o processador
            #         elif self.pcb[i].tDevice == 0 and self.pcb[i].tEnd > 0:
            #             self.pcb[i].status = executando
            #             self.pcb[i].tEnd -= 1
            #             self.pid_has_processor = i  # ganhou o processador
            #
            #     if self.pcb[i].status == dispositivo:
            #         if self.pcb[i].tDevice > 0:
            #             self.pid_has_device = i  # ganhou o dispositivo  #todo: e na proxima já deve usar dispositivo ou ficar bloqueado
            #             self.pcb[i].tDevice -= 1
            #         elif self.pid_has_device == i:  # dispositivo em uso pelo processo atual
            #             # permanece status dispositivo
            #             self.pcb[i].tDevice -= 1
            #         else:  # muda para bloqueado e tenta na proxima
            #             self.pcb[i].status = bloqueado
            #     else:
            #         self.pcb[i].status = apto
            #         self.pid_has_device = None  # liberou o dispositivo
            #
            #
            # elif self.get_process_status(i) == executando:  # o current_id já é o seu
            #     if self.pcb[i].tStart > 0:
            #         if self.ts_counter < self.ts:
            #             # self.pcb[i].status = executando  # já está executando
            #             self.pcb[i].tStart -= 1
            #         else:  # finalizou TS
            #             self.pcb[i].status = apto  # todo: implementar outros status?
            #             self.pid_has_processor = None  # perdeu o processador
            #
            #     elif self.pcb[i].tStart == 0:
            #         self.pcb[i].status = apto  # todo: implementar outros status?
            #         self.pid_has_processor = None  # liberou o processador
            #
            #     elif self.pcb[i].tDevice == 0 and self.pcb[i].tEnd > 0:
            #         if self.ts_counter < self.ts:
            #             self.pcb[i].status = executando
            #             self.pcb[i].tEnd -= 1
            #         else:  # finalizou TS
            #             self.pcb[i].status = fim  # todo: implementar outros status? ou Fim?
            #             self.pid_has_processor = None  # perdeu o processador
            # # self.set_availability()
            # if self.pcb[i].status in [apto, bloqueado, dispositivo]:
            #     if self.pcb[i].tStart == 0:
            #         if self.pcb[i].tDevice > 0:
            #             if self.device_available:
            #                 self.pcb[i].status = dispositivo
            #                 self.pid_has_device = i  # ganhou o dispositivo  #todo: e na proxima já deve usar dispositivo ou ficar bloqueado
            #                 self.pcb[i].tDevice -= 1
            #             elif self.pid_has_device == i:  # dispositivo em uso pelo processo atual
            #                 # permanece status dispositivo
            #                 self.pcb[i].tDevice -= 1
            #             else:  # muda para bloqueado e tenta na proxima
            #                 self.pcb[i].status = bloqueado
            #         else:
            #             self.pcb[i].status = apto
            #             self.pid_has_device = None  # liberou o dispositivo

        if not self.processor_available:
            self.ts_counter += 1


    def run(self):
        while self.current_time <= MAX_TIME:

            self.set_fila_pid_apto()
            self.set_fila_pid_exec()
            self.set_fila_pid_devc()
            #self.execute()
            self.set_scheduler_timeline()
            self.set_process_timeline()

            # print per time unit
            print(self)

            self.clock()


p1 = Process(1, 3, 4, 2)
p2 = Process(2, 2, 5, 1)
p3 = Process(3, 3, 3, 2)
# p1 = Process(0, 0, 1, 1)
# p2 = Process(1, 0, 0, 0)
# p3 = Process(2, 1, 0, 0)
lista_de_processos = [p1, p2, p3]
time_slice = 2
s = Scheduler(1, time_slice, lista_de_processos)
#print(s)
s.run()
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