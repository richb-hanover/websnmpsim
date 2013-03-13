Web GUI for snmpsim (http://snmpsim.sourceforge.net)

This is a small Twisted program that provides a Web interface on the
.snmprec files used by the snmpsimd.py SNMP Simulator program to
respond with simulated SNMP data. It does several things:

1) It launches snmpsimd.py, so that the simulator itself runs normally.
2) It provides a small web server GUI on port 8880 to list all the
   simulated device files and the associated SNMP community strings.
3) It allows you to add .snmprec files to the current directory. When
   you add a file, it stops and restarts snmpsimd.py using the new file
   
Read the "README.txt" file for much more information about the snmpsim project.

To use the websnmpsim.py program:

- Retrieve the repository from github. It's at:
	https://github.com/richb-hanover/websnmpsim
- Install the project (sudo python setup.py install)
- Then cd to the snmpsim/scripts directory 
- Run it from a terminal window by typing: python scripts/websnmpsim.py
  snmpsimd.py will be running on the address/port indicated in the
  web GUI.
- Connect to the web GUI at: http://localhost:8880
- To upload a .snmprec file to the current directory, click Browse to
  select a file, then click Add
- Ctl-C in the terminal window to abort the program

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
