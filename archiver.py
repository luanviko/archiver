# A program to archive my daily notes, 
# by saving the nano entry on a tex file.

# A config file will be created or read every time it starts up.
# The config file contains info such as:
# path to save files. path to backup.
# author

import sys, os
import subprocess
from subprocess import call,PIPE,run
import datetime
import glob

def openConfig(configfile):
    ## Opens the configu file.
    details = []
    configOpener = open(configfile,'r')
    configRaw = configOpener.readlines()
    for lines in configRaw:
        lineSplit = lines.split(': ')
        details.append(lineSplit[-1])
    return details

def generateConfig(configfile):
    ## Generate a config file.

    configwriter = open("./{0}".format(configfile), "w")
    configwriter.write("Directory to store entries:\n")
    configwriter.write("Directory to tex file:\n")
    configwriter.write("Author's name:\n")
    configwriter.write("Title:\n")
    configwriter.write("Prefered editor: nano\n")
    configwriter.close()
    call(["nano",configfile])

def tryConfig(configfile):
    ## Looks for a config file
    #  in the directory.
    command = ['ls','-l']
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

    if result.stdout.find(configfile) != -1:
        details = openConfig(configfile)
        
    else:
        details = []
        print("config file not found.")
        yn = input("Do you want to generate it? (y/n)")
        if yn == 'y':
            generateConfig(configfile)
        if yn == 'n':
            details.append(0)
        else:
            input("Please answer y or n.")
        
    return details

def generateTex(save_directory,tex_directory, year_number, AUTHOR, TITLE):
    ## Generates a tex file from the sfiles 
    ## in the save_directory. 
    ## The tex will be store at tex_directory.

    # Open the main tex file to be compiled
    texfile = tex_directory+"/{0}_{1}.tex".format(AUTHOR.replace(" ","_"),year_number)
    tex_writer = open(texfile, "w")

    # Copying the preamble as defined by the template
    tex_preamble = open("./preamble.tex","r")
    preamble = tex_preamble.readlines()
    for line in preamble:
        tex_writer.write(line)

    # Adding author and date information
    tex_writer.write("\n"+r"\author{"+"{0}".format(AUTHOR)+r"}"+"\n")
    tex_writer.write(r"\date{"+"{0}".format(year_number)+r"}"+"\n")
    tex_writer.write(r"\title{"+"{0}".format(TITLE)+r"}"+"\n")

    tex_writer.write(r"""\begin{document}
\maketitle
\pagestyle{plain}
""")

    # Opening all entries
    os.chdir(save_directory)
    files_list = sorted(glob.glob("*.tex"))
    for file_entry in files_list:
        tex_writer.write(r"\input{"+"{0}/{1}".format(save_directory,file_entry)+r"}"+"\n")

    # Closing the document
    tex_writer.write(r"\end{document}")

    # Closing the file
    tex_writer.close()

    yn = input(".tex file generated. Do you want to compile it with pdflatex? (y/n)")
    if yn == 'y':
        os.chdir(tex_directory)
        p=subprocess.Popen("pdflatex {0}".format(texfile), shell=True )
        p.wait()
    else:
        print("See you next time!")

def writeEntry(configfile):

    # Get date and time:
    today = datetime.datetime.now()

    # Separate time into its parts
    year_number  = today.strftime("%Y")
    month_number = today.strftime("%m")
    month_name   = today.strftime("%B")
    day_number   = today.strftime("%d")
    hour_24      = today.strftime("%H")
    minute       = today.strftime("%M")

    # Open config file
    details = tryConfig(configfile)
    #print(details)

    if details[0] == 0:
        print("Aborting generating config file.")
        
    else:
        
        ### Organize the details from config file

        # Path to save entries
        save_directory = details[0].replace("\n","")
        
        # Path to store tex and pdf file
        tex_directory =details[1].replace("\n","")
        
        # Author information
        AUTHOR = details[2].replace("\n","")

        # Title
        TITLE = details[3].replace("\n","")
        
        # Prefered editor
        EDITOR = details[4].replace("\n","")

        ### Proceed to creating entry

        # Entry's name and location
        file_name = "{0}-{1}-{2}_{3}:{4}.tex".format(year_number, month_number, day_number, hour_24, minute)
        final_path = "{0}/{1}".format(save_directory,file_name)
        
        # Write header to file:
        file_writer = open(final_path,"w")
        file_writer.write("\section*{"+"{0} {1}, {2}:{3}".format(month_name,day_number,hour_24,minute)+"}\n")
        file_writer.close()

        # Invoke editor of choice
        call([EDITOR,"{0}".format(final_path)])

        # Try to read the file, 
        # or pretend there was no entry. 
        try:
            tempreader = open(final_path,"r")
            tempcontents = tempreader.readlines()
        
            # If empty, delete it. 
            # If not empty, save it.
            # Then ask to create tex file.
            if len(tempcontents) == 1:
                print("Files with only the header present are not stored. Goodbye!")
                p = subprocess.Popen("rm {0}".format(final_path), shell=True )
                p.wait()
            else:     
                print("Entry's location: {0}".format(final_path) )
                yn = input("Do you want to generate and compile a tex file with all the entries? (y/n)")
                
                if yn == 'y':
                    generateTex(save_directory,tex_directory, year_number, AUTHOR, TITLE)
                    
                else:
                    print("Then it is all done. See you next time.")

        except OSError as e:
            print("No entry to be stored. Goodbye!")

configfile="archiver.config"
#ret = tryConfig(configfile)
writeEntry(configfile)


