from configparser import ConfigParser
import ast

class ConfigReader:

    def __init__(self, configFile):

        #Initialize config parser

        self.config = ConfigParser() 
        
        #Read specified config file
        
        self.config.read(configFile) 
    
    def getAuthConfig(self, valueKey):
       
        #Get value from config file
       
        value = self.config.get('Authentication', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 

        #Return value
                
        return value 

    def getShutdownConfig(self, valueKey):
        
        #Get value from config file

        value = self.config.get('Shutdown', valueKey) 
        
        #Parse value into correct format
        
        value = ast.literal_eval(value) 
        
        #Return value

        return value 
    
    def getPowerOnConfig(self, valueKey):
        
        #Get value from config file

        value = self.config.get('Power On', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 
        
        #Return value

        return value 

    def getKeypadConfig(self, valueKey):
       
        #Get value from config file

        value = self.config.get('Keypad', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 
        
        #Return value

        return value 

    def getLCDdriverConfig(self, valueKey):
        
        #Get value from config file

        value = self.config.get('LCD Driver', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 
        
        #Return value

        return value 

    def getLogConfig(self, valueKey):
        
        #Get value from config file

        value = self.config.get('Log', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 
        
        #Return value

        return value 

    def getPingTestConfig(self, valueKey):
        
        #Get value from config file

        value = self.config.get('Ping Test', valueKey) 
        
        #Parse value into correct format

        value = ast.literal_eval(value) 
        
        #Return value
        
        return value 