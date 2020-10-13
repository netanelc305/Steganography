from PIL import Image
from Crypto.Cipher import AES
from hashlib import md5
import argparse
import textwrap

##### Please install the following modules ####
# pip install pillow
# pip install pycrypto


def dataToBinaryStream(data):

    # This function will convert each letter from a given string to 8bit Ascii representation
    # given the word "Dog" as input the output will be : ["01000100","01101111","01100111"]

    binarySteam=[]
    for letter in data:
        binarySteam.append(format(ord(letter),'08b'))

    return binarySteam
def encrypt_data(key,data):

    # If no password provided no need to encrypt the data
    if key=="":
        return data
    else:
        aes_object = AES.new(key,AES.MODE_ECB)
        data = data+"@" # Add flag where padding start
        message_len=len(data)

        # If message is not x16 need to add padding
        if(message_len%16!=0):
            data+=(16-len(data)%16)*"*"

        return aes_object.encrypt(data)
def decrypt_data(key,data):

    # If no password provided no need to decrypt the data
    if key=="":
        return data
    else:
        aes_object=AES.new(key,AES.MODE_ECB)
        decrypted_message= str(aes_object.decrypt(data))    # Decrypt the data with given password(key)
        counter=1

        # Count the number of chars until we meet @ which is the end of padding flag
        for char in decrypted_message[::-1]:
            if(char=="@"):
                break
            else:
                counter+=1
        # Remove all the padding and return the original message
        return decrypted_message[0:-counter]
def modifyPixels(pix,data):
    datalist = dataToBinaryStream(data)
    imageData=iter(pix)

    # Each pixel is a tuple of 3 values (R,G,B) , each Ascii symbol represented with 8bits.
    # in order to encode one ascii char we need 3 pixels 3*(R,G,B) = 9 , the 9th bit will use as flag if the message is over.

    # DataList is an array where each element is a letter that converted to her binary ascii representation
    # for example the word "Dog" ["01000100","01101111","01100111"]

    # The data encoded with the following logic , for each bit in DataList if 1 then will be represented as odd if 0 will be represented as even.
    # assuming we want to encode 001 in one pixel(125,34,220):
    # pixel[0]=125 is even ? no we need to add 1.
    # pixel[1]=34 is even ? yes.
    # pixel[2]=220 is odd  ? if not we will add 1.
    # new pixel values are (126,34,221)

    for i in range(len(datalist)):

        # Each time we handle with 3 pixels , as explained above with 3 pixels we can encode 9bits - 8 for letter +1 flag.
        pix = [value for value in imageData.next()[:3] + imageData.next()[:3] + imageData.next()[:3]]

        for j in range(0,8):
            # If we need to encode the value 0 and pixel value is odd , add 1 to make it even.
            if (datalist[i][j]=="0") and (pix[j]% 2 != 0):
                if (pix[j]% 2 != 0):
                    pix[j] -= 1
            # If we need to encode the value 1 and pixel value is odd , add 1 to make it odd.
            elif (datalist[i][j] == "1") and (pix[j] % 2 == 0):
                pix[j] -= 1

        # If we on the last bit , set the end of message bit to odd.
        if (i == len(datalist)  - 1):
            if (pix[-1] % 2 == 0):
                pix[-1] -= 1

        # If we still have bits to encode , set flag bit to even.
        else:
            if (pix[-1] % 2 != 0):
                pix[-1] -= 1

        # Pack the new values as (R,G,B) and return

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]
def encode_enc(newImage,data):
    w = newImage.size[0]
    (x,y) = (0,0)

    for pixel in modifyPixels(newImage.getdata(), data):
        # Put modified pixels in the new image
        newImage.putpixel((x, y), pixel)

        if (x == w - 1):
            x = 0
            y += 1
        else:
            x += 1
def extension_check(file_type):
    # Use for interactive mode and make sure user will input the right extension
    while(True):
        file_name=raw_input("[+] Enter {} filename (with extension): ".format(file_type))
        extension=file_name.split(".")[-1].upper()
        if(extension == "PNG"):
            return file_name
        else:
            print "[+] Invalid extension - please provide png file"

def interactive():

    # Interactive mode deal with all the input require from the user

    while(True):
        mode=raw_input("1: Hiding data\n"
                       "2: Extract data\n"
                       "0: Exit\n")
        if(mode=="0"):
            print "[+] Thank you for using bye!"
            exit(0)
        elif(mode=="1"):
            print "[+] Hiding mode selected:"
            input_file = extension_check("Input file")

            password =raw_input("[+] Enter password (Optional): ")
            data = raw_input("[+] Enter the data you wish to hide :\n")
            output_file=extension_check("Output file")

            hide_in_image(data,password,input_file,output_file)
            print "[+] Data was embbedd sucessfully"
            print "\n"

        elif(mode=="2"):
            print "[+] Extraction mode selected:"
            print "[+] Input file:"
            input_file = extension_check("Input file")

            password = raw_input("[+] Enter the password you used to encrypt: ")
            print "[+] Data was extracted sucessfully:"
            print extract_from_image(password,input_file)

            print "\n"
        else:
            print "[+] Inavlid mode please try again"


def extract_from_image(password,input_file):
    try:
        image = Image.open(input_file)

        data=""
        imageData=iter(image.getdata())


        while(True):
            # Read 3 pixels
            pixels=[value for value in imageData.next()[:3]+imageData.next()[:3]+imageData.next()[:3]]

            binaryString=""
            # Decode first 8bit and convert to char
            for i in pixels[:8]:
                if(i%2==0):
                    binaryString+="0"
                else:
                    binaryString+="1"
            data+=chr(int(binaryString,2))
            # if end of message bit is on return the data
            # if data 16%==0 message probably encrypted so decrypt before you return
            if (pixels[-1] % 2 != 0):
                if (len(data)%16==0):
                    return decrypt_data(md5(password).hexdigest(),data)
                else:
                    return data
    except IOError:
        print "[+] No such file or directory: {}".format(input_file)

def hide_in_image(data,password,input_file,output_file):

    try:
        image=Image.open(input_file)
        newImage=image.copy()
        data =encrypt_data(md5(password).hexdigest(),data)

        if(newImage.size[0]*newImage.size[1] < len(data)):
            print "[+] Please provid bigger image"
            return

        encode_enc(newImage,data)

        newImage.save(output_file,"PNG")
        print "[+] new image: {}".format(output_file)

    except IOError :
        print "[+] No such file or directory: {}".format(input_file)




def main():

    parser = argparse.ArgumentParser(prog="Steganography project",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''
                                     This program use to hide and extract data from PNG images.
                                     You can use interactive mode or parse arguments.
                                     data can be encrypted with password before hide in an image, default password is blank.
                                     in order to successfully extract data from image the password used to hide need to be provided.
                                     '''),
                                     epilog=textwrap.dedent('''
                                     Exmples:
                                     python Stage.py --hide -i myInputFile.png -p myPassword -o myOutputFile.png -d "This is data to hide"
                                     python Stage.py --extract -i myInputFile.png -p myPassword
                                     python Stage.py --interactive
                                     '''))



    # Mode
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--extract", action="store_true",help="Extract data from image")
    modes.add_argument("--hide", action="store_true",help="Hide data inside image")
    modes.add_argument("--interactive", action="store_true",help="Interactive mode")


    # Arguments
    parser.add_argument("-o",type=str,metavar="",help="output png file")
    parser.add_argument("-i",type=str,metavar="",help="input png file")
    parser.add_argument("-p",type=str,metavar="",default="",help="password")
    parser.add_argument("-d",type=str,metavar="",help="Data to hide")
    args = parser.parse_args()


    if args.interactive:
        interactive()

    elif args.extract:
        if(args.i!=None):
            ext = str(args.i).split(".")[-1].upper()
            if(ext!="PNG"):
                print "[+] Invalid extension - please provide png file"
            else:
                data= extract_from_image(args.p,args.i)
                print "[+] Extracted data : {}".format(data)
        else:
            print "[+] One of the arguments are missing"
    elif args.hide:
        if(args.i!=None and args.o!=None and args.d!=None):
            ext = str(args.i).split(".")[-1].upper()
            ext2 = str(args.o).split(".")[-1].upper()
            if(ext!=ext2!="PNG"):
                print "[+] Invalid extension - please provide png file"
            else:
                hide_in_image(args.d,args.p,args.i,args.o)
        else:
            print "[+] One of the arguments are missing"
    else:
        parser.print_help()



if __name__ == '__main__':
    main()
