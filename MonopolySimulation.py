import time
import copy
from random import randrange, shuffle
t0 = time.time()

#Changable Parameters
Start_cash = 1500           #How much money each player starts with
Dice_sides = 6              #How many sides to the dice rolled
Pause = False               #If true, program will wait for input after each turn
Print_moves = False          #If false, only prints end summary
Number_of_games = 1000         #Total number of games to simulate
Randomize_first_turn = True #If false, Player 1 has first turn always
Max_houses = [5,5]          #Max number of houses [Player 1, Player2] will place on a given property
GoMoney = 200               #Amount recieved for passing Go
Tie_threshold = 5000        #Max number of turns in a game before a tie is declared
Min_bank = [100,100]        #Player [1, 2] will not buy something if it will put them below this value
Will_bail = [True, True]    #If True, Player [1, 2] will pay $50 to immediately get out of jail

#Takes player as input, rolls the dice and calls the appropriate function.
def Take_turn(p):
    r1 = randrange(Dice_sides)
    r2 = randrange(Dice_sides)
    #Jail Check
    if Players[p][5] > 0:
        if GooJ[p] > 0:
            GooJ[p] -= 1
            if Print_moves: print "Get out of jail free card used!"
            Players[p][5] = 0
        elif Players[p][5] == 1:
            Players[p][5] = 0
            Players[p][0] -= 50
            if Print_moves: print "$50 paid as bail. Out of Jail!"
        else:
            if Will_bail[p] and Players[p][0] >= 50+Min_bank[p]:
                Players[p][5] = 0
                Players[p][0] -= 50
                if Print_moves: print "$50 paid as bail. Out of Jail!"
            else:
                Players[p][5] -= 1
                if r1 == r2:
                    if Print_moves: print "Doubles rolled! Out of Jail!"
                else:
                    if Print_moves: print "Remaining in Jail..."
                    return
    if r1 == r2:
        if Players[p][2] == 2:
            if Print_moves: print "Doubles three times in a row? Go to Jail!"
            GtJ(p)
            return
        Players[p][2] += 1
    if Print_moves:
        print "Player " + str(p+1) + " rolls a " + str(r1+1) + " and a " + str(r2+1) + ", landing on " + Board[(Players[p][1]+r1+r2+2)%40] + "."
    if (Players[p][1]+r1+r2+2)%40 <= Players[p][1]:
        Players[p][0]+=GoMoney
        if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
    Players[p][1] = (Players[p][1]+r1+r2+2)%40
    Square_effect(p,r1+r2+2)
        
        
#Sends the player to jail.
def GtJ(p):
    Players[p][1] = 10
    Players[p][5] = 3
    return

#Processes the effect of landing on a given square.
def Square_effect(p,m):
    x = Players[p][1]
    #Handle all properties
    if x in Properties:
        #If unowned
        if Properties[x][0] == 0:
            if Players[p][0] >= Properties[x][1]+Min_bank[p]:
                Players[p][0] -= Properties[x][1]
                Properties[x][0] = p+1
                if Print_moves: print "Property Purchased for $" + str(Properties[x][1]) + ". $" + str(Players[p][0]) + " remaining."
                if x not in [5,12,15,25,28,35]: Group_check(p)
                else:
                    if x not in [12,28]:
                        #Railroad
                        Players[p][3] += 1
                    else:
                        #Utility
                        Players[p][4] += 1
                return
            else:
                if Print_moves: print "Purchase Declined - Not enough money!"
                return
        if Properties[x][0] == p+1 and Print_moves: print "Property already owned."
        #If owned by other player and not a Railroad/Utility
        if Properties[x][0] != p+1 and x not in [5,12,15,25,28,35]:
            if Properties[x][4]:
                if Print_moves: print "Property owned by other player, but is mortgaged!"
                return
            else:
                payout = Properties[x][2][Properties[x][3]]
                if G[Groups[x][1]] != 0 and G[Groups[x][1]] != p+1 and Properties[x][3] == 0:
                    #Account for double rent when group owned
                    payout += payout
                Players[p][0] -= payout
                if p == 0: Players[1][0] += payout
                else: Players[0][0] += payout
                if Print_moves:
                    print "Property owned by other player; $" + str(payout) + " Paid. $" + str(Players[p][0]) + " remaining."
                return
        #If owned by other player and a Railroad
        if Properties[x][0] != p+1 and x in [5,15,25,35]:
            if Properties[x][4]:
                if Print_moves: print "Property owned by other player, but is mortgaged!"
                return
            else:
                if p == 0: payout = (2**(Players[1][3]-1))*25
                else: payout = (2**(Players[0][3]-1))*25
                Players[p][0] -= payout
                if p == 0: Players[1][0] += payout
                else: Players[0][0] += payout
                if Print_moves:
                    print "Property owned by other player; $" + str(payout) + " Paid. $" + str(Players[p][0]) + " remaining."
                return
        #If owned by other player and a Utility
        if Properties[x][0] != p+1 and x in [12,28]:
            if Properties[x][4]:
                if Print_moves: print "Property owned by other player, but is mortgaged!"
                return
            else:
                if p == 0:
                    if Players[1][4] == 1: payout = 4*m
                    else: payout = 10*m
                else:
                    if Players[0][4] == 1: payout = 4*m
                    else: payout = 10*m
                Players[p][0] -= payout
                if p == 0: Players[1][0] += payout
                else: Players[0][0] += payout
                if Print_moves:
                    print "Property owned by other player; $" + str(payout) + " Paid. $" + str(Players[p][0]) + " remaining."
                return
    #Go To Jail
    if x == 30:
        GtJ(p)
        if Print_moves: print "Sent to jail!"
        return
    #Luxury Tax
    if x == 38:
        Players[p][0] -= 75
        if Print_moves: print "Pay $75! $" + str(Players[p][0]) + " remaining."
    #Chance
    if x in [7,22,36]:
        Chance(p, ChC[CurCh[0]])
        CurCh[0] += 1
        if CurCh[0] == 16:
            shuffle(ChC)
            CurCh[0] = 0
    #Community Chest
    if x in [2,17,33]:
        Community_chest(p, CcC[CurCc[0]])
        CurCc[0] += 1
        if CurCc[0] == 16:
            shuffle(CcC)
            CurCc[0] = 0
                
    return

#Checks to see if a property group is owned by a single player.
def Group_check(p):
    x = Players[p][1]
    for i in Groups[x][0]:
        if Properties[i][0] != p+1:
            return
    G[Groups[x][1]] = p+1
    return

#Handles the buying of houses
def Buy_houses(p):
    for i in range(8):
        if G[i] == p:
            while Players[p-1][0] >= ((i/2)*50+50)+Min_bank[p-1]:
                for j in range(len(Gr[i])-1,-1,-1):
                    x = Gr[i][j]
                    if j == len(Gr[i])-1:
                        if Properties[x][3] == Properties[Gr[i][(j+1)%len(Gr[i])]][3]:
                            if Players[p-1][0] >= (i/2)*50+50+Min_bank[p-1] and Properties[x][3] !=Max_houses[p-1]:
                                Players[p-1][0] -= (i/2)*50+50
                                Properties[x][3] += 1
                                if Print_moves: print "House bought on " + Board[x] + ". Currently at " + str(Properties[x][3]) + " houses. $" + str(Players[p-1][0]) + " remaining."
                    else:
                        if Properties[x][3] < Properties[Gr[i][(j+1)%len(Gr[i])]][3]:
                            if Players[p-1][0] >= (i/2)*50+50+Min_bank[p-1] and Properties[x][3] !=Max_houses[p-1]:
                                Players[p-1][0] -= (i/2)*50+50
                                Properties[x][3] += 1
                                if Print_moves: print "House bought on " + Board[x] + ". Currently at " + str(Properties[x][3]) + " houses. $" + str(Players[p-1][0]) + " remaining."
                if Properties[Gr[i][0]][3] == Max_houses[p-1]: break

#Handles the effects of the 16 Chance cards.
def Chance(p, n):
    if n == 0:
        if Print_moves: print "Advance to Boardwalk!"
        Players[p][1] = 39
        Square_effect(p,0)
    if n == 1:
        if Print_moves: print "Advance to Illinois Avenue!"
        if Players[p][1] == 36:
            Players[p][0]+=GoMoney
            if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
        Players[p][1] = 24
        Square_effect(p,0)
    if n == 2 or n == 15:  
        if Print_moves: print "Advance to nearest Railroad!"
        if Players[p][1] == 7:
            Players[p][1] = 15
            Square_effect(p,0)
        if Players[p][1] == 22:
            Players[p][1] = 25
            Square_effect(p,0)
        if Players[p][1] == 36:
            Players[p][1] = 5
            Players[p][0]+=GoMoney
            if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
            Square_effect(p,0)
    if n == 3:
        if Print_moves: print "Bank pays you dividend of $50!"
        Players[p][0] += 50
    if n == 4:
        if Print_moves: print "Advance to nearest Utility!"
        if Players[p][1] == 7:
            Players[p][1] = 12
            r1 = randrange(Dice_sides)
            r2 = randrange(Dice_sides)
            if Print_moves: print "Rolled a " + str(r1+1) + " and a " + str(r2+1) + "!"
            Square_effect(p,r1+r2+2)
        if Players[p][1] == 22:
            Players[p][1] = 28
            r1 = randrange(Dice_sides)
            r2 = randrange(Dice_sides)
            if Print_moves: print "Rolled a " + str(r1+1) + " and a " + str(r2+1) + "!"
            Square_effect(p,r1+r2+2)
        if Players[p][1] == 36:
            Players[p][1] = 12
            Players[p][0]+=GoMoney
            if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
            r1 = randrange(Dice_sides)
            r2 = randrange(Dice_sides)
            if Print_moves: print "Rolled a " + str(r1+1) + " and a " + str(r2+1) + "!"
            Square_effect(p,r1+r2+2)
    if n == 5:
        if Print_moves: print "Building and loan matures! Collect  $150!"
        Players[p][0] += 150
    if n == 6:
        if Print_moves: print "Elected chairman of the board! Pay $50 to other player!"
        Players[p][0] -= 50
        if p == 0: Players[1][0] += 50
        else: Players[0][0] += 50
    if n == 7:
        if Print_moves: print "General property repairs! Pay 25$ for each house!"
        houses = 0
        for i in Properties:
            if not i in [5,12,15,25,28,35]:
                if Properties[i][0] == p+1:
                    houses += Properties[i][3]
                    if Properties[i][3] == 5:
                        houses -= 1
        if Print_moves: print "$" + str(houses*25) + " paid!"
        Players[p][0] -= houses*25
    if n == 8:
        if Print_moves: print "Take a ride on Reading Railroad!"
        Players[p][1] = 5
        Players[p][0]+=GoMoney
        if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
        Square_effect(p,0)
    if n == 9:
        if Print_moves: print "Advance to Go! Collect $" + str(GoMoney) + "!"
        Players[p][0]+=GoMoney
        Players[p][1] = 0
    if n == 10:
        if Print_moves: print "Advance to St. Charles Place!"
        if Players[p][1] in [22,36]:
            Players[p][0]+=GoMoney
            if Print_moves: print "Go passed! Collect $" + str(GoMoney) + "!"
        Players[p][1] = 11
        Square_effect(p,0)  
    if n == 11:
        if Print_moves: print "Get out of jail free card!"
        GooJ[p] += 1
    if n == 12:
        if Print_moves: print "Go directly to jail! Do not pass go, do not collect $200!"
        GtJ(p)
    if n == 13:
        if Print_moves: print "Pay poor tax of $15!"
        Players[p][0] -= 15
    if n == 14:
        if Print_moves: print "Go back 3 spaces, landing on " + Board[(Players[p][1]-3)%40] + "!"
        Players[p][1] = (Players[p][1]-3)%40
        Square_effect(p,0)

#Handles the effects of the 16 Community Chest cards.
def Community_chest(p, n):
    if n == 0:
        if Print_moves: print "From sale of stock you get $45!"
        Players[p][0] += 45
    if n == 1:
        if Print_moves: print "Receive for services $25!"
        Players[p][0] += 25
    if n == 2:
        if Print_moves: print "Doctor's fee, pay $50!"
        Players[p][0] -= 50
    if n == 3:
        if Print_moves: print "Life insurance matures, collect $100!"
        Players[p][0] += 100
    if n == 4:
        if Print_moves: print "Bank error in your favor, collect $200!"
        Players[p][0] += 200
    if n == 5:
        if Print_moves: print "Income tax refund, collect $20!"
        Players[p][0] += 20
    if n == 6:
        if Print_moves: print "You are assessed for street repairs, pay $40 for each house, $115 for each hotel!"
        pay = 0
        for i in Properties:
            if not i in [5,12,15,25,28,35]:
                if Properties[i][0] == p+1:
                    if Properties[i][3] <= 4:
                        pay += Properties[i][3]*40
                    if Properties[i][3] == 5:
                        pay += 115
        if Print_moves: print "$" + str(pay) + " paid!"
        Players[p][0] -= pay
    if n == 7:
        if Print_moves: print "Pay hospital $100!"
        Players[p][0] -= 100
    if n == 8:
        if Print_moves: print "You have won second prize in a beauty contest, collect $10!"
        Players[p][0] += 10
    if n == 9:
        if Print_moves: print "Advance to Go! Collect $" + str(GoMoney) + "!"
        Players[p][0]+=GoMoney
        Players[p][1] = 0
    if n == 10:
        if Print_moves: print "Grand opera opening! Collect $50 from other player!"
        Players[p][0] += 50
        if p == 0: Players[1][0] -= 50
        else: Players[0][0] -= 50
    if n == 11:
        if Print_moves: print "Get out of jail free card!"
        GooJ[p] += 1
    if n == 12:
        if Print_moves: print "Go directly to jail! Do not pass go, do not collect $200!"
        GtJ(p)
    if n == 13:
        if Print_moves: print "Pay school tax of $150!"
        Players[p][0] -= 150
    if n == 14:
        if Print_moves: print "Xmas fun matures, collect $100!"
        Players[p][0] += 100
    if n == 15:
        if Print_moves: print "You inherit $100!"
        Players[p][0] += 100

#Attempts to sell Properties and Houses in order to get back to a positive amount of money
def Liquidate(p):
    if p == 0: op = 1
    else: op = 0
    P_list = []
    for i in Properties:
        if Properties[i][0] == p+1 and not Properties[i][4]:
            P_list.append(i)
    #First mortgages properties that are in groups you can never own
    for j in P_list:
        if j in Groups:
            for k in Groups[j][0]:
                if Properties[k][0] == op:
                    P_list.remove(j)
                    Properties[j][4] = True
                    Players[p][0] += Properties[j][1]/2
                    if Print_moves: print Board[j] + " mortgaged for $" + str(Properties[j][1]/2) + "."
                    if Players[p][0] >= 0:
                        return
                    break
    #Second mortgages Utilities
    if 12 in P_list:
        P_list.remove(12)
        Players[p][0] += 75
        Players[p][4] -= 1
        Properties[12][4] = True
        if Print_moves: print Board[12] + " mortgaged for $75."
        if Players[p][0] >= 0:
            return
    if 28 in P_list:
        P_list.remove(28)
        Players[p][0] += 75
        Players[p][4] -= 1
        Properties[28][4] = True
        if Print_moves: print Board[28] + " mortgaged for $75."
        if Players[p][0] >= 0:
            return
    #Third mortgages Railroads
    if 35 in P_list:
        P_list.remove(35)
        Players[p][0] += 100
        Players[p][3] -= 1
        Properties[35][4] = True
        if Print_moves: print Board[35] + " mortgaged for $100."
        if Players[p][0] >= 0:
            return
    if 25 in P_list:
        P_list.remove(25)
        Players[p][0] += 100
        Players[p][3] -= 1
        Properties[25][4] = True
        if Print_moves: print Board[25] + " mortgaged for $100."
        if Players[p][0] >= 0:
            return
    if 15 in P_list:
        P_list.remove(15)
        Players[p][0] += 100
        Players[p][3] -= 1
        Properties[15][4] = True
        if Print_moves: print Board[15] + " mortgaged for $100."
        if Players[p][0] >= 0:
            return
    if 5 in P_list:
        P_list.remove(5)
        Players[p][0] += 100
        Players[p][3] -= 1
        Properties[5][4] = True
        if Print_moves: print Board[5] + " mortgaged for $100."
        if Players[p][0] >= 0:
            return
    #Fourth mortgages properties you don't have the whole group of, but could potentially
    Gs = []
    """
    for y in range(8):
        if G[y] == p+1:
            Gs.append(Gr[y])
    
    for k in P_list:
        for l in Gs:
            if k in l:
                P_list.remove(k)
    for k in P_list:
        Players[p][0] += Properties[k][1]/2
        Properties[k][4] = True
        if Print_moves: print Board[k] + " mortgaged for $" + str(Properties[k][1]/2) + "."
        if Players[p][0] >= 0:
            return
    """
    #Fifth sells houses (least valuable first)
    for g in Gs:
        done = True
        while done:
            done = False
            for j in range(len(g)):
                if Properties[g[j]][3] >= Properties[g[(j+1)%len(g)]][3] and Properties[g[j]][3] > 0:
                    done = True
                    Properties[g[j]][3] -= 1
                    Players[p][0] += (g[j]/10)*25+25
                    if Print_moves: print "House on " + Board[g[j]] + " sold for " + str((g[j]/10)*25+25) + "."
                    if Players[p][0] >= 0:
                        return  
    #Fifth mortgages properties in groups you own
    return
       

    
#Position Labels
Board = ['Go','Mediterranean Avenue','Community Chest','Baltic Avenue',
         'Income Tax', 'Reading Railroad','Oriental Avenue', 'Chance',
         'Vermont Avenue','Connecticut Avenue','Jail - Just Visiting','St. Charles Place',
         'Electric Company','States Avenue','Virginia Avenue','Pennsylvania Railroad',
         'St. James Place', 'Community Chest', 'Tennessee Avenue', 'New York Avenue',
         'Free Parking','Kentucky Avenue', 'Chance', 'Indiana Avenue', 'Illinois Avenue',
         'B&O Railroad','Atlantic Avenue', 'Ventnor Avenue', 'Water Works',
         'Marvin Gardens', 'Go To Jail', 'Pacific Avenue', 'North Carolina Avenue',
         'Community Chest', 'Pennsylvania Avenue', 'Short Line Railroad', 'Chance',
         'Park Place','Luxury Tax', 'Boardwalk']

#Create Base Square Dictionary
#Properties: [Owner (0 means unowned), Cost, Payouts, Houses, Mortgaged]
Base = {1: [0,60,[2,10,30,90,160,250],0,False],
        3: [0,60,[4,20,60,180,320,450],0,False],
        5: [0,200,[],0,False],
        6: [0,100,[6,30,90,270,400,550],0,False],
        8: [0,100,[6,30,90,270,400,550],0,False],
        9: [0,120,[8,40,100,300,450,600],0,False],
        11: [0,140,[10,50,150,450,625,750],0,False],
        12: [0,150,[],0,False],
        13: [0,140,[10,50,150,450,625,750],0,False],
        14: [0,160,[12,60,180,500,700,900],0,False],
        15: [0,200,[],0,False],
        16: [0,180,[14,70,200,550,750,950],0,False],
        18: [0,180,[14,70,200,550,750,950],0,False],
        19: [0,200,[16,80,220,600,800,1000],0,False],
        21: [0,220,[18,90,250,700,875,1050],0,False],
        23: [0,220,[18,90,250,700,875,1050],0,False],
        24: [0,240,[20,100,300,750,925,1100],0,False],
        25: [0,200,[],0,False],
        26: [0,260,[22,110,330,800,975,1150],0,False],
        27: [0,260,[22,110,330,800,975,1150],0,False],
        28: [0,150,[],0,False],
        29: [0,280,[24,120,360,850,1025,1200],0,False],
        31: [0,300,[26,130,390,900,1100,1275],0,False],
        32: [0,300,[26,130,390,900,1100,1275],0,False],
        34: [0,320,[28,150,450,1000,1200,1400],0,False],
        35: [0,200,[],0,False],
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
    
    #Initialize Players: [Money, Position, # of doubles rolled on current turn, Railroad count, Utility count, Turns left in jail]
    Players = [[Start_cash, 0, 0, 0, 0, 0],[Start_cash, 0, 0, 0, 0, 0]]
    
    #Initialize Chance/Community Chest
    ChC = range(16)
    shuffle(ChC)
    CcC = range(16)
    shuffle(CcC)
    CurCh = [0]
    CurCc = [0]

    #Initialize Get out of Jail free cards
    GooJ = [0,0]

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
            Liquidate(Active_player-1)
            if Players[Active_player-1][0] < 0:
                if Print_moves:
                    print "Current money: $" + str(Players[Active_player-1][0]) + "."
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
            else:
                if Print_moves: print "Current money: $" + str(Players[Active_player-1][0]) + "."

        #Buy Houses (If possible)
        Buy_houses(Active_player)

        #Check if doubles rolled, if not switch active player
        if nd-cd == 0:
            Players[Active_player-1][2] = 0
            if Active_player == 1: Active_player = 2
            else: Active_player = 1
        if Print_moves and not Pause:
            print
            print
        if numrolls > Tie_threshold:
            if Print_moves: print "Board stall! Game ended in a tie."
            break
        if Pause: raw_input()


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
