from boto3 import resource
from boto3.dynamodb.conditions import Attr, Key
from datetime import datetime
import boto3

# Create a DynamoDB resource using the default session
dynamodbb = boto3.resource('dynamodb', region_name='us-east-2')

# Replace 'your-region' with the appropriate AWS region, e.g., 'us-west-2'
colony_table = dynamodb.Table('colony')

# Create a DynamoDB table
def save_coloy():
    response = colony_table.put_item(
    Item={
            'colony_id': '1', # Partion Key (Required and has to be unique)
            'colony_name': 'test', 
            'colony_created_at': datetime.now().isoformat(),
            'colony_enum': '954490278264311878', # Sort Key (Required)
            'colony_active_players' : [{"player_id" : '677718946270543882'}],
            'colony_ce' : 0,
            'colony_xp' : 0,
            'colony_active_market' : [{"ISOH" : 100, "SS" : 10}],
            'colony_active_npc' : [{"Sukuna" : ["CE", "RESPAWN", "SPAWNDATE"]}],
            'colony_active_mission' : [{"MISSION" : "MISSION"}],
            'colony_active_event' : [{"EVENT" : "EVENT"}]
             })
    print(f"Insert Response: {response}")
    
save_colony()


    # [ { "M" : { "name" : { "S" : "Sukuna" }, "respawn_timer" : { "S" : "100" }, "ce" : { "S" : "100" }, "spawndate" : { "S" : "10/10/10" } } } ]