import csv
import logging
from ConfigReader import ConfigReader

class CSVreader:
    """Read CSV files and parse into a list of lists"""

    def __init__(self, file):
        
        self.config = ConfigReader('config.ini')
        
        self.file = file
        self.header = False

        #Create and configure logger

        LOG_Format = "%(levelname)s %(asctime)s - %(message)s"
        logging.basicConfig(filename = self.config.getLogConfig('logFile'),
                            level = self.config.getLogConfig('logLevel'),
                            format = LOG_Format)

        self.logger = logging.getLogger()
        self.logger.info(f'CSV reader has been setup with specified file: {file}')

    def hasHeader(self):
        """Change self.header to True if called. 
        This will tell parseCSV that the specified CSV file has a header."""
        
        #Setup logger in this method

        log = self.logger 

        log.debug(f'hasHeader method has been run for specified file: {self.file}')
        self.header = True

    def parseCSV(self):
        """Return CSV file as a list of lists"""
       
        #Setup logger in this method
        
        log = self.logger 
        parsedCSV = []
        
        try:
            
            #Open the csv file

            file = open(self.file) 
            log.debug(f'Reading specified CSV file')
            
            #Read the csv file

            csvFile = csv.reader(file, delimiter=',') 
        
        #If file could not be opened
        
        except FileNotFoundError as e: 
            
            print(f'Could not open specified file \'{self.file}\'')
            log.error(f'Could not open specified CSV file {self.file}')
            log.error(f'Exception raised: \n\t{e}')
            
            #Retuen an empty list
            
            return [] 

        else:
            
            log.info(f'Parsing CSV file {self.file}')
            
            parsedCSV = []
            rowNumber = 0
            
            #Add each row in csvFile to a list of rows

            for row in csvFile:  
                
                log.debug(f'Current row is {row}')
                
                #Skip first row if csv has header

                if self.header == True and rowNumber == 0: 
                    log.debug(f'Skipped row because it was a header')
                    pass
                else:
                    parsedCSV.append(row) 
                
                rowNumber += 1
            
            log.debug(f'Closed {self.file}')
            
            #Close the opened csv file
            
            file.close()

            log.debug(f'Removing whitspace from parsedCSV')
            log.info(f'Parsed CSV file contains entries: ')
            
            #Loop through each item in parsedCSV and remove whitespace
            
            for row in parsedCSV: 
                for x in range(len(row)):
                    row[x] = row[x].lstrip()
                    row[x] = row[x].rstrip()
                log.info(f'{row}')
            return parsedCSV 
            