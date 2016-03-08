#!/usr/bin/env python

"""

"""

import os
import sys
import gtk
import gtk.glade
import time
import gobject
import hashlib
import pt_pro_calc
import pickle
import logging
import json


class fp_GUI(object):

    #fp_GUI_func_def_begin
    
    
    def announce_error(self):
        """ versteckt alle Fenster und oeffnet das Fenster fuer die Fehlermeldungen sobald ein registrierter Fehler auftritt
        Im geoeffneten Fenster werden dann entsprechende Texte zu den Fehlern angezeigt. Diese Funktion wird immer zusammen mit
        einem Eintrag in den Fehlerbuffer aufgerufen. Man koennte den Fehlerbuffer auch hier in der Funktion beschreiben und die Fehlermeldung
        als String uebergeben. Waere eine Ueberlegung fuer eine naechste Version der Software
        :param last_seen: letztes Fenster, das geoeffnet wurde, bevor der Fehler aufgetreten ist
        :return: 0
        """
        self.passwd_window.hide()
        self.quit_window.hide()
        self.load_backe_window.hide()
        self.backen_window.hide()
        #self.setup_window.hide()
        self.init_window.hide()
        self.backen_window.hide()
        self.bauteil_window.hide()
        self.fehlerfreie_fahrt = False
        if self.last_seen != None:
            self.last_seen = self.last_seen
            #print "last_seen, announce",self.last_seen
        self.gcode_error_window.show()
        return 0
    
    def bauteil_berechnen(self):
        """ Erzeugt aus den GUI Eingabewerten den GCODE fuer die Bearbeitung der Bauteile und schreibt den Code in eine Datei
        :return: Dateiname der gerade erzeugten GCODE Datei
        """
        bauteil_ankratzhoehe = self.auflageflaeche_hoehe_m_schlichter-self.length_ist+self.radius_hoehe
        bauteil_abschlusshoehe = self.auflageflaeche_hoehe_m_schlichter-self.length_soll+self.radius_hoehe
        safe_pos_x = 0
        safe_pos_z = bauteil_ankratzhoehe - 20
        # fase = False
        # fase = self.bearb_fase.get_active()
        # planen = False
        # planen = self.bearb_planen.get_active()
        # radius = False
        # radius = self.bearb_radius.get_active()
        andruecker_x_inpos = 43			#nachmessen
        andruecker_z_offset = -1			#die andrueckflaeche des Andrueckers befindet sich xx mm hoeher als die Werkzeugspitze
        andruecker_z_safe = bauteil_ankratzhoehe-5 	#das muesste eigentlich hinkommen, weil der andruecker hoeher liegt als das Werkzeug
        #soweit runter fahren, dass das Teil mit dem halben Hub des andrueckers angedrueckt wird
        andruecker_z_inpos = bauteil_ankratzhoehe + 10 	# + WERT das muss noch ausgemessen werden
        gcode = self.bauteil_ordner + str(round(time.time(),0))+'.ngc'
        j = 0
        fd = open(gcode,'w+')
        fd.write("G18\n")
        fd.write("M103\n")
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_inpos,3),self.positioning_speed/4))
        fd.write("G4 P0.5\n")
        fd.write("M115\n")
        fd.write("G4 P2\n")
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
        fd.write("M100\n")
        fd.write("G61\n")
        if self.length_ist > self.length_soll:

            """
            Schruppen der Bauteillaenge mit einem Rest von drei Hundertsteln zur Soll Bauteillaenge
            Nur wenn die angegebene SOLL-Laenge kleiner als die IST-Laenge ist, wird die Laengenbeareitung auch durchgefuehrt.
            Von der Angabe der Soll laenge haengt auch ab, wie weit der Andruecker zum andruecken herabfaehrt.
            """

            fd.write("G43 H1\n")
            fd.write("G42 D1\n")
            
            #Wulst an der Bohrung abdrehen
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 + 0.3, bauteil_abschlusshoehe - 0.03, self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.naben_durchm/2 - 0.8, bauteil_abschlusshoehe - 0.03, self.cutting_speed_max))
            #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 - 0.05, bauteil_abschlusshoehe - 0.03, self.cutting_speed_max))
            #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
            
        #fd.write("G42 D1\n")
        if self.length_fase > 0 :
            """
            Wenn die Fase nicht groesser als 0 gewaehlt wird, dann wird der Teil des Prozesses ausgelassen
            """
            fd.write("G40\n")
            fd.write("G49\n")
            #fd.write("G61\n")
            fd.write("G43 H2\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x-1.5, bauteil_abschlusshoehe,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x-1.5, bauteil_abschlusshoehe + self.length_fase ,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2    + self.length_fase + 0.3, bauteil_abschlusshoehe + self.length_fase,self.positioning_speed/2))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2    -self.length_fase , bauteil_abschlusshoehe + self.length_fase ,self.fase_cutting_speed))
            fd.write("G4 P2.5\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 , bauteil_ankratzhoehe -0.7 ,self.positioning_speed))
        else:
            #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe,self.positioning_speed))
            pass
        if self.length_ist > self.length_soll:
            """
            Schlichten der Bauteillaenge auf die endgueltige Soll-Bauteillaenge
            """
            fd.write("G40\n")
            fd.write("G49\n")
            #fd.write("G61\n")
            fd.write("G43 H1\n")
            fd.write("G42 D1\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z ,self.positioning_speed))
            #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_ankratzhoehe -0.2 ,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 + 0.4, bauteil_abschlusshoehe,self.positioning_speed))

            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.naben_durchm/2-0.8, bauteil_abschlusshoehe,self.cutting_speed_max))
        
        fd.write("G40\n")
        fd.write("G49\n")
        fd.write("G64\n")
        
        
        '''
        #Gcode fuer das Fahren mit nur einem Werkzeug(Schlichterplatte)
        fd.write("G18\n")
        fd.write("M103\n")
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_inpos,3),self.positioning_speed/4))
        fd.write("G4 P0.5\n")
        fd.write("M115\n")
        fd.write("G4 P1\n")
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
        fd.write("M100\n")
        fd.write("G43 H1\n")
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe,self.positioning_speed))
        #fd.write("G42 D1\n")
        if self.length_fase > 0 :
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe + self.length_fase +0.1 ,self.positioning_speed))
            fd.write("G42 D1\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 + 0.1, bauteil_abschlusshoehe + self.length_fase +0.1,self.fase_cutting_speed*2))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 - self.length_fase, bauteil_abschlusshoehe,self.fase_cutting_speed))
        else:
            #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, bauteil_abschlusshoehe,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.bohrung_durchm/2 + 0.4, bauteil_abschlusshoehe,self.positioning_speed))
            
                
        if self.radius_kante > 0:
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.naben_durchm/2 + self.radius_kante -0.12 , bauteil_abschlusshoehe,self.cutting_speed_max))
            fd.write("g03 g18 X%3.3f Z%3.3f R%3.3f F%f\n" %(-self.naben_durchm/2 - 0.12, bauteil_abschlusshoehe + self.radius_kante, self.radius_kante, self.radius_cutting_speed))
            fd.write("G40\n")
            fd.write("G41 D1\n")
        
        fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-self.naben_durchm/2-0.8, bauteil_abschlusshoehe,self.cutting_speed_max))
        fd.write("G40\n")
        fd.write("G49\n")
        '''
            
        fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
        fd.write("M101\n")
        fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %((-float(self.x_home_diff)),(-float(self.z_home_diff)),self.positioning_speed))
        #print self.backen.block_ueb

            #print "erste punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][1][0]+self.schnitttiefe, self.backen.block_ueb[0][1][1]-self.schnitttiefe)
            #print "letzter Punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0]-self.schnitttiefe,self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0])
        #self.backen.old_profile.append(round(self.backen.new_profile[0][0]+0.2,3),
        fd.write("M116\n")
        
        fd.write("G4 P2\n")
        fd.write("M104\n")
        
        
        fd.write("M30")
        fd.close()
        
        
        return gcode
    
     

    def load_logfile(self, file_location):
        """Das Logfile am ort "file_location" wird eingelesen und in ein Dictionary geschrieben, auf das im Laufe der Programmausfuehrung zugegriffen werden kann,
        um Werte fuer die Maschine auszulesen.
        :param file_location: Ort der cnc_logfile.csv. In dieser befinden sich informationen zum aktuellen Stand der entsprechenden Maschine.(Siehe init Bereich
        :return:Ein Dictionary mit entsprechenden Schluesseln und Werten fuer die Maschine
        """
        log_dict = {}
        try:
            log_source = open(file_location, 'r')
            log_list = log_source.readlines()
            for i in log_list:
                log_dict[i.partition(',')[0].strip(';#\n')] = str(i.partition(',')[2].strip(';#\n'))
            log_source.close()
        except IOError:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Log Datei konnte nicht geladen werden\n")
            self.announce_error()
            return -1
        return log_dict
    

    def save_logfile(self, log_dict, file_location):
        """Schreiben des Dictionaries log_dict in ein File an der Stelle file Location.

        :param log_dict: Dictionary mit verschiedenen Parametern, die unabhaengig von den Laufzeitvariablen extern gespeichert werden sollen
        :param file_location: Pfad an dem das Dictionary gespeichert werden soll
        :return: 0 bei Erfolg. -1 bei IOError
        """

        #print "2"
        try:
            log_source = open(file_location, 'w+')
            for i, j in log_dict.iteritems():
                log_source.write(i + ',' + j + '\n')
            log_source.close()
        except IOError:
            #print "4"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter(),"Log Datei konnte nicht gespeichert werden\n")
            self.announce_error()
            return -1
            #print "5"
        return 0

        
    


    def make_new_file(self):
        """Wenn ein neues Programm erstellt werden soll, dann wird nach der Bestaetigung des neuen Namens diese Funktion aufgerufen, um ein neues File im nc_files
        Ordner zu erstellen. Gelingt das, wird check_file aufgerufen, ansonsten ein Fehler ausgegeben.

        """
        if self.req_new_backe == True:
            self.backe_file_name = self.nc_folder + "/" + self.new_file_entry.get_text()
            if (self.backe_file_name.find('.backe') == -1) or (self.backe_file_name.find('.BACKE') == -1):
                self.backe_file_name = self.backe_file_name + '.backe'
            try:
                fd = open(self.backe_file_name,'wb')
                fd.write(self.neue_backe_template)
                fd.close()
                return 0
            except IOError:
                self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Die Datei " + self.backe_file_name + " kann nicht geladen werden\n")
                self.announce_error()
        #elif self.req_new_bauteil == True:
            #self.bauteil_file_name = self.nc_folder + "/" + self.new_file_entry.get_text()
            #if (self.bauteil_file_name.find('.bauteil') == -1) or (self.bauteil_file_name.find('.BAUTEIL') == -1):
        #self.bauteil_file_name = self.bauteil_file_name + '.bauteil'
            #try:
        #fd = open(self.bauteil_file_name,'wb')
        #bt = bauteil(0,0,0,0,0,0,0,0,0,0)
        #pickle.dump(bt,fd)
        ##fd.write(self.neue_backe_template)
        #fd.close()
        #self.durchm_buf.set_text(
        #return 0
            #except IOError:
        #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Die Datei " + self.backe_file_name + " kann nicht geladen werden\n")
        #self.announce_error(self.backen_window)
        
        elif self.req_new_bauteil == True:
            self.bauteil_file_name = self.nc_folder + "/" + self.new_file_entry.get_text()
            if (self.bauteil_file_name.find('.bt') == -1) or (self.bauteil_file_name.find('.BT') == -1):
                self.bauteil_file_name = self.bauteil_file_name + '.bt'
            self.load_new_bauteil(self.neues_bauteil_template)
            try:
                fd = open(self.bauteil_file_name,'wb')
                json.dump(self.neues_bauteil_template,fd)
                fd.close()

            except IOError:
                self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Die Datei " + self.bauteil_file_name + " kann nicht geladen werden\n")
                self.announce_error()
            return 0
            
        #else:
            #self.new_file = True
            #self.file_name = self.new_file_entry.get_text()
            #if (self.file_name.find('.ngc') == -1) or (self.file_name.find('.NGC') == -1):
        #self.file_name = self.file_name + '.ngc'
            #self.file_location = self.new_file_folder.get_filename() + '/' +    self.file_name
            #self.akt_prgm_lbl.set_markup("Akt. Programm: <b>%s</b>" % self.file_name)
            #try:
        #self.new = open(self.file_location, 'w+')
            #except IOError:
        #self.file_location = self.file_location + '/' + self.file_name
        #try:
            #self.new = open(self.file_location, 'w+')
            #if self.save_as == True:
                #self.new.write(self.source_file.get_text(self.source_file.get_start_iter(), self.source_file.get_end_iter(),False))
                #self.need_refresh = True
                #self.sf_changed = False
            #self.new.close()
            #self.check_file()
            #return 0
        #except IOError:
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Die Datei " + self.file_location + " kann nicht geladen werden\n")
            #self.announce_error()
            #return -1
            

    def load_new_bauteil(self,param_dict):
        """Laedt Werte aus einem Dictionary in die entsprechenden Buffer und Textfelder der GUI
        TODO: Vielleicht kann man diese Funktion direkt an die Stelle verlegen wo sie aufgerufen wird, sollte dieser
        separate Funktionsaufruf unkomfortabel sein.
        Beim Laden der Bauteilparameter aus einer Datei wird nach dem Lesen der Datei das daraus erzeugte
        Dictionary an diese Funktion uebergeben. Dann werden die Parameter hier in die Buffer und Textfelder eingetragen

        :param param_dict: Dictionary mit den Parametern fuer die Bauteile.
        :return:
        """
        self.durchm_buf.delete_text(0,len(self.durchm_buf.get_text()))	
        self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), str(param_dict['durchm']), -1)
        self.rad_buf.delete_text(0,len(self.rad_buf.get_text()))	
        self.rad_buf.insert_text(self.rad_tf_bt.get_position(), str(param_dict['rueckenradius']), -1)
        self.hoehe_rad_buf.delete_text(0,len(self.hoehe_rad_buf.get_text()))	
        self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), str(param_dict['rueckenradius_hoehe']), -1)
        self.aufl_buf.delete_text(0,len(self.aufl_buf.get_text()))	
        self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), str(param_dict['aufl']), -1)
        self.spannfl_buf.delete_text(0,len(self.spannfl_buf.get_text()))	
        self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), str(param_dict['spannfl']), -1)
        self.length_ist_buf.delete_text(0,len(self.length_ist_buf.get_text()))	
        self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), str(param_dict['length_ist']), -1)
        self.length_soll_buf.delete_text(0,len(self.length_soll_buf.get_text()))	
        self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), str(param_dict['length_soll']), -1)
        self.naben_durchm_buf.delete_text(0,len(self.naben_durchm_buf.get_text()))	
        self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), str(param_dict['naben_durchm']), -1)
        self.bohrung_durchm_buf.delete_text(0,len(self.bohrung_durchm_buf.get_text()))	
        self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), str(param_dict['bohrung_durchm']), -1)
        self.radius_kante_buf.delete_text(0,len(self.radius_kante_buf.get_text()))	
        self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), str(param_dict['radius_kante']), -1)
        self.length_fase_buf.delete_text(0,len(self.length_fase_buf.get_text()))	
        self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), str(param_dict['length_fase']), -1)
        self.schnitttiefe_buf.delete_text(0,len(self.schnitttiefe_buf.get_text()))	
        self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), str(param_dict['schnitttiefe']), -1)
        #print "geschafft"
        #self.durchm_buf.insert
        
    
    def save_bauteil(self):
        """Eingegebene bauteilparameter werden in einem File mit dem Pfad bauteil_file_name gespeichert
        in frueheren Versionen wurden die Files im Pickle Format abgelegt. Diese sind nichr ordentlich von Menschen lesbar, darum
        wird jetzt das json Format benutzt.
        """
        self.neues_bauteil = {"durchm" : float(self.durchm_buf.get_text()) , 
                            "rueckenradius" : float(self.rad_buf.get_text()),
                            "rueckenradius_hoehe" : float(self.hoehe_rad_buf.get_text()),
                            "aufl" : float(self.aufl_buf.get_text()) ,
                            "spannfl" : float(self.spannfl_buf.get_text()),
                            "length_ist" : float(self.length_ist_buf.get_text()),
                            "length_soll" :float(self.length_soll_buf.get_text()),
                            "naben_durchm" : float(self.naben_durchm_buf.get_text()),
                            "bohrung_durchm" : float(self.bohrung_durchm_buf.get_text()),
                            "radius_kante" : float(self.radius_kante_buf.get_text()),
                            "length_fase" : float(self.length_fase_buf.get_text()),
                            "schnitttiefe" : float(self.schnitttiefe_buf.get_text())}
        try:
            fd = open(self.bauteil_file_name,'wb')
            json.dump(self.neues_bauteil, fd)
        #pickle.dump(self.neues_bauteil,fd)
            fd.close()

        except IOError:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Die Datei " + self.bauteil_file_name + " kann nicht geladen werden\n")
            self.announce_error()
            #self.durchm_buf.insert_text(self.durchm_tf.get_position(), , 1)
        self.log_dict["bauteil_file_name"] = self.bauteil_file_name
        self.log_dict_changed = True
        
        
        
    def passwd_check(self):
        """Vergleicht das eingegebene Passwort mit dem aus dem Logfile. Verglichen werden die Hashes und nicht die Passwoerter selbst.
        :return: True wenn Passwoerter uebereinstimmen, ansonsten False
        """
        i = 0
        
        passwd = str(self.passwd_check_buff.get_text())
        if len(passwd) !=4:
            self.passwd_answer.set_label("Das Passwort soll genau 4 Zeichen Lang sein")
            return False
        while i<10000:
            passwd = hashlib.sha256(passwd).hexdigest()
            i +=1
        #print passwd
        #print self.log_dict['passwd']
        self.durchm_buf.insert_text(self.durchm_tf.get_position(), '0', 1)
        if passwd == self.log_dict['passwd']:
            return True
        else:
            return False
    
    '''
    make_new_passwd:
    '''
    
    def make_new_passwd(self):
        """Vergleicht die Passwoerter in den Puffern zur Erstellung eines neuen Passwortes und ruft passwd_check auf. Falls die Anforderungen stimmen, wird
        der Hashwert des neuen Passworts berechnet und ins Logfile geschrieben.
        :return: True falls neues Passwort erzeugt wurde, ansonsten False
        """
        a = self.new_passwd_buff.get_text() 
        b = self.new_passwd_buff2.get_text()
        if len(a) !=4 or len(b) != 4:
            self.passwd_answer.set_label("Das Passwort soll genau 4 Zeichen Lang sein")
            return False
        check = self.passwd_check()
        self.new_passwd_buff.delete_text(0,len(self.new_passwd_buff.get_text()))
        self.new_passwd_buff2.delete_text(0,len(self.new_passwd_buff2.get_text()))
        if check == True and a == b:
            i = 0
            while i<10000:
                a = hashlib.sha256(a).hexdigest()
                i +=1
            
            self.log_dict['passwd'] = a
            return True
        elif check == False:
            self.passwd_answer.set_label("altes Passwort ist nicht korrekt")
            return False
        elif a!=b:
            self.passwd_answer.set_label("Die neuen Passwoerter stimmen nicht ueberein")
            return False
            
    '''
    periodic:

    '''
    
    def periodic(self):
        """
        fuehrt regelmaessig in 100ms Intervallen diverse Pruefungen und andere Operationen durch, da viele Sachen noch nicht eventgesteuert funktionieren
        Das sollte aber irgendwann geaendert werden. Der Funktionsaufruf findet am Ende der __INIT__ statt. dort kann auch der Intervall geaendert werden
        Momentan ist alles auskommentiert, da die Kommunikation mit den Nanotec Karten anders funktionieren wird. Wahrscheinlich wird
        es so aussehen, dass nur darauf gewartet wird, dass eine entsprechende Meldung aus dem Seriellen Port kommt, die dann interpretiert werden
        muss
        """
        if self.manual_btn.get_active() :
            self.manual_tbl.show()
            self.num_pad_tbl.hide()
        #elif self.preview_btn.get_active():
            #self.manual_tbl.hide()
            #self.num_pad_tbl.hide()
        elif self.num_pad_btn.get_active():
            self.manual_tbl.hide()
            self.num_pad_tbl.show()

        if self.manual_btn_bt.get_active() :
            self.manual_tbl_bt.show()
            self.num_pad_tbl_bt.hide()
        #elif self.preview_btn_bt.get_active():
            #self.manual_tbl_bt.hide()
            #self.num_pad_tbl_bt.hide()
        elif self.num_pad_btn_bt.get_active():
            self.manual_tbl_bt.hide()
            self.num_pad_tbl_bt.show()

        # self.time2 = time.time()
        #self.s.poll()
        #error = self.e.poll()
        #print "state = " + str(self.s.state)
        #self.dt = datetime.datetime.now()
        #self.dt = self.dt.replace(microsecond=0)
        #self.version_lbl.set_text(self.version + "         "    + str(self.dt))#%s:%s:%s" %( str(datetime.time.hour), str(datetime.time.minute), str(datetime.time.second))) #str(datetime.datetime.now()))
        #self.version2.set_text(self.version)
        ##self.time.set_text(str(self.dt))
        #self.version1.set_text(self.version)
        ##self.time1.set_text(str(self.dt))
        
        #if self.override_changed == True:#    float(self.cont_speed.get_value()) != float(self.s.feedrate):
            #self.c.feedrate(self.override_value)
            #self.override_changed = False
        
        
        #if self.s.state == 2 and self.s.id > 0 and self.machine_running == False:
            #self.state = self.s.state
            #self.machine_running = True
            
        #if self.state == 2 and self.s.state != self.state and self.machine_running == True:
            #self.option_box.set_sensitive(True)
            #self.option_box_bt.set_sensitive(True)
            #self.c.wait_complete(0.5)
            #self.c.mode(linuxcnc.MODE_MANUAL)
            #self.prgm_start.set_label("Start")
            #self.backe_start.set_label("Start")
            #self.state = self.s.state
            #self.machine_running = False
            #self.program_ready = False
            #self.backe_start.set_sensitive(True)
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.end_code = True
        ##print "laeuft die maschine? ",self.machine_running
    
        #if self.bauteil_is_ready and self.bauteil_prog_ready:
            #self.exp_time_bt.set_label("Maschine ist bereit und\ndas Bearbeitungsprogramm\nist geladen")
            #if self.s.homed != 0 and self.bearbeitung_beendet == False:
        #self.bauteil_start.set_sensitive(True)
        #self.bauteil_stop.set_sensitive(True)
            #else:
        #self.bauteil_start.set_sensitive(False)
        #self.bauteil_stop.set_sensitive(False)
        #elif not self.bauteil_is_ready and self.bauteil_prog_ready:
            #self.exp_time_bt.set_label("Programm ist geladen,\ndie Maschine ist noch\nnicht bereit")
            #self.bauteil_start.set_sensitive(False)
            #self.bauteil_stop.set_sensitive(False)
        #elif not self.bauteil_is_ready and not self.bauteil_prog_ready:
            #self.bauteil_start.set_sensitive(False)
            #self.bauteil_stop.set_sensitive(False)
            #self.exp_time_bt.set_label("Es muss noch ein\nProgramm geladen werden\nbevor gestartet werden kann")
        
        
        #if self.bearbeitung_beendet == False:
            #self.backe_to_main.set_sensitive(False)
            #self.bauteil_to_main.set_sensitive(False)
            #self.backe_power.set_sensitive(False)
            #self.bauteil_power.set_sensitive(False)
            #self.backe_estop.set_sensitive(False)
            #self.bauteil_estop.set_sensitive(False)
            
        #else:
            #self.bauteil_to_main.set_sensitive(True)
            #self.backe_to_main.set_sensitive(True)
            
            #self.backe_estop.set_sensitive(True)
            #self.bauteil_estop.set_sensitive(True)
        #if self.s.estop == False:
            #self.backe_power.set_sensitive(True)
            #self.bauteil_power.set_sensitive(True)
            
        
        

            
            
        

            
        #if self.machine_running == False and self.end_code == True:
            ##print " hier sind wir am ende einer Fahrt"
            #self.c.mode(linuxcnc.MODE_MDI)
            ##self.prgm_refresh_tbl.hal_pin.set(False)
            ##if self.bt_mode == True and self.fehlerfreie_fahrt == True:
        ##self.c.mdi("M104")
            #self.end_code = False
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.backe_start.set_sensitive(True)
            #self.man_ctrl_tbl.set_sensitive(True)
            #self.reset_koord.set_sensitive(True)
            #self.load_prog.set_sensitive(True)
            ###print "self.fehlerfreie_fahrt",self.fehlerfreie_fahrt
            ##print "self.bt_mode",self.bt_mode
            ##print "self.prep_mode",self.prep_mode
            #if self.fehlerfreie_fahrt == True and self.bt_mode == False and self.prep_mode == False :
        ##print "hier muss er bei fehlerfreier Fahrt hin"
        #self.log_dict['auflageflaeche_hoehe_m_schlichter'] = str(self.auflageflaeche_hoehe_m_schlichter)
        #self.log_dict_changed = True
        #self.profile_tuple = self.backen.ausdrehen_start()
        #self.backen.set_profile_tuple(self.profile_tuple)
        #self.backe_preview.set_from_file('plot.png')
        #fd = open(self.backe_file_name,"wb")
        ###print "\nprofile_tuple nach der bearbeitung wie sie dann in der Datei abgespeichert wird\n",self.profile_tuple
        ##print "\n\n"
        #pickle.dump(self.profile_tuple,fd)
        #fd.close()

        #if self.s.estop:
            ##self.estop_lbl.set_text("Not-Aus ist aktiv")
            ##self.restart_tab.hal_pin.set(True)
            #self.backe_to_main.set_sensitive(True)
            #self.bauteil_to_main_tbl.set_sensitive(True)
            #self.option_box.set_sensitive(False)
            #self.option_box_bt.set_sensitive(False)
            #self.homing = 0
        #else:
            #if self.backe_to_main.get_sensitive() != False:
        ##self.estop_lbl.set_text("Not-Aus ist NICHT aktiv")
        #self.backe_to_main.set_sensitive(False)
        #self.bauteil_to_main_tbl.set_sensitive(False)
        ##self.estop_led.hal_pin.set(False)
        #if self.machine_running == False:
            #self.option_box.set_sensitive(True)
            #self.option_box_bt.set_sensitive(True)
        ##self.restart_tab.hal_pin.set(False)
            
        #if self.s.task_state != linuxcnc.STATE_ON:
            ###self.machine_lbl.set_text("Maschine ist ausgeschaltet")
            ##self.brush_ctrl.hal_pin.set(True)
            #self.option_box.set_sensitive(False)
            #self.option_box_bt.set_sensitive(False)
        
        #else:
            #pass

        
        #if self.log_dict_changed == True:
            #self.save_logfile(self.log_dict,self.log_name)
            #self. log_dict_changed = False
            
        #self.time3 = time.time()
        #self.time2 = self.time3 - self.time2
        ##print "Periodic: ", self.time2
        return True

        
     
    '''fp_GUI_func_def_end'''
    #
    '''main_window_signals_begin'''
    ##
    '''fp_tab_signals_begin'''
    
    '''
    rechts -> x+
    links -> x-
    runter -> z-
    hoch -> z+
    C -> spindel start
    X -> spindel stop
    F12 -> override+
    F11 -> override-
    1 -> greifer schliessen zustand merken und das andere ausfuehren
    
    '''	
    #def on_main_window_key_press_event(self, widget, event):
    
    def on_backen_window_key_press_event(self, widget, event):
        self.master_config.emit("key-press-event",event)
        
    def on_bauteil_window_key_press_event(self, widget, event):
        self.master_config.emit("key-press-event",event)
    
    def on_backen_window_key_release_event(self, widget, event):
        self.master_config.emit("key-release-event",event)
        
    def on_bauteil_window_key_release_event(self, widget, event):
        self.master_config.emit("key-release-event",event)



    def on_master_config_key_press_event(self, widget, event):
        """in dieser Funktion werden die Key Press Events des Config Windows ausgewertet. Fuer jedes weitere Fenster gibt es ein entsprechendes
        Event, welches diese Funktion aufruft und die Funktionalitaet auf die anderen Windows erweitert.
        Muss in Zukunft ebenfalls fuer die Serielle Nanotec Steuerung angepasst werden


        """

        keyname = gtk.gdk.keyval_name(event.keyval)
        if self.key_is_still_pressed == False:
            if keyname == "C":
                self.m100_btn.emit("clicked")
                self.key_is_still_pressed = True
            elif keyname == "X":
                self.m101_btn.emit("clicked")
                self.key_is_still_pressed = True
                #elif keyname == "1":
            #if self.is_closed==True:
                #self.m116_btn.emit("clicked")
                #self.key_is_still_pressed = True
            #else:
                #self.m115_btn.emit("clicked")
                #self.key_is_still_pressed = True
            elif keyname == "F1":
                self.conf_speed_0.set_active(True)
                self.key_is_still_pressed = True
            elif keyname == "F2":
                self.conf_speed_1.set_active(True)
                self.key_is_still_pressed = True
            elif keyname == "F3":
                self.conf_speed_2.set_active(True)
                self.key_is_still_pressed = True
            elif keyname == "F4":
                self.conf_speed_3.set_active(True)
                self.key_is_still_pressed = True
            elif keyname == "F5":
                self.setup_referenzfahrt.emit("clicked")
                self.key_is_still_pressed = True
            elif keyname == "F12":
                if self.cont_speed.get_value() < 100:
                    self.cont_speed.set_value(self.cont_speed.get_value() + 10)
                    self.key_is_still_pressed = True
            elif keyname == "F11":
                if self.cont_speed.get_value() > 5:
                    self.cont_speed.set_value(self.cont_speed.get_value() - 10)
                    self.key_is_still_pressed = True
            elif event.keyval == 65361:
                self.setup_x_l.emit("pressed")
                self.key_is_still_pressed = True
            elif event.keyval == 65363:
                self.setup_x_r.emit("pressed")
                self.key_is_still_pressed = True
            elif event.keyval == 65362:
                self.setup_z_d.emit("pressed")
                self.key_is_still_pressed = True
            elif event.keyval == 65364:
                self.setup_z_u.emit("pressed")
                self.key_is_still_pressed = True

        #print "Key %s (%d) was pressed" % (keyname, event.keyval)
        
    #def on_main_window_key_release_event(self, widget, event):
    def on_master_config_key_release_event(self, widget, event):
        self.key_is_still_pressed = False
        keyname = gtk.gdk.keyval_name(event.keyval)
        if event.keyval == 65361:
            self.setup_x_l.emit("released")
            #self.key_is_still_pressed = True
        elif event.keyval == 65363:
            self.setup_x_r.emit("released")
            #self.key_is_still_pressed = True
        elif event.keyval == 65362:
            self.setup_z_u.emit("released")
            #self.key_is_still_pressed = True
        elif event.keyval == 65364:
            self.setup_z_d.emit("released")
    
    def on_oeffnen_clicked(self, widget, data=None):
        pass
    def on_abbrechen_clicked(self, widget, data=None):
        pass
        
    def on_m100_btn_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::m100:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #pass
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M100")
        #self.c.mode(linuxcnc.MODE_AUTO)
        
    #def on_m101_btn_clicked(self, widget, data=None):
        #self.backen_window.show()
        #self.backe_preview.set_from_file("plot.png")
        #self.main_window.hide()
    
    def on_m101_btn_clicked(self, widget, data=None):
        
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::m101:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #koordinaten = self.backen.get_old_profile()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M101")
        #self.c.mode(linuxcnc.MODE_AUTO)
        
    def on_m116_btn_clicked(self, widget, data=None):
        koordinaten = self.backen.get_gcode_koord()
        
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::m116:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M116")
        #self.is_closed = False
        #self.c.mode(linuxcnc.MODE_AUTO)
        
        
    def on_backe_to_main_clicked(self, widget, data=None):
        #self.hal_gremlin1.destroy()
        
        self.backen_window.hide()
        self.init_window.show()
    
    def on_reset_koord_clicked(self, widget, data=None):
        #print "hier passiert was"
        
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::koordinaten_reset:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.s.poll()
        #self.setup_referenzfahrt.emit("clicked")
        #self.c.mode(linuxcnc.MODE_MDI)
        
        #self.c.wait_complete()
        #self.c.mdi("G92.1")
        #self.c.wait_complete(0.5)
        #self.bearbeitung_beendet = True
        #self.backe_start.set_sensitive(False)
        #self.backe_stop.set_sensitive(False)

        #self.c.mdi("M115")

        #self.backe_power.set_sensitive(True)
        
        
    def on_bauteil_power_clicked(self, widget, data=None):
        self.backe_power.emit("toggled")
    
    
    
    def on_bauteil_estop_clicked(self, widget, data=None):
        self.backe_estop.emit("toggled")
    
    def on_config_power_clicked(self, widget, data=None):
        self.backe_power.emit("toggled")
    
    def on_config_estop_clicked(self, widget, data=None):
        self.backe_estop.emit("toggled")
    
    
    def on_backe_power_toggled(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::backen_power:: btn muss neu implementiert werden.\n")
        self.announce_error()
        if self.bearbeitung_beendet == False:
            self.reset_koord.emit("clicked")
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , 'Vor dem Beenden des Programmteils, die Maschine erneut einschalten und den "Bearbeitung Beenden"-Button Druecken\n')
            #self.announce_error()
            
    def on_backe_estop_toggled(self, widget, data=None):	
        #print "hier ist was verkehrt"
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::backe_estop:: btn muss neu implementiert werden.\n")
        self.announce_error()
        if self.bearbeitung_beendet == False:
            self.reset_koord.emit("clicked")
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , 'Vor dem Beenden des Programmteils, die Maschine erneut einschalten und den "Bearbeitung Beenden"-Button Druecken\n')
            #self.announce_error()
    
    def on_calc_clicked(self, widget, data=None):
        self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Bitte warten</b>")
        #self.setup_referenzfahrt.emit("clicked")
        #self.last_seen = self.backen_window
        self.prep_mode = False
        self.backen.abgenutzt = False
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.wait_complete()
        #self.c.mdi("M116")
        #self.c.reset_interpreter
        try:
            os.remove("plot.png")
        except OSError:
            pass
        #self.cutting_speed_max = float(self.schnittgeschw_buf.get_text())	

        self.durchm = float(self.durchm_buf.get_text())
        #print "1"
        if self.durchm/2 > self.x_offset_backe+self.backenlaenge:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu gross fuer die Backen\n")
            self.announce_error()
            return 0
        if self.durchm/2 < self.x_offset_backe:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu klein fuer die Backen\n")
            self.announce_error()
            return 0
        self.radius = float(self.rad_buf.get_text())
        #print "2"
        self.radius_hoehe = float(self.hoehe_rad_buf.get_text())
        self.schnitttiefe = float(self.schnitttiefe_buf.get_text())
        self.aufl = float(self.aufl_buf.get_text())
        self.spannfl = float(self.spannfl_buf.get_text())
        
        #if self.radius+self.aufl<self.durchm/2-self.x_offset_backe:
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Wahrscheinlich ist die Auflageflaeche oder der Radius nicht der Zeichnung\nentsprechend eingetragen")
            #self.announce_error()
            #return 0
        #print "3"
        #self.profile_tuple = [[0,0]]
        self.randhoehe = 1#float(self.randhoehe_buf.get_text())
        self.randbreite = 1#float(self.randbreite_buf.get_text())
        #print "self.profile_tuple:" , self.profile_tuple
        if not(self.schnitttiefe > 0) or self.schnitttiefe > 0.25:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Vergessen die Schnitttiefe richtig einzutragen?")
            self.announce_error()
            return 0
        
        #self.ausdrehlimit = float(self.ausdrehlimit_buf.get_text())
        #self.profile_tuple=[[3.5,0],[3,2],[2.0,2.5],[2,4],[1,4],[0.7,5],[0.5,5.5],[0,6],[0.5,5.5],[1,5],[0,3],[2,3.5],[1,3],[3.5,1],[3.2,2],[4,0],[0,6]]
        #print "4"
        self.profile_tuple = self.backen.ausdrehen_calc([[self.durchm/2,0]],self.profile_tuple,self.cutting_speed_max,self.aufl ,self.spannfl,self.schnitttiefe,self.randbreite,self.randhoehe,self.radius,self.radius_hoehe,self.ausdrehlimit_z,self.x_offset_backe,self.backenlaenge)

        if self.backen.abgenutzt == True:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Backe ist aufgebraucht\n")
            self.announce_error()
        
        self.backe_preview.clear()
        ##print "6"
        self.backe_preview.set_from_file('plot.png')
        self.program = 1
        self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Kein Programm\ngeladen</b>")
        self.backe_start.set_sensitive(False)
        self.backe_stop.set_sensitive(False)
        self.est_time.set_text("Der Drehprozess wird \netwa %d Minuten dauern"%round(self.backen.est_time+5,0))
        
        #print "7"
    
    def on_backe_start_clicked(self, widget, data=None):
        
            #print getattr
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::backe_start:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.manual_btn.set_active(True)
        #self.setup_speed3.set_active(True)
        #self.fehlerfreie_fahrt = True
        ##self.s.poll()
        ##self.c.wait_complete(1)
        #self.backe_start.set_sensitive(False)
        #self.man_ctrl_tbl.set_sensitive(False)
        #self.reset_koord.set_sensitive(False)
        #self.load_prog.set_sensitive(False)
        #if not self.machine_running and    not self.machine_paused:
            #shutil.copy(self.backe_file_name, self.backe_file_name + ".backup")
            #fd = open(self.backe_file_name,"wb")
            #pickle.dump(self.backen.get_old_profile(),fd)
            #fd.close()
            #self.log_dict['backe_file_name'] = self.backe_file_name
            #self.log_dict_changed = True
            #self.backen.set_profile_tuple(self.profile_tuple)
            #self.backe_preview.set_from_file('plot.png')
            
        #if self.s.task_state == 4 and self.machine_running == False and self.machine_paused == False:
            ##self.c.mode(linuxcnc.MODE_AUTO)
            
            ##self.c.mode(linuxcnc.MODE_MANUAL)	
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.backe_start.set_label("Pause")
            #self.machine_running = True
            #self.c.wait_complete()
            #self.c.auto(linuxcnc.AUTO_RUN,1)
            #self.s.poll()
            #self.state = self.s.state
        #elif self.machine_running == True :
            ##self.c.wait_complete(0.5)
            #self.backe_start.set_label("Weiter")
            #self.machine_running = False
            #self.machine_paused = True
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.c.auto(linuxcnc.AUTO_PAUSE)
        #elif self.machine_running == False and self.machine_paused == True:
            #self.backe_start.set_label("Pause")
            #self.machine_running = True
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.c.auto(linuxcnc.AUTO_RESUME)
        #self.option_box.set_sensitive(False)
        #self.option_box_bt.set_sensitive(False)
            
    def on_backe_stop_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::backe_stop:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.fehlerfreie_fahrt = False
        ##self.c.abort()
     
        #self.backe_start.set_label("Start")
        #self.option_box.set_sensitive(True)
        #self.option_box_bt.set_sensitive(True)
        #self.c.wait_complete()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.wait_complete()
        #self.c.mdi("M101")
        #self.c.wait_complete()
        #self.c.mdi("G40")
        #self.c.wait_complete()
        #self.c.mdi("G49")
        #self.c.wait_complete()
        #self.c.mdi("G64")
        #self.c.wait_complete()
        ##self.c.mode(linuxcnc.MODE_AUTO)
        #self.c.mode(linuxcnc.MODE_AUTO)
        
            
    def on_load_prog_clicked(self, widget, data=None):
        #print "1"
        #self.hal_gremlin1.set_property('show_program',False)
        #print "2"
        if self.program == 1:
            koordinaten = self.backen.get_gcode_koord()
            #print koordinaten
            gcode = self.backen_ordner + str(round(time.time(),0))+'.ngc'
            j = 0
            fd = open(gcode,'w+')

            fd.write("T1\n")
            fd.write("M115\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(self.safe_pos_x, self.safe_pos_z,self.positioning_speed))
            fd.write("M100\n")

            fd.write("G4 P1\n")

            for i in koordinaten:
                if self.backen.ueb_counter == 0:
                    fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[1][0],3),round(self.z_offset_backe+self.backen.new_profile[0][1]-0.5,3),self.positioning_speed))

                self.backen.aufl_counter -=1
                self.backen.ueb_counter -=1
                j+=1

                #print "g01 X%3.3f Z%3.3f F%f    (schritt:%d)\n" %((i[0][0]),(round(self.z_offset_backe+i[0][1]-self.schnitttiefe*1.3,3)),self.positioning_speed,j)
                fd.write("g01 X%3.3f Z%3.3f F%f    (schritt:%d)\n" %((i[0][0]),(round(self.z_offset_backe+i[0][1]-self.schnitttiefe*1.3,3)),self.positioning_speed,j))
                #print "g01 X%3.3f Z%3.3f F%f" %((i[0][0]),(self.z_offset_backe+i[0][1]),self.cutting_speed_max)
                #print "g01 X%3.3f Z%3.3f F%f" %((i[1][0]),(self.z_offset_backe+i[1][1]),self.cutting_speed_max)
                if self.backen.aufl_counter == 0:
                    fd.write("(hier faengt die Auflageflaeche an)\n")

                    fd.write("g01 X%3.3f Z%3.3f F%f (1)\n" %((i[0][0]),(round(self.z_offset_backe+i[0][1]-self.schnitttiefe*0.2,3)),self.cutting_speed_max))
                    fd.write("g01 X%3.3f Z%3.3f F%f (2)\n" %((i[1][0]),(round(self.z_offset_backe+i[1][1]-self.schnitttiefe*0.2,3)),self.cutting_speed_max))
                    fd.write("g01 X%3.3f Z%3.3f F%f (5)\n" %((i[1][0]),(self.z_offset_backe+i[1][1]),self.cutting_speed_max))
                    fd.write("g01 X%3.3f Z%3.3f F%f (6)\n" %((i[0][0]),(self.z_offset_backe+i[1][1]),self.cutting_speed_max))

                    if self.aufl >3.0:
                        fd.write("g01 X%3.3f Z%3.3f F%f (1)\n" %((i[0][0]-3.0+0.1),(self.z_offset_backe+i[1][1]),self.cutting_speed_max/2))
                        fd.write("g03 g18 X%3.3f Z%3.3f R%3.3f F%f\n" %(round((i[0][0]-3.0),3), round(self.z_offset_backe+i[1][1]+0.1,3),round(0.1,3), self.radius_cutting_speed))
                    else:
                        fd.write("g01 X%3.3f Z%3.3f F%f (1)\n" %((i[0][0]-self.aufl+0.1),(self.z_offset_backe+i[1][1]),self.cutting_speed_max/2))
                        fd.write("g03 g18 X%3.3f Z%3.3f R%3.3f F%f\n" %(round((i[0][0]-self.aufl),3), round(self.z_offset_backe+i[1][1]+0.1,3),round(0.1,3), self.radius_cutting_speed))

                    self.auflageflaeche_hoehe_m_schlichter = self.z_offset_backe+i[1][1]+self.schlichter_comp #schlichter kompensation

                else:
                    fd.write("g01 X%3.3f Z%3.3f F%f\n" %((i[0][0]),(self.z_offset_backe+i[0][1]),self.cutting_speed_max))
                    fd.write("g01 X%3.3f Z%3.3f F%f\n" %((i[1][0]),(self.z_offset_backe+i[1][1]),self.cutting_speed_max))
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(self.x_offset_backe, self.z_offset_backe,self.positioning_speed))
            if self.backen.block_ueb != [0,0]:
                fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[1][0],3),round(self.z_offset_backe+self.backen.new_profile[0][1]-0.5,3),self.positioning_speed))
                #fd.write("g01 Z%3.3f F%3.3f\n" %(self.z_offset_backe+self.backen.ueb_start[1]-0.2, self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(self.backen.ueb_start[0]+0.05,round(self.z_offset_backe+self.backen.ueb_start[1]-self.schnitttiefe*1.3,3), self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%3.3F\n" %(self.backen.ueb_start[0]+0.015,self.z_offset_backe+self.backen.ueb_start[1]+0.015, self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%3.3F\n" %(self.backen.ueb_end[0]+0.015,self.z_offset_backe+self.backen.ueb_end[1]+0.015, round(self.cutting_speed_slow,3)))
                fd.write("g01 X%3.3f Z%3.3f F%3.3F\n" %(self.backen.ueb_end[0]-0.25,self.z_offset_backe+self.backen.ueb_end[1]+0.015, round(self.cutting_speed_slow,3)))

            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[1][0],3),round(self.z_offset_backe+self.backen.new_profile[0][1]-0.5,3),self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[0][0]-0.2,3),round(self.z_offset_backe+self.backen.new_profile[1][1]-0.2,3),self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[0][0]+0.12,3),round(self.z_offset_backe+self.backen.new_profile[1][1]+0.12,3),self.cutting_speed_slow))
            fd.write("G4 P2\n")
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(round(self.backen.new_profile[0][0]-0.2,3),round(self.z_offset_backe+self.backen.new_profile[1][1]-0.2,3),self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(self.safe_pos_x, self.safe_pos_z,self.positioning_speed))
            fd.write("M101\n")

            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %((-float(self.x_home_diff)+2),(-float(self.z_home_diff)+2),self.positioning_speed))
            #print self.backen.block_ueb
            fd.write("M116\n")
                #print "erste punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][1][0]+self.schnitttiefe, self.backen.block_ueb[0][1][1]-self.schnitttiefe)
                #print "letzter Punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0]-self.schnitttiefe,self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0])
            #self.backen.old_profile.append(round(self.backen.new_profile[0][0]+0.2,3),
            fd.write("M30")
            fd.close()
            #print "auflageflaeche_hoehe_m_schlichter", self.auflageflaeche_hoehe_m_schlichter

            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.program_open(gcode)
            #self.c.mode(linuxcnc.MODE_MANUAL)
            self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Backen ausdrehen</b>")
            self.backe_start.set_sensitive(True)
            self.backe_stop.set_sensitive(True)
            self.program = 2
        elif self.program == 0:
            self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Bitte erst\nKoordinaten\nberechnen</b>")
            self.backe_start.set_sensitive(False)
            self.backe_stop.set_sensitive(False)
        elif self.program == 2:
            self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Programm ist\nbereits\ngeladen</b>")
                #print "3"
                #self.hal_gremlin1.set_property('show_program',True)

                #self.hal_gremlin1.set_property('view','y')
                #self.hal_gremlin1.set_property('show_live_plot',False)
                #print "4"
                #break
    def on_load_backe_clicked(self, widget, data=None):
        self.load_backe_window.show()
        self.backen_window.hide()
        
        #self.schnitttiefe_tf self.builder.get_object("schnitttiefe_tf")
        #self.durchm_tf = self.builder.get_object("durchm_tf")
        #self.rad_tf = self.builder.get_object("rad_tf")
        #self.aufl_tf = self.builder.get_object("aufl_tf")
        #self.spannfl_tf = self.builder.get_object("spannfl_tf")
        #self.length_ist_tf= self.builder.get_object("length_ist_tf")
        #self.length_soll_tf= self.builder.get_object("length_soll_tf")
        #self.naben_durchm_tf= self.builder.get_object("naben_durchm_tf")
        #self.bohrung_durchm_tf = self.builder.get_object("bohrung_durchm_tf")
        #self.radius_kante_tf= self.builder.get_object("radius_kante_tf")
        #self.length_fase_tf= self.builder.get_object("length_fase_tf")
        
    def on_g921_clicked(self, widget, data=None):
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.wait_complete()
        #self.c.mdi("G92.1")
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::g92.1:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #print
        
        
    def on_num_pad_0_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '0', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '0', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '0', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '0', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
            
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '0', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '0', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
            
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '0', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '0', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '0', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '0', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '0', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '0', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '0', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
        
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '0', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '0', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '0', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '0', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '0', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '0', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '0', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '0', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '0', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '0', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '0', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '0', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '0', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '0', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '0', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '0', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '0', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '0', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
        
    def on_num_pad_1_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '1', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '1', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '1', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '1', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '1', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '1', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '1', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '1', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '1', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '1', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '1', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '1', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '1', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
        
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '1', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '1', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '1', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '1', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '1', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '1', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '1', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '1', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '1', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '1', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '1', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
            
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '1', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '1', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '1', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '1', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '1', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '1', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '1', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_2_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '2', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '2', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '2', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '2', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '2', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '2', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '2', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '2', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '2', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '2', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '2', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '2', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '2', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '2', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '2', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '2', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '2', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '2', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '2', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '2', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '2', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '2', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '2', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '2', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '2', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '2', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '2', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '2', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '2', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '2', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '2', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_3_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '3', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '3', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '3', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '3', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '3', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '3', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '3', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '3', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '3', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '3', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '3', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '3', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '3', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '3', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '3', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '3', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '3', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '3', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '3', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '3', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '3', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '3', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '3', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '3', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '3', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '3', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '3', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '3', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '3', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '3', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '3', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_4_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '4', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '4', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '4', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '4', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '4', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '4', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '4', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '4', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '4', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '4', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '4', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '4', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '4', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '4', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '4', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '4', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '4', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '4', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '4', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '4', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '4', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '4', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '4', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '4', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '4', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '4', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '4', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '4', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '4', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '4', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '4', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_5_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '5', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '5', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '5', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '5', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '5', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '5', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '5', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '5', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '5', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '5', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '5', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '5', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '5', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '5', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '5', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '5', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '5', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '5', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '5', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '5', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '5', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '5', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '5', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '5', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '5', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '5', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '5', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '5', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '5', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '5', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '5', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_6_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '6', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '6', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '6', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '6', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '6', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '6', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '6', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '6', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '6', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '6', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '6', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '6', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '6', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '6', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '6', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '6', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '6', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '6', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '6', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '6', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '6', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '6', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '6', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '6', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '6', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '6', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '6', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '6', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '6', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '6', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '6', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_7_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '7', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '7', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '7', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '7', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '7', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '7', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '7', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '7', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '7', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '7', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '7', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '7', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '7', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '7', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '7', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '7', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '7', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '7', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '7', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '7', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '7', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '7', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '7', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '7', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '7', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '7', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '7', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '7', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '7', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '7', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '7', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_8_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '8', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '8', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '8', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '8', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '8', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '8', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '8', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '8', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '8', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '8', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '8', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '8', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '8', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '8', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '8', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '8', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '8', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '8', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '8', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '8', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '8', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '8', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '8', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '8', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '8', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '8', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '8', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '8', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '8', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '8', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '8', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_9_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '9', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '9', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '9', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '9', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '9', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '9', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '9', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '9', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '9', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '9', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '9', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '9', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '9', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '9', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '9', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '9', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '9', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '9', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '9', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '9', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '9', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '9', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '9', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '9', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '9', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '9', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '9', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '9', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '9', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '9', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '9', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
    def on_num_pad_dot_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf.get_position(), '.', 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position() + 1)
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf.get_position(), '.', 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position() + 1)
        elif self.durchm_tf.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf.get_position(), '.', 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position() + 1)
        elif self.rad_tf.has_focus():
            self.rad_buf.insert_text(self.rad_tf.get_position(), '.', 1)
            self.rad_tf.set_position(self.rad_tf.get_position() + 1)
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf.get_position(), '.', 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position() + 1)
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.insert_text(self.hoehe_rad_tf_bt.get_position(), '.', 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position() + 1)
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf.get_position(), '.', 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position() + 1)
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf.get_position(), '.', 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position() + 1)
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf.get_position(), '.', 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position() + 1)
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf.get_position(), '.', 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position() + 1)
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf.get_position(), '.', 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position() + 1)
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf.get_position(), '.', 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position() + 1)
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf.get_position(), '.', 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position() + 1)
            
        elif self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.insert_text(self.length_fase_tf_bt.get_position(), '.', 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position() + 1)
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.insert_text(self.schnitttiefe_tf_bt.get_position(), '.', 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position() + 1)
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.insert_text(self.durchm_tf_bt.get_position(), '.', 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position() + 1)
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.insert_text(self.rad_tf_bt.get_position(), '.', 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position() + 1)
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.insert_text(self.aufl_tf_bt.get_position(), '.', 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position() + 1)
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.insert_text(self.spannfl_tf_bt.get_position(), '.', 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position() + 1)
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.insert_text(self.length_ist_tf_bt.get_position(), '.', 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position() + 1)
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.insert_text(self.length_soll_tf_bt.get_position(), '.', 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position() + 1)
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.insert_text(self.naben_durchm_tf_bt.get_position(), '.', 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position() + 1)
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.insert_text(self.bohrung_durchm_tf_bt.get_position(), '.', 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position() + 1)
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.insert_text(self.radius_kante_tf_bt.get_position(), '.', 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position() + 1)
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.insert_text(self.x_offset_backe_tf.get_position(), '.', 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position() + 1)
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.insert_text(self.z_offset_backe_tf.get_position(), '.', 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position() + 1)
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.insert_text(self.x_home_diff_tf.get_position(), '.', 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position() + 1)
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.insert_text(self.z_home_diff_tf.get_position(), '.', 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position() + 1)
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.insert_text(self.ausdrehlimit_z_tf.get_position(), '.', 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position() + 1)
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.insert_text(self.schlichter_comp_tf.get_position(), '.', 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position() + 1)
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.insert_text(self.backenlaenge_tf.get_position(), '.', 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position() + 1)
            
            #get_position()-1, 1)
    def on_num_pad_empty_clicked(self, widget, data=None):
        if self.length_fase_tf.has_focus():
            self.length_fase_buf.delete_text(self.length_fase_tf.get_position()-1, 1)
            self.length_fase_tf.set_position(self.length_fase_tf.get_position())
        elif self.schnitttiefe_tf.has_focus():
            self.schnitttiefe_buf.delete_text(self.schnitttiefe_tf.get_position()-1, 1)
            self.schnitttiefe_tf.set_position(self.schnitttiefe_tf.get_position())
        elif self.durchm_tf.has_focus():
            self.durchm_buf.delete_text(self.durchm_tf.get_position()-1, 1)
            self.durchm_tf.set_position(self.durchm_tf.get_position())
        elif self.rad_tf.has_focus():
            self.rad_buf.delete_text(self.rad_tf.get_position()-1, 1)
            self.rad_tf.set_position(self.rad_tf.get_position())
        
        elif self.hoehe_rad_tf.has_focus():
            self.hoehe_rad_buf.delete_text(self.hoehe_rad_tf.get_position()-1, 1)
            self.hoehe_rad_tf.set_position(self.hoehe_rad_tf.get_position())
        elif self.hoehe_rad_tf_bt.has_focus():
            self.hoehe_rad_buf.delete_text(self.hoehe_rad_tf_bt.get_position()-1, 1)
            self.hoehe_rad_tf_bt.set_position(self.hoehe_rad_tf_bt.get_position())
        
        elif self.aufl_tf.has_focus():
            self.aufl_buf.delete_text(self.aufl_tf.get_position()-1, 1)
            self.aufl_tf.set_position(self.aufl_tf.get_position())
        elif self.spannfl_tf.has_focus():
            self.spannfl_buf.delete_text(self.spannfl_tf.get_position()-1, 1)
            self.spannfl_tf.set_position(self.spannfl_tf.get_position())
        elif self.length_ist_tf.has_focus():
            self.length_ist_buf.delete_text(self.length_ist_tf.get_position()-1, 1)
            self.length_ist_tf.set_position(self.length_ist_tf.get_position())
        elif self.length_soll_tf.has_focus():
            self.length_soll_buf.delete_text(self.length_soll_tf.get_position()-1, 1)
            self.length_soll_tf.set_position(self.length_soll_tf.get_position())
        elif self.naben_durchm_tf.has_focus():
            self.naben_durchm_buf.delete_text(self.naben_durchm_tf.get_position()-1, 1)
            self.naben_durchm_tf.set_position(self.naben_durchm_tf.get_position())
        elif self.bohrung_durchm_tf.has_focus():
            self.bohrung_durchm_buf.delete_text(self.bohrung_durchm_tf.get_position()-1, 1)
            self.bohrung_durchm_tf.set_position(self.bohrung_durchm_tf.get_position())
        elif self.radius_kante_tf.has_focus():
            self.radius_kante_buf.delete_text(self.radius_kante_tf.get_position()-1, 1)
            self.radius_kante_tf.set_position(self.radius_kante_tf.get_position())
            
        if self.length_fase_tf_bt.has_focus():
            self.length_fase_buf.delete_text(self.length_fase_tf_bt.get_position()-1, 1)
            self.length_fase_tf_bt.set_position(self.length_fase_tf_bt.get_position())
        elif self.schnitttiefe_tf_bt.has_focus():
            self.schnitttiefe_buf.delete_text(self.schnitttiefe_tf_bt.get_position()-1, 1)
            self.schnitttiefe_tf_bt.set_position(self.schnitttiefe_tf_bt.get_position())
        elif self.durchm_tf_bt.has_focus():
            self.durchm_buf.delete_text(self.durchm_tf_bt.get_position()-1, 1)
            self.durchm_tf_bt.set_position(self.durchm_tf_bt.get_position())
        elif self.rad_tf_bt.has_focus():
            self.rad_buf.delete_text(self.rad_tf_bt.get_position()-1, 1)
            self.rad_tf_bt.set_position(self.rad_tf_bt.get_position())
        elif self.aufl_tf_bt.has_focus():
            self.aufl_buf.delete_text(self.aufl_tf_bt.get_position()-1, 1)
            self.aufl_tf_bt.set_position(self.aufl_tf_bt.get_position())
        elif self.spannfl_tf_bt.has_focus():
            self.spannfl_buf.delete_text(self.spannfl_tf_bt.get_position()-1, 1)
            self.spannfl_tf_bt.set_position(self.spannfl_tf_bt.get_position())
        elif self.length_ist_tf_bt.has_focus():
            self.length_ist_buf.delete_text(self.length_ist_tf_bt.get_position()-1, 1)
            self.length_ist_tf_bt.set_position(self.length_ist_tf_bt.get_position())
        elif self.length_soll_tf_bt.has_focus():
            self.length_soll_buf.delete_text(self.length_soll_tf_bt.get_position()-1, 1)
            self.length_soll_tf_bt.set_position(self.length_soll_tf_bt.get_position())
        elif self.naben_durchm_tf_bt.has_focus():
            self.naben_durchm_buf.delete_text(self.naben_durchm_tf_bt.get_position()-1, 1)
            self.naben_durchm_tf_bt.set_position(self.naben_durchm_tf_bt.get_position())
        elif self.bohrung_durchm_tf_bt.has_focus():
            self.bohrung_durchm_buf.delete_text(self.bohrung_durchm_tf_bt.get_position()-1, 1)
            self.bohrung_durchm_tf_bt.set_position(self.bohrung_durchm_tf_bt.get_position())
        elif self.radius_kante_tf_bt.has_focus():
            self.radius_kante_buf.delete_text(self.radius_kante_tf_bt.get_position()-1, 1)
            self.radius_kante_tf_bt.set_position(self.radius_kante_tf_bt.get_position())
        
        elif self.x_offset_backe_tf.has_focus():
            self.x_offset_backe_conf_buf.delete_text(self.x_offset_backe_tf.get_position()-1, 1)
            self.x_offset_backe_tf.set_position(self.x_offset_backe_tf.get_position())
        elif self.z_offset_backe_tf.has_focus():
            self.z_offset_backe_conf_buf.delete_text(self.z_offset_backe_tf.get_position()-1, 1)
            self.z_offset_backe_tf.set_position(self.z_offset_backe_tf.get_position())
        elif self.x_home_diff_tf.has_focus():
            self.x_home_diff_conf_buf.delete_text(self.x_home_diff_tf.get_position()-1, 1)
            self.x_home_diff_tf.set_position(self.x_home_diff_tf.get_position())
        elif self.z_home_diff_tf.has_focus():
            self.z_home_diff_conf_buf.delete_text(self.z_home_diff_tf.get_position()-1, 1)
            self.z_home_diff_tf.set_position(self.z_home_diff_tf.get_position())
        elif self.ausdrehlimit_z_tf.has_focus():
            self.ausdrehlimit_z_conf_buf.delete_text(self.ausdrehlimit_z_tf.get_position()-1, 1)
            self.ausdrehlimit_z_tf.set_position(self.ausdrehlimit_z_tf.get_position())
        elif self.schlichter_comp_tf.has_focus():
            self.schlichter_comp_buf.delete_text(self.schlichter_comp_tf.get_position()-1, 1)
            self.schlichter_comp_tf.set_position(self.schlichter_comp_tf.get_position())
        elif self.backenlaenge_tf.has_focus():
            self.backenlaenge_conf_buf.delete_text(self.backenlaenge_tf.get_position()-1, 1)
            self.backenlaenge_tf.set_position(self.backenlaenge_tf.get_position())
    def on_new_backe_clicked(self, widget, data=None):
        self.req_new_backe = True
        self.aufgebraucht = False
        self.save_new_file_window.show()
        self.backen_window.hide()
        
    def on_new_bauteil_clicked(self, widget, data=None):
        self.return_to_backe = True
        #self.return_to = self.backen_window
        self.new_bauteil_bt.clicked()
        
    def on_load_bauteil_clicked(self, widget, data=None):
        self.return_to_backe = True
        #self.return_to = self.backen_window
        self.load_bauteil_bt.clicked()
        
    def on_save_bauteil_clicked(self, widget, data=None):
        self.return_to_backe = True
        #self.return_to = self.backen_window
        self.save_bauteil_bt.clicked()
        
    def on_load_b_ok_clicked(self, widget, data=None):
        self.backe_file_name = self.load_backe_window.get_filename()
        if self.backe_file_name != None:
            fd = open(self.backe_file_name,"rb")
            self.profile_tuple = pickle.load(fd)
            fd.close()
            self.backen.set_profile_tuple(self.profile_tuple)
            self.backe_preview.set_from_file('plot.png')
            self.b_load_lbl.set_text("Aktuelle Backen:\n" + os.path.basename(self.backe_file_name))
            self.log_dict['backe_file_name'] = self.backe_file_name
            self.log_dict_changed = True
            self.backen_window.show()
            self.load_backe_window.hide()	
        else:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Keine Datei ausgewaehlt. Bitte erneut versuchen.\n")
            self.announce_error()
    
    def on_load_b_cancel_clicked(self, widget, data=None):
        
        self.backen_window.show()
        self.load_backe_window.hide()	
    #backeeinrichtenWP

 
    
    #def on_referenzfahrt_clicked(self, widget, data=None):
        #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::referenzfahrt:: btn muss neu implementiert werden.\n")
        #self.announce_error()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #self.c.wait_complete(1)
        #self.c.unhome(0)				
        ##self.c.wait_complete()
        ##self.c.unhome(1)
        #self.c.wait_complete(1)
        #self.c.unhome(2)
        #self.c.wait_complete(1)
        #self.c.home(2)
        #time.sleep(4)
        #self.c.home(0)
        #self.c.wait_complete(1)
        #self.c.home(1)
        #self.c.wait_complete()
    
    def on_speed0_clicked(self, widget, data=None):
        self.increment = self.speed["speed0"]
        self.jog_mode = self.j_mode["increment"]
        
    def on_speed1_clicked(self, widget, data=None):
        self.increment = self.speed["speed1"]	
        self.jog_mode = self.j_mode["increment"]
    
    def on_speed2_clicked(self, widget, data=None):
        self.increment = self.speed["speed2"]
        self.jog_mode = self.j_mode["increment"]
    
    def on_speed3_clicked(self, widget, data=None):
        self.jog_mode = self.j_mode["continuous"]
    
    def on_speed4_clicked(self, widget, data=None):
        self.increment = self.speed["speed4"]
        self.jog_mode = self.j_mode["increment"]
        
    

    def on_cont_speed_value_changed(self, widget, data=None):
        self.override_value = float(self.cont_speed.get_value())/100
        self.override_changed = True
        
        
    def on_hal_referenzfahrt_activate(self, widget, data=None):
        pass
    
    '''manual_tab_signals_end'''
    ##
    '''main_window_signals_end'''
    #
    '''quit_window_signals_begin'''
    def on_quit_clicked(self, widget, data=None):
        sys.exit(0)
    
    def on_cancel_quit_clicked(self, widget, data=None):
        self.quit_window.hide()
        self.init_window.show()
        
    def on_restart_quit_clicked(self, widget, data=None):
        os.system("/sbin/shutdown -r now")

    
        
    def on_snfw_cancel_clicked(self, widget, data=None):
        if self.req_new_backe == True:
            self.req_new_backe = False
            self.backen_window.show()
            self.save_new_file_window.hide()
        elif self.req_new_bauteil ==True:
            self.req_new_bauteil = False
            if self.return_to_backe == True:
                self.backen_window.show()
                self.return_to_backe = False
            else:
                self.bauteil_window.show()
            self.save_new_file_window.hide()
        else:
            self.init_window.show()
            self.save_new_file_window.hide()
    
    def on_snfw_ok_clicked(self, widget, data=None):
            
        self.make_new_file()
        self.save_new_file_window.hide()
        
        if self.req_new_backe == True:
            fd = open(self.backe_file_name,"rb")
            self.profile_tuple = pickle.load(fd)
            fd.close()
            self.b_load_lbl.set_text("Aktuelle Backen:\n" + os.path.basename(self.backe_file_name))
            self.backen.set_profile_tuple(self.profile_tuple)
            self.backe_preview.set_from_file('plot.png')
            self.req_new_backe = False
            self.setup_btn.emit("clicked")
            self.backen_window.show()
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "-Werkzeug pruefen!\n-Ist ein Schrupper eingebaut?\n\nAls naechstes bitte die Initialisierungsfahrt durchfuehren.\nProgramm ist schon geladen. Der Start-Knopf startet die Initialisierungsfahrt.")
            self.announce_error()
        elif self.req_new_bauteil == True:
            #fd = open(self.bauteil_file_name,"rb")
            #self.bauteil = pickle.load(fd)
            #fd.close()
            #print "hier war er in der schleife"
            self.b_load_lbl_bt.set_text("Aktuelles Bauteil:\n" + os.path.basename(self.bauteil_file_name))
            self.b_load_lbl.set_text("Aktuelles Bauteil:\n" + os.path.basename(self.bauteil_file_name))
            self.req_new_bauteil = False
            
            if self.return_to_backe == True:
                self.backen_window.show()
                self.return_to_backe = False
            else:
                self.bauteil_window.show()
            self.bauteil_window.set_keep_above(True)
        else:
            #print " hier war er nicht in der schleife"
            pass
            #self.file_id = self.new_file_folder.get_file()
            #self.prgm_edit.set_label("Programm bearbeiten")
            #self.init_window.show()
        
    def on_shiftn_clicked(self, widget, data=None):
        if self.capital == False:
            self.shift.set_active(True)
            self.capital = True
        else:
            self.shift.set_active(False)
            self.capital = False
    
    def on_qn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'Q',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'q',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_wn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'W',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'w',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_en_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'E',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'e',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_rn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'R',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'r',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_tn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'T',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'t',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_zn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'Z',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'z',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_un_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'U',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'u',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_in_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'I',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'i',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_on_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'O',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'o',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_pn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'P',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'p',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_an_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'A',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'a',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_sn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'S',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'s',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_dn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'D',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'d',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_fn_clicked(self, widget, data=None):	
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'F',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'f',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_gn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'G',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'g',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_hn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'H',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'h',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_jn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'J',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'j',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_kn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'K',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'k',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_ln_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'L',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'l',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_yn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'Y',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'y',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_xn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'X',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'x',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_cn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'C',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'c',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_vn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'V',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'v',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_bn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'B',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'b',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_nn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'N',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'n',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_mn_clicked(self, widget, data=None):
        if self.capital == True:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'M',1)
        else:
            self.new_file_name.insert_text( self.new_file_entry.get_position() ,'m',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_spacen_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,' ',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_tabn_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'        ',4)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_colonn_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,',',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_pointn_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'.',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    def on_backspacen_clicked(self, widget, data=None):
        if self.new_file_name.get_length()-1 > -1:
            self.new_file_name.delete_text( self.new_file_entry.get_position()-1,1)
        self.new_file_entry.set_position(self.new_file_entry.get_position())
        
    def on_b0n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'0',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
        
    def on_b1n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'1',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
        
    def on_b2n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'2',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
        
    def on_b3n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'3',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b4n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'4',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b5n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'5',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b6n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'6',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b7n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'7',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b8n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'8',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_b9n_clicked(self, widget, data=None):
        self.new_file_name.insert_text( self.new_file_entry.get_position() ,'9',1)
        self.new_file_entry.set_position(self.new_file_entry.get_position() + 1)
    
    def on_forgot_passwd_clicked(self, widget, data=None):
        self.passwd_answer.set_label("Pech gehabt. Bitte bei der Automatisierungsabteilung melden.")
        
    def on_cancel_passwd_clicked(self, widget, data=None):
        self.new_passwd_buff.delete_text(0,len(self.new_passwd_buff.get_text()))
        self.new_passwd_buff2.delete_text(0,len(self.new_passwd_buff2.get_text()))
        self.passwd_check_buff.delete_text(0,len(self.passwd_check_buff.get_text()))
        self.passwd_window.hide()
        
    def on_new_passwd_clicked(self, widget, data=None):
        self.passwd_answer.set_label("Warte auf Eingabe")
        self.new_passwd = True
        #self.new_passwd_tab.hal_pin.set(True)
    
    def on_p_ok_clicked(self, widget, data=None):
        if self.new_passwd == False:
            if(self.passwd_check()):
                self.passwd_window.hide()
                if self.file_loaded == True: #self.source_file.get_line_count() > 1:

                    self.sf_changed = False
                else:
                    pass
            else:
                self.passwd_answer.set_label("Falsches Passwort")
        else:
            if self.make_new_passwd() == True:
                self.new_passwd_buff.delete_text(0,len(self.new_passwd_buff.get_text()))
                self.new_passwd_buff2.delete_text(0,len(self.new_passwd_buff2.get_text()))
                self.passwd_answer.set_label("Neues Passwort gespeichert")
                self.new_passwd = False
                self.log_dict_changed = True

    def on_p0_clicked(self, widget, data=None):
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '0', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '0', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '0', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)
            
    def on_p1_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '1', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '1', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '1', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p2_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '2', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '2', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '2', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p3_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '3', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '3', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '3', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p4_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '4', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '4', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '4', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p5_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '5', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '5', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '5', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p6_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '6', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '6', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '6', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p7_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '7', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '7', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '7', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p8_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '8', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '8', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '8', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		
    
    def on_p9_clicked(self, widget, data=None):	
        if self.passwd_check_entry.has_focus():
            self.passwd_check_buff.insert_text(self.passwd_check_entry.get_position(), '9', 1)
            self.passwd_check_entry.set_position(self.passwd_check_entry.get_position() + 1)
        if self.new_passwd_entry.has_focus():
            self.new_passwd_buff.insert_text(self.new_passwd_entry.get_position(), '9', 1)
            self.new_passwd_entry.set_position(self.new_passwd_entry.get_position() + 1)
        if self.new_passwd_entry2.has_focus():
            self.new_passwd_buff2.insert_text(self.new_passwd_entry2.get_position(), '9', 1)
            self.new_passwd_entry2.set_position(self.new_passwd_entry2.get_position() + 1)		

    '''passwd_window_signals_end'''
    #
    '''g_code_error_windwo_signals_begin'''
            
    def on_gcode_error_ok_clicked(self, widget, data=None):
        self.gcode_error_buff.delete(self.gcode_error_buff.get_start_iter(),self.gcode_error_buff.get_end_iter()) 
        self.gcode_error_window.hide()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        if self.last_seen!=None:
            self.last_seen.show()
        else:
            self.last_seen = None
            self.init_window.show()
    '''g_code_error_windwo_signals_end'''
    
    #def on_MDI_action_clicked(self, widget, data=None):
        #cmd = self.entrybuffer1.get_text()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.wait_complete()
        ##self.prgm_refresh_tbl.hal_pin.set(False)
        #self.c.mdi(cmd)
        ##self.end_code = False
        #self.c.wait_complete()
        #self.c.mode(linuxcnc.MODE_AUTO)
        
    
    def on_setup_btn_clicked(self, widget, data=None):
        #self.setup_window.show()
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::backen_werzeugwechsel:: btn muss neu implementiert werden.\n")
        self.announce_error()
        
        self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Bitte warten</b>")
        self.setup_referenzfahrt.emit("clicked")
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.wait_complete()
        #self.c.mdi("M115")
        self.prep_mode = True
        #self.last_seen = self.backen_window
        setup_counter = 1
        prog_time = 0.0
        
        fd = open("setup.ngc","w+")
        #pass
        fd.write("T1\n")
        fd.write("G01 X%3.3f Z%3.3f F%5f\n" %( self.safe_pos_x, self.safe_pos_z, self.positioning_speed))
        fd.write("M100\n")
        fd.write("G4 P1\n")
        self.schnitttiefe = float(self.schnitttiefe_buf.get_text())
        print "schnitttiefe",self.schnitttiefe
        init_speed = self.positioning_speed/15
        while setup_counter >=0:
            fd.write("G01 X%3.3f Z%3.3f F%5f\n" %((self.x_offset_backe+self.backenlaenge),round(self.z_offset_backe-self.schnitttiefe*setup_counter-0.2,3),init_speed))
            fd.write("G01 X%3.3f Z%3.3f F%5f\n" %((self.x_offset_backe+self.backenlaenge),round(self.z_offset_backe-self.schnitttiefe*setup_counter,3),self.cutting_speed_max))
            fd.write("G01 X%3.3f Z%3.3f F%5f\n" %((self.x_offset_backe-0.2),round(self.z_offset_backe-self.schnitttiefe*setup_counter,3),self.cutting_speed_max))
            setup_counter -=1
            init_speed = init_speed*15
        #fd.write("G01 X%3.3f Z%3.3f F%5f\n" %( -(self.safe_pos_x), self.safe_pos_z, self.positioning_speed)
        fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %(-(self.safe_pos_x), self.safe_pos_z,self.positioning_speed))
        fd.write("M101\n")
        fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %((-self.x_home_diff)+2,(-self.z_home_diff)+2,self.positioning_speed))
        fd.write("M30")
        fd.close()
        #self.setup_ok.set_label("Backen Einrichtung starten")
        self.setup_start = True
        #self.c.mode(linuxcnc.MODE_AUTO)
        #self.c.program_open("setup.ngc")
        #self.hal_gremlin1.set_property('show_program',True)
        #self.hal_gremlin1.set_property('show_live_plot',False)
        self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Backen-\n/Werkzeugwechsel</b>")
        self.backe_start.set_sensitive(True)
        self.backe_stop.set_sensitive(True)
        self.program = 2

            #self.hal_gremlin1.pan(45,0)
        
        #self.backen_window.hide()
    
        #self.speed0.emit("clicked")
        
        #self.speed1.emit("clicked")
    
        #self.speed2.emit("clicked")
    
    def on_setup_speed0_clicked(self, widget, data=None):
        self.increment = self.speed["speed0"]
        self.jog_mode = self.j_mode["increment"]
        
    def on_setup_speed1_clicked(self, widget, data=None):
        self.increment = self.speed["speed1"]	
        self.jog_mode = self.j_mode["increment"]
    
    def on_setup_speed2_clicked(self, widget, data=None):
        self.increment = self.speed["speed2"]
        self.jog_mode = self.j_mode["increment"]
    
    def on_setup_speed3_clicked(self, widget, data=None):
        self.jog_mode = self.j_mode["continuous"]
    
    #def on_speed4_clicked(self, widget, data=None):
        #self.increment = self.speed["speed4"]
        #self.jog_mode = self.j_mode["increment"]
    
    def on_setup_x_l_pressed(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::x_l_pressed:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode ==self.j_mode["continuous"]:
            #self.c.jog(self.jog_mode,0,-self.cont_speed.get_value() /100 * 20)        		#jog(mode:cont,axis,speed)
        #else:
            #self.c.jog(self.jog_mode,0,1,-self.increment) 					#jog(mode:inrement,axis,inc-length)

    def on_setup_x_l_released(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::x_l_released:: btn muss neu implementiert werden.\n")
        self.announce_error()
        ##self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode ==self.j_mode["continuous"]:
            #self.c.jog(0,0)     								#jog(mode:stop,axis)

    def on_setup_x_r_pressed(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::x_r_pressed:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(self.jog_mode,0,self.cont_speed.get_value() /100 * 20)     
        #else:
            #self.c.jog(self.jog_mode,0,1,self.increment)     
    
    def on_setup_x_r_released(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::x_r_released:: btn muss neu implementiert werden.\n")
        self.announce_error()
        ##self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(0,0)     
 
    def on_setup_z_u_pressed(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::z_u_pressed:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(self.jog_mode,2,-self.cont_speed.get_value() /100 * 20)     
        #else:
            #self.c.jog(self.jog_mode,2,1,-self.increment)     

    def on_setup_z_u_released(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::z_u_pressed:: btn muss neu implementiert werden.\n")
        self.announce_error()
        ##self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(0,2)     

    def on_setup_z_d_pressed(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::z_d_pressed:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(self.jog_mode,2,self.cont_speed.get_value() /100 * 20)     
        #else:
            #self.c.jog(self.jog_mode,2,1,self.increment)     

    def on_setup_z_d_released(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::z_d_released:: btn muss neu implementiert werden.\n")
        self.announce_error()
        ##self.c.mode(linuxcnc.MODE_MANUAL)
        #if self.jog_mode == self.j_mode["continuous"]:
            #self.c.jog(0,2)     
    
        

    
        
    
    #def on_back_setup_clicked(self, widget, data=None):
        #self.backen_window.show()
        ##self.last_seen = self.backen_window
        #self.setup_window.hide()
        
    #def on_setup_ok_clicked(self, widget, data=None):
        '''
        if self.setup_start == True and self.setup_running == False:
            self.c.mode(linuxcnc.MODE_AUTO)
            self.c.wait_complete()
        
            self.c.auto(linuxcnc.AUTO_RUN,1)
            self.setup_ok.set_label("Backen Einrichtung stoppen")
            #self.setup_ok.set_label("Positions Setup quittieren\nund Einrichtung vorbereiten")
            self.setup_start = False
            self.setup_running = True
        elif self.setup_start == False and self.setup_running == False:
            
        elif self.setup_start == False and self.setup_running == True:
            self.setup_ok.set_label("Backen Einrichtung starten")
            self.c.mode(linuxcnc.MODE_AUTO)
            self.c.auto(linuxcnc.AUTO_PAUSE)
            self.setup_start = True
            self.setup_running = False
            #self.backen_window.show()
        #self.setup_window.hide()
        '''
        
        
        
    
        
    def on_setup_referenzfahrt_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::referenzfahrt:: btn muss neu implementiert werden.\n")
        self.announce_error()

        #self.referenzfahrt.emit("clicked")
        #self.s.poll()
        #while self.s.axis[0]['homing'] != 0 or self.s.axis[2]['homing'] != 0:
            #self.c.wait_complete()	
            #self.s.poll()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("G92.1")
        #self.c.wait_complete()
        #if self.bt_mode == True:
            #self.c.mdi("G92 X%3.3f Z%3.3f" %(-self.x_home_diff,-self.z_home_diff))
        #else:
            #self.c.mdi("G92 X%3.3f Z%3.3f" %(-self.x_home_diff+0.4,-self.z_home_diff))
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #self.bearbeitung_beendet = False
        ##self.backe_power.set_sensitive(False)
        
        
    #def on_reset_clicked(self, widget, data=None):
        
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("G92.1")
        #self.c.mode(linuxcnc.MODE_MANUAL)
        #self.x_ref_lbl.set_text("Aktueller Koordinaten\nNullpunkt bei " + str(0.0))
        #self.z_ref_lbl.set_text("Aktueller Koordinaten\nNullpunkt bei " + str(0.0))
        
        
    def on_init_cancel_clicked(self, widget, data=None):
        self.save_logfile(self.log_dict,self.log_name)
        self.quit_window.show()
        self.init_window.hide()
        
    def on_bauteil_bearb_clicked(self, widget, data=None):
        #pass
        self.bt_mode = True
        #self.hal_gremlin_bt = self.builder.get_object("hal_gremlin_bt")
        self.b_load_lbl_bt.set_label("Aktuelles Bauteil:\n%s" %os.path.basename(self.bauteil_file_name))
        self.auflageflaeche_hoehe_m_schlichter = float(self.log_dict['auflageflaeche_hoehe_m_schlichter'])
        self.bauteil_window.show()
        self.init_window.hide()
        #self.hal_gremlin_bt.set_property('view','y')
    
    def on_backen_bearb_clicked(self, widget, data=None):
        self.bt_mode = False
        #d = sysconfig.get_config_vars()
        #for i in d:
            #print i, "    ::    ", d[i]
        self.neue_backe_template = """(lp0
                                        (lp1
                                        I%g
                                        aI0
                                        aa.""" %long(self.x_offset_backe)
        self.backen.old_profile = self.profile_tuple
        self.backen.x_offset_backe = self.x_offset_backe
        self.backen.backenlaenge = float(self.backenlaenge)
        self.backen.ausdrehlimit_z = self.ausdrehlimit_z
        self.backen.print_old_profile()
        self.backe_preview.set_from_file('plot.png')
        self.backen_window.show()
        self.init_window.hide()
        
    def on_backe_kurz_toggled(self, widget, data=None):
        self.backe_lang.emit("toggled")
        
    def on_backe_lang_toggled(self, widget, data=None):
        #print "hab auch reagiert"
        if self.backe_kurz.get_active():

            self.x_offset_backe = 20.3
            self.x_offset_backe_conf_buf.set_text(str(self.x_offset_backe),len(str(self.x_offset_backe)))
            self.log_dict["x_offset_backe"] = str(self.x_offset_backe)
        elif self.backe_lang.get_active():
            self.x_offset_backe = 12
            self.x_offset_backe_conf_buf.set_text(str(self.x_offset_backe),len(str(self.x_offset_backe)))
            self.log_dict["x_offset_backe"] = str(self.x_offset_backe)
            
    def on_backe_hoch_toggled(self, widget, data=None):
        self.backe_flach.emit("toggled")
            
    def on_backe_flach_toggled(self, widget, data=None):
        #print "hab reagiert"
        if self.backe_hoch.get_active():
            self.ausdrehlimit_z = 10
            #self.ausdrehlimit_z_conf_buf.set_text(str(self.ausdrehlimit_z),len(str(self.ausdrehlimit_z)))
            #self.log_dict["ausdrehlimit_z"] = str(self.ausdrehlimit_z)
            self.z_offset_backe = -23.5
            self.z_offset_backe_conf_buf.set_text(str(self.z_offset_backe),len(str(self.z_offset_backe)))
            self.log_dict["z_offset_backe"] = str(self.z_offset_backe)
        elif self.backe_flach.get_active():
            self.ausdrehlimit_z = 4
            #self.ausdrehlimit_z_conf_buf.set_text(str(self.ausdrehlimit_z),len(str(self.ausdrehlimit_z)))
            #self.log_dict["ausdrehlimit_z"] = str(self.ausdrehlimit_z)
            self.z_offset_backe = -17.5
            self.z_offset_backe_conf_buf.set_text(str(self.z_offset_backe),len(str(self.z_offset_backe)))
            self.log_dict["z_offset_backe"] = str(self.z_offset_backe)
        
    def on_button1_clicked(self, widget, data=None):
        #print "knopf gedrueckt!"
        self.bt_mode = True
        self.x_offset_backe_conf_buf.set_text(str(self.x_offset_backe),len(str(self.x_offset_backe)))
        self.z_offset_backe_conf_buf.set_text(str(self.z_offset_backe),len(str(self.z_offset_backe)))
        self.x_home_diff_conf_buf.set_text(str(self.x_home_diff),len(str(self.x_home_diff)))
        self.z_home_diff_conf_buf.set_text(str(self.z_home_diff),len(str(self.z_home_diff)))
        #self.ausdrehlimit_z_conf_buf.set_text(str(self.ausdrehlimit_z),len(str(self.ausdrehlimit_z)))
        #self.backenlaenge_conf_buf.set_text(str(self.backenlaenge),len(str(self.backenlaenge)))
        #self.schlichter_comp_buf.set_text(str(self.schlichter_comp),len(str(self.schlichter_comp)))
        #print self.x_offset_backe_conf_buf
        self.init_window.hide()
        self.master_config.show()
    
    def on_ok_conf_clicked(self, widget, data=None):
        self.init_window.show()
        self.log_dict['x_offset_backe'] = str(self.x_offset_backe)
        self.log_dict['z_offset_backe'] = str(self.z_offset_backe)
        self.log_dict['x_home_diff'] = str(self.x_home_diff)
        self.log_dict['z_home_diff'] = str(self.z_home_diff)
        #self.log_dict['backenlaenge'] = str(self.backenlaenge)
        #self.log_dict['ausdrehlimit_z'] = str(self.ausdrehlimit_z)
        self.bt_mode = False
        self.log_dict_changed = True
        self.master_config.hide()
        
    def on_backen_window_show(self, widget, data=None):
        self.last_seen = self.backen_window    
    def on_init_window_show(self, widget, data=None):
        self.last_seen = self.init_window    
    def on_backen_window_show(self, widget, data=None):
        self.last_seen = self.backen_window    
    def on_load_backe_window_show(self, widget, data=None):
        self.last_seen = self.backen_window    
    def on_load_bauteil_window_show(self, widget, data=None):
        self.last_seen = self.load_bauteil_window
    def on_bauteil_window_show(self, widget, data=None):
        self.last_seen = self.bauteil_window
        print "bauteil_window"
        
    def on_master_config_show(self, widget, data=None):
        self.last_seen = self.master_config
        
    def on_quit_window_show(self, widget, data=None):
        self.last_seen = self.quit_window    
    
    def on_save_new_file_window_show(self, widget, data=None):
        self.last_seen = self.save_new_file_window    
        
    def on_ref_clicked(self, widget, data=None):
        self.setup_referenzfahrt.emit("clicked")
    def on_vor_pressed(self, widget, data=None):
        self.setup_x_r.emit("pressed")
    def on_runter_pressed(self, widget, data=None):
        self.setup_z_d.emit("pressed")
    def on_zurueck_pressed(self, widget, data=None):
        self.setup_x_l.emit("pressed")
    def on_hoch_pressed(self, widget, data=None):
        self.setup_z_u.emit("pressed")
    def on_vor_released(self, widget, data=None):
        self.setup_x_r.emit("released")
    def on_runter_released(self, widget, data=None):
        self.setup_z_d.emit("released")
    def on_zurueck_released(self, widget, data=None):
        self.setup_x_l.emit("released")
    def on_hoch_released(self, widget, data=None):
        self.setup_z_u.emit("released")
        
    def on_conf_speed_0_clicked(self, widget, data=None):
        self.setup_speed0.emit("clicked")
        
    def on_conf_speed_1_clicked(self, widget, data=None):
        self.setup_speed1.emit("clicked")
    
    def on_conf_speed_2_clicked(self, widget, data=None):
        self.setup_speed2.emit("clicked")
    
    def on_conf_speed_3_clicked(self, widget, data=None):
        self.setup_speed3.emit("clicked")
        
    def on_conf_0_clicked(self, widget, data=None):
        self.num_pad_0.emit("clicked")
    def on_conf_1_clicked(self, widget, data=None):
        self.num_pad_1.emit("clicked")
    def on_conf_2_clicked(self, widget, data=None):    
        self.num_pad_2.emit("clicked")
    def on_conf_3_clicked(self, widget, data=None):
        self.num_pad_3.emit("clicked")
    def on_conf_4_clicked(self, widget, data=None):
        self.num_pad_4.emit("clicked")
    def on_conf_5_clicked(self, widget, data=None):
        self.num_pad_5.emit("clicked")
    def on_conf_6_clicked(self, widget, data=None):
        self.num_pad_6.emit("clicked")
    def on_conf_7_clicked(self, widget, data=None):
        self.num_pad_7.emit("clicked")
    def on_conf_8_clicked(self, widget, data=None):
        self.num_pad_8.emit("clicked")
    def on_conf_9_clicked(self, widget, data=None):
        self.num_pad_9.emit("clicked")
    def on_conf_p_clicked(self, widget, data=None):
        self.num_pad_dot.emit("clicked")
    def on_conf_loe_clicked(self, widget, data=None):
        self.num_pad_empty.emit("clicked")
        
    def on_confirm_entry_clicked(self, widget, data=None):
        self.x_offset_backe = float(self.x_offset_backe_conf_buf.get_text())
        self.z_offset_backe = float(self.z_offset_backe_conf_buf.get_text())
        self.x_home_diff = float(self.x_home_diff_conf_buf.get_text())
        self.z_home_diff = float(self.z_home_diff_conf_buf.get_text())
        self.cutting_speed_max = float(self.ausdrehlimit_z_conf_buf.get_text())
        self.innenradius_test = float(self.backenlaenge_conf_buf.get_text())/2
        self.cutting_speed_scrub = float(self.schlichter_comp_buf.get_text())/2
        self.log_dict['x_offset_backe'] = str(self.x_offset_backe)
        self.log_dict['z_offset_backe'] = str(self.z_offset_backe)
        self.log_dict['x_home_diff'] = str(self.x_home_diff)
        self.log_dict['z_home_diff'] = str(self.z_home_diff)
        #self.log_dict['ausdrehlimit_z'] = str(self.ausdrehlimit_z)
        #self.log_dict['backenlaenge'] = str(self.backenlaenge)
        #self.log_dict['schlichter_comp'] = str(self.schlichter_comp)
        self.log_dict_changed = True
        
    def on_load_test_clicked(self, widget, data=None):
        self.innenradius_test = float(self.bohrung_durchm_buf.get_text())/2#float(self.backenlaenge_conf_buf.get_text())/2
        self.aussenradius_test = float(self.naben_durchm_buf.get_text())/2#float(self.schlichter_comp_buf.get_text())/2
        #print "self.radius_hoehe:",self.radius_hoehe
        bauteil_ankratzhoehe = self.auflageflaeche_hoehe_m_schlichter-self.length_ist+self.radius_hoehe+0.1
        bauteil_abschlusshoehe = self.auflageflaeche_hoehe_m_schlichter-self.length_soll+self.radius_hoehe
        safe_pos_x = 0
        safe_pos_z = bauteil_ankratzhoehe - 20
        fase = False
        #fase = self.bearb_fase.get_active()
        #planen = False
        #planen = self.bearb_planen.get_active()
        #radius = False
        #radius = self.bearb_radius.get_active()
        andruecker_x_inpos = 27			#nachmessen
        andruecker_z_offset = -1			#die andrueckflaeche des Andrueckers befindet sich xx mm hoeher als die Werkzeugspitze
        andruecker_z_safe = bauteil_ankratzhoehe-5 	#das muesste eigentlich hinkommen, weil der andruecker hoeher liegt als das Werkzeug
        #soweit runter fahren, dass das Teil mit dem halben Hub des andrueckers angedrueckt wird
        andruecker_z_inpos = bauteil_ankratzhoehe + 10 	# + WERT das muss noch ausgemessen werden
        #gcode = self.bauteil_ordner + str(round(time.time(),0))+'.ngc'
        #print "innenradius_test:",self.innenradius_test
        #print "aussenradius_test:",self.aussenradius_test
        #print "bauteil_ankratzhoehe:", bauteil_ankratzhoehe
        #print "auflageflaeche_hoehe_m_schlichter:", self.auflageflaeche_hoehe_m_schlichter
        drittel = (self.aussenradius_test-self.innenradius_test)/4
        j = 0
        try:
            if self.test_mode == 2:
                fd = open("test_end.ngc","w+")
            else:
                fd = open("test.ngc","w+")
            fd.write("T1\n")
            fd.write("M103\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_inpos,3),self.positioning_speed/4))
            fd.write("G4 P0.5\n")
            fd.write("M115\n")
            fd.write("G4 P1\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(round(andruecker_x_inpos,3),round(andruecker_z_safe,3),self.positioning_speed))
            fd.write("M100\n")
            fd.write("G4 P0.5\n")
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(safe_pos_x, safe_pos_z,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(0, bauteil_ankratzhoehe-0.2,self.positioning_speed))
            if self.test_mode == 2:
                #fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test-0.2), bauteil_ankratzhoehe - 0.2,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test-0.2), bauteil_ankratzhoehe + 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.aussenradius_test+0.2), bauteil_ankratzhoehe + 0.2,self.planen_cutting_speed))
                bauteil_ankratzhoehe = bauteil_ankratzhoehe + 0.2
            else:
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test), bauteil_ankratzhoehe-0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test), bauteil_ankratzhoehe + 0.2,self.planen_cutting_speed/2))
                fd.write("G4 P1\n")
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+drittel-0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+drittel-0.3), bauteil_ankratzhoehe - 0.05,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+drittel+0.3), bauteil_ankratzhoehe - 0.05,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+drittel+0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))

                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+2*drittel-0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+2*drittel-0.3), bauteil_ankratzhoehe,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+2*drittel+0.3), bauteil_ankratzhoehe,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+2*drittel+0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))

                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+3*drittel-0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+3*drittel-0.3), bauteil_ankratzhoehe + 0.05,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+3*drittel+0.3), bauteil_ankratzhoehe + 0.05,self.planen_cutting_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.innenradius_test+3*drittel+0.3), bauteil_ankratzhoehe - 0.2,self.positioning_speed))



                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.aussenradius_test), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.aussenradius_test), bauteil_ankratzhoehe + 0.2,self.planen_cutting_speed/2))
                fd.write("G4 P1\n")
                fd.write("g01 X%3.3f Z%3.3f F%f\n" %(-(self.aussenradius_test), bauteil_ankratzhoehe - 0.2,self.positioning_speed))
            fd.write("g01 X%3.3f Z%3.3f F%f\n" %(self.safe_pos_x, safe_pos_z,self.positioning_speed))
            fd.write("M101\n")
            fd.write("g01 X%3.3f Z%3.3f F%3.3f\n" %((-float(self.x_home_diff)+2),(-float(self.z_home_diff)+2),self.positioning_speed))
            #print self.backen.block_ueb

        #print "erste punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][1][0]+self.schnitttiefe, self.backen.block_ueb[0][1][1]-self.schnitttiefe)
        #print "letzter Punkt: X%3.3f Z%3.3f" %(-self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0]-self.schnitttiefe,self.backen.block_ueb[0][len(self.backen.block_ueb[0])-1][0])
            #self.backen.old_profile.append(round(self.backen.new_profile[0][0]+0.2,3),
            fd.write("M116\n")

            fd.write("G4 P2\n")
            fd.write("M104\n")


            fd.write("M30")
            fd.close()
        except IOError:
            print "Kann Test Datei nicht laden"

        #self.c.mode(linuxcnc.MODE_AUTO)
        #if self.test_mode == 2:
            #self.c.program_open("test_end.ngc")
        #else:
            #self.c.program_open("test.ngc")
    
        
            
    
    
    
        
    def on_conf_m100_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::conf_m100:: spindel Starten btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M100")
    
    def on_conf_m102_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::conf_m102:: spindel stoppen btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M102")    
    def on_conf_m115_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::conf_m115:: backen schliessen btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M115")
    def on_conf_m116_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::conf_m116:: backen oeffnen btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M116")
        
    
    
    def on_num_pad_0_bt_clicked(self, widget, data=None):
        self.num_pad_0.emit("clicked")
    def on_num_pad_1_bt_clicked(self, widget, data=None):
        self.num_pad_1.emit("clicked")
    def on_num_pad_2_bt_clicked(self, widget, data=None):    
        self.num_pad_2.emit("clicked")
    def on_num_pad_3_bt_clicked(self, widget, data=None):
        self.num_pad_3.emit("clicked")
    def on_num_pad_4_bt_clicked(self, widget, data=None):
        self.num_pad_4.emit("clicked")
    def on_num_pad_5_bt_clicked(self, widget, data=None):
        self.num_pad_5.emit("clicked")
    def on_num_pad_6_bt_clicked(self, widget, data=None):
        self.num_pad_6.emit("clicked")
    def on_num_pad_7_bt_clicked(self, widget, data=None):
        self.num_pad_7.emit("clicked")
    def on_num_pad_8_bt_clicked(self, widget, data=None):
        self.num_pad_8.emit("clicked")
    def on_num_pad_9_bt_clicked(self, widget, data=None):
        self.num_pad_9.emit("clicked")
    def on_num_pad_dot_bt_clicked(self, widget, data=None):
        self.num_pad_dot.emit("clicked")
    def on_num_pad_empty_bt_clicked(self, widget, data=None):
        self.num_pad_empty.emit("clicked")
    
    def on_setup_referenzfahrt_bt_clicked(self, widget, data=None):
        self.setup_referenzfahrt.emit("clicked")
    def on_setup_x_r_bt_pressed(self, widget, data=None):
        self.setup_x_r.emit("pressed")
    def on_setup_z_d_bt_pressed(self, widget, data=None):
        self.setup_z_d.emit("pressed")
    def on_setup_x_l_bt_pressed(self, widget, data=None):
        self.setup_x_l.emit("pressed")
    def on_setup_z_u_bt_pressed(self, widget, data=None):
        self.setup_z_u.emit("pressed")
    def on_setup_x_r_bt_released(self, widget, data=None):
        self.setup_x_r.emit("released")
    def on_setup_z_d_bt_released(self, widget, data=None):
        self.setup_z_d.emit("released")
    def on_setup_x_l_bt_released(self, widget, data=None):
        self.setup_x_l.emit("released")
    def on_setup_z_u_bt_released(self, widget, data=None):
        self.setup_z_u.emit("released")
        
    def on_setup_speed0_bt_clicked(self, widget, data=None):
        self.setup_speed0.emit("clicked")
        
    def on_setup_speed1_bt_clicked(self, widget, data=None):
        self.setup_speed1.emit("clicked")
    
    def on_setup_speed2_bt_clicked(self, widget, data=None):
        self.setup_speed2.emit("clicked")
    
    def on_setup_speed3_bt_clicked(self, widget, data=None):
        self.setup_speed3.emit("clicked")
        pass
        
    def on_bauteil_reset_koord_clicked(self, widget, data=None):
        self.test_mode = 0
        self.reset_koord.clicked()
        
    def on_setup_btn_bt_clicked(self, widget, data=None):
        self.backen_window.show()
        self.bauteil_window.hide()
        
    def on_new_bauteil_bt_clicked(self, widget, data=None):
        self.req_new_bauteil = True
        
        #self.return_to = self.bauteil_window
        #self.new_passwd_tab.hal_pin.set(False)
        #self.passwd_window.show()
        
        self.save_new_file_window.show()
        self.bauteil_window.hide()
    
    def on_save_bauteil_bt_clicked(self, widget, data=None):
        self.save_bauteil()
        #self.return_to = self.bauteil_window
        self.b_load_lbl_bt.set_text("Bauteil\ngespeichert")
        self.b_load_lbl.set_text("Bauteil\ngespeichert")
        
    def on_load_bauteil_bt_clicked(self, widget, data=None):
        #self.return_to = self.bauteil_window
        
        self.load_bauteil_window.show()
        self.backen_window.hide()
        self.bauteil_window.hide()
        
    def on_load_bauteil_ok_clicked(self, widget, data=None):
        self.bauteil_file_name = self.load_bauteil_window.get_filename()
        if self.bauteil_file_name != None:
            fd = open(self.bauteil_file_name,"rb")
            #bauteil_dict = pickle.load(fd)
            bauteil_dict = json.load(fd)
            fd.close()
            self.load_new_bauteil(bauteil_dict)
            self.b_load_lbl_bt.set_text("Aktuelles Bauteil:\n" + os.path.basename(self.bauteil_file_name))
            self.b_load_lbl.set_text("Aktuelles Bauteil:\n" + os.path.basename(self.bauteil_file_name))
            self.log_dict['bauteil_file_name'] = self.bauteil_file_name
            self.log_dict_changed = True
            if self.return_to_backe == True:
                self.backen_window.show()
                #self.last_seen = self.backen_window
                self.return_to_backe = False
            else:
                self.bauteil_window.show()
            self.load_bauteil_window.hide()	
        else:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Keine Datei ausgewaehlt. Bitte erneut versuchen.\n")
            self.announce_error()
    
    def on_load_bauteil_cancel_clicked(self, widget, data=None):
        if self.return_to_backe == True:
            self.backen_window.show()
            self.return_to_backe = False
        else:
            self.bauteil_window.show()
        self.load_bauteil_window.hide()
    
    def on_calc_bt_clicked(self, widget, data=None):
        
        self.prep_mode = False
        self.bt_mode = True
        self.setup_referenzfahrt.clicked()
        self.length_ist = float(self.length_ist_buf.get_text())
        self.length_soll = float(self.length_soll_buf.get_text())
        self.radius_hoehe = float(self.hoehe_rad_buf.get_text())
        self.bohrung_durchm    = float(self.bohrung_durchm_buf.get_text())
        self.naben_durchm = float(self.naben_durchm_buf.get_text())
        self.durchm = float(self.durchm_buf.get_text())
        self.length_fase = float(self.length_fase_buf.get_text())
        self.radius_kante = float(self.radius_kante_buf.get_text())
        if self.durchm/2 > self.x_offset_backe+self.backenlaenge:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu gross fuer die Backen\n")
            self.announce_error()
            return 0
        if self.durchm/2 < self.x_offset_backe:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu klein fuer die Backen\n")
            self.announce_error()
            return 0
            
        if self.length_ist <10 or self.length_ist >100:
            print "1"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Ist-Laenge zu gross oder zu klein?\n")
            self.announce_error()
            return 0
        if self.length_ist - self.length_soll < - 1 :
            print "2"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Soll-Laenge zu gross oder zu klein?\n")
            self.announce_error()
            return 0

        if self.radius_hoehe <0.5 or self.radius_hoehe >10:
            print "3"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Bauteilparameter noch einmal Pruefen. Vielleicht liegt irgendwo ein Tipfehler vor?\n")
            self.announce_error()
            return 0

        if self.bohrung_durchm <1 or self.bohrung_durchm >20:
            print "4"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Bauteilparameter noch einmal Pruefen. Vielleicht liegt irgendwo ein Tipfehler vor?\n")
            self.announce_error()
            return 0

        if self.naben_durchm < self.bohrung_durchm or self.naben_durchm >50:
            print "5"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Bauteilparameter noch einmal Pruefen. Vielleicht liegt irgendwo ein Tipfehler vor?\n")
            self.announce_error()
            return 0

        if self.length_fase > 1:
            print "6"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Bauteilparameter noch einmal Pruefen. Vielleicht liegt irgendwo ein Tipfehler vor?\n")
            self.announce_error()
            return 0

        if self.radius_kante > 1:
            print "7"
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Bauteilparameter noch einmal Pruefen. Vielleicht liegt irgendwo ein Tipfehler vor?\n")
            self.announce_error()
            return 0

            #self.hal_gremlin_bt.set_property('view','y')
        #self.hal_gremlin_bt.set_property('show_live_plot',False)
        if self.length_fase == 1234567809.0:
            self.length_fase = 0.2
            self.test_mode = 1
            self.load_test.clicked()
        elif self.length_fase == 1234567809.1:
            self.length_fase = 0.2
            self.test_mode = 2
            self.load_test.clicked()
        else:
            self.test_mode = 0
            
        #print "1"
        #if self.durchm/2 > self.x_offset_backe+self.backenlaenge:
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu gross fuer die Backen\n")
            #self.announce_error()
            #return 0
        #if self.durchm/2 < self.x_offset_backe:
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Der Durchmesser ist zu klein fuer die Backen\n")
            #self.announce_error()
            #return 0
        self.radius = float(self.rad_buf.get_text())
        #print "2"
        self.radius_hoehe = float(self.hoehe_rad_buf.get_text())
        self.schnitttiefe = float(self.schnitttiefe_buf.get_text())
        self.aufl = float(self.aufl_buf.get_text())
        self.spannfl = float(self.spannfl_buf.get_text())
        
        #if self.radius+self.aufl<self.durchm/2-self.x_offset_backe and self.test_mode == 0:
            #self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Wahrscheinlich ist die Auflageflaeche oder der Radius nicht der Zeichnung\nentsprechend eingetragen")
            #self.announce_error()
            #return 0
        ##print "3"
        #self.profile_tuple = [[0,0]]
        self.randhoehe = 1#float(self.randhoehe_buf.get_text())
        self.randbreite = 1#float(self.randbreite_buf.get_text())
        if not(self.schnitttiefe > 0) or self.schnitttiefe > 0.25 and self.test_mode == 0:
            self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "Vergessen die Schnitttiefe richtig einzutragen?")
            self.announce_error()
            return 0
        self.bauteil_prog_ready = True
    #def on_auto_start_clicked(self, widget, data=None):
        #self.c.mode(linuxcnc.MODE_AUTO)
        #self.c.wait_complete(1)
        #self.auto_start_led.hal_pin.set(True)
        #print "start"
        #self.auto_start.hal_pin.set(False)
        
    def on_tool_edit_clicked(self, widget, data=None):
        os.system("tooledit tool.tbl")
    
    def on_reload_tool_tbl_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::reload_tool_table:: btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.c.tool_offset(0,0,0,0.35,142,177,1)
        #self.c.load_tool_table()
        ##self.c.mode(linuxcnc.MODE_MDI)
        ##self.c.wait_complete(1)
        ##self.c.mdi("T1")
        #table = self.s.tool_table
        #for i in table:
            #if i.id != -1:
        #print i
        #print "\n_END_OF_TABLE_\n"
        ##print "tool in spindle:", self.s.tool_in_spindle
        ##print "tool Table:", self.s.tool_offset
        
        
    def on_bauteil_start_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::bauteil_start:: btn muss neu implementiert werden.\n")
        self.announce_error()
        
        #self.manual_btn_bt.set_active(True)
        #self.fehlerfreie_fahrt = True
        #self.s.poll()
        #self.c.wait_complete(1)
        #if self.s.task_state == 4 and self.machine_running == False and self.machine_paused == False:
            ##self.c.mode(linuxcnc.MODE_AUTO)
            
            ##self.c.mode(linuxcnc.MODE_MANUAL)	
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.backe_start.set_label("Pause")
            #self.machine_running = True
            #self.c.wait_complete()
            #self.c.auto(linuxcnc.AUTO_RUN,1)
            #self.s.poll()
            #self.state = self.s.state
        #elif self.machine_running == True :
            ##self.c.wait_complete(0.5)
            #self.backe_start.set_label("Weiter")
            #self.machine_running = False
            #self.machine_paused = True
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.c.auto(linuxcnc.AUTO_PAUSE)
        #elif self.machine_running == False and self.machine_paused == True:
            #self.backe_start.set_label("Pause")
            #self.machine_running = True
            #self.c.mode(linuxcnc.MODE_AUTO)
            #self.c.wait_complete(0.5)
            #self.c.auto(linuxcnc.AUTO_RESUME)
        #self.option_box.set_sensitive(False)
        #self.option_box_bt.set_sensitive(False)
        
    def on_bauteil_stop_clicked(self, widget, data=None):
        self.backe_stop.clicked()
        
    def on_bauteil_ready_clicked(self, widget, data=None):
        self.gcode_error_buff.insert(self.gcode_error_buff.get_end_iter() , "::bauteil_ready:: btn muss neu implementiert werden.\n")
        self.announce_error()
        #self.c.mode(linuxcnc.MODE_MDI)
        #self.c.mdi("M104")
        #self.bauteil_is_ready = True
        
    def on_bauteil_to_main_clicked(self, widget, data=None):
        self.bauteil_window.hide()
        self.init_window.show()
        
    def on_bauteil_bearb_enter_notify_event(self, widget, data=None):
        self.window1.show()
        
    def on_window1_leave_notify_event(self, widget, data=None):
        self.window1.hide()
        
    def __init__(self):#, inifile):
        self.backen_ordner = "backen_ausdrehen/"
        self.bauteil_ordner = "bauteil_bearbeiten/"
        self.file_loaded = False
        self.end_code = False
        self.wd = os.getcwd()
        self.sf_changed = False
        self.builder = gtk.Builder()
        self.builder.add_from_file("fp.glade")
        self.builder.connect_signals(self)
        self.bearbeitung_beendet_led = self.builder.get_object("bearbeitung_beendet_led")
        self.bearbeitung_beendet = True
        self.capital = False
        self.new_file_entry = self.builder.get_object("new_file_entry")
        self.new_file_name = self.builder.get_object("new_file_name")
        self.new_file_folder = self.builder.get_object("new_file_folder")
        self.window1 = self.builder.get_object("window1")
        self.gcode_error_window = self.builder.get_object("gcode_error_window")
        self.gcode_error_window.fullscreen()
        self.passwd_window = self.builder.get_object("passwd_window")
        self.passwd_window.fullscreen()
        self.init_window = self.builder.get_object("init_window")
        self.init_window.fullscreen()
        self.init_window.show()
        self.req_quit = self.builder.get_object("req_quit")
        self.last_seen = self.init_window
        self.save_new_file_window = self.builder.get_object("save_new_file_window")
        self.save_new_file_window.fullscreen()
        self.quit_window = self.builder.get_object("quit_window")
        self.quit_window.fullscreen()
        self.gcode_error_buff = self.builder.get_object("gcode_error_buff")        
        self.state = -1
        self.machine_running = False
        self.machine_paused = False
        self.homing = 0
        self.speed = {"speed0" :0.01 , "speed1" : 0.1 , "speed2" : 1 , "speed4" : 5, "speed3" : "kontinuous"}
        self.speed0 = self.builder.get_object("speed0")
        self.speed1 = self.builder.get_object("speed1")
        self.speed2 = self.builder.get_object("speed2")
        self.speed3 = self.builder.get_object("speed3")
        self.x_ref_lbl = self.builder.get_object("x_ref_lbl")
        self.z_ref_lbl = self.builder.get_object("z_ref_lbl")
        self.referenzfahrt = self.builder.get_object("referenzfahrt")
        self.increment = 0
        self.jog_mode = 0
        self.j_mode ={"increment" : 2, "continuous" : 1, "stop" : 0}
        self.cont_speed = self.builder.get_object("cont_speed")
        self.cont_speed.set_value(100.0)
        self.override_value = 0
        self.override_value = float(self.cont_speed.get_value())/100
        self.estop_lbl = self.builder.get_object("estop_lbl")
        self.machine_lbl = self.builder.get_object("machine_lbl")
        self.manual_ctrl = self.builder.get_object("manual_ctrl")
        self.cycle_count_lbl = self.builder.get_object("cycle_count_lbl")
        self.restart_tab = self.builder.get_object("restart_tab")
        self.override_changed = False
        self.gcode_error_view = self.builder.get_object("gcode_error_view")
        self.gcode_has_errors = False
        self.passwd_check_entry = self.builder.get_object("passwd_check_entry")
        self.passwd_check_buff = self.builder.get_object("passwd_check_buff")
        self.passwd_answer = self.builder.get_object("passwd_answer")
        self.new_passwd_entry = self.builder.get_object("new_passwd_entry")
        self.new_passwd_entry2= self.builder.get_object("new_passwd_entry2")
        self.new_passwd_buff= self.builder.get_object("new_passwd_buff")
        self.new_passwd_buff2= self.builder.get_object("new_passwd_buff2")
        self.new_passwd_tab = self.builder.get_object("new_passwd_tab")
        self.new_passwd = False
        self.passwd_check_entry.set_visibility(False)
        self.new_passwd_entry.set_visibility(False)
        self.new_passwd_entry2.set_visibility(False)
        file_filter_ngc = gtk.FileFilter()
        file_filter_ngc.add_pattern("*.ngc")
        file_filter_ngc.add_pattern("*.NGC")
        self.akt_prgm_lbl = self.builder.get_object("akt_prgm_lbl")
        self.speed3 = self.builder.get_object("speed3")
        self.increment = self.speed["speed0"]
        self.jog_mode = self.j_mode["increment"]
        self.new_file_name = self.builder.get_object("new_file_name")
        self.new_file_folder = self.builder.get_object("new_file_folder")
        self.m100_btn = self.builder.get_object("m100_btn")
        self.m101_btn = self.builder.get_object("m101_btn")
        self.m115_btn = self.builder.get_object("m115_btn")
        self.m116_btn = self.builder.get_object("m116_btn")
        self.is_closed = False
        self.setup_x_l = self.builder.get_object("setup_x_l")
        self.setup_x_r = self.builder.get_object("setup_x_r")
        self.setup_z_u = self.builder.get_object("setup_z_u")
        self.setup_z_d = self.builder.get_object("setup_z_d")
        self.key_is_still_pressed = False
        self.save_new_file_window.set_keep_above(True)
        self.save_new_file_window.fullscreen()
        '''
        Das externe Logfile wird gelesen und fuer die entsprechenden Werte im Programm ausgewertet:
        -bauteillaenge_offset
        -fase_offset
        -zuletzt geladenes ngc File
        -Zeitstempel des letzten Buerstenwechsels
        -Anzahl der Zyklen der aktuellen Buerste seit dem Wechsel
        -Passwort
        
        Ist kein Logfile im Config-Ordner vorhanden, wird eins erstellt und mit Standardwerten gefuellt
        '''
        self.log_name = os.path.join(self.wd, 'cnc_logfile.csv')
        if not os.path.isfile(self.log_name):
            open(self.wd + "/cnc_logfile.csv", "w+").close()
        self.file_location = ''
        self.file_name = ''
        self.log_dict = self.load_logfile(self.log_name)
        self.cutting_speed_max = 10
        self.cutting_speed_scrub = 20
        self.cutting_speed_slow = 2
        self.positioning_speed = 3000
        self.fase_cutting_speed = 5
        self.planen_cutting_speed = 15
        self.radius_cutting_speed = 2
        self.backe_estop = self.builder.get_object("backe_estop")
        self.bauteil_estop = self.builder.get_object("bauteil_estop")		
        self.x_offset_backe = 12	#abstand von x=0 bis zur Backeninnenkante (muss ausgemessen und in den Code eingetragen werden. sollte dann immer gleich bleiben)
        self.z_offset_backe = -17.5		#anstand von z=0 bit zu Backenoberkante
        self.safe_pos_x = 0.0 	#in der Mitte der Spindelachse
        self.safe_pos_z = -25.0     #100mm ueber der spindelplatte. hier sollte kein Bauteil oder Backe mehr sein
        self.backenlaenge = 25
        self.backen_window = self.builder.get_object("backen_window")
        self.z_offset_backe_tf = self.builder.get_object("z_offset_backe_tf")
        self.backenlaenge_tf = self.builder.get_object("backenlaenge_tf")
        self.x_offset_backe_tf = self.builder.get_object("x_offset_backe_tf")
        self.ausdrehlimit_z_tf = self.builder.get_object("ausdrehlimit_z_tf")
        self.x_home_diff_tf = self.builder.get_object("x_home_diff_tf")
        self.z_home_diff_tf = self.builder.get_object("z_home_diff_tf")
        self.backe_hoch = self.builder.get_object("backe_hoch")
        self.backe_flach = self.builder.get_object("backe_flach")
        self.backe_lang = self.builder.get_object("backe_lang")
        self.backe_kurz = self.builder.get_object("backe_kurz")
        self.est_time = self.builder.get_object("est_time")
        self.reset_koord = self.builder.get_object("reset_koord")
        self.backe_stop =    self.builder.get_object("backe_stop")
        self.x_offset_backe_conf_buf = self.builder.get_object("x_offset_backe_conf_buf")
        self.conf_speed_0 = self.builder.get_object("conf_speed_0")
        self.conf_speed_1 = self.builder.get_object("conf_speed_1")
        self.conf_speed_2 = self.builder.get_object("conf_speed_2")
        self.conf_speed_3 = self.builder.get_object("conf_speed_3")
        self.z_offset_backe_conf_buf = self.builder.get_object("z_offset_backe_conf_buf")
        self.backenlaenge_conf_buf = self.builder.get_object("backenlaenge_conf_buf")
        self.ausdrehlimit_z_conf_buf = self.builder.get_object("ausdrehlimit_z_conf_buf")
        self.schlichter_comp_buf = self.builder.get_object("schlichter_comp_buf")
        self.schlichter_comp_tf = self.builder.get_object("schlichter_comp_tf")
        self.x_home_diff_conf_buf = self.builder.get_object("x_home_diff_conf_buf")
        self.z_home_diff_conf_buf = self.builder.get_object("z_home_diff_conf_buf")
        self.backen_window.fullscreen()
        self.backe_power = self.builder.get_object("backe_power")
        self.backe_to_main = self.builder.get_object("backe_to_main")
        self.backe_preview = self.builder.get_object("backe_preview")
        self.aufl_buf = self.builder.get_object("aufl_buf")
        self.durchm_buf = self.builder.get_object("durchm_buf")
        self.spannfl_buf = self.builder.get_object("spannfl_buf")
        self.rad_buf = self.builder.get_object("rad_buf")
        self.hoehe_rad_buf = self.builder.get_object("hoehe_rad_buf")
        self.schnittgeschw_buf = self.builder.get_object("schnittgeschw_buf")
        self.schnitttiefe_buf = self.builder.get_object("schnitttiefe_buf")
        self.randbreite_buf    = self.builder.get_object("randbreite_buf")
        self.randhoehe_buf = self.builder.get_object("randhoehe_buf")
        self.load_backe_window = self.builder.get_object("load_backe_window")
        self.load_backe_window.fullscreen()
        self.setup_start = False
        self.setup_running = False
        filters = self.load_backe_window.list_filters()
        file_filter = gtk.FileFilter()
        file_filter.add_pattern("*.backe")
        for i in filters:
            self.load_backe_window.remove_filter(i)
        self.load_backe_window.set_filter(file_filter)
        self.durchm = 8.0
        self.radius = 1.0
        self.schnitttiefe = 0.1
        self.length_ist = 0
        self.length_soll = 0
        self.naben_durchm = 0
        self.bohrung_durchm = 0
        self.length_fase = 0
        self.radius_kante = 0
        self.aufl = 1.0
        self.spannfl = 1.0
        self.profile_tuple = [[0,0]]
        self.randbreite = 1.0
        self.randhoehe = 1.0
        self.ausdrehlimit_z = 4.0
        self.backe_file_name = "neue_backe.backe"
        self.req_new_backe = False
        self.setup_btn = self.builder.get_object("setup_btn")
        self.backen = pt_pro_calc.BackenAusdrehen()#[[(self.durchm/2),0]],self.profile_tuple,self.cutting_speed_max,self.aufl,self.spannfl,self.schnitttiefe,self.randbreite,self.randhoehe,self.radius,self.ausdrehlimit_z)
        self.b_load_lbl = self.builder.get_object("b_load_lbl")
        self.b_load_lbl.set_text("Aktuelle Backen:\nkeine Backe geladen")
        self.neue_backe_template = ""
        self.hal_ausdrehen_tbl = self.builder.get_object("hal_ausdrehen_tbl")
        self.log_dict_changed = False
        self.bauteil_window    = self.builder.get_object("bauteil_window")
        self.bauteil_window.fullscreen()
        self.manual_tbl_bt = self.builder.get_object("manual_tbl_bt")
        self.man_ctrl_tbl = self.builder.get_object("man_ctrl_tbl")
        self.load_prog = self.builder.get_object("load_prog")
        self.man_ctrl_tbl_bt = self.builder.get_object("man_ctrl_tbl_bt")
        self.num_pad_tbl_bt = self.builder.get_object("num_pad_tbl_bt")
        self.option_box_bt = self.builder.get_object("option_box_bt")
        self.bauteil_start = self.builder.get_object("bauteil_start")
        self.bauteil_stop = self.builder.get_object("bauteil_stop")
        self.bauteil_ready = self.builder.get_object("bauteil_ready")
        self.bauteil_load_prog = self.builder.get_object("bauteil_load_prog")
        self.manual_btn_bt = self.builder.get_object("manual_btn_bt")
        self.num_pad_btn_bt = self.builder.get_object("num_pad_btn_bt")
        self.manual_btn_bt.set_active(True)
        self.setup_speed0 = self.builder.get_object("setup_speed0")
        self.setup_speed1 = self.builder.get_object("setup_speed1")
        self.setup_speed2 = self.builder.get_object("setup_speed2")
        self.setup_speed3 = self.builder.get_object("setup_speed3")
        self.setup_speed3.set_active(True)
        self.bauteil_power = self.builder.get_object("bauteil_power")
        self.bauteil_to_main_tbl = self.builder.get_object("bauteil_to_main_tbl")
        self.bauteil_to_main = self.builder.get_object("bauteil_to_main")
        self.schnitttiefe_tf_bt=self.builder.get_object("schnitttiefe_tf_bt")
        self.durchm_tf_bt= self.builder.get_object("durchm_tf_bt")
        self.rad_tf_bt = self.builder.get_object("rad_tf_bt")
        self.hoehe_rad_tf_bt = self.builder.get_object("hoehe_rad_tf_bt")
        self.aufl_tf_bt = self.builder.get_object("aufl_tf_bt")
        self.spannfl_tf_bt = self.builder.get_object("spannfl_tf_bt")
        self.length_ist_tf_bt = self.builder.get_object("length_ist_tf_bt")
        self.length_soll_tf_bt = self.builder.get_object("length_soll_tf_bt")
        self.naben_durchm_tf_bt = self.builder.get_object("naben_durchm_tf_bt")
        self.bohrung_durchm_tf_bt = self.builder.get_object("bohrung_durchm_tf_bt")
        self.radius_kante_tf_bt = self.builder.get_object("radius_kante_tf_bt")
        self.length_fase_tf_bt = self.builder.get_object("length_fase_tf_bt")
        self.calc_bt = self.builder.get_object("calc_bt")
        self.new_bauteil_bt = self.builder.get_object("new_bauteil_bt")
        self.load_bauteil_bt = self.builder.get_object("load_bauteil_bt")
        self.save_bauteil_bt = self.builder.get_object("save_bauteil_bt")
        self.est_time_bt = self.builder.get_object("est_time_bt")
        self.b_load_lbl_bt = self.builder.get_object("b_load_lbl_bt")
        self.setup_btn_bt = self.builder.get_object("setup_btn_bt")
        self.req_new_bauteil = False
        self.load_bauteil_window = self.builder.get_object("load_bauteil_window")
        self.bearb_planen = self.builder.get_object("bearb_planen")
        self.bearb_fase = self.builder.get_object("bearb_fase")
        self.bearb_radius = self.builder.get_object("bearb_radius")
        filters = self.load_bauteil_window.list_filters()
        file_filter_bauteil = gtk.FileFilter()
        file_filter_bauteil.add_pattern("*.bt")
        self.exp_time_bt = self.builder.get_object("exp_time_bt")
        self.bauteil_is_ready = False
        self.bauteil_prog_ready = False
        self.aussenradius_test = 0
        self.innenradius_test = 0
        self.radius_hoehe = 0
        self.test_mode = 0
        self.load_test = self.builder.get_object("load_test")
        self.start_test = self.builder.get_object("start_test")
        self.stop_test = self.builder.get_object("stop_test")
        
        try:
            stat = os.stat(self.bauteil_ordner)
            os.path.isdir(self.bauteil_ordner)
        except OSError:
            os.mkdir(self.bauteil_ordner)
            stat = os.stat(self.bauteil_ordner)
        dirlist = os.listdir(self.bauteil_ordner)
        dirlist = sorted(dirlist,reverse=True)
        
        while len(dirlist) > 50:
            os.remove(self.bauteil_ordner + dirlist[-1])
            del dirlist[-1]
        
        self.nc_folder = "/home/cnc/linuxcnc/nc_files"
        self.load_backe_window.set_current_folder(self.nc_folder)
        self.load_bauteil_window.set_current_folder(self.nc_folder)
        #os.system("python " + self.wd + "/startup_extern.py")
        self.version = "2.2016-02-16\n!!!TESTVERSION!!!\nkein Linuxcnc"
        
        logname = "cnc_errorlog.log"
        logging.basicConfig(filename=logname,level=logging.DEBUG, format='%(message)s')
        logging.getLogger().addHandler(logging.StreamHandler())
        
        with open(logname,'w'):
            pass
        
        self.version2 = self.builder.get_object("version2")
        self.version1 = self.builder.get_object("version1")
        self.time = self.builder.get_object("time")
        self.time1 = self.builder.get_object("time1")
        self.version2.set_text(self.version)
        self.time.set_text("")
        self.version1.set_text(self.version)
        self.time1.set_text("")
        self.version_lbl = self.builder.get_object("version_lbl")
        self.manual_tbl = self.builder.get_object("manual_tbl")
        self.num_pad_tbl = self.builder.get_object("num_pad_tbl")
        self.num_pad_0 = self.builder.get_object("num_pad_0")
        self.num_pad_1 = self.builder.get_object("num_pad_1")
        self.num_pad_2 = self.builder.get_object("num_pad_2")
        self.num_pad_3 = self.builder.get_object("num_pad_3")
        self.num_pad_4 = self.builder.get_object("num_pad_4")
        self.num_pad_5 = self.builder.get_object("num_pad_5")
        self.num_pad_6 = self.builder.get_object("num_pad_6")
        self.num_pad_7 = self.builder.get_object("num_pad_7")
        self.num_pad_8 = self.builder.get_object("num_pad_8")
        self.num_pad_9 = self.builder.get_object("num_pad_9")
        self.num_pad_dot = self.builder.get_object("num_pad_dot")
        self.num_pad_empty = self.builder.get_object("num_pad_empty")
        self.num_pad_btn = self.builder.get_object("num_pad_btn")
        self.manual_btn = self.builder.get_object("manual_btn")
        self.manual_btn.set_active(True)
        self.prog_lbl = self.builder.get_object("prog_lbl")
        self.prog_lbl.set_markup("Aktuelles Programm:\n<b>Kein Programm\ngeladen</b>")
        self.setup_referenzfahrt = self.builder.get_object("setup_referenzfahrt")
        self.program = 0
        self.backe_start = self.builder.get_object("backe_start")
        self.option_box = self.builder.get_object("option_box")
        self.schnitttiefe_tf =self.builder.get_object("schnitttiefe_tf")
        self.durchm_tf = self.builder.get_object("durchm_tf")
        self.rad_tf = self.builder.get_object("rad_tf")
        self.hoehe_rad_tf = self.builder.get_object("hoehe_rad_tf")
        self.aufl_tf = self.builder.get_object("aufl_tf")
        self.spannfl_tf = self.builder.get_object("spannfl_tf")
        self.length_ist_tf = self.builder.get_object("length_ist_tf")
        self.length_soll_tf = self.builder.get_object("length_soll_tf")
        self.naben_durchm_tf = self.builder.get_object("naben_durchm_tf")
        self.bohrung_durchm_tf = self.builder.get_object("bohrung_durchm_tf")
        self.radius_kante_tf = self.builder.get_object("radius_kante_tf")
        self.length_fase_tf = self.builder.get_object("length_fase_tf")
        self.length_ist_buf = self.builder.get_object("length_ist_buf")
        self.length_soll_buf = self.builder.get_object("length_soll_buf")
        self.naben_durchm_buf = self.builder.get_object("naben_durchm_buf")
        self.bohrung_durchm_buf = self.builder.get_object("bohrung_durchm_buf")
        self.radius_kante_buf = self.builder.get_object("radius_kante_buf")
        self.length_fase_buf = self.builder.get_object("length_fase_buf")
        self.auflageflaeche_hoehe_m_schlichter = 0
        self.backe_start = self.builder.get_object("backe_start")
        self.backe_stop = self.builder.get_object("backe_stop")
        self.backe_start.set_sensitive(False)
        self.backe_stop.set_sensitive(False)
        self.master_config = self.builder.get_object("master_config")
        self.master_config.fullscreen()
        self.backe_lang.set_active(True)
        self.backe_flach.set_active(True)
        self.neues_bauteil_template = {"durchm" : 0.0 , 
                                        "rueckenradius" : 0.0,
                                        "rueckenradius_hoehe" : 0.0,
                                        "aufl" : 0.0 ,
                                        "spannfl" : 0.0,
                                        "length_ist" : 0.0,
                                        "length_soll" :0.0,
                                        "naben_durchm" : 0.0,
                                        "bohrung_durchm" : 0.0,
                                        "radius_kante" : 0.0,
                                        "length_fase" : 0.0,
                                        "schnitttiefe" : 0.0}
        self.neues_bauteil = {}
        self.fehlerfreie_fahrt = True
        self.return_to_backe = False
        self.load_bauteil_window.fullscreen()
        
        for i in filters:
            self.load_bauteil_window.remove_filter(i)
        self.load_bauteil_window.set_filter(file_filter_bauteil)
        
        try: 
            self.backe_file_name = self.log_dict['backe_file_name']
        except KeyError:
            self.log_dict['backe_file_name'] = "neue_backe.backe"
            self.backe_file_name = self.log_dict['backe_file_name']
        
        try: 
            self.x_offset_backe = float(self.log_dict['x_offset_backe'])
        except KeyError:
            self.log_dict['x_offset_backe'] = "12.0"
            self.x_offset_backe = float(self.log_dict['x_offset_backe'])
        
        try: 
            self.z_offset_backe = float(self.log_dict['z_offset_backe'])
        except KeyError:
            self.log_dict['z_offset_backe'] = "-17.5"
            self.z_offset_backe = float(self.log_dict['z_offset_backe'])
        
        try:
            self.schlichter_comp = float(self.log_dict['schlichter_comp'])
        except KeyError:
            self.log_dict['schlichter_comp'] = "5"
            self.schlichter_comp = float(self.log_dict['schlichter_comp'])
        
        try: 
            self.auflageflaeche_hoehe_m_schlichter = float(self.log_dict['auflageflaeche_hoehe_m_schlichter'])
        except KeyError:
            self.log_dict['auflageflaeche_hoehe_m_schlichter'] = "0"
            self.auflageflaeche_hoehe_m_schlichter = float(self.log_dict['auflageflaeche_hoehe_m_schlichter'])
        
        try:
            fd = open(self.backe_file_name,"rb")
            self.profile_tuple = pickle.load(fd)
            fd.close()
            self.backen.set_profile_tuple(self.profile_tuple)
            self.backe_preview.set_from_file('plot.png')
            self.b_load_lbl.set_text("Aktuelle Backen:\n" + os.path.basename(self.backe_file_name))
        except IOError:
            pass
        
        try:
            self.bauteil_file_name = self.log_dict["bauteil_file_name"]
        except KeyError:
            self.log_dict["bauteil_file_name"] = "keins"
            self.bauteil_file_name = self.log_dict["bauteil_file_name"]
        
        try:
            fd = open(self.bauteil_file_name,"rb")
            self.load_new_bauteil(json.load(fd))
            fd.close()
        except:
            self.load_new_bauteil(self.neues_bauteil_template)
        
        try:
            self.file_location = str(self.log_dict['last_g_file'])
            if self.file_location != '':
                self.file_name = self.file_location[self.file_location.rfind('/')+1: len(self.file_location)]
                self.file_loaded = True
        except KeyError:
            self.log_dict['last_g_file'] = ''
            self.file_location = str(self.log_dict['last_g_file'])
            self.file_loaded = False

        try:
            self.x_home_diff = float(self.log_dict['x_home_diff'])
        except KeyError:
            self.log_dict['x_home_diff'] = str(107.25)
            self.x_home_diff = float(self.log_dict['x_home_diff'])
            
        try:
            self.z_home_diff = float(self.log_dict['z_home_diff'])
        except KeyError:
            self.log_dict['z_home_diff'] = str(90.3)
            self.z_home_diff = float(self.log_dict['z_home_diff'])
        
        try:
            passwd = self.log_dict['passwd']
        except KeyError:
            self.log_dict['passwd'] = "be2e41ec5420db9a790fc3dbab54b77d98e6265278412a16087196b95d0b2cb8"
        
        self.save_logfile(self.log_dict,self.log_name)        
        
        try:
            stat = os.stat(self.backen_ordner)
            os.path.isdir(self.backen_ordner)
        except OSError:
            os.mkdir(self.backen_ordner)
            stat = os.stat(self.backen_ordner)
        
        dirlist = os.listdir(self.backen_ordner)
        dirlist = sorted(dirlist,reverse=True)
        while len(dirlist) > 50:
            os.remove(self.backen_ordner + dirlist[-1])
            del dirlist[-1]
        self.log_dict_changed = False
        self.x_home_diff = float(self.log_dict['x_home_diff'])
        self.z_home_diff = float(self.log_dict['z_home_diff'])
        self.bt_mode = False
        self.prep_mode = False
        gobject.timeout_add(200, self.periodic)

        
if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == '-ini':
        app = fp_GUI(sys.argv[2])
    else:
        app = fp_GUI()

    
    
    gtk.main()
    