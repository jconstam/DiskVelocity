import json
import time
import os.path
import datetime
import subprocess

from datetime import date

class DiskInfo:
    def __init__( self, timestamp = 0, size = 0, used = 0 ):
        self.timestamp = timestamp
        self.size = size
        self.used = used

    def getCurrentInfo( self ):
        self.size = 0
        self.used = 0

        df = subprocess.Popen( [ "df" ], stdout = subprocess.PIPE )

        output = df.communicate( )[ 0 ]
        self.timestamp = datetime.datetime.now( )

        for descript in output.splitlines( )[ 1: ]:
            name, size, used, available, percent, mountpoint = descript.split( )
            self.size += int( size )
            self.used += int( used )
    
    def posixTimestamp( self ):
        return time.mktime( self.timestamp.timetuple( ) )

    def percentUsed( self ):
        return float( self.used ) / float( self.size ) * 100.0

    def printInfo( self, indent = 0 ):
        print "{}TIMESTAMP: {} ({}) - SIZE: {} - USED: {} ({:0.2f}%)".format( '\t'*indent, self.timestamp, self.posixTimestamp( ), self.size, self.used, self.percentUsed( ) )

class DiskTimeline:
    MIN_RECORDS_FOR_ESTIMATE = 5
    MAX_YEARS_FOR_ESTIMATE = 5

    def __init__( self ):
        self.records = []

    def addRecord( self, info ):
        self.records.append( info )
    
    def printAll( self ):
        for record in self.records:
            record.printInfo( )

    def printFullDate( self, force ):
        count = len( self.records )
        if not force and count < self.MIN_RECORDS_FOR_ESTIMATE:
            print 'Not enough data to make an estimate.'
            return

        sumY = float( 0 )
        sumX = float( 0 )
        sumXsq = float( 0 )
        sumXY = float( 0 )

        for record in self.records:
            sumY = sumY + record.percentUsed( )
            sumX = sumX + record.posixTimestamp( )
            sumXsq = sumXsq + ( record.posixTimestamp( ) ** 2 )
            sumXY = sumXY + ( record.percentUsed( ) * record.posixTimestamp( ) )

        slope = ( ( count * sumXY ) - ( sumX * sumY ) ) / ( ( count * sumXsq ) - ( sumX ** 2 ) )
        intercept = ( ( sumY * sumXsq ) - ( sumX * sumXY ) ) / ( ( count * sumXsq ) - ( sumX ** 2 ) )

        fullDate = date.fromtimestamp( ( 100 - intercept ) / slope )
        if slope < 0:
            print 'Disk is not filling up.'
        elif fullDate.year > datetime.datetime.now( ).year + self.MAX_YEARS_FOR_ESTIMATE:
            print 'Disk is filling too slowly to track.'
        else:
            print 'Disk will be full on {:%b %d %Y}'.format( fullDate )
        
class DiskHistory:
    MAX_NUM_RECORDS = 20

    @staticmethod
    def getTimelineFromFile( filePath ):
        if not os.path.exists( filePath ):
            return DiskTimeline( )

        timeline = DiskTimeline( )

        data = json.load( open( filePath ) )
        for record in data[ "records" ]:
            timestamp = datetime.datetime.strptime( record[ "timestamp" ], "%Y-%m-%dT%H:%M:%S.%f")
            size = record[ "size" ]
            used = record[ "used" ]
            
            timeline.addRecord( DiskInfo( timestamp, size, used ) )
        
        return timeline

    @staticmethod
    def writeTimelineToFile( filePath, timeline ):
        data = {}
        data[ "records" ] = []
        for record in timeline.records[ -DiskHistory.MAX_NUM_RECORDS : ]:
            newRecord = {}
            newRecord[ "timestamp" ] = record.timestamp.isoformat( )
            newRecord[ "size" ] = record.size
            newRecord[ "used" ] = record.used

            data[ "records" ].append( newRecord )

        with open( filePath, 'w' ) as outfile:
            json.dump( data, outfile, indent = 4 )

