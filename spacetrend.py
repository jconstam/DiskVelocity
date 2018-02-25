import argparse
from lib import storage

def printIfVerbose( verbose, line ):
    if( verbose ):
        print line

parser = argparse.ArgumentParser( )
parser.add_argument( 'dataFile', help = 'JSON file containing past data' )
parser.add_argument( '-f', '--force', required = False, action = 'store_true' )
parser.add_argument( '-v', '--verbose', required = False, action = 'store_true' )
args = parser.parse_args( )

printIfVerbose( args.verbose, '01 - Reading past data from file {}.'.format( args.dataFile ) )
timeline = storage.DiskHistory.getTimelineFromFile( args.dataFile )

printIfVerbose( args.verbose, '\tRead {} past measurements.'.format( len( timeline.records ) ) )
if args.verbose:
    for record in timeline.records:
        record.printInfo( indent = 2 )

printIfVerbose( args.verbose, '02 - Reading current data.' )
currInfo = storage.DiskInfo( )
currInfo.getCurrentInfo( )
if args.verbose:
    print currInfo.printInfo( indent = 1 )

printIfVerbose( args.verbose, '03 - Adding current data to historical data.' )
timeline.addRecord( currInfo )

printIfVerbose( args.verbose, '04 - Calculating date when disk will be full.' )
timeline.printFullDate( args.force )

printIfVerbose( args.verbose, '05 - Writing data to file {}.'.format( args.dataFile ) )
storage.DiskHistory.writeTimelineToFile( args.dataFile, timeline )
printIfVerbose( args.verbose, '06 - Done.' )