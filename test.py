#zuletzt getaner schritt: Die ueberhangstufe wird jetzt entsprechend gedreht. aber es muss noch ein bisschen geprueft werden, was passiert, wenn verschiedene 
#Datepunkte irgendwo dazwischen liegen. und es soll so gedreht werden, dass die schraege immer bis auf die hoehe des spannstufenanfangs geht.
#weiterhin muessen die Datenpunkte der schraege in die old_profile liste mit aufgenommen werden, sodass bei einer spaeteren Bearbeitung
# sinnvoll mit diesen sektionen umgegangen werden kann. Vielleicht ist es eine gute Idee die Punkte in x richtung um eine halbe schrittlaenge nach innen
#zu verschieben. bei weiterer Bearbeitung kann dann mit den punkten sicher normal umgegangen werden
#rueckfahrt zum start der Treppe mit einer Radiusfahrt mit r = sqrt(a*a+b*b)/2




#neue Idee: Es wird geprueft, wieviele Punkte zwischen den Eckpunkten der Auflageflaeche ist und dann geschaut, wie weit die Auflageflaeche nach unten
#verschoben werden muss, damit ein bestimmter Prozentsatz der Flaeche garantiert zur Verfuegung steht. Vorschlaege koennen gemacht werden fuer etwas weniger
#Auflageflaeche, aber dafuer eine kuerzere Bearbeitungszeit und weniger Backenabnutzung. Das koennte man machen, indem man die naechsten bzw die vorigen stufen
#bzgl der hoehe und breite auswertet.
#wahrscheinlich gibt es eine maximallaenge der auflageflaeche, die benoetigt wird. wovon die Abhaengig ist muss noch geklaert werden, damit das direkt von
#der Software ermittelt werden kann. vielleicht ist eine abstimmung mit dem Bediener dann noch sinnvoll.

'''
die Funktion backen_ausdrehen gibt abschliessend die Koordinaten fuer einen kurzen GCode Schnipse aus, die dann gefahren werden. Die Koordinaten werden
in einem speziellen Format als Liste ausgegeben:
list = [Block_rad,Block_auflage,Block_ueberhang]
Block = [step_a,step_b,step_c,...,step_n,block_area,block_time]
Step = [start,end,area,step_time]
start = [x_start,z_start]
end   = [x_end,z_end]
area  = (x_start - x_end)*(z_end - z_start)
step_time = area/(depth*speed)
block_time = step_time_0+step_time_1+...+step_time_n

das new_profile enthaelt die 5 koordinaten der backen, wie sie nachher zur Verfuegung stehen soll. Eine koordinate mehr, um im Radius zeit zu sparen.
das old_profile enthaelt eine beliebige Anzahl von Koordinaten die schon in die Backen eingedreht sind.
nach einem Drehdurchgang ist es notwendig die neuen Eckkoordinaten in das old_profile einzutragen und nicht mehr vorhandene Koordinaten zu loeschen
'''
import math
import matplotlib.pyplot as plt

#ion()
plt.axis([5,0,6,0])
mindest_auflagefl = 2
mindest_spannfl   = 0.1
sicherheit_spannfl = 0
depth = 0.1
speed = 5
ueberhang_stufe_x = 1
ueberhang_stufe_y = 1
ausdrehlimit = 10
#start = []
#end = []
#area = 0
#step_time

koord_tuple = [[3.0,0],[2,0.6],[0,1.6]]
profile_tuple = [[5,0],[3.5,1],[3.2,2],[0,3],[2.5,2.5],[2,3.5],[1,3],[1,5],[0.5,5.5],[0,6]] #[[3.5,0],[3,2],[2.5,2.5],[2,3],[1,4],[0.7,5],[0.5,5.5],[0,6]]
 #[[5,0],[4.5,0.5],[4,0.5],[3.5,1],[3,2],[2.5,2.5],[2,3],[1,4],[0.7,5],[0.5,5.5],[0,6]]


def clean_up_profile(old_profile):
  old_profile = sorted(old_profile,key=lambda x: x[0], reverse=True)
  #print old_profile
  h = 0
  #w = 100
  index = 0
  rm_list =[]
  for i in old_profile:
    if h>=i[1] and index != 0:
      rm_list.insert(0,index)
    else:
      h = i[1]
    index += 1
    
  #print rm_list
  while rm_list != []:
    del old_profile[rm_list[0]]
    del rm_list[0]
  old_profile = sorted(old_profile,key=lambda x: x[0], reverse=False)
  #print old_profile
  h = 0
  #w = 100
  index = 0
  rm_list =[]
  for i in old_profile:
    if h>=i[0] and index != 0:
      rm_list.insert(0,index)
    else:
      h = i[0]
    index += 1
    
  #print rm_list
  while rm_list != []:
    del old_profile[rm_list[0]]
    del rm_list[0]
  old_profile = sorted(old_profile,key=lambda x: x[0], reverse=True)
  
  return old_profile
  
def print_old_profile(profile_tuple):
  backe_max_x = 6
  backe_max_z = 7



  plt.axis([backe_max_x+0.5,-1,backe_max_z+0.5,-1])
  old_profile = clean_up_profile(profile_tuple)
  j = 0
  #print old_profile
  plt.plot([backe_max_x+0.5,old_profile[j][0]],[0,old_profile[j][1]],'r-')
  plt.fill_between([backe_max_x+0.5,backe_max_x+0.5,old_profile[j][0]],[0,backe_max_z+0.5,backe_max_z+0.5],color='b')
  #print "\n\n0:" , [backe_max_x+0.5,old_profile[j][0]],[0,old_profile[j][1]]
  #if len(old_profile) > 1:
  while j < len(old_profile):
      if j < len(old_profile)-1:
	#print str(j)+":",[old_profile[j][0],old_profile[j][0]],[old_profile[j][1],old_profile[j+1][1]]
	#print str(j)+":",[old_profile[j][0],old_profile[j+1][0]],[old_profile[j+1][1],old_profile[j+1][1]]
	plt.plot([old_profile[j][0],old_profile[j][0]],[old_profile[j][1],old_profile[j+1][1]],'r-')
	plt.plot([old_profile[j][0],old_profile[j+1][0]],[old_profile[j+1][1],old_profile[j+1][1]],'r-')
	#if j == 0:
	plt.fill_between([old_profile[j+1][0],old_profile[j+1][0],old_profile[j][0]],[old_profile[j+1][1],backe_max_z+0.5,backe_max_z+0.5],[old_profile[j+1][1],old_profile[j+1][1],old_profile[j+1][1]],color='b')
	#plt.fill_between(
      j+=1
  plt.plot([old_profile[-1][0], 0],[old_profile[-1][1], backe_max_z+0.5],'r-')
  #print [old_profile[-1][0], 0],[old_profile[-1][1], backe_max_z+0.5]
  plt.grid(True)
  #plt.show()
  #plt.fill_between([0,backe_max_x+0.5],[
  plt.savefig("plot.png")
  #print "grafik erstellt"
  return old_profile

def ueberhang(start_aufl,depth,old_profile,erste_stufe_x,erste_stufe_y,new_profile):#start_run_ueb,end_run_ueb,depth,old_profile):
  #print "old_profile: %s" %str(old_profile)
  #print "new_profile: %s" %str(new_profile)
  #j = 0
  #if old_profile[0][0]-start_aufl[0] < erste_stufe_x:
    #erste_stufe_x = start_aufl[0]+(old_profile[0][0] - start_aufl[0])
    #pass	
  #print "erste_stufe_x: %s" %erste_stufe_x
  if start_aufl[1]-old_profile[0][1] <erste_stufe_y:
    erste_stufe_y = start_aufl[1]-old_profile[0][1]
  step_ueb = []
  block_area = 0
  block_time = 0
  step_ueb_time = 0
  area_ueb = 0
  block_ueb_run = []
  #end_run = [0,0]
  #current_x = 0
  #current_z = 0
  start_run = [0,0]
  start_erste_stufe = [0,0]
  end_erste_stufe = [0,0]
  index = 0
  
  start_erste_stufe[0] = (start_aufl[0]+erste_stufe_x)
  end_erste_stufe = start_aufl
  for i in old_profile:
    if i[0] < (start_erste_stufe[0]):
      start_erste_stufe[1] = i[1]
      current_x = i[0]
      current_z = i[1]
      #print "break"
      break
    index += 1
  start_run = start_erste_stufe
  if (start_aufl[1]-start_erste_stufe[1]) > erste_stufe_y:
    diff = round(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth),3)
    #print diff
    if diff > 0:
      start_run = [start_erste_stufe[0],round(start_erste_stufe[1]+(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
      #print start_run
      end_run = [current_x,round(start_erste_stufe[1]+(math.fmod((start_aufl[1]-start_erste_stufe[1]),depth)),3)]
    else:
      start_run = [start_erste_stufe[0],start_erste_stufe[1]+depth]
      end_run = [current_x,start_erste_stufe[1]+depth]
    area_ueb = round((start_run[0]-end_run[0]),3)
    block_area = block_area + area_ueb
    step_ueb_time = round((area_ueb/speed),3)
    step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
    block_time = block_time + step_ueb_time
    block_ueb_run.append(step_ueb)
    
    while (start_aufl[1] - start_run[1] > erste_stufe_y):
      
      start_run = [start_erste_stufe[0],round(start_run[1]+depth,3)]
      for i in old_profile:
	if i[0] < start_run[0]:
	  current_x = i[0]
	  current_z = i[1]
	  break
      #print "current_x: %s current_z: %s" %(current_x, current_z)
      end_run = [current_x,start_run[1]]
      area_ueb = round((start_run[0]-end_run[0]),3)
      if start_run[1] > current_z:
	block_area = block_area + area_ueb
	step_ueb_time = round((area_ueb/speed),3)
      
	step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
      #print step_ueb
	block_time = block_time + step_ueb_time
	block_ueb_run.append(step_ueb)
      
    #for i in block_ueb_run:
      #print "blockrun: %s" %str(i)
    index = 0
    while (start_aufl[1] > start_run[1]):
      start_run = [round(start_run[0]-depth,3),round(start_run[1]+depth,3)]
      for i in old_profile:
	index += 1
	current_z = i[1]
	current_x = i[0]
	if i[0] < start_run[0]:
	  break
      #print "current_x: %s current_z: %s" %(current_x, current_z)
      end_run = [current_x,start_run[1]]
      area_ueb = round((start_run[0]-end_run[0]),3)
      if start_run[1] > current_z:
	block_area = block_area + area_ueb
	step_ueb_time = round((area_ueb/speed),3)
	step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
	block_time = block_time + step_ueb_time
	block_ueb_run.append(step_ueb)
      
    block_ueb_run.append(block_area)
    block_ueb_run.append(block_time)
    #for i in block_ueb_run:
      #print "blockrun: %s" %str(i)
    #while
  
  #print "start: %s  end: %s" %(str(start_run),str(end_run))
  #print "current_x: %s index: %s" %(current_x, index)
  #print "current_z: %s index: %s" %(current_z, index)
  #index = 0
  #diff = round(math.fmod((end_run_ueb[1]-start_run_ueb[1]),depth),3)
  #print "end_run: %s start_run: %s diff: %s" %(str(end_run_ueb),str(start_run_ueb),str(diff))
  
  #if diff != 0:
    #start_run = [start_run_ueb[0]-(math.fmod((end_run_ueb[1]-start_run_ueb[1]),depth)),start_run_ueb[1]]
    #end_run = [current_x,current_z+depth]
  ##else:
  #start_run = [start_run[0]-depth,start_run[1]]
  #end_run = [current_x,start_run[1]+depth]
  #area_ueb = round((start_run[0]-end_run[0])*(end_run[1]-start_run[1]),3)
  #block_area = block_area + area_ueb
  #step_ueb_time = round(area_ueb/(depth*speed),3)
  #step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
  ##print step_ueb
  #block_time = block_time + step_ueb_time
  #block_ueb_run.append(step_ueb)
  #j+=1
  
  #while(start_run[1] < end_run_ueb[1]):
    ##print "hier"
    
    
    #index = 0
    #start_run = [round(start_run[0]-depth,3),round(start_run[1]+depth,3)]
    ##start_run[1] = round(start_run[1]+depth,3)
    ##print start_run
    ##end_run = [round(start_run[0]-depth,3),round(start_run[1]+depth,3)]
    #end_run = [current_x,round(start_run[1]+depth,3)]
    ##end_run[1] = round(start_run[1]+depth,3)	
    ##print end_run
    #area_ueb = round((start_run[0]-end_run[0])*(end_run[1]-start_run[1]),3)
    #step_ueb_time = round(area_ueb/(depth*speed),3)
    ##print step_ueb
    #step_ueb = [start_run,end_run,area_ueb,step_ueb_time]
    ##print block_ueb_run
    #block_time = block_time + step_ueb_time  
    #block_area = block_area + area_ueb
    #block_ueb_run.append(step_ueb)
    #j+=1
  #area_ueb = round(((((start_run_ueb[0]-end_run_ueb[0])**2)+((end_run_ueb[1]-start_run_ueb[1])**2))**(1.0/2.0)),3)
  #step_ueb_time = round(area_ueb/(speed),3)
  #step_ueb = [start_run_ueb,end_run_ueb,area_ueb,step_ueb_time]
  #block_time = block_time + step_ueb_time  
  #block_ueb_run.insert(0,step_ueb)
  #block_ueb_run.append(block_area)
  #block_ueb_run.append(block_time)

  return block_ueb_run
  
def rueckenradius(end_aufl,end_rad, depth, old_profile):
  #print "end_aufl: %s" %end_aufl
  #print end_aufl[0]
  #print end_rad[1]
  #print end_aufl[1]
  #print end_rad[1]-end_aufl[1]
  #print (end_aufl[0]/(end_rad[1]-end_aufl[1]))
  #print depth
  #print depth*(end_aufl[0]/(end_rad[1]-end_aufl[1]))
  start_run = [0,0]
  end_run = [0,0]
  schrittweite_x = round(depth*(end_aufl[0]/(end_rad[1]-end_aufl[1])),3)
  schrittweite_y = round(depth,3)
  #print "schrittweite_x: %f" %schrittweite_x
  current_x = 0
  current_z = 0
  start_run = end_aufl
  block_area = 0
  block_time = 0
  block_rad = []
  while start_run[1] < end_rad[1]:
    #if current_x < round(start_run[0]-schrittweite_x,3):
    start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
      #continue
    #else:
      #start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
    
    
    for i in old_profile:
      #index += 1
      
      current_x = i[0]
      current_z = i[1]
      #print "current_x: %f  current_z: %f " %(current_x, current_z)
      #print "start_run[0]: %f  start_run[1]: %f " %(start_run[0], start_run[1])
      if i[0] < start_run[0]:
	break
    #print "current_x: %f  current_z: %f " %(current_x, current_z)
    #if current_x < round(start_run[0]-schrittweite_x,3):
      ##start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
    end_run 	= [current_x,start_run[1]]
      #continue
    #else:
      #start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
      #end_run 	= [current_x,start_run[1]]
    area = round((start_run[0]-end_run[0]),3)
    if start_run[1] > current_z:
      step_time = round(area/(speed),3)
      step = [start_run,end_run,area,step_time]
    #if current_x < round(start_run[0]-schrittweite_x,3):
    #start_run = [round(start_run[0]-schrittweite_x,3),round(start_run[1]+schrittweite_y,3)]
    #end_run 	= [current_x,start_run[1]]
      #continue
    #else:
    #end_run 	= [current_x,start_run[1]]
    #area = round((start_run[0]-end_run[0]),3)
    #step_time = round(area/(speed),3)
    #step = [start_run,end_run,area,step_time]
      block_area = block_area + area
      block_time = block_time + step_time
      block_rad.append(step)
  block_rad.append(block_area)
  block_rad.append(block_time)
  j = 0
  #for i in block_rad:
    #print "%d: %s" %(j,str(i))
    #j += 1
    
  return block_rad

    
def backen_drehen(new_profile, old_profile):
  block_rad = []
  block_aufl= []
  pre_block_aufl= []
  
  block_ueb = []
  proc_dict = {}
  block_area = 0
  proc_dict['proc_time'] = 0
  proc_dict['proc_area'] = 0
  
  
def spannstufe(old_profile,new_profile,start_run,end_run):
  current_x = 0
  current_z = 0
  area = 0
  #proc_time = 0# = block_time_rad + block_time_aufl + block_time_ueb 
  new_profile = sorted(new_profile,key=lambda x: x[0], reverse=True)
  old_profile = sorted(old_profile,key=lambda x: x[0], reverse=True)
  #print new_profile
  
  for i in old_profile:
    if i[0]<new_profile[0][0]:
      current_z = i[1]
      current_x = i[0]
      #print current_x
      break
    
  #current_z = old_profile[index][1]
  ##current_x = old_profile[index][0]
  #print "current_x drehen: %s" %current_x
  #print "current_z drehen: %s" %current_z
  #print "new_profile:"
  h = 0
  for i in new_profile:
    i[1] = round(i[1]+current_z,3)
    #print "%d: %s" %(h,i) 
    if i[1] >= ausdrehlimit:
      #print "Backe ist zu abgenutzt. Bitte auswechseln!"
      return 0
    h += 1
  unter_spannfl =[]
  steps = 0
  bottom_koord = False
  next_to_spannfl = []
  start_found = False
  end_found = False
  has_min_spannfl = False
  block_time = 0
  index = 0
  #print "spannflaeche zwischen x: %d-%d mit hoehein z: %d" %(new_profile[1][0], new_profile[2][0],(new_profile[2][1]-new_profile[1][1]))
  #als erstes suchen wir nach einer eventuell vorhandenen spannflaeche, oder Punkte in richtung 0 nahe der Spannflaeche
  #print "block_time: %f" %block_time
  
  for i in old_profile:
   
    if i[0] == new_profile[0][0] and start_found == False:
      #print "spannflaeche gefunden: %s" %str(i)
      unter_spannfl.append(i)
      next_to_spannfl = i
      next_to_spannfl_index = index
      start_found = True

      #print "start Nr1: %s" %str(i)
      
    elif i[0] < new_profile[0][0] and start_found == False: #and i[0] > new_profile[2][0]:
      #print "punkte kleiner als Spannflaeche aber groesser als radiusstufe: %s" %str(i)
      #print "start Nr2: %s" %str(new_profile[0])
      next_to_spannfl = i
      next_to_spannfl_index = index
      unter_spannfl.append(i)
      unter_spannfl.insert(0,new_profile[0])
      start_found = True
      spannfl_hoehe = i[1]
      steps += 1

    elif start_found == True and end_found == False and (i[1]-next_to_spannfl[1]) >= mindest_spannfl and (next_to_spannfl[0] - i[0]) >= mindest_auflagefl:
      end_found = True
      if has_min_spannfl != True:
	unter_spannfl.append([i[0],next_to_spannfl[1]+mindest_spannfl])
	#print "ende: %s" %str([i[0],next_to_spannfl[1]+mindest_spannfl])
	next_to_radius_index = index
      else:
	unter_spannfl.append(i)
	next_to_radius_index = index
	##print "ende: %s" %str(i)
      break
    elif i[0]< new_profile[0][0]:
      #print i
      if i[1]-mindest_spannfl > 0:
	has_min_spannfl = True
      steps += 1
      unter_spannfl.append(i)
    index += 1
    
    
  
    #print steps
    
    
    
    #if bottom_koord == True:
      #unter_spannfl.append(i)
      #bottom_koord = False
      #break
    #if i[0] == new_profile[1][0]:
      #print "spannflaeche gefunden: %s" %str(i)
      #unter_spannfl.append(i)
      #spannfl_hoehe = i[1]
    #if i[1]-spannfl_hoehe>= (mindest_spannfl+sicherheit_spannfl):
      #bottom_koord = True
     
  #print unter_spannfl
  #print next_to_spannfl
  step_counter = 0
  #print "old_profile: %s" %str(old_profile)
  #print "new_profile: %s" %str(new_profile)
  end_ueb = []
  if len(old_profile) < 2:
    pass
    
  while (steps > step_counter):
    start = [unter_spannfl[0][0],unter_spannfl[step_counter+1][1]]
    if unter_spannfl[step_counter+2][1] > new_profile[1][1]:
      end = [unter_spannfl[step_counter+1][0],new_profile[1][1]]
    else:
      end = [unter_spannfl[step_counter+1][0],unter_spannfl[step_counter+2][1]]
    #if end[1] - start[1] > new_profile[1][1]-new_profile[0][1] and step_counter == 0:
      #end_ueb = [start[0],end[1]-(new_profile[1][1]-new_profile[0][1])]
      #start = end_ueb
    #old_profile.append(end)
    #print "start: %s end: %s" %(str(start), str(end))
    area = (start[0]-end[0])
    step_time = area/(speed)
    step = [start,end,area,step_time]
    #block_area = block_area + area
    #block_time = block_time + step_time
    #print "area: %f" %area
    pre_block_aufl.append(step)
    step_counter += 1
    j = 0
  pre_block_aufl.append(block_area)
  pre_block_aufl.append(block_time)
  index = 0
  #print "block_time: %f" %block_time
  
  while(index < len(pre_block_aufl)-2):
    start_run = pre_block_aufl[index][0]
    end_run = pre_block_aufl[index][1]
    #print "start_run_aufl: %s end_run_aufl: %s" %(start_run, end_run)
    for i in old_profile:
      #index += 1
      
	current_x = i[0]
	current_z = i[1]
      
      #print "start_run[0]: %f  start_run[1]: %f " %(start_run[0], start_run[1])
	if i[0] < start_run[0]:
	  break
    if round(math.fmod(end_run[1]-start_run[1],depth) > 0):
      end = [current_x,round(start_run[1]+math.fmod(end_run[1]-start_run[1],depth),3)]
      start_run = [start_run[0],round(start_run[1]+math.fmod(end_run[1]-start_run[1],depth),3)]
      area = round((start_run[0]-current_x),3)
      step_time = round(area/(speed),3)
      step = [start_run,end,area,step_time]
      block_area = block_area + area
      block_time = block_time + step_time
      block_aufl.append(step)
    
  
    
    while(start_run[1] < end_run[1]):
      index = 0
      for i in old_profile:
	index += 1	
      
	current_z = i[1]
	
	current_x = i[0]
	#print "start_run[0]: %f  start_run[1]: %f " %(start_run[0], start_run[1])
	if i[0] < start_run[0] :
	  break
      #print "current_x: %f  current_z: %f " %(current_x, current_z)
      end = [current_x,round(start_run[1]+depth,3)]
      start_run = [start_run[0],round(start_run[1]+depth,3)]
      area = round((start_run[0]-current_x),3)
      step_time = round(area/speed,3)
      step = [start_run,end,area,step_time]
      block_area = block_area + area
      block_time = block_time + step_time
      block_aufl.append(step)
  
    index += 1
  
  #print "block_time: %f" %block_time
  block_aufl.append(block_area)
  block_aufl.append(block_time)
  
  #for i in block_aufl:
    #print "%d: %s" %(j,str(i))
    #j +=1
  #print old_profile
  old_profile = clean_up_profile(old_profile)
  #print new_profile
  block_ueb = ueberhang(new_profile[0],depth,old_profile,ueberhang_stufe_x,ueberhang_stufe_y,new_profile)#[new_profile[0][0]+erste_stufe_x,new_profile[0][1]-erste_stufe_y],new_profile[0],depth,old_profile)
  block_rad = rueckenradius(new_profile[1],new_profile[2],depth, old_profile)
  proc_dict['block_rad'] = block_rad
  proc_dict['block_ueb'] = block_ueb
  #print block_ueb
  if len(block_ueb) > 0:
    proc_dict['proc_time'] = proc_dict['proc_time'] + proc_dict['block_ueb'][len(proc_dict['block_ueb'])-1]
    proc_dict['proc_area'] = proc_dict['proc_area'] + proc_dict['block_ueb'][len(proc_dict['block_ueb'])-2]
  proc_dict['block_aufl'] = block_aufl
  proc_dict['proc_time'] = proc_dict['proc_time'] + proc_dict['block_aufl'][len(proc_dict['block_aufl'])-1]
  proc_dict['proc_area'] = proc_dict['proc_area'] + proc_dict['block_aufl'][len(proc_dict['block_aufl'])-2]
  j = 0
  
  #print old_profile
  #print new_profile
  #print "koord_list:"
  #print "Ueberhang:"
  for i in proc_dict['block_ueb']:
    if type(i) is not float:
      #plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'b-')#,i[1])
      #plt.plot(i[1][0],i[1][1],'bo')
      ##print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[1][0]),str(i[0][1]),str(i[1][1]))
      j +=1
    #else:
      #print i
  #print "Auflage:"
  for i in proc_dict['block_aufl']:
    if type(i) is not float:
      #plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'b-')#,i[1])
      
      #plt.plot(i[0][0],i[0][1],'bo')#,i[1])
      #plt.plot(i[1][0],i[1][1],'bo')
      #print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
      j +=1
    #else:
      #print i
  #print "Radius:"
  if len(proc_dict['block_rad']) >2:
    for i in proc_dict['block_rad']:
      if type(i) is not float:
	#plt.plot([i[0][0],i[1][0]],[i[0][1],i[1][1]],'b-')#,i[1])
	
	#plt.plot(i[0][0],i[0][1],'bo')#,i[1])plt.plot(i[1][0],i[1][1],'ro')
	#plt.plot(i[1][0],i[1][1],'bo')
	#print "%d: %s %s %s %s" %(j,str(i[0][0]),str(i[0][1]),str(i[1][0]),str(i[1][1]))
	j +=1
  #print "Prozesszeit: %s Minuten" %str(proc_dict['proc_time'])
  #print "entnommene Flaeche: %s qmm" %str(proc_dict['proc_area'])
backen_drehen(koord_tuple,profile_tuple)