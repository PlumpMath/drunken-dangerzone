import time
import copy
from random import randrange, shuffle
t0 = time.time()

#Changable Parameters
Start_cash = 1500           #How much money each player starts with
Dice_sides = 6              #How many sides to the dice rolled
Print_moves = True          #If false, only prints end summary
Number_of_games = 1         #Total number of games to simulate
Randomize_first_turn = True #If false, Player 1 has first turn always
Max_houses = [5,5]          #Max number of houses [Player 1, Player2] will place on a given property
GoMoney = 200               #Amount recieved for passing Go
Tie_threshold = 500         #Max number of turns in a game before a tie is declared

#Takes player as input, rolls the dice and calls the appropriate function.
def Take_turn(p):
    r1 = randrange(Dice_sides)
    r2 = randrange(Dice_sides)
    if r1 == r2:
        if Players[p][2] == 2:
            if Print_moves: print "Doubles three times in a row? Go to Jail!"
            GtJ(p)
        Players[p][2] += 1
    if Print_moves:
        print "Player " + str(p+1) + " rolls a " + str(r1+1) + " and a " + str(r2+1) + ", landing on " + Board[(Players[p][1]+r1+r2+2)%40] + "."
    if (Players[p][1]+r1+r2+2)%40 <= Players[p][1]:
        Players[p][0]+=GoMoney
        if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
    Players[p][1] = (Players[p][1]+r1+r2+2)%40
    Square_effect(p)
        
        
#Sends the player to jail.
def GtJ(Player):
    return

#Processes the effect of landing on a given square.
def Square_effect(p):
    x = Players[p][1]
    if x in Properties:
        if Properties[x][0] == 0:
            if Players[p][0] >= Properties[x][1]:
                Players[p][0] -= Properties[x][1]
                Properties[x][0] = p+1
                if Print_moves: print "Property Purchased for $" + str(Properties[x][1]) + ". $" + str(Players[p][0]) + " remaining."
                if x not in [5,12,15,25,28,35]: Group_check(p)
                return
            else:
                if Print_moves: print "Purchase Declined - Not enough money!"
                return
        if Properties[x][0] != p+1 and x not in [5,12,15,25,28,35]:
            payout = Properties[x][2][Properties[x][3]]
            if G[Groups[x][1]] != 0 and G[Groups[x][1]] != p+1 and Properties[x][3] == 0:
                #Account for double rent when group owned
                payout += payout
            Players[p][0] -= payout
            if p == 0: Players[1][0] += payout
            else: Players[0][0] += payout
            if Print_moves:
                print
                print "Property owned by other player; $" + str(payout) + " Paid. $" + str(Players[p][0]) + " remaining."
                
    return

#Checks to see if a property group is owned by a single player.
def Group_check(p):
    x = Players[p][1]
    for i in Groups[x][0]:
        if Properties[i][0] != p+1:
            return
    G[Groups[x][1]] = p+1
    return

def Buy_houses(p):
    for i in range(8):
        if G[i] == p:
            while Players[p-1][0] >= (i/2)*50+50:
                for j in range(len(Gr[i])-1,-1,-1):
                    x = Gr[i][j]
                    if j == len(Gr[i])-1:
                        if Properties[x][3] == Properties[Gr[i][(j+1)%len(Gr[i])]][3]:
                            if Players[p-1][0] >= (i/2)*50+50 and Properties[x][3] !=Max_houses[p-1]:
                                Players[p-1][0] -= (i/2)*50+50
                                Properties[x][3] += 1
                                if Print_moves: print "House bought on " + Board[x] + ". Currently at " + str(Properties[x][3]) + " houses. $" + str(Players[p-1][0]) + " remaining."
                    else:
                        if Properties[x][3] < Properties[Gr[i][(j+1)%len(Gr[i])]][3]:
                            if Players[p-1][0] >= (i/2)*50+50 and Properties[x][3] !=Max_houses[p-1]:
                                Players[p-1][0] -= (i/2)*50+50
                                Properties[x][3] += 1
                                if Print_moves: print "House bought on " + Board[x] + ". Currently at " + str(Properties[x][3]) + " houses. $" + str(Players[p-1][0]) + " remaining."
                if Properties[Gr[i][0]][3] == Max_houses[p-1]: break
    
#Position Labels
Board = ['Go','Mediterranean Avenue','Community Chest','Baltic Avenue',
         'Income Tax', 'Reading Railroad','Oriental Avenue', 'Chance',
         'Vermont Avenue','Connecticut Avenue','Jail - Just Visiting','St. Charles Place',
         'Electric Company','States Avenue','Virginia Avenue','Pennsylvania Railroad',
         'St. James Place', 'Community Chest', 'Tennessee Avenue', 'New York Avenue',
         'Free Parking','Kentucky Avenue', 'Chance', 'Indiana Avenue', 'Illinois Avenue',
         'B&O Railroad','Atlantic Avenue', 'Ventnor Avenue', 'Water Works',
         'Marvin Gardens', 'Go To Jail', 'Pacific Avenue', 'North Carolina Avenue',
         'Community Chest', 'Pennsylvania Avenue', 'Pacific Railroad', 'Chance',
         'Park Place','Luxury Tax', 'Boardwalk']

#Create Base Square Dictionary
#Properties: [Owner (0 means unowned), Cost, Payouts, Houses, Mortgaged]
Base = {1: [0,60,[2,10,30,90,160,250],0,False],
        3: [0,60,[4,20,60,180,320,450],0,False],
        5: [0,200],
        6: [0,100,[6,30,90,270,400,550],0,False],
        8: [0,100,[6,30,90,270,400,550],0,False],
        9: [0,120,[8,40,100,300,450,600],0,False],
        11: [0,140,[10,50,150,450,625,750],0,False],
        12: [0,150],
        13: [0,140,[10,50,150,450,625,750],0,False],
        14: [0,160,[12,60,180,500,700,900],0,False],
        15: [0,200],
        16: [0,180,[14,70,200,550,750,950],0,False],
        18: [0,180,[14,70,200,550,750,950],0,False],
        19: [0,200,[16,80,220,600,800,1000],0,False],
        21: [0,220,[18,90,250,700,875,1050],0,False],
        23: [0,220,[18,90,250,700,875,1050],0,False],
        24: [0,240,[20,100,300,750,925,1100],0,False],
        25: [0,200],
        26: [0,260,[22,110,330,800,975,1150],0,False],
        27: [0,260,[22,110,330,800,975,1150],0,False],
        28: [0,150],
        29: [0,280,[24,120,360,850,1025,1200],0,False],
        31: [0,300,[26,130,390,900,1100,1275],0,False],
        32: [0,300,[26,130,390,900,1100,1275],0,False],
        34: [0,320,[28,150,450,1000,1200,1400],0,False],
        35: [0,200],
        37: [0,350,[35,175,500,1100,1300,1500],0,False],
        39: [0,400,[50,200,600,1400,1700,2000],0,False],}

#Create Property Groups
Groups = {1: [[1,3],0],
          3: [[1,3],0],
          6: [[6,8,9],1],
          8: [[6,8,9],1],
          9: [[6,8,9],1],
          11: [[11,13,14],2],
          13: [[11,13,14],2],
          14: [[11,13,14],2],
          16: [[16,18,19],3],
          18: [[16,18,19],3],
          19: [[16,18,19],3],
          21: [[21,23,24],4],
          23: [[21,23,24],4],
          24: [[21,23,24],4],
          26: [[26,27,29],5],
          27: [[26,27,29],5],
          29: [[26,27,29],5],
          31: [[31,32,34],6],
          32: [[31,32,34],6],
          34: [[31,32,34],6],
          37: [[37,39],7],
          39: [[37,39],7]}

Gr = { 0: [1,3],
       1: [6,8,9],
       2: [11,13,14],
       3: [16,18,19],
       4: [21,23,24],
       5: [26,27,29],
       6: [31,32,34],
       7: [37,39]}

#Interesting Statistics Initialization
Biggest_win = 0
wins = [0,0]
Longest_game = 0

GameNo = 1
while GameNo <= Number_of_games:
    if Print_moves: print "Starting game number " + str(GameNo) + "!"
    numrolls = 0 
    #Initialize Properties Board 
    Properties = copy.deepcopy(Base)

    #Initialize Property Group Ownership
    G = [0,0,0,0,0,0,0,0]
    
    #Initialize Players: [Starting money, Starting position, # of doubles rolled on current turn, Railroad count]
    Players = [[Start_cash, 0, 0, 0],[Start_cash, 0, 0, 0]]
    
    #Initialize Chance/Community Chest
    ChC = range(16)
    shuffle(ChC)
    CcC = range(16)
    shuffle(CcC)

    #Who goes first?
    Active_player = 1
    if Randomize_first_turn: Active_player = randrange(2) + 1
    if Print_moves: print "Player " + str(Active_player) + " has the first roll!"

    #Ready to roll!
    while 1:
        #Take active player's turn
        numrolls += 1
        cd = Players[Active_player-1][2]
        if Print_moves:
            print "################ Player " + str(Active_player) + "'s Turn! ################"
            print
        Take_turn(Active_player-1)
        nd = Players[Active_player-1][2]

        #Bankruptcy Check
        if Players[Active_player-1][0] < 0:
            ###Liquidation Function###
            if Print_moves:
                print
                print
                print "##################################################"
                print
                print
            if Active_player == 1:
                wins[1]+=1
                if Print_moves: print "Game Over! Player 2 wins with $" + str(Players[1][0]) + " left to spare!"
            else:
                wins[0]+=1
                if Print_moves: print "Game Over! Player 1 wins with $" + str(Players[0][0]) + " left to spare!"
            if Print_moves: print "Game completed in " + str(numrolls) + " rolls."
            #End the current game
            if numrolls > Longest_game: Longest_game = numrolls
            if Active_player == 1 and Players[1][0] > Biggest_win: Biggest_win = Players[1][0]
            if Active_player == 2 and Players[0][0] > Biggest_win: Biggest_win = Players[0][0]
            break

        #Buy Houses (If possible)
        Buy_houses(Active_player)

        #Check if doubles rolled, if not switch active player
        if nd-cd == 0:
            Players[Active_player-1][2] = 0
            if Active_player == 1: Active_player = 2
            else: Active_player = 1
        if Print_moves:
            print
            print
        if numrolls > Tie_threshold:
            if Print_moves: print "Board stall! Game ended in a tie."
            break


    GameNo += 1

if Number_of_games > 1:
    print "Results:"
    print "Player 1 - " + str(wins[0]) + " win(s)!"
    print "Player 2 - " + str(wins[1]) + " win(s)!"
    print str(Number_of_games-wins[0]-wins[1]) + " ties! (Due to board stall)"
    print
    print "Some statistics:"
    print "Longest non-tie game - " + str(Longest_game) + " turns."
    print "Biggest winning margin - $" + str(Biggest_win)
    print "Good Game(s)!"

t1= time.time()
total = t1-t0
print
print "Run time: ", total, "seconds"
