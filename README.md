# Web GUI for snmpsim - http://snmpsim.sourceforge.net

This provides a Web interface for the snmpsimd.py SNMP Simulator program written by written by Ilya Etingof <ilya@glas.net> 
The snmpsim program responds to SNMP queries as if it is a set of SNMP-speaking devices, thus simulating them. 
snmpsim uses the community string of the SNMP query to select which set of SNMP responses to send.

websnmpsim.py is basically a single file added to the base snmpsim distribution that 
provides the Web GUI. When it's installed, websnmpsim.py does several things:

1. It launches snmpsimd.py, so that the simulator itself runs normally.
2. It provides a small web-based GUI on port 8880 to list all the
   simulated devices and the associated SNMP community strings.
3. It allows you to import additional files that contain SNMP data, so that you can simulate additional devices.
   
Read the "README.txt" file for much more information about the snmpsim project. 
This project is based on the snmpsim 0.2.0 release of 12 March 2013.

To use the websnmpsim.py program:

- Retrieve the repository from github. It's at: https://github.com/richb-hanover/websnmpsim 
	or use `git clone https://github.com/richb-hanover/websnmpsim.git`
- cd to the websnmpsim folder and run the setup `sudo python setup.py install`
- cd to the snmpsim/scripts directory and run websnmpsim with `python websnmpsim.py`
- Connect to the web GUI at: http://localhost:8880. You will see a list of all the simulated devices.
  In addition, snmpsimd.py will be listening for SNMP queries address/port indicated in the
  web GUI.
- To upload a .snmprec file to the current directory, click Browse to
  select a file, then click Add
- Ctl-C in the terminal window to abort both the Web GUI and snmpsimd.py

Prequisites: You may need to install the following packages/modules 
	before snmpsimd.py and websnmpsim.py will run:
- easy_install (install this first to get the others)
- twisted
- pyasn1
- pysnmp 

WARNING: Although this program seems to work, it is a two-weekend hack.
   I wanted to learn a little about Twisted, so this program was
   a decent vehicle for that learning. I make no claim to the value
   of this as a starting point for further work.

   Since snmpsimd.py is already based on Python's asyncore, that module
   may be a better base for long-term development. In fact, the are
   a lot of lines of communication between the Web GUI and snmpsimd.py
   which argues that they should be combined.

Please let me know if this is useful for you, or contribute your
changes back to the snmpsim project. http://snmpsim.sourceforge.net

Rich Brown  
Hanover NH USA  
richb.hanover@gmail.com
