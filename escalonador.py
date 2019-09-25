import os

# variaveis dos processos
executando = 'x'
apto = '.'
dispositivo = 'd'
bloqueado = 'b'
fim = ' '


class Process:

    def __init__(self, id, t_start, t_device, t_end, status_inicial):
        self.id = id
        self.tStart = t_start
        self.tDevice = t_device
        self.tEnd = t_end
        self.status = status_inicial

    def __str__(self):
        return '{:2}{:3}{:2}{:2} '.format(self.id, self.tStart, self.tDevice, self.tEnd)


class Scheduler:

    def __init__(self, id, ts, process_list):
        self.pid_has_processor = None
        self.pid_has_device = None
        self.id = id
        self.ts = ts
        self.ts_counter = 0
        self.process_list = process_list
        self.current_time = 0
        self.processor_available = True
        self.device_available = True  # todo: implement device class
        self.timeline = []
        self.process_timeline = []
        for i in range(len(self.process_list)):
            self.process_timeline.append([]*1)

    def __str__(self):
        text = 'Escalonador: {}\n'.format(self.id)
        text += 'Pid T D T\n'
        row = 0
        for process in self.process_list:
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

        return text

    def clock(self):
        self.current_time += 1

    def set_scheduler_timeline(self):
        self.timeline.append(self.current_time)

    def set_process_timeline(self):
        for i in range(len(self.process_list)):
            self.process_timeline[i].append(self.process_list[i].status)

    # def get_process_status(self, order, time):
    #     return self.process_timeline[order][time]

    def get_process_status(self, order):
        return self.process_list[order].status

    def set_availability(self):  # for processor and 1 device
        for i in range(len(self.process_list)):
            if self.get_process_status(i) == executando:
                self.processor_available = False
                break
            else:
                self.processor_available = True

        for i in range(len(self.process_list)):
            if self.get_process_status(i) == dispositivo:
                self.device_available = False
                break
            else:
                self.device_available = True


    def execute(self):  # a cada unidade de tempo
        if self.ts_counter > self.ts:
            self.ts_counter = 0

        for i in range(len(self.process_list)):

            self.set_availability()

            if self.processor_available:

                if self.get_process_status(i) == apto:
                    if self.process_list[i].tStart > 0:
                        self.process_list[i].status = executando
                        self.process_list[i].tStart -= 1
                        self.pid_has_processor = i  # ganhou o processador
                    elif self.process_list[i].tDevice == 0 and self.process_list[i].tEnd > 0:
                        self.process_list[i].status = executando
                        self.process_list[i].tEnd -= 1
                        self.pid_has_processor = i  # ganhou o processador

                if self.process_list[i].status == dispositivo:
                    if self.process_list[i].tDevice > 0:
                        self.pid_has_device = i  # ganhou o dispositivo  #todo: e na proxima já deve usar dispositivo ou ficar bloqueado
                        self.process_list[i].tDevice -= 1
                    elif self.pid_has_device == i:  # dispositivo em uso pelo processo atual
                        # permanece status dispositivo
                        self.process_list[i].tDevice -= 1
                    else:  # muda para bloqueado e tenta na proxima
                        self.process_list[i].status = bloqueado
                else:
                    self.process_list[i].status = apto
                    self.pid_has_device = None  # liberou o dispositivo


            elif self.get_process_status(i) == executando:  # o current_id já é o seu
                if self.process_list[i].tStart > 0:
                    if self.ts_counter < self.ts:
                        # self.process_list[i].status = executando  # já está executando
                        self.process_list[i].tStart -= 1
                    else:  # finalizou TS
                        self.process_list[i].status = apto  # todo: implementar outros status?
                        self.pid_has_processor = None  # perdeu o processador

                elif self.process_list[i].tStart == 0:
                    self.process_list[i].status = apto  # todo: implementar outros status?
                    self.pid_has_processor = None  # liberou o processador

                elif self.process_list[i].tDevice == 0 and self.process_list[i].tEnd > 0:
                    if self.ts_counter < self.ts:
                        self.process_list[i].status = executando
                        self.process_list[i].tEnd -= 1
                    else:  # finalizou TS
                        self.process_list[i].status = fim  # todo: implementar outros status? ou Fim?
                        self.pid_has_processor = None  # perdeu o processador
            # self.set_availability()
            if self.process_list[i].status in [apto, bloqueado, dispositivo]:
                if self.process_list[i].tStart == 0:
                    if self.process_list[i].tDevice > 0:
                        if self.device_available:
                            self.process_list[i].status = dispositivo
                            self.pid_has_device = i  # ganhou o dispositivo  #todo: e na proxima já deve usar dispositivo ou ficar bloqueado
                            self.process_list[i].tDevice -= 1
                        elif self.pid_has_device == i:  # dispositivo em uso pelo processo atual
                            # permanece status dispositivo
                            self.process_list[i].tDevice -= 1
                        else:  # muda para bloqueado e tenta na proxima
                            self.process_list[i].status = bloqueado
                    else:
                        self.process_list[i].status = apto
                        self.pid_has_device = None  # liberou o dispositivo



            # if self.process_list[i].status == apto:
            #     if self.process_list[i].tStart > 0 and self.processor_available:
            #         self.process_list[i].status = executando
            #         self.process_list[i].tStart -= 1
            #         self.pid_has_processor = i  # ganhou o processador  # DEVE PASSAR PRA OUTRO i
            #     elif self.process_list[i].tDevice > 0 and self.process_list[i].tStart == 0:
            #         if self.device_available:
            #             self.process_list[i].status = dispositivo
            #             self.pid_has_device = i  # ganhou o dispositivo  # DEVE PASSAR PRA OUTRO i
            #             self.process_list[i].tDevice -= 1
            #         else:  # se nao tem device disponivel, entao não é dele, já que ele agora é apto
            #             self.process_list[i].status = bloqueado  # DEVE PASSAR PRA OUTRO i
            #     else:
            #         if self.process_list[i].tEnd > 0 and self.processor_available and self.process_list[i].tStart == 0:
            #             self.process_list[i].status = executando
            #             self.process_list[i].tEnd -= 1
            #             self.pid_has_processor = i  # ganhou o processador  # DEVE PASSAR PRA OUTRO i
            #         else:
            #             self.process_list[i].status = fim
            #
            # elif self.process_list[i].status == executando:
            #     if self.ts_counter < self.ts:  # ainda tem TS
            #         if self.process_list[i].tStart > 0:
            #             self.process_list[i].tStart -= 1  # DEVE PASSAR PRA OUTRO i
            #         elif self.process_list[i].tDevice > 0 and self.process_list[i].tStart == 0:  # todo: device nada a ver com tstart q acabou
            #             if self.device_available:
            #                 self.process_list[i].status = dispositivo
            #                 self.pid_has_device = i  # ganhou o dispositivo  # DEVE PASSAR PRA OUTRO i
            #                 self.process_list[i].tDevice -= 1
            #             else:  # se nao tem device disponivel, entao não é dele, já que ele agora é apto
            #                 self.process_list[i].status = bloqueado  # DEVE PASSAR PRA OUTRO i
            #         elif self.process_list[i].tEnd > 0 and self.process_list[i].tStart == 0:
            #             self.process_list[i].tEnd -= 1  # DEVE PASSAR PRA OUTRO i
            #         else:
            #             self.process_list[i].status = fim
            #     else:
            #         self.process_list[i].status = apto
            #         self.pid_has_processor = None  # liberou o processador





        if not self.processor_available:
            self.ts_counter += 1


    def run(self):
        while self.current_time <= 17:

            self.execute()
            self.set_scheduler_timeline()
            self.set_process_timeline()

            # print per time unit
            print(self)

            self.clock()


p1 = Process(0, 3, 4, 2, apto)
p2 = Process(1, 2, 5, 1, apto)
p3 = Process(2, 3, 3, 2, apto)
lista_de_processos = [p1, p2, p3]
time_slice = 1
s = Scheduler(1, time_slice, lista_de_processos)
#print(s)
s.run()
#print(s.process_timeline[0][10])
print(p1)
print(s.process_list[0])
print(s.process_list[0].tStart)
