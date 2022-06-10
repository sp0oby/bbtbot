from web3 import Web3 
from telebot import TeleBot, types
import config, helper, json
from web3._utils.events import EventLogErrorFlags
from apscheduler.schedulers.background import BackgroundScheduler


bot = TeleBot(config.api_token)
web3 = Web3(Web3.HTTPProvider(config.rpc_url))
schd = BackgroundScheduler(daemon=True)
class myFilter: rpcFilter = web3.eth.filter({
#    'address': config.contract_address,
    'topics': [config.sig_to_track],
})

def handleTX(x, ca):
    allTX = helper.getAllTX()
    if x.lower() in allTX: return print('Tx already exists')
    logsR = web3.eth.getTransactionReceipt(x)
    with open('./token.json', 'r') as file: abiData = json.load(file)
   
    txInfo = web3.eth.getTransaction(x)
    print(getattr(txInfo, "from"), getattr(txInfo, "to"))


    contract = web3.eth.contract(address=web3.toChecksumAddress(ca), abi=abiData)

    logs = contract.events.SettledRPSLSvsChainlink().processReceipt(logsR, errors=EventLogErrorFlags.Discard)
    if len(logs) == 0: return print('No Valid Event Found')

    validData = logs[0].args
    print(validData)
    wagererAddress = validData.wagerer
    amountWagerer = validData.amountWagered / 10 ** 18
    hand = validData.hand
    chainLink = validData.chainlinkPlayed
    resultMatch = validData.result

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Transaction Hash", url="https://etherscan.io/tx/"+x)
    markup.add(btn)

    player_stats = contract.functions.playerStats(wagererAddress).call()
    print(logsR)
    wins = player_stats[0]
    loses = player_stats[2]
    draws = player_stats[4]

    amountWin = 0 if player_stats[1] == 0 else player_stats[1] / 10 ** 18
    amountLoss = 0 if player_stats[3] == 0 else player_stats[3] / 10 ** 18


    
    text_to_send = f"""<b>Round</b> : <b><a href='{config.scan_url + wagererAddress}'>{wagererAddress[0:5] + '...'}</a></b> wagered <b>{helper.roundToNearestZero(amountWagerer)} $BBT</b> and <b>{helper.getResult(resultMatch)}</b> with <b>{helper.getHandWithNumber(hand)}!</b>

<b>Player Stats:</b>
🐸Wins:{wins}  🛑Loses: {loses} ✏️Draws: {draws} -
BBT WON/LOSS: ({int(amountWin)}, {int(amountLoss)})
"""

    video_link = open("./YouWon.mp4", "rb") if helper.getResult(resultMatch) == 'won' else open("./YouLost.mp4", "rb")



    bot.send_video(
        video=video_link,
        caption=text_to_send,
        chat_id="-1001763761758",
        reply_markup=markup,
        parse_mode= "HTML"
    )

    

    # bot.send_photo(
    #     chat_id="-1001763761758",
    #     caption=text_to_send,
    #     parse_mode="HTML",
    #     reply_markup=markup,
    #     # disable_web_page_preview=True,
    #     photo=""" # )
    helper.insertTX(x.lower())


def checkTokenBuys():
    try:
       allEntries = myFilter.rpcFilter.get_new_entries()
    except:
       myFilter.rpcFilter = web3.eth.filter({ 'topics': [config.sig_to_track] })
       return print("filter broken")
    allEntries = helper.removeDuplicateEntries(allEntries)
    print(allEntries)

    for x in allEntries:
        handleTX(x.transactionHash.hex(), "0x0c4A49567Cf002A99941cb19C973E794c04B8c30") #x.address


schd.add_job(checkTokenBuys, 'interval', seconds=5)
schd.start()
while True: pass

# result = myFilter.rpcFilter.get_all_entries()
# result = helper.removeDuplicateEntries(result)
# print(result)
