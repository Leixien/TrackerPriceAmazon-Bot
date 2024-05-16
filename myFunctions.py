import scraper

def modLink(userinput):
    userinput = userinput[5:]
    return userinput

def saveLink(userinput):
    sendScraper = scraper.saveInFile(userinput)
    return sendScraper

def createSubStringLinkAmazon(str):
    segments = str.strip().rpartition('/')
    if len(segments) == 3: 
        return segments[-1]
    else:
        return "" 

def leggiFileCSV():
    try:
        with open('file.csv', 'r') as f:
            key = 1
            prod = {}
            for line in f:
                print(f"Lettura riga: {line}")
                value = createSubStringLinkAmazon(line)
                print(f"Value : {value}")
                if value:
                    prod[key] = value
                    key += 1
                    value = ''
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        prod = {}
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