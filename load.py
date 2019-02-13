from config import config
import myNotebook as nb
from urllib import quote_plus
import requests

from canonn import journaldata
from canonn import factionkill
from canonn import nhss
from canonn import codex
from canonn import hdreport
from canonn import news



import ttk
import Tkinter as tk
import sys
    
this = sys.modules[__name__]

this.nearloc = {
   'Latitude' : None,
   'Longitude' : None,
   'Altitude' : None,
   'Heading' : None,
   'Time' : None
}
this.systemCache={ "Sol": (0,0,0) }

myPlugin = "EDMC-Canonn"

#this.debuglevel=2
this.version="4.8.0"
this.client_version="{}.{}".format(myPlugin,this.version)
this.body_name=None
    
def plugin_prefs(parent, cmdr, is_beta):
    """
    Return a TK Frame for adding to the EDMC settings dialog.
    """
    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)
    this.news.plugin_prefs(frame, cmdr, is_beta,1)
    return frame

    
def prefs_changed(cmdr, is_beta):
    """
    Save settings.
    """
    this.news.prefs_changed(cmdr, is_beta)
    
   
def plugin_start():
    """
    Load Template plugin into EDMC
    """
    
    #print this.patrol
    
    return 'Canonn'
    
def plugin_app(parent):

    this.parent = parent
    #create a new frame as a containier for the status
    padx, pady = 10, 5  # formatting
    sticky = tk.EW + tk.N  # full width, stuck to the top
    anchor = tk.NW

    frame = this.frame = tk.Frame(parent)
    frame.columnconfigure(0, weight=1)

    table = tk.Frame(frame)
    table.columnconfigure(1, weight=1)
    table.grid(sticky="NSEW")
    
    
    this.news = news.CanonnNews(table,0)
    
    
    
    return frame
    
   
def journal_entry(cmdr, is_beta, system, station, entry, state):
    '''
    Commanders may want to be anonymous so we we have a journal entry anonymiser
    that passes the journale entry to the one that does all the real work
    '''
    # capture some stats when we launch not read for that yet
    # startup_stats(cmdr)

    if config.getint("Anonymous") >0:
        commander="Anonymous"
        if cmdr in str(entry):
            #entry["cmdrName"]="Anonymous"
            s = str(entry).replace(cmdr,"Anonymous")
            entry=eval(s)
    else:
        commander=cmdr
        
    if ('Body' in entry):
            this.body_name = entry['Body']        
        
    if system:
        x,y,z=edsmGetSystem(system)
    else:
        x=None
        y=None
        z=None    
    
    return journal_entry_wrapper(commander, is_beta, system, station, entry, state,x,y,z,this.body_name,this.nearloc['Latitude'],this.nearloc['Longitude'],this.client_version)    
    
# Detect journal events
def journal_entry_wrapper(cmdr, is_beta, system, station, entry, state,x,y,z,body,lat,lon,client):
    factionkill.submit(cmdr, is_beta, system, station, entry,client)
    nhss.submit(cmdr, is_beta, system, station, entry,client)
    hdreport.submit(cmdr, is_beta, system, station, entry,client)
    #codex.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
    #btreports.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
    #fgreports.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
    #csreports.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
    codex.submit(cmdr, is_beta, system, x,y,z, entry, body,lat,lon,client)
    journaldata.submit(cmdr, is_beta, system, station, entry,client)
    
def dashboard_entry(cmdr, is_beta, entry):
      
    
    this.landed = entry['Flags'] & 1<<1 and True or False
    this.SCmode = entry['Flags'] & 1<<4 and True or False
    this.SRVmode = entry['Flags'] & 1<<26 and True or False
    this.landed = this.landed or this.SRVmode
      #print "LatLon = {}".format(entry['Flags'] & 1<<21 and True or False)
      #print entry
    if(entry['Flags'] & 1<<21 and True or False):
        if('Latitude' in entry):
            this.nearloc['Latitude'] = entry['Latitude']
            this.nearloc['Longitude'] = entry['Longitude']
    else:
        this.body_name = None
        this.nearloc['Latitude'] = None
        this.nearloc['Longitude'] = None    
    
def edsmGetSystem(system):
    
    if this.systemCache.has_key(system):
    
        return this.systemCache[system]
        
    else:
        url = 'https://www.edsm.net/api-v1/system?systemName='+quote_plus(system)+'&showCoordinates=1'      
        #print url
        r = requests.get(url)
        s =  r.json()
        #print s
    
        this.systemCache[system]=(s["coords"]["x"],s["coords"]["y"],s["coords"]["z"])
        return s["coords"]["x"],s["coords"]["y"],s["coords"]["z"]    