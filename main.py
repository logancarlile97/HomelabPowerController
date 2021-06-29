from KeypadDriver import KeypadDriver, Authenticator
from ConfigReader import ConfigReader
import logging
from LcdDriver import LcdDriver
import time
import subprocess
from CSVreader import CSVreader
import sys

class HLPC:
    """
    Class to allow for all frontend operations of the HLPC program.
    """
    
    def __init__(self):
        self.config = ConfigReader('config.ini')

        #Create and configure logger
        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)

        self.log = logging.getLogger()

        self.lcd = LcdDriver()
        self.keypad = KeypadDriver()

        self.auth = Authenticator()

    def exitPrgm(self):
        """
        Makes user confirm they want to exit program
        """
        self.lcd.print('Confirm: 2468#', 'Go Back: #')
        userConfirmation = self.keypad.input()
        if(userConfirmation == '2468'):
            return True
        else: 
            return False
        
    def printIpAddr(self):
        """
        Prints host IP address to lcd
        """
        log = self.log
        lcd = self.lcd
        keypad = self.keypad

        hostname = subprocess.run('hostname', shell=True, capture_output=True, text = True).stdout #Command in linux to return hostname
        ipAddress = subprocess.run('hostname -I', shell=True, capture_output=True, text = True).stdout #Command in linux to return currently set ipv4 addresses
        hostname = hostname.strip() #Remove all escape sequences
        ipAddress = ipAddress.strip()#Remove all escape sequences
            
        lcd.print('Press any key', 'to exit')
        time.sleep(2)
        log.info(f'print IP has gathered that the host hostname is {hostname}, and the ip is {ipAddress}')
        
        
        atEnd = False
        for i in range(len(ipAddress)): #This for loop will scroll an ip that is too long to fit on the lcd
            shortIP = ''
            for x in range(16):
                if (i+x >= len(ipAddress)):
                    atEnd = True
                    break
                else:
                    shortIP += ipAddress[i+x]
            lcd.print(f'{hostname}', f'{shortIP}')
            time.sleep(1)
            if (atEnd):
                lcd.print('', f'{ipAddress}')
                break

        keypad.press() #Wait for user to press a key to contine

    def remoteShutdown(self):
        """
        Method to run a remote shutdown of hosts via SSH. Uses CSV file specified in config.ini
        """
        log = self.log
        lcd = self.lcd

        log.warning(f'User is running HLPC shutdown')
        shutdownCSV = CSVreader(self.config.getShutdownConfig('shutdownCSVfile'))
        shutdownCSV.hasHeader() #Shutdown CSV is expected to have a header
        remoteMachinesInfo = shutdownCSV.parseCSV() #Parse the csv file to a list of lists

        for remoteInfo in remoteMachinesInfo: #Loop through each list in the the remoteMachinesInfo list
            machineName = remoteInfo[0]
            ipAddr = remoteInfo[1]
            rmtUsr = remoteInfo[2]
            cmd = remoteInfo[3]
            pingCmd = f'ping -c 3 {ipAddr}'
            sshCmd = f'ssh -t -t -o BatchMode=yes -o ConnectTimeout=15 {rmtUsr}@{ipAddr} \'{cmd}\'' 

            log.debug(f'Current constructed ping command is: \n\t{pingCmd}')
            log.debug(f'Current constructed ssh command is: \n\t{sshCmd}')
            log.info(f'Checking if {machineName} is alive')
            lcd.print(f'Checking', f'{machineName}')
            
            ping = subprocess.run(pingCmd, shell=True, capture_output=True, text = True) #Run a ping command for the current machine
            pingRtrnCode = ping.returncode #Capture return code
            pingOutput = ping.stdout #Capture output
            pingErrOutput = ping.stderr #Capture errors

            log.info(f'Ping output for {machineName} is: \n{pingOutput}\n{pingErrOutput}')
            log.info(f'Ping return code is: {pingRtrnCode}')
            time.sleep(2)
            
            if(pingRtrnCode == 0): #If ping was succesful
                lcd.print(f'{machineName}', 'is Alive')
                time.sleep(2)
                log.warning(f'{machineName} is alive')
                
                lcd.print(f'Shutting Down', f'{machineName}')
                log.warning(f'Performing shutdown on {machineName} ({ipAddr}) via user {rmtUsr} using shutdown command {cmd}')
                
                ssh = subprocess.run(sshCmd, shell=True, capture_output=True, text = True)
                sshErrOutput = ssh.stderr #Capture errors
                sshOutput = ssh.stdout #Capture output
                sshRtrnCode = ssh.returncode #Capture return code
                
                log.info(f'SSH output for {machineName} is: \n{sshOutput}\n{sshErrOutput}')
                log.info(f'SSH return code is: {sshRtrnCode}')
                if(sshRtrnCode != 0): #If ssh command was not succesful
                    lcd.print(f'Error Please',f'Check Logs')
                    log.error(f'Error shuting down {machineName}, ssh return code is: {sshRtrnCode}')
                    log.error(f'SSH output: \n{sshOutput}\n{sshErrOutput}')
                    time.sleep(3)
                time.sleep(2)
            else: #If ping was not succesful
                log.warning(f'{machineName} was not determind to be alive, assumed dead')
                lcd.print(f'{machineName}', f'is Dead')
                time.sleep(2)
        lcd.clear()

    def remotePowerOn(self):
        """
        Method to run a remote power on of hosts. Uses CSV file specified in config.ini.
        """
        log = self.log
        lcd = self.lcd

        log.warning(f'User is running HLPC powerOn')
        powerOnCSV = CSVreader(self.config.getPowerOnConfig('powerOnCSVfile'))
        powerOnCSV.hasHeader() #Shutdown CSV is expected to have a header
        remoteMachinesInfo = powerOnCSV.parseCSV() #Parse the csv file to a list of lists

        for remoteInfo in remoteMachinesInfo: #Loop through each list in the the remoteMachinesInfo list
            machineName = remoteInfo[0]
            ipAddr = remoteInfo[1]
            cmd = remoteInfo[2]
            pingCmd = f'ping -c 3 {ipAddr}'

            log.debug(f'Current constructed ping command is: \n\t{pingCmd}')
            log.info(f'Checking if {machineName} is alive')
            lcd.print(f'Checking', f'{machineName}')

            ping = subprocess.run(pingCmd, shell=True, capture_output=True, text = True) #Run a ping command for the current machine
            pingRtrnCode = ping.returncode #Capture return code
            pingOutput = ping.stdout #Capture output
            pingErrOutput = ping.stderr #Capture errors            

            log.info(f'Ping output for {machineName} is: \n{pingOutput}\n{pingErrOutput}')
            log.info(f'Ping return code is: {pingRtrnCode}')
            time.sleep(2)

            if(pingRtrnCode == 0): #If ping was succesful
                lcd.print(f'{machineName}', 'is Alive')
                time.sleep(2)
                log.warning(f'{machineName} is alive')
            else: #If ping was not succesful
                log.warning(f'{machineName} was not determind to be alive, assumed dead')
                lcd.print(f'{machineName}', f'is Dead')
                time.sleep(2)
                lcd.print(f'Attempting', 'Power On')

                pwrCmd = subprocess.run(cmd, shell=True, capture_output=True, text = True) #Run power on command for current machine
                pwrCmdRtrnCode = pwrCmd.returncode #Capture return code
                pwrCmdOutput = pwrCmd.stdout #Capture output
                pwrCmdErrOutput = pwrCmd.stderr #Capture errors

                log.info(f'Power on command output for {machineName} is: \n{pwrCmdOutput}\n{pwrCmdErrOutput}')
                log.info(f'Power on command return code is: {pwrCmdRtrnCode}')
                time.sleep(2)

                if(pwrCmdRtrnCode != 0): #If ssh command was not succesful
                    lcd.print(f'Error Please',f'Check Logs')
                    log.error(f'Error powering on {machineName}, command return code is: {pwrCmdRtrnCode}')
                    log.error(f'Power on command output: \n{pwrCmdOutput}\n{pwrCmdErrOutput}')
                    time.sleep(3)
                time.sleep(2)
        lcd.clear()
    
    def mainMenu(self):
        """
        Main Menu for HLPC Program allows user to select operation to run via LCD screen and keypad
        """
        keypad = self.keypad
        lcd = self.lcd
        log = self.log
        auth = self.auth #Will return true or false depending on if user could be verified

        mainMenuPages = [['HLPC', 'Shutdown: A'],['HLPC','Power On: B'],['Display HLPC', 'IP Address: C'],['Exit HLPC','Program: D']] #Text to show depending on current main menu page, the second index determins top [0] or bottom [1] of LCD
        crntMenuPage = 0
        pressedKey = ''
        pageIncrementKey = '#' #Key on keypad to be used to change mainMenuPage

        endPrgm = False #If this is set to True the main menu loop will end and the program will exit

        lcd.print(mainMenuPages[crntMenuPage][0],mainMenuPages[crntMenuPage][1]) #Set initial menu page on LCD
        while(True): #Main loop
            pressedKey = keypad.press() #Get a keypress from user
            log.debug(f'User pressed {pressedKey} on keypad')

            if(pressedKey == pageIncrementKey): #If user presses the increment page button
                crntMenuPage += 1 #Increment current page
                log.debug(f'User incremented main menu page via keypad')
                if(crntMenuPage >= len(mainMenuPages)): #If at last page in menu go to the first page
                    crntMenuPage = 0
                    log.debug(f'Current page is {crntMenuPage}')
            
            else: #Check if user selected an option from menu
                if (pressedKey == 'A'): #If user presses A
                    lcd.print('HLPC Shutdown', 'Loading...')
                    log.info(f'User has selected HLPC Shutdown')
                    time.sleep(2)
                    if(auth.verified()): #If user can be verified then proceed with shutdown
                        self.remoteShutdown()
                elif (pressedKey == 'B'):
                    lcd.print('HLPC Power On', 'Loading...')
                    log.info(f'User has selected HLPC Power On')
                    time.sleep(2)
                    if(auth.verified()):
                        self.remotePowerOn()
                elif (pressedKey == 'C'):
                    self.printIpAddr()
                elif (pressedKey == 'D'):
                    if(auth.verified()):
                        if(self.exitPrgm()):
                            endPrgm = True
                            log.warning('User has ended program via keypad')
                else:
                    lcd.clear()
                    lcd.print('Unkown Input',' ')
                    time.sleep(1)
            
            lcd.clear()
            lcd.print(mainMenuPages[crntMenuPage][0],mainMenuPages[crntMenuPage][1]) #Update main menu

            if (endPrgm == True): #Used to exit program and prevent an infinate loop  
                log.debug('endPrgm has been set to True, program will end')
                lcd.print('Program Ended','Via Keypad')#This message will remain on keypad until program is restarted or power is pulled from device
                break

if(__name__ == "__main__"):
    try:
        mainHLPC = HLPC()
        if(len(sys.argv) > 1): #Check if user specified arguments
            arg = str(sys.argv[1]) #Get the argument that user specified
            validArgs = ['shutdown','powerOn','help']
            if(arg == validArgs[0]):
                mainHLPC.remoteShutdown()
            elif(arg == validArgs[1]):
                mainHLPC.remotePowerOn()
            elif(arg == validArgs[2]):
                helpStr = ''
                for validArg in validArgs:
                    helpStr += f'{validArg} '
                print(helpStr)
            else:
                print('Unknown Argument')
                print(f'Valid Arguments: {validArgs}')
                print('Exiting program')
        else:
            mainHLPC.mainMenu()
    except KeyboardInterrupt:
        print('User exited program via Keyboard Interupt')