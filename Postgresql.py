import psycopg2, os, json, traceback, game

from psycopg2.sql import NULL
from cogs import colonies



def save_player(player):
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS player(
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
            "name" TEXT,
            "level" INT,
            ct_level INT,
            xp BIGINT,
            cgp INT,
            skp INT,
            technique TEXT,
            inventory JSONB,
            equipment JSONB,
            tools JSONB,
            shiki JSONB,
            spirits JSONB,
            souls JSONB,
            rules JSONB,
            vows JSONB,
            BFluck INT,
            hp INT,
            max_hp INT,
            defense TEXT DEFAULT NULL,
            speed INT,
            attack INT,
            imbued INT,
            ce INT,
            max_ce INT,
            RCT BOOLEAN, 
            mode INT,
            colony_id BIGINT,
            enemy TEXT,
            hr BOOLEAN, victory_msg TEXT DEFAULT NULL,
            UNIQUE(colony_id, user_id))
            """)

    # Serialize inventory and equipment to JSON
    inventory_json = json.dumps(player.inventory)
    equipment_json = json.dumps(player.equipment)
    shikigami_json = json.dumps(player.shiki)
    spirits_json = json.dumps(player.spirits)
    tool_json = json.dumps(player.tools)
    vows_json = json.dumps(player.vows)
    rules_json = json.dumps(player.rules)
    

    colony_data = read_colony(player.colony)
    if colony_data:
        colony = colonies.Colony(**colony_data)
        colony.members.append(player.user_id)
        save_colony(colony)
        
    # Values to be inserted
    values = (player.name, player.level, player.ct_level, player.xp, player.cgp, player.skp, player.technique, inventory_json, equipment_json, tool_json, shikigami_json, spirits_json, vows_json,  rules_json, player.luck, player.user_id, player.hp, player.max_hp, player .defense, player.speed, player.attack, player.imbued, player.ce, player.max_ce, player.RCT, int(player.mode), player.colony, player.enemy, player.HR, player.victory_msg)
    print("Number of values:", len(values))
    print("Values:", values)
    query = """INSERT INTO player ("name", "level", ct_level, xp, cgp, skp, technique, inventory, equipment,user_id, hp, max_hp, defense, speed, attack, imbued, ce, max_ce, RCT, mode, colony_id, enemy, hr, victory_msg)
        VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id, colony_id) 
        DO UPDATE SET 
        name=EXCLUDED.name, 
        level=EXCLUDED.level, 
        ct_level=EXCLUDED.ct_level, 
        xp=EXCLUDED.xp, 
        cgp=EXCLUDED.cgp, 
        skp=EXCLUDED.skp, 
        technique=EXCLUDED.technique, 
        inventory=EXCLUDED.inventory, 
        equipment=EXCLUDED.equipment, 
        hp=EXCLUDED.hp, 
        max_hp=EXCLUDED.max_hp, 
        defense=EXCLUDED.defense, 
        speed=EXCLUDED.speed, 
        attack=EXCLUDED.attack, 
        imbued=EXCLUDED.imbued, 
        ce=EXCLUDED.ce, 
        max_ce=EXCLUDED.max_ce, 
        RCT=EXCLUDED.rct, 
        mode=EXCLUDED.mode, 
        enemy=EXCLUDED.enemy, 
        hr=EXCLUDED.hr, 
        victory_msg=EXCLUDED.victory_msg"""
    
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

    return



def read_player(user_id, guild_id):
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute("SELECT * FROM player WHERE user_id = %s AND colony_id = %s", (user_id, guild_id))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        # Ensure data is valid before parsing JSON
        inventory_data = json.loads(result[9]) if isinstance(result[9], str) else result[9]
        equipment_data = json.loads(result[10]) if isinstance(result[10], str) else result[10]
        player_data = {
            'user_id': result[1],
            'name': result[2],
            'level': result[3],
            'ct_level': result[4],
            'xp': result[5],
            'cgp': result[6],
            'skp': result[7],
            'technique': result[8],
            'inventory': inventory_data,
            'equipment': equipment_data,
            'hp': result[11],
            'max_hp': result[12],
            'defense': result[13],
            'speed': result[14],
            'attack': result[15],
            'imbued': result[16],
            'ce': result[17],
            'max_ce': result[18],
            'RCT': result[19],
            'mode': result[20],
            'colony': result[21],
            'enemy': result[22],
            'HR': result[23],
            'victory_msg':result[24]
        }
        return player_data
    else:
        return None


    
    
def save_colony(colony):
    ai_list = json.dumps(colony.ai)
    unique_members = list(set(colony.members))
    values = (colony.id, colony.name, colony.owner, json.dumps(unique_members), ai_list, colony.xp, colony.colony_color)

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS colony(
        id SERIAL PRIMARY KEY,
        colony_id BIGINT,
        name TEXT,
        owner BIGINT,
        members JSONB,
        ai JSONB,
        xp BIGINT,
        colony_color TEXT,
        UNIQUE(colony_id))
        """)
    query = """
           INSERT INTO colony (colony_id, name, owner, members, ai, xp, colony_color)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
           ON CONFLICT (colony_id) DO UPDATE SET
               name = EXCLUDED.name,
               owner = EXCLUDED.owner,
               members = EXCLUDED.members,
               ai = EXCLUDED.ai,
               xp = EXCLUDED.xp,
               colony_color = EXCLUDED.colony_color
        """
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()

def read_colony(colony_id):

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute("SELECT * FROM colony WHERE colony_id = %s", (colony_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
    
        players_data = result[4]
        ai_data = result[5]
        # This is the corrected section using the ternary operator.
        ai_data = json.loads(ai_data) if isinstance(ai_data, str) else result[5]
        players_data = json.loads(players_data) if isinstance(players_data, str) else result[4]
    
        colony_data = {
            'id': result[1],  
            'name': result[2],
            'owner': result[3],
            'members': players_data,
            'ai': ai_data,
            'xp': result[6],
            'colony_color': result[7]
        }
        return colony_data
    else:
        return None
        
def update_colony(colony_id, column, value):
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    if isinstance(value, (list, dict)):
        value = json.dumps(value)  # Ensure JSON serialization before use
    query = f"UPDATE colony SET {column} = %s WHERE colony_id = %s;"  # Corrected column_id usage
    values = (value, colony_id)
    print(f"Updating colony id {colony_id}: {column} = {value}")
    cur.execute(query, values)
    conn.commit()
    cur.close()
    conn.close()
    

    
def delete_from_colony(colony_id, column, value):
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        colony_data = read_colony(colony_id)
        if colony_data:
            if column == "members":
                member_list = colony_data["members"]
                if value in member_list:
                    for m in member_list:
                        if m == value:
                            member_list.remove(m)
                            continue
                    new_members_data = json.dumps(member_list)
                    # Remove player from the colony table by user_id and colony_id
                    query1 = '''UPDATE colony SET members = %s WHERE colony_id = %s;'''
                    query2 = '''DELETE FROM player WHERE user_id = %s AND colony_id = %s;'''
                    values1 = (new_members_data, colony_id)
                    values2 = (value, colony_id)
                    cur.execute(query1, values1)
                    cur.execute(query2, values2)
            elif column == "ai":
                ai_list = colony_data["ai"]
                if value in ai_list:
                    ai_list.remove(value)
                    new_ai_data = json.dumps(ai_list)
                    query = "UPDATE colony SET ai = %s WHERE colony_id = %s"
                    cur.execute(query, (new_ai_data, colony_id))
            else:
                query = f"DELETE FROM colony WHERE colony_id = %s AND {column} = %s"
                cur.execute(query, (colony_id, value))
            conn.commit()
            cur.close()
            conn.close()
        else:
            cur.close()
            conn.close()
            return None
    except Exception as e:
        traceback.print_exc()
        
def save_lobby(host_id, colony_id, name, players, t_count, targets=None, turn=None, locked=False, invites=None, mode=None, ready=None, team1=None, team2=None, team1q = None, team2q = None, mark=None):
    try:
        con = psycopg2.connect(os.environ['DATABASE_URL'])
        print(f"Saving targets to LOBBY: {targets}")
        cur = con.cursor()
        target_list = None
        if targets:
            target_list = []
            for t in targets:
                if isinstance(t, game.Enemy):
                    tango = t.to_dict()
                    target_list.append(tango)
                elif isinstance(t, game.Character):
                    tango = t.to_dict()
                    target_list.append(tango)
                else:
                    target_list.append(t)

        values = (host_id, colony_id, json.dumps(players), turn, json.dumps(target_list), name,locked, json.dumps(invites), mode, json.dumps(ready), json.dumps(team1), json.dumps(team2), json.dumps(team1q), json.dumps(team2q), json.dumps(mark), t_count)
        cur.execute(
            """CREATE TABLE IF NOT EXISTS lobby(
        id SERIAL PRIMARY KEY,host_id BIGINT, colony_id BIGINT, players JSONB, turn BIGINT DEFAULT NULL, target JSONB DEFAULT NULL, name TEXT, locked BOOLEAN DEFAULT false, invites JSONB DEFAULT NULL, mode INT DEFAULT NULL, ready JSONB DEFAULT NULL, team1 JSONB DEFAULT NULL, team2 JSONB DEFAULT NULL, team1q JSONB DEFAULT NULL, team2q JSONB DEFAULT NULL, mark JSONB DEFAULT NULL, t_count INT, UNIQUE(host_id, colony_id))"""
        )
        query2 = """INSERT INTO lobby ("host_id", "colony_id", "players", "turn", "target", "name", "locked", "invites", "mode", "ready", "team1", "team2", "team1q", "team2q", "mark", "t_count")
        VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (host_id, colony_id) DO UPDATE SET players=EXCLUDED.players, turn=EXCLUDED.turn, target=EXCLUDED.target, name=EXCLUDED.name, locked=EXCLUDED.locked, invites=EXCLUDED.invites, mode=EXCLUDED.mode, ready=EXCLUDED.ready, team1=EXCLUDED.team1, team2=EXCLUDED.team2, team1q=EXCLUDED.team1q, team2q=EXCLUDED.team2q, mark=EXCLUDED.mark, t_count=EXCLUDED.t_count"""
        cur.execute(query2, values)
        con.commit()  # Commit the changes to the database
        cur.close()
        con.close()
        return
    except Exception as e:
        print(f"Error in save_lobby() function: {e}")
        traceback.print_exc()
        
def read_lobby(host_id, colony_id):
    con = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = con.cursor()
    values = (host_id, colony_id)
    cur.execute('SELECT * FROM lobby WHERE host_id = %s AND colony_id=%s', values)
    result = cur.fetchone()
    cur.close()
    con.close()
    if result: 
        lobby_data = {
            'host': result[1],
            'colony': result[2],
            'players': result[3],
            'turn': result[4],
            'targets': result[5],
            'name': result[6],
            'locked': result[7],
            'invites': result[8],
            'mode': result[9],
            'ready': result[10],
            'team1': result[11],
            'team2': result[12],
            'team1q' : result[13],
            'team2q' : result[14],
            'mark' : result[15],
            't_count' : result[16]
        }
        return lobby_data

def delete_from_lobby(host_id, colony_id, user=None):
    con = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = con.cursor()
    values = (host_id, colony_id)
    lobby = read_lobby(host_id, colony_id)
    if not lobby:
        cur.close()
        con.close()
        return
    if user:
        players = lobby['players'] or []
        team1 = lobby['team1'] or []
        team2 = lobby['team2'] or []
        if user in players:
            players.remove(user)
        if user in team1:
            team1.remove(user)
        if user in team2:
            team2.remove(user)
        if len(players) == 0:
            values1 = (host_id, colony_id)
            query1 = 'DELETE FROM lobby WHERE host_id = %s AND colony_id = %s'
            cur.execute(query1, values1)
            con.commit()
            cur.close()
            con.close()
            return
        new_values = (json.dumps(players), json.dumps(team1), json.dumps(team2), host_id, colony_id)
        query = 'UPDATE lobby SET players = %s, team1 = %s, team2 = %s WHERE host_id = %s AND colony_id = %s'
        cur.execute(query, new_values)
        con.commit()
        cur.close()
        con.close()
        return

    else:
        query = 'DELETE FROM lobby WHERE host_id = %s AND colony_id = %s'
        cur.execute(query, values)

    con.commit()
    cur.close()
    con.close()


        
        
        