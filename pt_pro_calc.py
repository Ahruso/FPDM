
import math
import matplotlib
matplotlib.use('GTKAgg')
import matplotlib.pyplot as plt




class BackenAusdrehen(object):

    def clean_up_profile(self):
        """old_profile wird von ueberfluessigen Punkten befreit
        Das old_profile Array wird in zwei verschiedenen Orientierungen geprueft. Alle Punkte, die sich ausserhalb
        der Backe befinden wuerden werden geloescht, sodass die minimale Anzahl an Koordinaten uebrig bleibt,
        die die Backe komplett beschreiben

        :return:
        """

        """ Array abwaerts sortieren"""
        self.old_profile = sorted(self.old_profile, key=lambda x: x[0], reverse=True)
        h = 0
        index = 0
        rm_list = []
        """in der folgenden Schleife wird geprueft, ob es koordinaten gibt die oberhalb der Backe liegen(Z-Achse)"""
        for i in self.old_profile:
            if h >= i[1] and index != 0:
                rm_list.insert(0,index) #""" rm_list enthaelt die indizes der Koordinaten, die geloescht werden sollen"""
            else:
                h = i[1]
            index += 1
        while rm_list != []:#"""punkte mit den Indizes aus rm_list werden aus old_profile entfernt"""
            del self.old_profile[rm_list[0]]
            del rm_list[0]
        """Array aufwaerts sortieren"""
        self.old_profile = sorted(self.old_profile, key=lambda x: x[0], reverse=False)
        h = 0
        index = 0
        rm_list =[]
        """
        in der folgenden Schleife wird geprueft, ob es koordinaten gibt die auf der berflaeche
        der Backe liegen(X-Achse)
        """
        for i in self.old_profile:
            if h >= i[0] and index != 0:
                rm_list.insert(0,index)
            else:
                h = i[0]
            index += 1
        while rm_list != []:
            del self.old_profile[rm_list[0]]
            del rm_list[0]
        """Array wieder richtigherum sortieren"""
        self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
        return 0

    def print_old_profile(self):
        """Grafik wird mit myplotlib gezeichnet
        Die koordinaten aus dem old_profile array werden ausgewertet und gezeichnet. Anschliessend wird das Bild in
        plot.png gespeichert
        :return:
        """

        plt.clf()
        plt.axis([self.x_offset_backe+self.backenlaenge+0.5, self.x_offset_backe-1, self.ausdrehlimit_z+0.5, -1])
        self.clean_up_profile()
        j = 0
        plt.plot([self.x_offset_backe+self.backenlaenge+0.5, self.old_profile[j][0]], [0, self.old_profile[j][1]], 'r-')
        plt.fill_between([self.x_offset_backe+self.backenlaenge+0.5, self.x_offset_backe+self.backenlaenge+0.5,
                          self.old_profile[j][0]], [0, self.ausdrehlimit_z+0.5, self.ausdrehlimit_z+0.5], color='b')
        while j < len(self.old_profile):
            if j < len(self.old_profile)-1:
                plt.plot([self.old_profile[j][0], self.old_profile[j][0]],
                         [self.old_profile[j][1],self.old_profile[j+1][1]], 'r-')
                plt.plot([self.old_profile[j][0], self.old_profile[j+1][0]],
                         [self.old_profile[j+1][1], self.old_profile[j+1][1]],'r-')
                plt.fill_between([self.old_profile[j+1][0], self.old_profile[j+1][0], self.old_profile[j][0]],
                                 [self.old_profile[j+1][1], self.ausdrehlimit_z+0.5, self.ausdrehlimit_z+0.5],
                                 [self.old_profile[j+1][1],self.old_profile[j+1][1],self.old_profile[j+1][1]],
                                 color='b')
            j += 1
        plt.plot([self.old_profile[-1][0], 0], [self.x_offset_backe, self.ausdrehlimit_z+0.5], 'r-')
        plt.grid(True)
        plt.savefig("plot.png")
        return 0

    def spannstufe(self, new_profile):
        """Die Koordinaten fuer die Backenstufe(Spannstufe), die das Bauteil haelt, werden berechnet
        Es wird geprueft, auf welche hoehe die Spannstufe gelegt werden muss. Dazu wird geprueft wie weit die
        Backen an der x-Position abgedreht sind. Die hoehe + spannflaechenhoehe wird dann in new_profile geschrieben.
        Ausserdem wird auch noch die naechste Koordinate ins Array geschrieben, die das Ende der Spannstufe beschreibt
        :param new_profile: die ersten Koordinaten, die aus den Parametern des Bauteils abgeleitet wurden
        :return: new_profile enthaelt jetzt die Anfangs- und die Endkoordinate der Spannstufe
        """
        # current_x = 0
        # current_z = 10
        # area = 0
        new_profile = sorted(new_profile,key=lambda x: x[0], reverse=True)
        self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
        '''
        hier ist das Profil noch so, wie is in eine frische Backe gedreht werden wuerde,
        So kann man am einfachsten die Koordinaten uebergeben.
        Jetzt muss das neue Profil aber an die schon eingedrehte Backe angepasst werden.
        Dazu wird ermittelt, wo das neue Profil anfaengt und die entsprechende hoehe als oberste Kante der Backe angegeben
        '''
        self.clean_up_profile()
        aufl_start_z_found = False
        aufl_end_z_found = False
        """
        Begrenzung der maximalen Auflageflaechenlaenge. Wollten die Bediener begrenzt haben, damit die Bauteile
        nicht so viel Kontakt mit den Backen haben. Soll das geaendert werden, dann muss das auch noch im GCODE
        Generator in der Funktion on_load_prog_clicked in fp.py geaendert werden
        """
        if self.mindest_auflagefl > 3.0:

            new_profile.append([round(new_profile[0][0] - 3.0, 3), round(new_profile[0][1] + self.mindest_spannfl, 3)])
        else:
            new_profile.append([round(new_profile[0][0] - self.mindest_auflagefl, 3),
                                round(new_profile[0][1] + self.mindest_spannfl, 3)])
        for i in self.old_profile:
            if i[0] <= new_profile[0][0] and new_profile[0][1] == 0 and aufl_start_z_found == False:
                new_profile[0][1] = round(i[1], 3)
                new_profile[1][1] = round(new_profile[0][1] + self.mindest_spannfl, 3)
                aufl_start_z_found = True
            if i[0] <= new_profile[1][0] and i[1] == new_profile[0][1] and aufl_end_z_found == False:
                new_profile[1][1] = round(new_profile[0][1] + self.mindest_spannfl, 3)
                aufl_end_z_found = True
                break
            if i[0] < new_profile[1][0] and i[1] > new_profile[1][1] and aufl_end_z_found == False:
                new_profile[1][1] = i[1]
                new_profile[0][1] = round(new_profile[1][1] - self.mindest_spannfl, 3)
                aufl_end_z_found = True
                break
            if i[0] < new_profile[1][0] and i[1] < new_profile[1][1] and aufl_end_z_found == False:
                break
        return new_profile

    def spannstufe_koordinaten(self, start_run, end_run, depth):
        """Koordinaten fuer die Spannstufe werden berechnet
        Anhand der maximalen Schnitttiefe werden die Koordinaten berechnet, die nachher zur Erzeugung des GCODES
        benutzt werden.
        :param start_run:   Startkoordinate der aktuellen abzudrehenden Schicht, Wird mit jedem schnitt veraendert
        :param end_run: Endkoordinate der aktuellen Stufe(hier die Spannstufe
        :param depth: die maximale Schnitttiefe fuer die Bearbeitung
        :return: Die Koordinaten der Spannstufe in einem Array, das wie folgt aufgebaut ist:
        (((startx1,startz1),(endex1,endez1)schnittlaenge in mm, schnittdauer),...,
        ((startxn,startzn),(endexn,endezn)schnittlaenge in mm, schnittdauer)) fuer n Schnittebenen.
        """
        block_area = 0
        block_time = 0
        end = []
        area = 0
        step = []
        block_aufl = []
        current_x = 0
        current_z = 0
        self.aufl_counter = 0
        while(start_run[1] < end_run[1]):
                index = 0
                for i in self.old_profile:
                    index += 1
                    current_z = i[1]
                    if i[1] > start_run[1] :
                        break
                    current_x = i[0]
                if round(math.fmod(end_run[1]-start_run[1], depth), 3) > 0.0:
                    end = [round(current_x-0.1, 3), round(start_run[1]+math.fmod(end_run[1]-start_run[1], depth), 3)]
                    for i in self.old_profile:
                        if i[1] < end[1] and i[0] < end[0]:
                            end[0] = round(i[0]-0.1, 3)
                    start_run = [start_run[0], round(start_run[1]+math.fmod(end_run[1]-start_run[1], depth), 3)]
                    if round(start_run[0]-end[0], 3) > round(0.1, 1):
                        area = round((start_run[0]-current_x-0.1), 3)
                        step_time = round(area/self.speed, 3)
                        step = [start_run, end, area, step_time]
                        block_area += area
                        block_time += step_time
                        self.aufl_counter += 1
                        block_aufl.append(step)
                else:
                    end = [round(current_x-0.1, 3), round(start_run[1]+depth, 3)]
                    for i in self.old_profile:
                        if i[1] < end[1] and i[0] < end[0]:
                            end[0] = round(i[0]-0.1, 3)
                    start_run = [start_run[0], round(start_run[1]+depth, 3)]
                    if round(start_run[0]-end[0], 3) > round(0.1, 1):
                        area = round((start_run[0]-current_x-0.1), 3)
                        step_time = round(area/self.speed, 3)
                        step = [start_run, end, area, step_time]
                        block_area += area
                        block_time += step_time
                        self.aufl_counter += 1
                        block_aufl.append(step)
        block_aufl.append(block_area)
        block_aufl.append(block_time)
        return block_aufl

    def ueberhang(self,start_aufl,depth,erste_stufe_x,erste_stufe_y):#,new_profile):#start_run_ueb,end_run_ueb,depth):
        """Berechnung der Ueberhangstufe
        So aehnlich wie Spannstufe mit Spannstufe_koordinaten direkt im Anschluss. Dabei werden aber Koordinaten
        erzeugt, die beim Ausdrehen eine
        :param start_aufl: Startpunkt der Spannstufe. Von hier aus wird die Ueberhangstufe berechnet
        :param depth: maximale Schnitttiefe
        :param erste_stufe_x: laenge der Ueberhangstufe. Konstante in fp.py
        :param erste_stufe_y: hoehe der Ueberhangstufe. Konstante in fp.py
        :return: Array nach Format wie auch das return von Spannstufe_koordinaten nur fuer den Ueberhang
        """
        #self.ueb_counter = 0
        if start_aufl[1]-self.old_profile[0][1] < erste_stufe_y:
            erste_stufe_y = start_aufl[1]-self.old_profile[0][1]
        current_x = 0
        current_z = 0
        step_ueb = []
        block_area = 0
        block_time = 0
        step_ueb_time = 0
        area_ueb = 0
        block_ueb_run = []
        start_run = [0,0]
        start_erste_stufe = [0,0]
        end_erste_stufe = [0,0]
        index = 0
        start_erste_stufe[0] = (start_aufl[0]+erste_stufe_x)
        end_erste_stufe = start_aufl
        for i in self.old_profile:
            if i[0] < (start_erste_stufe[0]):
                start_erste_stufe[1] = i[1]
                current_x = i[0]
                current_z = i[1]
                break
            index += 1
        start_run = start_erste_stufe
        if (start_aufl[1]-start_erste_stufe[1]) > erste_stufe_y:
            if round(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth),3) > 0:
                start_run = [start_erste_stufe[0],round(start_erste_stufe[1] + (math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
                end_run = [current_x-0.1,round(start_erste_stufe[1]+(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
            else:
                start_run = [start_erste_stufe[0],start_erste_stufe[1]+depth]
                end_run = [current_x-0.1,start_erste_stufe[1]+depth]
            for i in self.old_profile:
                if i[1]< end_run[1] and i[0]< end_run[0]:
                    end_run[0] = i[0]-0.1
            area_ueb = round((start_run[0]-end_run[0]),3)
            block_area += area_ueb
            step_ueb_time = round((area_ueb/self.speed),3)
            step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
            block_time += step_ueb_time
            self.aufl_counter += 1
            self.ueb_counter += 1
            block_ueb_run.append(step_ueb)
            while (round(start_aufl[1] - start_run[1],3) > erste_stufe_y):
                start_run = [start_erste_stufe[0],round(start_run[1]+depth,3)]
                for i in self.old_profile:
                    if i[0] < start_run[0]:
                        current_x = round(i[0],3)
                        current_z = round(i[1],3)
                        break
                end_run = [round(current_x-0.1,3),start_run[1]]
                for i in self.old_profile:
                    if i[1]< end_run[1] and i[0]< end_run[0]:
                        end_run[0] = round(i[0]-0.1,3)
                area_ueb = round((start_run[0]-end_run[0]),3)
                if start_run[1] > current_z:
                    block_area+= area_ueb
                    step_ueb_time = round((area_ueb/self.speed),3)
                    step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
                    block_time = round(block_time + step_ueb_time,3)
                    self.aufl_counter+= 1
                    self.ueb_counter += 1
                    block_ueb_run.append(step_ueb)
        #print "self.ueb_start", self.ueb_start
        self.ueb_start = start_run
        while (start_aufl[1] > start_run[1]):
            start_run = [round(start_run[0]-depth,3),round(start_run[1]+depth,3)]
            for i in self.old_profile:
                current_z = i[1]
                current_x = i[0]
                if i[0] < start_run[0]:
                    break
            for i in self.old_profile:
                if start_run[1] < i[1]:
                    break
                current_x = i[0]
            end_run = [round(current_x-0.1,3),start_run[1]]
            area_ueb = round((start_run[0]-end_run[0]),3)
            if start_run[1] > current_z:
                self.ueb_end = [start_run[0],start_run[1]]
                block_area = round(block_area + area_ueb,3)
                step_ueb_time = round((area_ueb/self.speed),3)
                step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
                block_time = round(block_time + step_ueb_time,3)
                self.aufl_counter+= 1
                self.ueb_counter += 1
                block_ueb_run.append(step_ueb)
        block_ueb_run.append(block_area)
        block_ueb_run.append(block_time)
        return block_ueb_run

    def rueckenradius(self,new_profile,hoehe_radius, depth):
        """Berechnet die Koordinaten fuer die Radiusstufe
        Berechnet die Koordinaten, die zur Erzeugung des GCODES fuer die Radrueckenstufe genutzt werden. Dabei
        faengt die Stufe am Endpunkt der Spannstufe an und endet am Ende der Backe auf einer hoehe die im folgenden
        noch berechnet wird

        :param new_profile: Array mit den Koordinaten fuer die Stufen der neuen Backe
        :param hoehe_radius: der Abstand zwischen der Auflageflaeche und der Planflaeche an der Unterseite des Bauteils
        :param depth: maximale schnitttiefe
        :return: Array nach Format wie auch das return von Spannstufe_koordinaten, allerdings fuer die Radrueckenstufe
        """
        end_aufl = new_profile[1]
        current_z = 0
        current_x = 0
        schrittweite_y = round(depth,3)
        #hier beginnt die hoehenberechnung
        l = new_profile[0][0]-self.mindest_auflagefl - self.ruecken_nabe_durchm/2
        steigung = hoehe_radius/l
        d = steigung *(new_profile[0][0]-self.mindest_auflagefl-self.x_offset_backe)
        for i in self.old_profile:
            if round(new_profile[1][0] - hoehe_radius,3) > round(i[0],3):
                current_x = i[0]
                current_z = i[1]
                break
        new_profile.append([current_x,round(new_profile[1][1],3)])
        new_profile[2][1] = new_profile[1][1] + d
        end_rad = new_profile[2]
        schritte = (end_rad[1]-end_aufl[1])/depth
        schrittweite_x = (end_aufl[0]-self.x_offset_backe)/schritte
        if new_profile[1][0] == self.x_offset_backe:
            new_profile[2][1] = round(new_profile[1][1] + 0.05,3)
            new_profile[1][0] = round(0.05,3)
        start_run = [0,0]
        end_run = [0,0]
        schrittweite_y = round(depth,3)
        current_x = 0
        current_z = 0
        start_run = end_aufl
        block_area = 0
        block_time = 0
        block_rad = []
        index= 0
        while start_run[1] <= end_rad[1]:
            if index == 0:
                start_run = [round(start_run[0],3),round(start_run[1]+schrittweite_y,3)]
            else:
                if round(math.fmod(end_rad[1]-start_run[1],schrittweite_y),3) > 0 and index >= 2:
                    start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+round(math.fmod(end_rad[1]-start_run[1],schrittweite_y),3),3)]
                else:
                    start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
            index += 1
            for i in self.old_profile:
                current_x = i[0]
                current_z = i[1]
                if i[0] < start_run[0]:
                    break
            for i in self.old_profile:
                if start_run[1] < i[1]:
                    break
                current_x = round(i[0],3)
            if start_run[0] < 0:
                break
            end_run 	= [round(current_x-0.1,3),start_run[1]]
            for i in self.old_profile:
                if i[1]< end_run[1] and i[0]< end_run[0]:
                    end_run[0] = round(i[0]-0.1,3)
            area = round((start_run[0]-end_run[0]),3)
            if start_run[1] > current_z and start_run[0] > end_run[0]:
                step_time = round(area/(self.speed),3)
                step = [start_run,end_run,area,step_time]
                block_area = round(block_area + area,3)
                block_time = round(block_time + step_time,3)
                block_rad.append(step)
        block_rad.append(block_area)
        block_rad.append(block_time)
        j = 0
        for i in block_rad:
            j += 1
        return block_rad

    def print_koordinates(self,block_ueb,block_stufe,block_rad,run):
        """Zeichnen der Schnittstufen in die Grafik der Backenvorschau und schreiben der neuen Koordinaten
        in das old_profile Backenarray
        Die einzelnen Stufenbloecke werden nacheinander ausgewertet und in das Backenprofil eingefuegt.
        :param block_ueb: Koordinatenarray der Ueberhangstufe
        :param block_stufe: Koordinatenarray der Spannstufe
        :param block_rad: Koordinatenarray der Radiusstufe
        :param run: Flag, welches steuert, ob die neuen Koordinaten auch in das old_profile Array geschrieben werden sllen oder nicht
        :return: 0
        """
        j = 0
        for i in block_ueb:
            j += 1
        if block_ueb != [0,0]:
            for i in block_ueb:
                if type(i) is not float:
                    if i[1][1] > self.ausdrehlimit_z:
                        self.abgenutzt = True
                        return 1
                    plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')
                    plt.plot(i[0][0],i[0][1],'ro')
                    plt.plot(i[1][0],i[1][1],'go')
                    if run == True:
                        self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
                        self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
                    self.gcode_koord.append([i[0],i[1]])
                    j +=1
        if len(block_stufe) > 2:
            for i in block_stufe:
                j += 1
            for i in block_stufe:
                if type(i) is not float:
                    if i[1][1] > self.ausdrehlimit_z:
                        self.abgenutzt = True
                        return 1
                    plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')
                    plt.plot(i[0][0],i[0][1],'ro')
                    plt.plot(i[1][0],i[1][1],'go')
                    if run == True:
                        self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
                        self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
                    self.gcode_koord.append([i[0],i[1]])
                    j +=1
        else:
            pass
        if len(block_rad) >2:
            for i in block_rad:
                j += 1
            for i in block_rad:
                if type(i) is not float:
                    if i[1][1] > self.ausdrehlimit_z:
                        self.abgenutzt = True
                        return 1
                    plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')#,i[1])
                    plt.plot(i[0][0],i[0][1],'ro')#,i[1])plt.plot(i[1][0],i[1][1],'ro')
                    plt.plot(i[1][0],i[1][1],'go')
                    if run == True:
                        self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
                        self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
                    self.gcode_koord.append([i[0],i[1]])
                j +=1
        else:
            pass
        plt.savefig("plot.png")
        self.est_time = block_ueb[-1]+block_stufe[-1]+block_rad[-1]
        return 0
        
    def get_old_profile(self):
        """ Zeichnet die Grafik fuer die Backen und gibt das Backenprofil zurueck
        Ist eigentlich umstaendlich gemacht und sollte vielleicht direkt in der aufrufenden Funktion umgesetzt werden.
        So wie es jetzt ist, ist es waehrend der Entwicklung gewachsen und deswegen eventuell etwas unsinnig.
        :return: Array mit Backenkoordinaten
        """
        self.print_old_profile()
        return self.old_profile
    
    def get_gcode_koord(self):
        """
        liefert die Koordinaten zurueck, die in den Gcode fuer ein neues Backenprofil mit einfliessen
        :return: self.gcode_koord Array aus Koordinaten
        """
        self.gcode_koord = []
        self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,False)
        return self.gcode_koord

    def set_profile_tuple(self,profile_tuple):
        """ Bekommt ein Array mit Koordinaten uebergeben und speichert es im Backen-Array
        Die Funktion wird in FP immer dann aufgerufen, wenn ein aelteres Backenprofil geladen wird. Dann wird das Backenprofil sortiert
        und mit print_old_profile gezeichnet. Das passiert einmal zum Start des Programms und ausserdem immer wenn man auf den Button
        Backen laden klickt und sich alte Backen aussucht.
        :param profile_tuple: Ein Array welches Backenkoordinaten enthaelt.
        """
        self.old_profile = sorted(profile_tuple,key=lambda x: x[0], reverse=True)
        self.print_old_profile()

    def ausdrehen_calc(self,koord_tuple,profile_tuple,speed,mindest_auflagefl,mindest_spannfl,depth,ueberhang_stufe_x,ueberhang_stufe_z,ruecken_nabe_durchm,hoehe_radius,ausdrehlimit_z,backe_innenkante,backenlaenge):
        """ Fuehrt alle Funktionen aus, sodass zum Schluss die Koordinaten zum Ausdrehen der Backen feststehen und das neue Profil der Backen
        wird zurueckgegeben

        :param koord_tuple: Koordinaten der Wirkgeometrie fuer die Backen. Enthealt bis hier her nur ddie ersten zwei Punkte
        :param profile_tuple: Die Koordinaten des aktuellen Backenprofils
        :param speed: Die Vorschubgeschwindigkeit fuer den Drehprozess. Dient hier nur zur Berechnung der Prozesszeit
        :param mindest_auflagefl: Die laenge der Auflageflaeche, so wie sie im Textfeld der Software eingegeben wurde
        :param mindest_spannfl: Die heohe der Spannflaeche, wie sie im Textfeld der Software eingegeben wurde
        :param depth: die maximale Schnitttiefe fuer den Bearbeitungsprozess, wie sie im Textfeld der Software eingegeben wurde
        :param ueberhang_stufe_x: laenge der Ueberhangstufe. Dieser Wert ist eine Konstante in FP und heisst dort "randbreite"
        :param ueberhang_stufe_z: hoehe der Ueberhangstufe. Dieser Wert ist eine Konstante in FP und heisst dort "randhoehe"
        :param ruecken_nabe_durchm: Entspricht der Angabe in der GUI fuer den Durchmesser fuer die Planflaeche am Bauteil Ruecken
        :param hoehe_radius: Entspricht der Angabe in der GUI fuer den Abstand der Planflaeche zur Auflageflaeche
        :param ausdrehlimit_z: Dies ist die hoehe, die maximal in die Backen eingedreht werden kann.
        :param backe_innenkante: ungefaehrer Abstand der Spindeldrehachse bis zu der Innenkante der Backen.
        :param backenlaenge: Angabe wie weit die Backen maximal ausgedreht werden koennen. Die eigentliche Laenge der Backen ist
        groesser, aber diese Grenze wurde einfach aus praktischen Gruenden gewaehlt. Kann vielleicht auch noch geaendert werden
        :return: gibt das alte Backenprofil wieder zurueck
        """

        self.speed = speed
        self.mindest_auflagefl = mindest_auflagefl
        self.mindest_spannfl = mindest_spannfl
        self.depth = depth
        self.ueberhang_stufe_x = ueberhang_stufe_x
        self.ueberhang_stufe_z = ueberhang_stufe_z
        self.hoehe_radius = hoehe_radius
        self.ruecken_nabe_durchm = ruecken_nabe_durchm
        self.x_offset_backe = backe_innenkante
        self.backenlaenge = backenlaenge
        self.old_profile = sorted(profile_tuple,key=lambda x: x[0], reverse=True)
        self.clean_up_profile()
        self.new_profile = sorted(koord_tuple,key=lambda x: x[0], reverse=True)
        self.gcode_koord = []
        passed = 0
        self.print_old_profile()
        self.new_profile = self.spannstufe(self.new_profile)
        self.block_stufe = self.spannstufe_koordinaten(self.new_profile[0],self.new_profile[1],self.depth)
        self.block_ueb = self.ueberhang(self.new_profile[0],self.depth,self.ueberhang_stufe_x,self.ueberhang_stufe_z)#,self.new_profile)
        self.block_rad = self.rueckenradius(self.new_profile,self.hoehe_radius,self.depth)
        self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,False)
        # print self.block_stufe
        return self.old_profile

    def ausdrehen_start(self):
        """ Erzeut die Koordinaten fuer den Ausdrehprozess und schreibt sie dann auch ins old_profile array

        :return: gibt das neue Backenprofil zurueck
        """

        self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,True)
        return self.old_profile


    def __init__(self):
        #die meisten der folgenden Variablen werden in ausdrehen_calc vom aufrufenden Prozess definiert
        self.ausdrehlimit_z = 0	#Maximale Ausdrehhoehe der kleinen Backen in mm, wird erst spaeter fuer den Prozess durch einen Funktionsaufruf gesetzt
        self.backenlaenge = 0	#Maximal nutzbare laenge der Backen. backenlaenge + x_offset_backe geben den maximal nutzbaren Bauteilradius an
        plt.clf()
        plt.figure(figsize=(6.5,2),dpi=200)
        self.aufl_counter = 0	#anzahl der schritte bis das Profil die Auflageflaeche erreicht hat
        self.x_offset_backe= 0	#Abstand der Spindelachse zur Backeninnenkante
        self.ueb_start = []     #beschreibt die erste Eintrittsstelle des Werkzeugs beim Ausdrehen des Profils
        self.ueb_end = []       #beschreibt das Ende des Ueberhangs bzw den Anfang der Auflagestufe
        self.new_profile = [[0,0]]      #Dieses Array enthaelt die Mindestangabe der Punkte fuer ein neues Backenprofil.
        """Das aktuell ausgedrehte Backenprofil 
        Ein Backenprofil besteht aus Koordinaten, die die innenliegenden Ecken beschreiben. Dabei wird von der oberen Innenkante der Backen aus gezaehlt.
        Frische Backen enthalten nur eine Ecke, und zwar [[0,0]](erste Komponente in x Richtung, zweite Komponente in z Richtung). Wird eine Zeile der Backe abgedreht, enthaelt das neue Profil zwei Punkte. Wurde z.b. eine
        flaeche von 2mmx1mm(laenge x tiefe von der Seite der Backe aus betrachtet) aus der Backe herausgedreht, ist das neue Profil [[2,0],[0,1]]
        """
        self.old_profile = [[0,0]]
        self.speed = 0                  #sollte urspruenglich mal dazu gedacht sein die ungefaehre Prozessdauer zu ermitteln. Gibt die Vorschunbgeschrindigkeit einer Bewegung an
        self.mindest_auflagefl = 0      #gibt an, welche die mindestlaenge der Auflageflaeche ist. Funtkionsflaeche in x Richtung.
        self.mindest_spannfl = 0        #gibt an, wie hoch die Spannflaeche mindestens sein muss. Fuktionsflaeche in z Richtung
        self.depth = 0                  #gibt die Schnitttiefe des aktuellen prozesses an. Normalerweise ein Wert zwischen 0.1 und 0.2, je nach Material und Werkzeug
        self.ueberhang_stufe_x = 0      #groesse des sicherheitsbereichs in x Richtung in der aeussersten Stufe der backe 
        self.ueberhang_stufe_z = 0      #groesse des sicherheitsbereichs in z Richtung in der aeussersten Stufe der backe
        self.hoehe_radius = 0           #wenn auch ein Radius in ein Bauteil gedreht werden soll, dann gibt dieser Wert die hoehe eines 90 grad Radius an
        self.gcode_koord = []           #hier werden die Start- und Endkoordinaten der einzelnen Backenschnitte gespeichert. Form:(((startx1,startz1),(endex1,endez1)),((startx2,startz2),(endex2,endez2))) fuer 2 Schnitte
        self.abgenutzt = False          #Flag fuer abgenutzte backen. Wenn eine der Koodrinaten in gcode_koord groesser als ausdrehlimit_z ist, wird dieses Flag auf True gesetzt
        self.block_stufe = []           #Teil der koordinaten aus gcode_koord
        self.block_ueb = []             #Teil der koordinaten aus gcode_koord
        self.block_rad = []             #Teil der koordinaten aus gcode_koord
        self.est_time = 0
        self.ueb_counter = 0