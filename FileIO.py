'''appends  str to file with filename. Creates if file not exist,
doesnt write if file containts same strr.
returns 1 if write, returns 0 if there is no file write.'''
def dosyayaYaz(filename,strr):
    try:
        file=open(filename,'r', encoding="utf8",errors='ignore')
    except FileNotFoundError:
        file = open(filename, 'w', encoding="utf8",errors='ignore')
        file.close()
    file=open(filename,'r+')
    wholeFile= file.read()
    if wholeFile.find(strr)==-1:
        file.close()
        file=open(filename,'a', encoding="utf8",errors='ignore')
        file.write(strr)
        file.close()
        return 1
    file.close()
    return 0
  
def saveResponse(filename,str):
    f=open(filename,'w')
    f.write(str)
    f.close()