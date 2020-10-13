## Steganography

# Description
Python2.7 script for hide and extract messages in PNG images.

# Usage
Download the files\clone the repository  and execute - pip install -r requirements.txt.


```usage: Steganography project [-h] [--extract | --hide | --interactive] [-o]
                             [-i] [-p] [-d]

This program use to hide and extract data from PNG images.
You can use interactive mode or parse arguments.
data can be encrypted with password before hide in an image, default password is blank.
in order to successfully extract data from image the password used to hide need to be provided.

optional arguments:
  -h, --help     show this help message and exit
  --extract      Extract data from image
  --hide         Hide data inside image
  --interactive  Interactive mode
  -o             output png file
  -i             input png file
  -p             password
  -d             Data to hide

Exmples:
python Stage.py --hide -i myInputFile.png -p myPassword -o myOutputFile.png -d "This is data to hide"
python Stage.py --extract -i myInputFile.png -p myPassword
python Stage.py --interactive
```
