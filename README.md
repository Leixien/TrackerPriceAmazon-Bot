# <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot'>TrackerPriceAmazon-Bot</a>
A simple Amazon price tracking bot written in Python by <a href = 'https://github.com/Leixien'>Leixien</a>

# Description of the Code

<b><i>Brief description of the code</i><b></br>
  
This Telegram Bot checks the price of a given Amazon Product. 
  - You can save the product and check the price when you want with a single tap. 
  - You can check the prices of different amazon store states by sending the link of the product itself
  - Join my <a href = 'https://discord.gg/kTg5fhVERQv' >discord</a> :)
  - Find a new song (try it <3 )
                             
The modules I used are:

  - <a href = 'https://www.crummy.com/software/BeautifulSoup/bs4/doc/' >BeautifulSoup (BS4)</a> - to scrap Amazon website
  - <a href = 'https://python-telegram-bot.org/'>Telegram API</a> - for Bot API

# Bot Code
I created 3 files to make the code <a href = 'https://www.martinfowler.com/bliki/CodeAsDocumentation.html#:~:text=I%20think%20part,began%20to%20program.'>clear</a> and <a href = 'https://www.martinfowler.com/bliki/CodeAsDocumentation.html#:~:text=I%20think%20part,began%20to%20program.'>readable</a>!

In the files You will find:
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/main.py'> main.py</a> - Main code whit Telegram API
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/myFunctions.py'>myFunctions.py</a> - Functions implements for manipulate the data and 
  - <a href = 'https://github.com/Leixien/TrackerPriceAmazon-Bot/blob/main/scraper.py'>scraper.py</a> - Scraper Amazon site with BeautifulSoup

# Next Upgrade 
I will try to add some new features every month to make this bot useful
Some features I will improve in the next month:
  - Schedulable Messages for price alert
  - A graphic with the price of the product
  - Inline mode for SuperGroups
