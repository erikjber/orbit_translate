# orbit_translate
Scrape TLE orbit parameters from the internet and translate them to Celestia SSC format.

It can generate SSC data for any satellite found in the CelesTrak database:
http://celestrak.com/NORAD/elements/

The program is implemented in a single Python 3 file with no dependencies.

## Installation
1. Install Python 3. 
2. Download the file translate_orbit.py and put it anywhere.

## Usage
To get program parameters and options, run it with the -h switch:  
`python translate_orbit.py -h`

To generate the SSC output for a sattelite you need to know two pieces of information:
a) the category
b) the name

To get a list of categories, run the program without parameters:  
`python translate_orbit.py`

To get a list of all satellites in a category, use the -c parameter:  
`python translate_orbit.py -c stations`

Once you have found the name, create the SSC output using the -s parameter along with the -c parameter:  
`python translate_orbit.py -c stations -s "ISS (ZARYA)"`

Both the name of the category and the name of the satellite are case sensitive.

## Optional parameters
You can choose the mesh model to with the -m argument:   
`python translate_orbit.py -c stations -s "ISS (ZARYA)" -m iss.cmod `

You can define the size of the satellite, in kilometres, using the -r parameter:  
`python translate_orbit.py -c stations -s "ISS (ZARYA)" -m iss.cmod -r 0.04`

Finally you can specify a custom orientation using the -o argument. 
The argument is an array of four numbers. The first is the rotation, in degrees. 
The last three arguments are the components of the rotation axis.  
`python translate_orbit.py -c stations -s "ISS (ZARYA)" -m iss.cmod -r 0.04 -o "[ 90 0 0 1 ]"`
