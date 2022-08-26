import scraper

def modLink(userinput):
    userinput = userinput[5:]
    return userinput

def saveLink(userinput):
    sendScraper = scraper.saveInFile(userinput)
    return sendScraper

def createSubStringLinkAmazon(str):
    str = str.split('/')[3]
    return str

def leggiFileCSV():
    with open('file.csv', 'r') as f:
        key = 1
        prod = {}
        for line in f:
            value = createSubStringLinkAmazon(line)
            prod[key] = value
            key += 1
    return prod        

def trovaLink(inputLink):
    with open('file.csv', 'r') as f:
        for line in f:
            if line != None and inputLink in line:
                return line 
    
def nomeProdotto(productTitle):
    productTitle = productTitle[:13]
    return productTitle

def duplicateProd(link):
    with open('file.csv', 'r') as f:
        if f.read().find(link) != -1:
            return "Product already in the list"
        else:
            return saveLink(link)
        
    return 'Nessuna operazione svolta!'