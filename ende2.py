'''
Als letztes muss jetzt noch die Justierung der Maschine und die Ermittlung der Offsets bewerkstelligt werden. dafuer soll ein separates Fenster
genutzt werden, auf dem so wenig Buttons wie moeglich sind, um die Einstellungen moeglichst simpel zu gestalten Die Reihenfolge der Einrichtung wird
dabei genau vorgegeben und schritt fuer schritt erklaert. Die erklaerung wird dann in einem extra Textfeld dargestellt.
'''



import math
import matplotlib
matplotlib.use('GTKAgg')
import matplotlib.pyplot as plt
import pickle

class backen_ausdrehen(object):


  def clean_up_profile(self):
    self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
    h = 0
    index = 0
    rm_list =[]
    for i in self.old_profile:
      if h>=i[1] and index != 0:
	rm_list.insert(0,index)
      else:
	h = i[1]
      index += 1
    while rm_list != []:
      del self.old_profile[rm_list[0]]
      del rm_list[0]
    self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=False)
    h = 0
    index = 0
    rm_list =[]
    for i in self.old_profile:
      if h>=i[0] and index != 0:
	rm_list.insert(0,index)
      else:
	h = i[0]
      index += 1
      

    while rm_list != []:
      del self.old_profile[rm_list[0]]
      del rm_list[0]
    
    self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
    
    return 0
    
  def print_old_profile(self):
    #backe_max_x = 6
    #backe_max_z = 7
    plt.clf()
    plt.axis([self.x_offset_backe+self.backenlaenge+0.5,self.x_offset_backe-1,self.ausdrehlimit_z+0.5,-1])
    self.clean_up_profile()
    j = 0
    plt.plot([self.x_offset_backe+self.backenlaenge+0.5,self.old_profile[j][0]],[0,self.old_profile[j][1]],'r-')
    plt.fill_between([self.x_offset_backe+self.backenlaenge+0.5,self.x_offset_backe+self.backenlaenge+0.5,self.old_profile[j][0]],[0,self.ausdrehlimit_z+0.5,self.ausdrehlimit_z+0.5],color='b')
    while j < len(self.old_profile):
	if j < len(self.old_profile)-1:
	  
	  plt.plot([self.old_profile[j][0],self.old_profile[j][0]],[self.old_profile[j][1],self.old_profile[j+1][1]],'r-')
	  plt.plot([self.old_profile[j][0],self.old_profile[j+1][0]],[self.old_profile[j+1][1],self.old_profile[j+1][1]],'r-')
	  plt.fill_between([self.old_profile[j+1][0],self.old_profile[j+1][0],self.old_profile[j][0]],[self.old_profile[j+1][1],self.ausdrehlimit_z+0.5,self.ausdrehlimit_z+0.5],[self.old_profile[j+1][1],self.old_profile[j+1][1],self.old_profile[j+1][1]],color='b')
	j+=1
    plt.plot([self.old_profile[-1][0], 0],[self.x_offset_backe, self.ausdrehlimit_z+0.5],'r-')
    plt.grid(True)
    
    plt.savefig("plot.png")
    return 0
    
  def spannstufe(self,new_profile):
    
    current_x = 0
    current_z = 10
    area = 0
    new_profile = sorted(new_profile,key=lambda x: x[0], reverse=True)
    
    self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
    '''
    hier ist das Profil noch so, wie is in eine frische Backe gedreht werden wuerde,
    So kann man am einfachsten die Koordinaten uebergeben.
    Jetzt muss das neue Profil aber an die schon eingedrehte Backe angepasst werden.
    Dazu wird ermittelt, wo das neue Profil anfaengt und die entsprechende hoehe als oberste Kante der Backe angegeben
    '''
    self.clean_up_profile()
    
    hight_found = False
    width_found = False
    aufl_start_z_found = False
    aufl_end_z_found = False
    if self.mindest_auflagefl > 3.0:
      new_profile.append([round(new_profile[0][0] - 3.0,3),round(new_profile[0][1] + self.mindest_spannfl,3)])
    else:
      new_profile.append([round(new_profile[0][0] - self.mindest_auflagefl,3),round(new_profile[0][1] + self.mindest_spannfl,3)])
    for i in self.old_profile:
      if i[0]<=new_profile[0][0] and new_profile[0][1] == 0 and aufl_start_z_found == False:
	new_profile[0][1] = round(i[1],3)
	new_profile[1][1] = round(new_profile[0][1] +self.mindest_spannfl,3)
	aufl_start_z_found= True
      if i[0]<=new_profile[1][0] and i[1] == new_profile[0][1] and aufl_end_z_found == False:
	new_profile[1][1] = round(new_profile[0][1] + self.mindest_spannfl,3)
	aufl_end_z_found = True
	break
      if i[0] < new_profile[1][0] and i[1] > new_profile[1][1] and aufl_end_z_found == False:
	new_profile[1][1] = i[1]
	new_profile[0][1] = round(new_profile[1][1] - self.mindest_spannfl,3)
	aufl_end_z_found = True
	break
      if i[0] < new_profile[1][0] and i[1] < new_profile[1][1] and aufl_end_z_found == False:
	break
    return new_profile

  def spannstufe_koordinaten(self,start_run,end_run, depth):
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
	if round(math.fmod(end_run[1]-start_run[1],depth),3) > 0.0:
	  end = [round(current_x-0.1,3),round(start_run[1]+math.fmod(end_run[1]-start_run[1],depth),3)]
	  for i in self.old_profile:
	    if i[1]< end[1] and i[0]< end[0]:
	      end[0] = round(i[0]-0.1,3)
	  start_run = [start_run[0],round(start_run[1]+math.fmod(end_run[1]-start_run[1],depth),3)]
	  
	  if round(start_run[0]-end[0],3) > round(0.1,1):
	    area = round((start_run[0]-current_x-0.1),3)
	    step_time = round(area/(self.speed),3)
	    step = [start_run,end,area,step_time]
	    block_area = block_area + area
	    block_time = block_time + step_time
	    self.aufl_counter += 1
	    block_aufl.append(step)
	else:
	  end = [round(current_x-0.1,3),round(start_run[1]+depth,3)]
	  for i in self.old_profile:
	    if i[1]< end[1] and i[0]< end[0]:
	      end[0] = round(i[0]-0.1,3)
	  start_run = [start_run[0],round(start_run[1]+depth,3)]
	  if round(start_run[0]-end[0],3) > round(0.1,1):
	    area = round((start_run[0]-current_x-0.1),3)
	    step_time = round(area/self.speed,3)
	    step = [start_run,end,area,step_time]
	    block_area = block_area + area
	    block_time = block_time + step_time
	    self.aufl_counter += 1
	    block_aufl.append(step)
    block_aufl.append(block_area)
    block_aufl.append(block_time)
    #print "am ende der Funktion 'spannstufe_koordinaten' sind die Spannstufenschichten berechnet und auch der parameter aufl_counter ist festgelegt. aufl_counter = ", self.aufl_counter
    return block_aufl

    
    
    
  def ueberhang(self,start_aufl,depth,erste_stufe_x,erste_stufe_y,new_profile):#start_run_ueb,end_run_ueb,depth):
    self.ueb_counter = 0
    if start_aufl[1]-self.old_profile[0][1] < erste_stufe_y:
      erste_stufe_y = start_aufl[1]-self.old_profile[0][1]
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
	start_run = [start_erste_stufe[0],round(start_erste_stufe[1]+(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
	end_run = [current_x-0.1,round(start_erste_stufe[1]+(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
      else:
	start_run = [start_erste_stufe[0],start_erste_stufe[1]+depth]
	end_run = [current_x-0.1,start_erste_stufe[1]+depth]
      for i in self.old_profile:
	    if i[1]< end_run[1] and i[0]< end_run[0]:
	      end_run[0] = i[0]-0.1
      area_ueb = round((start_run[0]-end_run[0]),3)
      block_area = block_area + area_ueb
      step_ueb_time = round((area_ueb/self.speed),3)
      step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
      block_time = block_time + step_ueb_time
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
	  block_area = block_area + area_ueb
	  step_ueb_time = round((area_ueb/self.speed),3)
	
	  step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
	  block_time = round(block_time + step_ueb_time,3)
	  self.aufl_counter+= 1
	  self.ueb_counter += 1
	  block_ueb_run.append(step_ueb)
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
    end_aufl = new_profile[1]
    current_z = 0
    current_x = 0
    schrittweite_y = round(depth,3)
    #print "new_profile[1][0]", new_profile[1][0]
    l = new_profile[0][0]-self.mindest_auflagefl - self.ruecken_nabe_durchm/2
    steigung = hoehe_radius/l
    d = steigung *(new_profile[0][0]-self.mindest_auflagefl-self.x_offset_backe)
    
    #a = 0
    #b = 0
    #c = 0
    #d = 0
    #try:
      #b = new_profile[1][0]-self.x_offset_backe
      #c = hoehe_radius-0.1
      #a = math.sqrt(math.pow(c,2)-math.pow(b,2))
      #d = round(c-a,3)
    #except ValueError:
      #print "Fehler im Radius"
    #print "a:%f, b:%f, c:%f, d%f." %(a,b,c,d) 
    for i in self.old_profile:
      if round(new_profile[1][0] - hoehe_radius,3) > round(i[0],3):
	current_x = i[0]
	current_z = i[1]
	#print "current_x:" ,current_x
	#print "current_z:" ,current_z
	break
    #rad_tiefe = math.sqrt(math.pow(hoehe_radius,2)-math.pow(end_aufl[0]-self.old_profile[-1][0],2))
    #print "rad_tiefe",rad_tiefe
    #if current_z > round(new_profile[1][1]+hoehe_radius,3):
      ##new_profile.append([new_profile[1][0]-hoehe_radius,current_z])
      #new_profile.append([current_x,current_z])
    #else:
      #new_profile.append([new_profile[1][0]-hoehe_radius,new_profile[1][1]+hoehe_radius])
    new_profile.append([current_x,round(new_profile[1][1],3)])
    new_profile[2][1] = new_profile[1][1] + d
    end_rad = new_profile[2]
    schritte = (end_rad[1]-end_aufl[1])/depth
    #print "schritte", schritte
    schrittweite_x = (end_aufl[0]-self.x_offset_backe)/schritte
    #print "new_profile\nhallo\n", new_profile
    if new_profile[1][0] == self.x_offset_backe:
      new_profile[2][1] = round(new_profile[1][1] + 0.05,3)
      new_profile[1][0] = round(0.05,3)
    ##print "new_profile", new_profile
    start_run = [0,0]
    end_run = [0,0]
    #schrittweite_x = round(depth,3)#*(end_aufl[0]/(end_rad[1]-end_aufl[1])),3)
    schrittweite_y = round(depth,3)
    #print "schrittweite_x: %f" %schrittweite_x
    current_x = 0
    current_z = 0
    start_run = end_aufl
    block_area = 0
    block_time = 0
    block_rad = []
    index= 0
    
    
    while start_run[1] <= end_rad[1]:
      #print "start_run[1]:",start_run[1]
      #print "end_rad[1]:",end_rad[1]	
      #if current_x < round(start_run[0]-schrittweite_x,3):
      if index == 0:
	start_run = [round(start_run[0],3),round(start_run[1]+schrittweite_y,3)]
      else:
	if round(math.fmod(end_rad[1]-start_run[1],schrittweite_y),3) > 0 and index >= 2:
	  start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+round(math.fmod(end_rad[1]-start_run[1],schrittweite_y),3),3)]
	else:
	  start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
	#continue
      #else:
	#start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
      
      index += 1
      for i in self.old_profile:
	#index += 1
	
	current_x = i[0]
	current_z = i[1]
	#print "current_x: %f  current_z: %f " %(current_x, current_z)
	#print "start_run[0]: %f  start_run[1]: %f " %(start_run[0], start_run[1])
	if i[0] < start_run[0]:
	  break
      #print "current_x: %f  current_z: %f " %(current_x, current_z)
      for i in self.old_profile:
	if start_run[1] < i[1]:
	  break
	current_x = round(i[0],3)
      if start_run[0] < 0:
	break
      #if current_x < round(start_run[0]-schrittweite_x,3):
	##start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
      end_run 	= [round(current_x-0.1,3),start_run[1]]
      for i in self.old_profile:
	if i[1]< end_run[1] and i[0]< end_run[0]:
	  end_run[0] = round(i[0]-0.1,3)
	#pass
      #if end_run[0] < 0.0:
	#end_run[0] = -0.1
	#continue
      #else:
	#start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
	#end_run 	= [current_x,start_run[1]]
      area = round((start_run[0]-end_run[0]),3)
      if start_run[1] > current_z and start_run[0] > end_run[0]:
	#if round(start_run[0]-end_run[0],3) > round(0.1,1):
	step_time = round(area/(self.speed),3)
	step = [start_run,end_run,area,step_time]
	#print "step:",step
	#if current_x < round(start_run[0]-schrittweite_x,3):
	#start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
	#end_run 	= [current_x,start_run[1]]
	  #continue
	#else:
	#end_run 	= [current_x,start_run[1]]
	#area = round((start_run[0]-end_run[0]),3)
	#step_time = round(area/(self.speed),3)
	#step = [start_run,end_run,area,step_time]
	block_area = round(block_area + area,3)
	block_time = round(block_time + step_time,3)
	block_rad.append(step)
    block_rad.append(block_area)
    block_rad.append(block_time)
    j = 0
    #print "block_rad nr 2?:"
    for i in block_rad:
      #print "%d: %s" %(j,str(i))
      j += 1
    #print "new_profile:", new_profile
    return block_rad
    
  def print_koordinates(self,block_ueb,block_stufe,block_rad,run):
    j = 0
    #print self.old_profile
    #print "block_ueb koordinaten list enhaelt folgende elemente:\n"
    for i in block_ueb:
      #print "%d: %s" %(j,str(i))
      j += 1
    if block_ueb != [0,0]:
      for i in block_ueb:
	  if type(i) is not float:
	    if i[1][1] > self.ausdrehlimit_z:
	      #print "backe ist abgenutzt"
	      self.abgenutzt = True
	      return 1
	    plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')
	    
	    plt.plot(i[0][0],i[0][1],'ro')
	    plt.plot(i[1][0],i[1][1],'go')
	    if run == True:
	      self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
	      self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
	    #print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	    #print "%d: (%s, %s) -> (%s, %s)" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	    self.gcode_koord.append([i[0],i[1]])
	    j +=1
    if len(block_stufe) > 2: 
      #print "block_stufe koordinaten list enhaelt folgende elemente:\n"
      for i in block_stufe:
	#print "%d: %s" %(j,str(i))
	j += 1
      for i in block_stufe:
	if type(i) is not float:
	  if i[1][1] > self.ausdrehlimit_z:
	    #print "backe ist abgenutzt"
	    self.abgenutzt = True
	    return 1
	  plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')
	  
	  plt.plot(i[0][0],i[0][1],'ro')
	  plt.plot(i[1][0],i[1][1],'go')
	  if run == True:
	    self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
	    self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
	  #print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	  #print "%d: (%s, %s) -> (%s, %s)" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	  self.gcode_koord.append([i[0],i[1]])
	  j +=1
    else:
      pass#print "blockstufe auch nicht"
      
    if len(block_rad) >2:
      #print "block_rad koordinaten list enhaelt folgende elemente:\n",
      for i in block_rad:
	#print "%d: %s" %(j,str(i))
	j += 1
      for i in block_rad:
	if type(i) is not float:
	  if i[1][1] > self.ausdrehlimit_z:
	    #print "backe ist abgenutzt"
	    self.abgenutzt = True
	    return 1
	  plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'r-')#,i[1])
	  
	  plt.plot(i[0][0],i[0][1],'ro')#,i[1])plt.plot(i[1][0],i[1][1],'ro')
	  plt.plot(i[1][0],i[1][1],'go')
	  if run == True:
	    self.old_profile.append([round(i[0][0],3),round(i[0][1]-self.depth,3)])
	    self.old_profile.append([round(i[1][0]+0.1,3),round(i[1][1],3)])
	  #print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	  #print "%d: (%s, %s) -> (%s, %s)" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	  self.gcode_koord.append([i[0],i[1]])
	j +=1
    else:
      pass	
      #print "abgefahren"
    plt.savefig("plot.png")
    #self.print_old_profile()
    #print "old_profile:", self.old_profile
    #print "self.ueb_start:",self.ueb_start
    #print "self.ueb_end:" ,self.ueb_end
    #print "block_ueb",block_ueb[-1]
    #print "block_stufe",block_stufe[-1]
    #print "block_rad",block_rad[-1]
    self.est_time = block_ueb[-1]+block_stufe[-1]+block_rad[-1]
    return 0
  
  def get_old_profile(self):
    self.print_old_profile()
    #print self.old_profile
    return self.old_profile
    
  def get_gcode_koord(self):
    self.gcode_koord = []
    self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,False)
    #print "Koordinaten der Start- und Endpunkte fuer das Drehen der Backe"
    #print "Die werden dann, mit den entsprechenden Offsets, in den GCode eingetragen"
    #for i in self.gcode_koord:
      #print i
    return self.gcode_koord
    
  def set_profile_tuple(self,profile_tuple):
    self.old_profile = sorted(profile_tuple,key=lambda x: x[0], reverse=True)
    self.print_old_profile()
  
  def ausdrehen_calc(self,koord_tuple,profile_tuple,speed,mindest_auflagefl,mindest_spannfl,depth,ueberhang_stufe_x,ueberhang_stufe_y,ruecken_nabe_durchm,hoehe_radius,ausdrehlimit_z,ausdrehlimit_x,backe_innenkante,backenlaenge): 
    self.x_offset_backe = backe_innenkante
    self.backenlaenge = backenlaenge
    self.old_profile = sorted(profile_tuple,key=lambda x: x[0], reverse=True)
    self.clean_up_profile()
    self.new_profile = sorted(koord_tuple,key=lambda x: x[0], reverse=True)
    #print "new_profile 1", self.new_profile
    
    #print "self.old_profile:" , self.old_profile
    self.speed = speed
    self.mindest_auflagefl = mindest_auflagefl
    self.mindest_spannfl = mindest_spannfl
    self.depth = depth
    self.ueberhang_stufe_x = ueberhang_stufe_x
    self.ueberhang_stufe_y = ueberhang_stufe_y
    self.hoehe_radius = hoehe_radius
    self.ruecken_nabe_durchm = ruecken_nabe_durchm
    self.gcode_koord = []
    #self.print_old_profile()
    #self.new_profile = self.spannstufe(self.new_profile)
    
    
    passed = 0
    self.print_old_profile()
    self.new_profile = self.spannstufe(self.new_profile)
    #print "new_profile 2", self.new_profile
    #print "ausdr", self.new_profile
    self.block_stufe = self.spannstufe_koordinaten(self.new_profile[0],self.new_profile[1],self.depth)
    self.block_ueb = self.ueberhang(self.new_profile[0],self.depth,self.ueberhang_stufe_x,self.ueberhang_stufe_y,self.new_profile)
    self.block_rad = self.rueckenradius(self.new_profile,self.hoehe_radius,self.depth)
    self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,False)
    #print "self.block_ueb",self.block_ueb
    #print "self.block_aufl",self.block_aufl
    #print "self.block_rad",self.block_rad
    
    return self.old_profile
    
  def ausdrehen_start(self):
    self.print_koordinates(self.block_ueb,self.block_stufe,self.block_rad,True)
    return self.old_profile
    
    
  
  def __init__(self):#,koord_tuple,profile_tuple,speed,mindest_auflagefl,mindest_spannfl,depth,ueberhang_stufe_x,ueberhang_stufe_y,hoehe_radius,ausdrehlimit_z,ausdrehlimit_x): 
    self.ausdrehlimit_z = 4
    self.ausdrehlimit_x = 25
    self.backe_innenkante = 12
    self.backenlaenge = 20
    koord_tuple = [[0,0]]
      #return None
    plt.clf()
    plt.figure(figsize=(6.5,2),dpi=200)
    self.aufl_counter = 0
    profile_tuple = [[0,0]]
    self.x_offset_backe= 12
    #koord_tuple = [[4.5,0]]
    #self.old_profile = pickle.load(open("profile.backe","rb"))
    #self.old_profile =[[3.5,0],[3,2],[2.0,2.5],[2,4],[1,4],[0.7,5],[0.5,5.5],[0,6],[0.5,5.5],[1,5],[0,3],[2,3.5],[1,3],[3.5,1],[3.2,2],[4,0],[0,6]]
    #self.old_profile =[[0,0]]
    self.new_profile = sorted(koord_tuple,key=lambda x: x[0], reverse=True)
    #if self.new_profile[0][0] > self.ausdrehlimit_x:
      #print "das Bauteil ist zu gross fuer die Backen" 
    #self.old_profile = sorted(self.old_profile,key=lambda x: x[0], reverse=True)
    self.old_profile = sorted(profile_tuple,key=lambda x: x[0], reverse=True)
    self.clean_up_profile()
    #print "self.old_profile:" , self.old_profile
    self.speed = 5# speed
    self.mindest_auflagefl = 0# mindest_auflagefl
    self.mindest_spannfl = 0#mindest_spannfl
    self.depth = 0#depth
    self.ueberhang_stufe_x = 0#ueberhang_stufe_x
    self.ueberhang_stufe_y = 0#ueberhang_stufe_y
    self.hoehe_radius = 0#hoehe_radius
    self.gcode_koord = []
    self.abgenutzt = False 
    #self.print_old_profile()
    #self.new_profile = self.spannstufe(self.new_profile)
    self.block_stufe = []#self.spannstufe_koordinaten(self.new_profile[0],self.new_profile[1],self.depth)
    self.block_ueb = []#self.ueberhang(self.new_profile[0],self.depth,self.ueberhang_stufe_x,self.ueberhang_stufe_y,self.new_profile)
    self.block_rad = []#self.rueckenradius(self.new_profile,self.hoehe_radius,self.depth)
    self.ueb_start = 0.0
    self.ueb_end = 0.0
    self.est_time = 0
    #self.aufl_hoehe = 0
    #self.print_koodinates(self.block_ueb,self.block_stufe,self.block_rad)
    #print "block_ueb:" ,block_ueb
    j = 0
    #print self.old_profile
    #for i in self.gcode_koord:
      #print i
    #fd = open("profile.backe","wd")
    #pickle.dump(self.old_profile,fd)
    #fd.close()
##if __name__ == "__main__":
  #backen = backen_ausdrehen([[0,0]],[[0,0]],5,1,1,0.1,1,1,1,4,6)